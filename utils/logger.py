import logging
import os
from pathlib import Path
from datetime import datetime
import json
import traceback
from utils.config import config

class Logger:
    def __init__(self):
        self.log_dir = Path.home() / ".domain_checker" / "logs"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Create loggers
        self.app_logger = self._setup_logger('app', 'app.log')
        self.error_logger = self._setup_logger('error', 'errors.log')
        self.analytics_logger = self._setup_logger('analytics', 'analytics.log')
        
        # Performance tracking
        self.performance_data = []
    
    def _setup_logger(self, name, filename):
        """Setup individual logger"""
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        
        # Prevent duplicate handlers
        if logger.handlers:
            return logger
        
        # File handler
        file_handler = logging.FileHandler(self.log_dir / filename)
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def log_info(self, message, category="general"):
        """Log informational message"""
        self.app_logger.info(f"[{category}] {message}")
    
    def log_error(self, message, error=None, category="general"):
        """Log error message with optional exception details"""
        error_msg = f"[{category}] {message}"
        if error:
            error_msg += f"\nException: {str(error)}\nTraceback: {traceback.format_exc()}"
        
        self.error_logger.error(error_msg)
        
        # Also log to app logger for visibility
        self.app_logger.error(error_msg)
    
    def log_warning(self, message, category="general"):
        """Log warning message"""
        self.app_logger.warning(f"[{category}] {message}")
    
    def log_analytics(self, event, data=None):
        """Log analytics events"""
        if not config.get_setting('enable_analytics'):
            return
        
        analytics_data = {
            'timestamp': datetime.now().isoformat(),
            'event': event,
            'data': data or {}
        }
        
        self.analytics_logger.info(json.dumps(analytics_data))
    
    def log_performance(self, operation, duration):
        """Log performance metrics"""
        self.performance_data.append({
            'operation': operation,
            'duration': duration,
            'timestamp': datetime.now().isoformat()
        })
        
        # Keep only last 1000 entries
        if len(self.performance_data) > 1000:
            self.performance_data = self.performance_data[-1000:]
        
        self.app_logger.debug(f"Performance: {operation} took {duration:.2f}s")
    
    def get_performance_stats(self):
        """Get performance statistics"""
        if not self.performance_data:
            return {}
        
        operations = {}
        for entry in self.performance_data:
            op = entry['operation']
            if op not in operations:
                operations[op] = []
            operations[op].append(entry['duration'])
        
        stats = {}
        for op, durations in operations.items():
            stats[op] = {
                'count': len(durations),
                'avg_duration': sum(durations) / len(durations),
                'min_duration': min(durations),
                'max_duration': max(durations)
            }
        
        return stats
    
    def log_crash(self, error, context=None):
        """Log application crashes"""
        crash_data = {
            'timestamp': datetime.now().isoformat(),
            'error': str(error),
            'traceback': traceback.format_exc(),
            'context': context or {}
        }
        
        crash_file = self.log_dir / f"crash_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(crash_file, 'w') as f:
                json.dump(crash_data, f, indent=2)
        except Exception as e:
            self.log_error("Failed to save crash report", e)
    
    def cleanup_old_logs(self, days=30):
        """Clean up old log files"""
        cutoff_date = datetime.now().timestamp() - (days * 24 * 60 * 60)
        
        for log_file in self.log_dir.glob("*.log"):
            if log_file.stat().st_mtime < cutoff_date:
                try:
                    log_file.unlink()
                    self.log_info(f"Cleaned up old log file: {log_file.name}")
                except Exception as e:
                    self.log_error(f"Failed to delete old log file: {log_file.name}", e)

# Global logger instance
logger = Logger() 