// Command stars-header prints the plaintext header of Stars! game files.
//
//	stars-header FILE...
//
// One line per file: path, size, short SHA-256, and the decoded header, or the
// reason the header could not be decoded. Later blocks are not decrypted.
package main

import (
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"io"
	"os"

	"stars-elegy/internal/starsfile"
)

func main() {
	os.Exit(run(os.Args[1:], os.Stdout, os.Stderr))
}

func run(paths []string, stdout, stderr io.Writer) int {
	if len(paths) == 0 {
		fmt.Fprintln(stderr, "usage: stars-header FILE...")
		return 2
	}

	status := 0
	for _, path := range paths {
		data, err := os.ReadFile(path)
		if err != nil {
			fmt.Fprintf(stderr, "stars-header: %v\n", err)
			status = 1
			continue
		}
		fmt.Fprintln(stdout, describe(path, data))
	}
	return status
}

func describe(path string, data []byte) string {
	sum := sha256.Sum256(data)
	prefix := fmt.Sprintf("%s\t%d bytes\tsha256:%s", path, len(data), hex.EncodeToString(sum[:6]))

	h, err := starsfile.ParseHeader(data)
	if err != nil {
		return fmt.Sprintf("%s\theader error: %v", prefix, err)
	}
	return fmt.Sprintf("%s\tgame=%d version=%s turn=%d year=%d player=%d flags=0x%02x",
		prefix, h.GameID, h.Version, h.Turn, h.Year, h.PlayerIndex, h.Flags)
}
