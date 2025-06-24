import re
import socket
import ssl
from urllib.parse import urlparse
from utils.logger import logger

class DomainValidator:
    def __init__(self):
        # Domain regex pattern
        self.domain_pattern = re.compile(
            r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$'
        )
        
        # Common TLDs for validation
        self.common_tlds = {
            '.com', '.org', '.net', '.edu', '.gov', '.mil', '.int',
            '.co', '.io', '.ai', '.app', '.dev', '.tech', '.online',
            '.store', '.shop', '.blog', '.news', '.info', '.biz',
            '.uk', '.de', '.fr', '.jp', '.cn', '.in', '.br', '.au',
            '.ca', '.mx', '.ru', '.it', '.es', '.nl', '.se', '.no'
        }
    
    def clean_domain(self, domain):
        """Clean and normalize domain input"""
        if not domain:
            return None
        
        # Remove whitespace
        domain = domain.strip()
        
        # Remove protocol if present
        if domain.startswith(('http://', 'https://')):
            domain = domain.split('://', 1)[1]
        
        # Remove www. prefix
        if domain.startswith('www.'):
            domain = domain[4:]
        
        # Remove trailing slash
        domain = domain.rstrip('/')
        
        # Remove port if present
        if ':' in domain:
            domain = domain.split(':')[0]
        
        # Remove path if present
        if '/' in domain:
            domain = domain.split('/')[0]
        
        return domain.lower()
    
    def validate_domain(self, domain):
        """Validate domain format and existence"""
        if not domain:
            return False, "Domain cannot be empty"
        
        # Clean the domain
        clean_domain = self.clean_domain(domain)
        if not clean_domain:
            return False, "Invalid domain format"
        
        # Check basic format
        if not self.domain_pattern.match(clean_domain):
            return False, "Invalid domain format"
        
        # Check for valid TLD
        tld = '.' + clean_domain.split('.')[-1]
        if tld not in self.common_tlds:
            logger.log_warning(f"Uncommon TLD detected: {tld}", "validation")
        
        # Check for suspicious patterns
        suspicious_patterns = [
            r'\d{4,}',  # Too many consecutive digits
            r'[a-z]{20,}',  # Too many consecutive letters
            r'[0-9]{3,}[a-z]{3,}',  # Many digits followed by many letters
            r'[a-z]{3,}[0-9]{3,}',  # Many letters followed by many digits
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, clean_domain):
                logger.log_warning(f"Suspicious domain pattern detected: {clean_domain}", "validation")
                break
        
        return True, clean_domain
    
    def check_domain_resolution(self, domain):
        """Check if domain resolves to an IP address"""
        try:
            ip = socket.gethostbyname(domain)
            return True, ip
        except socket.gaierror:
            return False, "Domain does not resolve"
        except Exception as e:
            logger.log_error(f"Error resolving domain {domain}", e, "validation")
            return False, f"Resolution error: {str(e)}"
    
    def check_ssl_certificate(self, domain):
        """Check SSL certificate information"""
        try:
            context = ssl.create_default_context()
            with socket.create_connection((domain, 443), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert = ssock.getpeercert()
                    
                    # Extract certificate information
                    cert_info = {
                        'subject': dict(x[0] for x in cert['subject']),
                        'issuer': dict(x[0] for x in cert['issuer']),
                        'version': cert['version'],
                        'serial_number': cert['serialNumber'],
                        'not_before': cert['notBefore'],
                        'not_after': cert['notAfter'],
                        'san': cert.get('subjectAltName', [])
                    }
                    
                    return True, cert_info
        except Exception as e:
            logger.log_error(f"Error checking SSL certificate for {domain}", e, "validation")
            return False, f"SSL check failed: {str(e)}"
    
    def calculate_domain_age(self, creation_date):
        """Calculate domain age from creation date"""
        if not creation_date:
            return None
        
        from datetime import datetime
        
        try:
            if isinstance(creation_date, list):
                creation_date = creation_date[0]
            
            if isinstance(creation_date, str):
                # Try different date formats
                date_formats = [
                    '%Y-%m-%d',
                    '%Y-%m-%d %H:%M:%S',
                    '%d-%b-%Y',
                    '%Y-%m-%dT%H:%M:%SZ'
                ]
                
                for fmt in date_formats:
                    try:
                        creation_date = datetime.strptime(creation_date, fmt)
                        break
                    except ValueError:
                        continue
                else:
                    return None
            
            age_days = (datetime.now() - creation_date).days
            age_years = age_days / 365.25
            
            return {
                'days': age_days,
                'years': round(age_years, 2)
            }
        except Exception as e:
            logger.log_error(f"Error calculating domain age", e, "validation")
            return None
    
    def check_suspicious_indicators(self, domain, whois_info):
        """Check for suspicious indicators"""
        indicators = []
        
        # Check domain age
        if whois_info.get('creation_date'):
            age = self.calculate_domain_age(whois_info['creation_date'])
            if age and age['days'] < 30:
                indicators.append({
                    'type': 'recent_registration',
                    'severity': 'medium',
                    'description': f"Domain registered recently ({age['days']} days ago)"
                })
        
        # Check for privacy protection
        if whois_info.get('registrar'):
            registrar = whois_info['registrar'].lower()
            privacy_indicators = ['privacy', 'proxy', 'anonymous', 'protected']
            if any(indicator in registrar for indicator in privacy_indicators):
                indicators.append({
                    'type': 'privacy_protection',
                    'severity': 'low',
                    'description': "Domain uses privacy protection services"
                })
        
        # Check for suspicious registrar
        suspicious_registrars = ['godaddy', 'namecheap', '1and1', 'hostgator']
        if whois_info.get('registrar'):
            registrar = whois_info['registrar'].lower()
            if any(susp in registrar for susp in suspicious_registrars):
                indicators.append({
                    'type': 'common_registrar',
                    'severity': 'low',
                    'description': "Domain registered with common registrar"
                })
        
        return indicators

# Global validator instance
validator = DomainValidator() 