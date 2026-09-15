package starsfile

import (
	"encoding/binary"
	"errors"
	"fmt"
)

const (
	fileHeaderType = 8
	fileHeaderSize = 16
	firstYear      = 2400
)

// Version is the Stars! file-format version encoded in a file header.
type Version struct {
	Major     uint8
	Minor     uint8
	Increment uint8
}

func (v Version) String() string {
	return fmt.Sprintf("%d.%d.%d", v.Major, v.Minor, v.Increment)
}

// Header contains the plaintext metadata in the first block of a Stars! file.
type Header struct {
	GameID      uint32
	Version     Version
	Turn        uint16
	Year        int
	Salt        uint16
	PlayerIndex uint8
	Flags       uint8
}

// ParseHeader decodes the plaintext FileHeader block at the start of a Stars!
// file. It deliberately does not decrypt or interpret any later blocks.
func ParseHeader(file []byte) (Header, error) {
	if len(file) < 2+fileHeaderSize {
		return Header{}, errors.New("stars file is too short for a file header")
	}

	blockHeader := binary.LittleEndian.Uint16(file[:2])
	blockType := blockHeader >> 10
	blockSize := blockHeader & 0x03ff
	if blockType != fileHeaderType || blockSize != fileHeaderSize {
		return Header{}, fmt.Errorf("unexpected first block: type=%d size=%d", blockType, blockSize)
	}

	data := file[2 : 2+fileHeaderSize]
	if string(data[:4]) != "J3J3" {
		return Header{}, fmt.Errorf("unexpected Stars! magic %q", data[:4])
	}

	versionData := binary.LittleEndian.Uint16(data[8:10])
	playerData := binary.LittleEndian.Uint16(data[12:14])
	turn := binary.LittleEndian.Uint16(data[10:12])

	return Header{
		GameID: binary.LittleEndian.Uint32(data[4:8]),
		Version: Version{
			Major:     uint8(versionData >> 12),
			Minor:     uint8((versionData >> 5) & 0x7f),
			Increment: uint8(versionData & 0x1f),
		},
		Turn:        turn,
		Year:        firstYear + int(turn),
		Salt:        playerData >> 5,
		PlayerIndex: uint8(playerData & 0x1f),
		Flags:       data[15],
	}, nil
}
