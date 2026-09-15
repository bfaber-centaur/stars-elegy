package main

import (
	"context"
	"flag"
	"fmt"
	"log"
	"os"
	"os/signal"

	"stars-elegy/internal/recorder"
)

func main() {
	os.Exit(run())
}

func run() int {
	watchDir := flag.String("watch", "", "directory containing Stars! .HST files")
	outDir := flag.String("out", "", "directory where snapshots and observations are archived")
	interval := flag.Duration("interval", recorder.DefaultPollInterval, "poll interval")
	flag.Usage = func() {
		fmt.Fprintf(flag.CommandLine.Output(), "Usage: %s -watch DIR -out DIR [options]\n\n", os.Args[0])
		flag.PrintDefaults()
	}
	flag.Parse()

	if *watchDir == "" || *outDir == "" {
		flag.Usage()
		return 2
	}
	if *interval <= 0 {
		fmt.Fprintln(os.Stderr, "interval must be greater than zero")
		return 2
	}

	logger := log.New(os.Stderr, "stars-record: ", log.LstdFlags)
	r, err := recorder.New(recorder.Config{
		WatchDir:     *watchDir,
		OutDir:       *outDir,
		PollInterval: *interval,
	}, logger)
	if err != nil {
		logger.Printf("error: %v", err)
		return 1
	}

	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt)
	defer stop()

	logger.Printf("watching %s every %s; output %s", *watchDir, interval.String(), *outDir)
	if err := r.Run(ctx); err != nil {
		logger.Printf("error: %v", err)
		return 1
	}
	logger.Print("stopped")
	return 0
}
