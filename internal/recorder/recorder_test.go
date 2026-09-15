package recorder

import (
	"bytes"
	"encoding/binary"
	"encoding/json"
	"log"
	"os"
	"path/filepath"
	"strconv"
	"strings"
	"testing"
)

func TestRecorderRequiresTwoStableReads(t *testing.T) {
	watch := t.TempDir()
	out := t.TempDir()
	var logs bytes.Buffer
	r := newTestRecorder(t, watch, out, &logs)

	path := filepath.Join(watch, "PG001.HST")
	writeTestHST(t, path, 92584875, 0, "first")

	if err := r.scanOnce(); err != nil {
		t.Fatal(err)
	}
	if got := readObservations(t, out, 92584875); len(got) != 0 {
		t.Fatalf("after one read got %d observations, want 0", len(got))
	}

	if err := r.scanOnce(); err != nil {
		t.Fatal(err)
	}
	obs := readObservations(t, out, 92584875)
	if len(obs) != 1 {
		t.Fatalf("after two stable reads got %d observations, want 1", len(obs))
	}
	if got, want := obs[0].Year, 2400; got != want {
		t.Errorf("year = %d, want %d", got, want)
	}
	if _, err := os.Stat(filepath.Join(out, filepath.FromSlash(obs[0].File))); err != nil {
		t.Fatalf("archived snapshot: %v", err)
	}
}

func TestRecorderDoesNotAcceptSupersededCandidate(t *testing.T) {
	watch := t.TempDir()
	out := t.TempDir()
	r := newTestRecorder(t, watch, out, nil)
	path := filepath.Join(watch, "PG001.HST")

	writeTestHST(t, path, 92584875, 0, "candidate-a")
	if err := r.scanOnce(); err != nil {
		t.Fatal(err)
	}
	writeTestHST(t, path, 92584875, 1, "candidate-b")
	if err := r.scanOnce(); err != nil {
		t.Fatal(err)
	}
	if err := r.scanOnce(); err != nil {
		t.Fatal(err)
	}

	obs := readObservations(t, out, 92584875)
	if len(obs) != 1 || obs[0].Turn != 1 {
		t.Fatalf("observations = %#v, want only turn 1", obs)
	}
}

func TestRecorderWarnsOnMissedAndDivergentTurns(t *testing.T) {
	watch := t.TempDir()
	out := t.TempDir()
	var logs bytes.Buffer
	r := newTestRecorder(t, watch, out, &logs)
	path := filepath.Join(watch, "PG001.HST")

	recordTestHST(t, r, path, 92584875, 0, "turn-0")
	recordTestHST(t, r, path, 92584875, 2, "turn-2-a")
	recordTestHST(t, r, path, 92584875, 2, "turn-2-b")

	got := logs.String()
	if !strings.Contains(got, "missed turn(s): last=0 now=2") {
		t.Errorf("logs missing missed-turn warning:\n%s", got)
	}
	if !strings.Contains(got, "turn 2 has multiple distinct HST states") {
		t.Errorf("logs missing divergent-turn warning:\n%s", got)
	}
	if obs := readObservations(t, out, 92584875); len(obs) != 3 {
		t.Fatalf("got %d observations, want 3", len(obs))
	}
}

func TestRecorderReloadsExistingObservations(t *testing.T) {
	watch := t.TempDir()
	out := t.TempDir()
	path := filepath.Join(watch, "PG001.HST")
	writeTestHST(t, path, 92584875, 0, "turn-0")

	first := newTestRecorder(t, watch, out, nil)
	if err := first.scanOnce(); err != nil {
		t.Fatal(err)
	}
	if err := first.scanOnce(); err != nil {
		t.Fatal(err)
	}

	second := newTestRecorder(t, watch, out, nil)
	if err := second.scanOnce(); err != nil {
		t.Fatal(err)
	}
	if err := second.scanOnce(); err != nil {
		t.Fatal(err)
	}

	if obs := readObservations(t, out, 92584875); len(obs) != 1 {
		t.Fatalf("after restart got %d observations, want 1", len(obs))
	}
}

func newTestRecorder(t *testing.T, watch, out string, logs *bytes.Buffer) *Recorder {
	t.Helper()
	var logger *log.Logger
	if logs != nil {
		logger = log.New(logs, "", 0)
	}
	r, err := New(Config{WatchDir: watch, OutDir: out}, logger)
	if err != nil {
		t.Fatalf("New() error = %v", err)
	}
	return r
}

func recordTestHST(t *testing.T, r *Recorder, path string, gameID uint32, turn uint16, payload string) {
	t.Helper()
	writeTestHST(t, path, gameID, turn, payload)
	if err := r.scanOnce(); err != nil {
		t.Fatal(err)
	}
	if err := r.scanOnce(); err != nil {
		t.Fatal(err)
	}
}

func writeTestHST(t *testing.T, path string, gameID uint32, turn uint16, payload string) {
	t.Helper()
	data := make([]byte, 18)
	binary.LittleEndian.PutUint16(data[:2], uint16(8<<10|16))
	copy(data[2:6], "J3J3")
	binary.LittleEndian.PutUint32(data[6:10], gameID)
	binary.LittleEndian.PutUint16(data[10:12], 0x2a60) // 2.83.0
	binary.LittleEndian.PutUint16(data[12:14], turn)
	binary.LittleEndian.PutUint16(data[14:16], 31)
	data = append(data, payload...)
	if err := os.WriteFile(path, data, 0o644); err != nil {
		t.Fatalf("write HST: %v", err)
	}
}

func readObservations(t *testing.T, out string, gameID uint32) []Observation {
	t.Helper()
	path := filepath.Join(out, strconv.FormatUint(uint64(gameID), 10), "observations.jsonl")
	data, err := os.ReadFile(path)
	if os.IsNotExist(err) {
		return nil
	}
	if err != nil {
		t.Fatalf("read observations: %v", err)
	}
	var result []Observation
	for _, line := range bytes.Split(bytes.TrimSpace(data), []byte("\n")) {
		if len(line) == 0 {
			continue
		}
		var obs Observation
		if err := json.Unmarshal(line, &obs); err != nil {
			t.Fatalf("parse observation: %v", err)
		}
		result = append(result, obs)
	}
	return result
}
