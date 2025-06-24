import json
import time
import hashlib
from pathlib import Path
from threading import Lock
from utils.config import config
from utils.logger import logger

class CacheManager:
    def __init__(self):
        self.cache_dir = Path.home() / ".domain_checker" / "cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.memory_cache = {}
        self.cache_lock = Lock()
        
        # Load cache settings
        self.cache_duration = config.get_setting('cache_duration', 3600)  # 1 hour default
        self.max_cache_size = 100 * 1024 * 1024  # 100MB
        
        # Clean up old cache files on startup
        self.cleanup_cache()
    
    def _get_cache_key(self, domain, check_type):
        """Generate cache key for domain and check type"""
        key_string = f"{domain}_{check_type}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _get_cache_file(self, cache_key):
        """Get cache file path for a given key"""
        return self.cache_dir / f"{cache_key}.json"
    
    def get_cached_result(self, domain, check_type):
        """Get cached result for domain check"""
        cache_key = self._get_cache_key(domain, check_type)
        
        # Check memory cache first
        with self.cache_lock:
            if cache_key in self.memory_cache:
                cached_data = self.memory_cache[cache_key]
                if time.time() - cached_data['timestamp'] < self.cache_duration:
                    logger.log_info(f"Cache hit (memory): {domain} - {check_type}", "cache")
                    return cached_data['data']
                else:
                    # Remove expired entry
                    del self.memory_cache[cache_key]
        
        # Check file cache
        cache_file = self._get_cache_file(cache_key)
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    cached_data = json.load(f)
                
                # Check if cache is still valid
                if time.time() - cached_data['timestamp'] < self.cache_duration:
                    # Add to memory cache
                    with self.cache_lock:
                        self.memory_cache[cache_key] = cached_data
                    
                    logger.log_info(f"Cache hit (file): {domain} - {check_type}", "cache")
                    return cached_data['data']
                else:
                    # Remove expired cache file
                    cache_file.unlink()
            except Exception as e:
                logger.log_error(f"Error reading cache file for {domain}", e, "cache")
                if cache_file.exists():
                    cache_file.unlink()
        
        return None
    
    def cache_result(self, domain, check_type, data):
        """Cache result for domain check"""
        cache_key = self._get_cache_key(domain, check_type)
        cache_file = self._get_cache_file(cache_key)
        
        cache_data = {
            'domain': domain,
            'check_type': check_type,
            'data': data,
            'timestamp': time.time()
        }
        
        # Save to memory cache
        with self.cache_lock:
            self.memory_cache[cache_key] = cache_data
        
        # Save to file cache
        try:
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
            
            logger.log_info(f"Cached result: {domain} - {check_type}", "cache")
        except Exception as e:
            logger.log_error(f"Error saving cache for {domain}", e, "cache")
    
    def invalidate_cache(self, domain=None, check_type=None):
        """Invalidate cache entries"""
        if domain and check_type:
            # Invalidate specific entry
            cache_key = self._get_cache_key(domain, check_type)
            cache_file = self._get_cache_file(cache_key)
            
            with self.cache_lock:
                if cache_key in self.memory_cache:
                    del self.memory_cache[cache_key]
            
            if cache_file.exists():
                cache_file.unlink()
                
            logger.log_info(f"Invalidated cache: {domain} - {check_type}", "cache")
        else:
            # Clear all cache
            with self.cache_lock:
                self.memory_cache.clear()
            
            for cache_file in self.cache_dir.glob("*.json"):
                cache_file.unlink()
            
            logger.log_info("Cleared all cache", "cache")
    
    def cleanup_cache(self):
        """Clean up expired cache files"""
        current_time = time.time()
        cleaned_count = 0
        
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                with open(cache_file, 'r') as f:
                    cached_data = json.load(f)
                
                if current_time - cached_data['timestamp'] > self.cache_duration:
                    cache_file.unlink()
                    cleaned_count += 1
            except Exception as e:
                logger.log_error(f"Error cleaning cache file {cache_file}", e, "cache")
                cache_file.unlink()
                cleaned_count += 1
        
        if cleaned_count > 0:
            logger.log_info(f"Cleaned up {cleaned_count} expired cache files", "cache")
    
    def get_cache_stats(self):
        """Get cache statistics"""
        memory_entries = len(self.memory_cache)
        file_entries = len(list(self.cache_dir.glob("*.json")))
        
        total_size = 0
        for cache_file in self.cache_dir.glob("*.json"):
            total_size += cache_file.stat().st_size
        
        return {
            'memory_entries': memory_entries,
            'file_entries': file_entries,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'cache_duration_hours': self.cache_duration / 3600
        }

class RateLimiter:
    def __init__(self):
        self.requests = {}
        self.limits = {
            'whois': {'requests': 10, 'window': 60},  # 10 requests per minute
            'dns': {'requests': 20, 'window': 60},    # 20 requests per minute
            'ssl': {'requests': 15, 'window': 60},    # 15 requests per minute
            'blacklist': {'requests': 5, 'window': 60} # 5 requests per minute
        }
    
    def can_make_request(self, request_type):
        """Check if request can be made within rate limits"""
        current_time = time.time()
        
        if request_type not in self.requests:
            self.requests[request_type] = []
        
        # Remove old requests outside the window
        window = self.limits[request_type]['window']
        self.requests[request_type] = [
            req_time for req_time in self.requests[request_type]
            if current_time - req_time < window
        ]
        
        # Check if we're under the limit
        limit = self.limits[request_type]['requests']
        if len(self.requests[request_type]) < limit:
            self.requests[request_type].append(current_time)
            return True
        
        return False
    
    def get_wait_time(self, request_type):
        """Get time to wait before next request"""
        if request_type not in self.requests or not self.requests[request_type]:
            return 0
        
        current_time = time.time()
        window = self.limits[request_type]['window']
        oldest_request = min(self.requests[request_type])
        
        return max(0, window - (current_time - oldest_request))

# Global instances
cache_manager = CacheManager()
rate_limiter = RateLimiter() 