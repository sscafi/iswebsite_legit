import os
import json
from pathlib import Path
from dotenv import load_dotenv
from cryptography.fernet import Fernet
import base64

class ConfigManager:
    def __init__(self):
        self.config_dir = Path.home() / ".domain_checker"
        self.config_file = self.config_dir / "config.json"
        self.encrypted_file = self.config_dir / "encrypted_config.bin"
        
        # Create config directory if it doesn't exist
        self.config_dir.mkdir(exist_ok=True)
        
        # Load environment variables
        load_dotenv()
        
        # Initialize encryption key
        self._init_encryption_key()
        
        # Load configuration
        self.config = self._load_config()
    
    def _init_encryption_key(self):
        """Initialize or load encryption key for sensitive data"""
        key_file = self.config_dir / "key.bin"
        if key_file.exists():
            with open(key_file, 'rb') as f:
                self.key = f.read()
        else:
            self.key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(self.key)
        
        self.cipher = Fernet(self.key)
    
    def _load_config(self):
        """Load configuration from file or create default"""
        default_config = {
            'api_keys': {
                'dns_tracking': os.getenv('DNS_TRACKING_API_KEY', ''),
                'virustotal': os.getenv('VIRUSTOTAL_API_KEY', ''),
                'abuseipdb': os.getenv('ABUSEIPDB_API_KEY', '')
            },
            'settings': {
                'enable_analytics': os.getenv('ENABLE_ANALYTICS', 'false').lower() == 'true',
                'enable_crash_reporting': os.getenv('ENABLE_CRASH_REPORTING', 'false').lower() == 'true',
                'dark_mode': os.getenv('DARK_MODE', 'false').lower() == 'true',
                'auto_update': os.getenv('AUTO_UPDATE', 'true').lower() == 'true',
                'cache_duration': 3600,  # 1 hour
                'max_history': 100
            },
            'ui': {
                'window_width': 800,
                'window_height': 600,
                'theme': 'default'
            }
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    saved_config = json.load(f)
                    # Merge with defaults
                    default_config.update(saved_config)
            except Exception as e:
                print(f"Error loading config: {e}")
        
        return default_config
    
    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get_api_key(self, service):
        """Get API key for a specific service"""
        return self.config['api_keys'].get(service, '')
    
    def set_api_key(self, service, key):
        """Set API key for a specific service"""
        self.config['api_keys'][service] = key
        self.save_config()
    
    def get_setting(self, key, default=None):
        """Get a setting value"""
        return self.config['settings'].get(key, default)
    
    def set_setting(self, key, value):
        """Set a setting value"""
        self.config['settings'][key] = value
        self.save_config()
    
    def encrypt_sensitive_data(self, data):
        """Encrypt sensitive data"""
        return self.cipher.encrypt(data.encode())
    
    def decrypt_sensitive_data(self, encrypted_data):
        """Decrypt sensitive data"""
        try:
            return self.cipher.decrypt(encrypted_data).decode()
        except Exception:
            return ""

# Global config instance
config = ConfigManager() 