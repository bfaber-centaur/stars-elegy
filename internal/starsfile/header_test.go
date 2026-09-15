package starsfile

import (
	"encoding/binary"
	"testing"
)

func TestParseHeaderPG001(t *testing.T) {
	// First 18 bytes of PG001.HST, turn 0, captured from J-RC3.
	file := []byte{
		0x10, 0x20,
		0x4a, 0x33, 0x4a, 0x33,
		0xab, 0xbb, 0x84, 0x05,
		0x60, 0x2a,
		0x00, 0x00,
		0x5f, 0x09,
		0x02, 0x00,
	}

	header, err := ParseHeader(file)
	if err != nil {
		t.Fatalf("ParseHeader() error = %v", err)
	}

	if got, want := header.GameID, uint32(92584875); got != want {
		t.Errorf("GameID = %d, want %d", got, want)
	}
	if got, want := header.Version.String(), "2.83.0"; got != want {
		t.Errorf("Version = %q, want %q", got, want)
	}
	if got, want := header.Turn, uint16(0); got != want {
		t.Errorf("Turn = %d, want %d", got, want)
	}
	if got, want := header.Year, 2400; got != want {
		t.Errorf("Year = %d, want %d", got, want)
	}
	if got, want := header.PlayerIndex, uint8(31); got != want {
		t.Errorf("PlayerIndex = %d, want %d", got, want)
	}
}

func TestParseHeaderRejectsInvalidFiles(t *testing.T) {
	valid := make([]byte, 18)
	binary.LittleEndian.PutUint16(valid[:2], uint16(fileHeaderType<<10|fileHeaderSize))
	copy(valid[2:6], "J3J3")

	tests := []struct {
		name string
		file []byte
	}{
		{name: "short", file: valid[:17]},
		{name: "wrong magic", file: func() []byte { b := append([]byte(nil), valid...); copy(b[2:6], "NOPE"); return b }()},
		{name: "wrong block type", file: func() []byte {
			b := append([]byte(nil), valid...)
			binary.LittleEndian.PutUint16(b[:2], uint16(7<<10|fileHeaderSize))
			return b
		}()},
		{name: "wrong block size", file: func() []byte {
			b := append([]byte(nil), valid...)
			binary.LittleEndian.PutUint16(b[:2], uint16(fileHeaderType<<10|15))
			return b
		}()},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if _, err := ParseHeader(tt.file); err == nil {
				t.Fatal("ParseHeader() error = nil, want error")
			}
		})
	}
}
