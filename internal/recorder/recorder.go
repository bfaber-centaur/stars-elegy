package recorder

import (
	"bufio"
	"context"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"log"
	"os"
	"path/filepath"
	"strconv"
	"strings"
	"time"

	"stars-elegy/internal/starsfile"
)

const DefaultPollInterval = 100 * time.Millisecond

type Config struct {
	WatchDir     string
	OutDir       string
	PollInterval time.Duration
}

type Observation struct {
	RecordedAt time.Time `json:"recorded_at"`
	GameID     uint32    `json:"game_id"`
	Turn       uint16    `json:"turn"`
	Year       int       `json:"year"`
	SHA256     string    `json:"sha256"`
	SourceFile string    `json:"source_file"`
	File       string    `json:"file"`
}

type candidate struct {
	hash        [sha256.Size]byte
	stableReads int
	attempted   bool
}

type turnKey struct {
	gameID uint32
	turn   uint16
}

type Recorder struct {
	cfg        Config
	logger     *log.Logger
	candidates map[string]candidate
	seenHashes map[string]struct{}
	turnHashes map[turnKey]map[string]struct{}
	latestTurn map[uint32]uint16
	hasLatest  map[uint32]bool
}

func New(cfg Config, logger *log.Logger) (*Recorder, error) {
	if cfg.WatchDir == "" {
		return nil, errors.New("watch directory is required")
	}
	if cfg.OutDir == "" {
		return nil, errors.New("output directory is required")
	}
	if cfg.PollInterval <= 0 {
		cfg.PollInterval = DefaultPollInterval
	}
	if logger == nil {
		logger = log.New(io.Discard, "", 0)
	}

	watchDir, err := filepath.Abs(cfg.WatchDir)
	if err != nil {
		return nil, fmt.Errorf("resolve watch directory: %w", err)
	}
	outDir, err := filepath.Abs(cfg.OutDir)
	if err != nil {
		return nil, fmt.Errorf("resolve output directory: %w", err)
	}
	cfg.WatchDir = watchDir
	cfg.OutDir = outDir

	info, err := os.Stat(cfg.WatchDir)
	if err != nil {
		return nil, fmt.Errorf("stat watch directory: %w", err)
	}
	if !info.IsDir() {
		return nil, fmt.Errorf("watch path %q is not a directory", cfg.WatchDir)
	}
	if err := os.MkdirAll(cfg.OutDir, 0o755); err != nil {
		return nil, fmt.Errorf("create output directory: %w", err)
	}

	r := &Recorder{
		cfg:        cfg,
		logger:     logger,
		candidates: make(map[string]candidate),
		seenHashes: make(map[string]struct{}),
		turnHashes: make(map[turnKey]map[string]struct{}),
		latestTurn: make(map[uint32]uint16),
		hasLatest:  make(map[uint32]bool),
	}
	if err := r.loadObservations(); err != nil {
		return nil, err
	}
	return r, nil
}

func (r *Recorder) Run(ctx context.Context) error {
	if err := r.scanOnce(); err != nil {
		return err
	}

	ticker := time.NewTicker(r.cfg.PollInterval)
	defer ticker.Stop()

	for {
		select {
		case <-ctx.Done():
			return nil
		case <-ticker.C:
			if err := r.scanOnce(); err != nil {
				return err
			}
		}
	}
}

func (r *Recorder) scanOnce() error {
	entries, err := os.ReadDir(r.cfg.WatchDir)
	if err != nil {
		return fmt.Errorf("read watch directory: %w", err)
	}

	present := make(map[string]struct{})
	for _, entry := range entries {
		if entry.IsDir() || !strings.EqualFold(filepath.Ext(entry.Name()), ".hst") {
			continue
		}

		path := filepath.Join(r.cfg.WatchDir, entry.Name())
		present[path] = struct{}{}

		data, err := os.ReadFile(path)
		if err != nil {
			r.logger.Printf("warning: read %s: %v", entry.Name(), err)
			delete(r.candidates, path)
			continue
		}
		hash := sha256.Sum256(data)

		c, ok := r.candidates[path]
		if !ok || c.hash != hash {
			c = candidate{hash: hash, stableReads: 1}
		} else {
			c.stableReads++
		}

		if c.stableReads >= 2 && !c.attempted {
			c.attempted = true
			if err := r.accept(entry.Name(), data, hash); err != nil {
				r.logger.Printf("warning: reject stable %s: %v", entry.Name(), err)
			}
		}
		r.candidates[path] = c
	}

	for path := range r.candidates {
		if _, ok := present[path]; !ok {
			delete(r.candidates, path)
		}
	}
	return nil
}

func (r *Recorder) accept(sourceName string, data []byte, hash [sha256.Size]byte) error {
	hashString := hex.EncodeToString(hash[:])
	if _, ok := r.seenHashes[hashString]; ok {
		return nil
	}

	header, err := starsfile.ParseHeader(data)
	if err != nil {
		return fmt.Errorf("parse HST header: %w", err)
	}

	key := turnKey{gameID: header.GameID, turn: header.Turn}
	if hashes := r.turnHashes[key]; len(hashes) > 0 {
		if _, duplicate := hashes[hashString]; !duplicate {
			r.logger.Printf("WARNING: game %d turn %d has multiple distinct HST states", header.GameID, header.Turn)
		}
	}
	if r.hasLatest[header.GameID] && header.Turn > r.latestTurn[header.GameID]+1 {
		r.logger.Printf("WARNING: game %d missed turn(s): last=%d now=%d", header.GameID, r.latestTurn[header.GameID], header.Turn)
	}

	gameDir := filepath.Join(r.cfg.OutDir, strconv.FormatUint(uint64(header.GameID), 10))
	rawDir := filepath.Join(gameDir, "raw")
	if err := os.MkdirAll(rawDir, 0o755); err != nil {
		return fmt.Errorf("create raw snapshot directory: %w", err)
	}

	stem := safeStem(strings.TrimSuffix(sourceName, filepath.Ext(sourceName)))
	archiveName := fmt.Sprintf("%d-%s-%s.HST", header.Year, stem, hashString[:8])
	archivePath := filepath.Join(rawDir, archiveName)
	if err := writeSnapshot(archivePath, data, hash); err != nil {
		return err
	}

	relPath, err := filepath.Rel(r.cfg.OutDir, archivePath)
	if err != nil {
		return fmt.Errorf("make archive path relative: %w", err)
	}
	obs := Observation{
		RecordedAt: time.Now().UTC(),
		GameID:     header.GameID,
		Turn:       header.Turn,
		Year:       header.Year,
		SHA256:     hashString,
		SourceFile: sourceName,
		File:       filepath.ToSlash(relPath),
	}
	if err := appendObservation(filepath.Join(gameDir, "observations.jsonl"), obs); err != nil {
		return err
	}

	r.index(obs)
	r.logger.Printf("recorded game=%d turn=%d year=%d source=%s sha256=%s", header.GameID, header.Turn, header.Year, sourceName, hashString[:8])
	return nil
}

func (r *Recorder) loadObservations() error {
	entries, err := os.ReadDir(r.cfg.OutDir)
	if err != nil {
		return fmt.Errorf("read output directory: %w", err)
	}

	for _, entry := range entries {
		if !entry.IsDir() {
			continue
		}
		path := filepath.Join(r.cfg.OutDir, entry.Name(), "observations.jsonl")
		file, err := os.Open(path)
		if errors.Is(err, os.ErrNotExist) {
			continue
		}
		if err != nil {
			return fmt.Errorf("open %s: %w", path, err)
		}

		scanner := bufio.NewScanner(file)
		line := 0
		for scanner.Scan() {
			line++
			var obs Observation
			if err := json.Unmarshal(scanner.Bytes(), &obs); err != nil {
				file.Close()
				return fmt.Errorf("parse %s line %d: %w", path, line, err)
			}
			r.index(obs)
		}
		scanErr := scanner.Err()
		closeErr := file.Close()
		if scanErr != nil {
			return fmt.Errorf("scan %s: %w", path, scanErr)
		}
		if closeErr != nil {
			return fmt.Errorf("close %s: %w", path, closeErr)
		}
	}
	return nil
}

func (r *Recorder) index(obs Observation) {
	r.seenHashes[obs.SHA256] = struct{}{}
	key := turnKey{gameID: obs.GameID, turn: obs.Turn}
	if r.turnHashes[key] == nil {
		r.turnHashes[key] = make(map[string]struct{})
	}
	r.turnHashes[key][obs.SHA256] = struct{}{}
	if !r.hasLatest[obs.GameID] || obs.Turn > r.latestTurn[obs.GameID] {
		r.latestTurn[obs.GameID] = obs.Turn
		r.hasLatest[obs.GameID] = true
	}
}

func appendObservation(path string, obs Observation) error {
	file, err := os.OpenFile(path, os.O_CREATE|os.O_APPEND|os.O_WRONLY, 0o644)
	if err != nil {
		return fmt.Errorf("open observation log: %w", err)
	}
	if err := json.NewEncoder(file).Encode(obs); err != nil {
		file.Close()
		return fmt.Errorf("append observation: %w", err)
	}
	if err := file.Close(); err != nil {
		return fmt.Errorf("close observation log: %w", err)
	}
	return nil
}

func writeSnapshot(path string, data []byte, wantHash [sha256.Size]byte) error {
	file, err := os.OpenFile(path, os.O_CREATE|os.O_EXCL|os.O_WRONLY, 0o644)
	if err == nil {
		if _, writeErr := file.Write(data); writeErr != nil {
			file.Close()
			return fmt.Errorf("write snapshot: %w", writeErr)
		}
		if closeErr := file.Close(); closeErr != nil {
			return fmt.Errorf("close snapshot: %w", closeErr)
		}
		return nil
	}
	if !errors.Is(err, os.ErrExist) {
		return fmt.Errorf("create snapshot: %w", err)
	}

	existing, readErr := os.ReadFile(path)
	if readErr != nil {
		return fmt.Errorf("read existing snapshot: %w", readErr)
	}
	if sha256.Sum256(existing) != wantHash {
		return fmt.Errorf("snapshot path collision at %s", path)
	}
	return nil
}

func safeStem(s string) string {
	if s == "" {
		return "snapshot"
	}
	var b strings.Builder
	for _, r := range s {
		switch {
		case r >= 'a' && r <= 'z', r >= 'A' && r <= 'Z', r >= '0' && r <= '9', r == '-', r == '_', r == '.':
			b.WriteRune(r)
		default:
			b.WriteByte('_')
		}
	}
	return b.String()
}
