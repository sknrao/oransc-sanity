package services

import (
	"sync"
	"time"
)

type RmrMessageThrottler struct {
	messageCounters      map[string]*messageCounter
	mutex                sync.RWMutex
	maxMessagesPerSecond int
	windowSize           time.Duration
}

type messageCounter struct {
	count  int
	window time.Time
}

func NewRmrMessageThrottler(maxMessagesPerSecond int) *RmrMessageThrottler {
	return &RmrMessageThrottler{
		messageCounters:      make(map[string]*messageCounter),
		maxMessagesPerSecond: maxMessagesPerSecond,
		windowSize:           time.Second,
	}
}

func (t *RmrMessageThrottler) AllowMessage(ranName string) bool {
	t.mutex.Lock()
	defer t.mutex.Unlock()

	now := time.Now()
	counter, exists := t.messageCounters[ranName]

	if !exists || now.Sub(counter.window) > t.windowSize {
		t.messageCounters[ranName] = &messageCounter{count: 1, window: now}
		return true
	}

	if counter.count >= t.maxMessagesPerSecond {
		return false
	}

	counter.count++
	return true
}
