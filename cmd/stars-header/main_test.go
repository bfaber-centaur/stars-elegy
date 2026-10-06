package main

import (
	"strings"
	"testing"
)

func TestDescribePG001Header(t *testing.T) {
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

	got := describe("PG001.HST", file)
	want := "game=92584875 version=2.83.0 turn=0 year=2400 player=31 flags=0x00"
	if !strings.HasSuffix(got, want) {
		t.Errorf("describe() = %q, want suffix %q", got, want)
	}
}

func TestDescribeReportsUndecodableFiles(t *testing.T) {
	got := describe("junk.HST", []byte("not a stars file at all"))
	if !strings.Contains(got, "header error:") {
		t.Errorf("describe() = %q, want a header error", got)
	}
}
