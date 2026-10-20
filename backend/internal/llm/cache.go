package llm

import (
	"container/list"
	"sync"
	"time"
)

// Cache is a bounded LRU with TTL for completed generations. Keys must already include tenant,
// prompt version and route chain; partial or failed streams are never stored.
type Cache struct {
	mu    sync.Mutex
	size  int
	ttl   time.Duration
	order *list.List
	items map[string]*list.Element
	now   func() time.Time
}
type cacheEntry struct {
	key     string
	value   Result
	expires time.Time
}

func NewCache(size int, ttl time.Duration) *Cache {
	return &Cache{size: size, ttl: ttl, order: list.New(), items: map[string]*list.Element{}, now: time.Now}
}
func (c *Cache) Get(key string) (Result, bool) {
	c.mu.Lock()
	defer c.mu.Unlock()
	e, ok := c.items[key]
	if !ok {
		return Result{}, false
	}
	entry := e.Value.(*cacheEntry)
	if c.now().After(entry.expires) {
		c.order.Remove(e)
		delete(c.items, key)
		return Result{}, false
	}
	c.order.MoveToFront(e)
	return entry.value, true
}
func (c *Cache) Put(key string, v Result) {
	c.mu.Lock()
	defer c.mu.Unlock()
	if e, ok := c.items[key]; ok {
		e.Value = &cacheEntry{key, v, c.now().Add(c.ttl)}
		c.order.MoveToFront(e)
		return
	}
	c.items[key] = c.order.PushFront(&cacheEntry{key, v, c.now().Add(c.ttl)})
	for c.order.Len() > c.size {
		oldest := c.order.Back()
		c.order.Remove(oldest)
		delete(c.items, oldest.Value.(*cacheEntry).key)
	}
}
func (c *Cache) Len() int {
	c.mu.Lock()
	defer c.mu.Unlock()
	return c.order.Len()
}
