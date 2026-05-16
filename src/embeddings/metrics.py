from prometheus_client import Counter, Histogram

EMBED_CACHE_HITS = Counter("embedding_cache_hits_total", "Cache hits")
EMBED_CACHE_MISSES = Counter("embedding_cache_misses_total", "Cache misses")
EMBED_CACHE_LATENCY = Histogram("embedding_cache_latency_seconds", "Cache lookup latency")
