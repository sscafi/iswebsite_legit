import time
import requests
import whois
import socket
import ssl
from datetime import datetime
from utils.config import config
from utils.logger import logger
from utils.validators import validator
from utils.cache import cache_manager, rate_limiter

class DomainChecker:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'DomainChecker/1.0 (Security Tool)'
        })
    
    def check_domain_comprehensive(self, domain):
        """Perform comprehensive domain security check"""
        start_time = time.time()
        
        # Validate domain first
        is_valid, clean_domain = validator.validate_domain(domain)
        if not is_valid:
            return {'error': clean_domain}
        
        logger.log_info(f"Starting comprehensive check for domain: {clean_domain}", "checker")
        
        results = {
            'domain': clean_domain,
            'timestamp': datetime.now().isoformat(),
            'checks': {}
        }
        
        # Check cache first
        cached_result = cache_manager.get_cached_result(clean_domain, 'comprehensive')
        if cached_result:
            logger.log_info(f"Using cached result for {clean_domain}", "checker")
            return cached_result
        
        # Perform all checks
        try:
            # WHOIS Information
            results['checks']['whois'] = self._check_whois(clean_domain)
            
            # DNS Resolution
            results['checks']['dns'] = self._check_dns_resolution(clean_domain)
            
            # SSL Certificate
            results['checks']['ssl'] = self._check_ssl_certificate(clean_domain)
            
            # Domain Age
            results['checks']['age'] = self._check_domain_age(clean_domain, results['checks']['whois'])
            
            # Suspicious Indicators
            results['checks']['suspicious'] = self._check_suspicious_indicators(clean_domain, results['checks']['whois'])
            
            # Blacklist Check
            results['checks']['blacklist'] = self._check_blacklists(clean_domain)
            
            # Malware Check
            results['checks']['malware'] = self._check_malware_databases(clean_domain)
            
            # Social Media Presence
            results['checks']['social'] = self._check_social_media_presence(clean_domain)
            
            # Calculate overall risk score
            results['risk_score'] = self._calculate_risk_score(results['checks'])
            results['risk_level'] = self._get_risk_level(results['risk_score'])
            
            # Cache the result
            cache_manager.cache_result(clean_domain, 'comprehensive', results)
            
            duration = time.time() - start_time
            logger.log_performance(f"comprehensive_check_{clean_domain}", duration)
            logger.log_analytics('domain_check_completed', {
                'domain': clean_domain,
                'duration': duration,
                'risk_score': results['risk_score']
            })
            
            return results
            
        except Exception as e:
            logger.log_error(f"Error during comprehensive domain check for {clean_domain}", e, "checker")
            return {'error': f"Check failed: {str(e)}"}
    
    def _check_whois(self, domain):
        """Check WHOIS information"""
        if not rate_limiter.can_make_request('whois'):
            wait_time = rate_limiter.get_wait_time('whois')
            logger.log_warning(f"Rate limited for WHOIS check, waiting {wait_time}s", "checker")
            time.sleep(wait_time)
        
        try:
            whois_info = whois.whois(domain)
            
            # Convert to serializable format
            serializable_whois = {}
            for key, value in whois_info.items():
                if hasattr(value, 'isoformat'):  # Handle datetime objects
                    serializable_whois[key] = value.isoformat()
                elif isinstance(value, list):
                    serializable_whois[key] = [str(v) for v in value]
                else:
                    serializable_whois[key] = str(value) if value is not None else None
            
            return {
                'success': True,
                'data': serializable_whois
            }
        except Exception as e:
            logger.log_error(f"WHOIS check failed for {domain}", e, "checker")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _check_dns_resolution(self, domain):
        """Check DNS resolution"""
        if not rate_limiter.can_make_request('dns'):
            wait_time = rate_limiter.get_wait_time('dns')
            time.sleep(wait_time)
        
        try:
            ip = socket.gethostbyname(domain)
            return {
                'success': True,
                'ip': ip,
                'resolves': True
            }
        except socket.gaierror:
            return {
                'success': True,
                'resolves': False,
                'error': 'Domain does not resolve'
            }
        except Exception as e:
            logger.log_error(f"DNS resolution check failed for {domain}", e, "checker")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _check_ssl_certificate(self, domain):
        """Check SSL certificate"""
        if not rate_limiter.can_make_request('ssl'):
            wait_time = rate_limiter.get_wait_time('ssl')
            time.sleep(wait_time)
        
        try:
            context = ssl.create_default_context()
            with socket.create_connection((domain, 443), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert = ssock.getpeercert()
                    
                    # Check certificate expiration
                    not_after = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                    days_until_expiry = (not_after - datetime.now()).days
                    
                    return {
                        'success': True,
                        'valid': True,
                        'issuer': dict(x[0] for x in cert['issuer']),
                        'expires': cert['notAfter'],
                        'days_until_expiry': days_until_expiry,
                        'subject_alt_names': cert.get('subjectAltName', [])
                    }
        except Exception as e:
            logger.log_error(f"SSL certificate check failed for {domain}", e, "checker")
            return {
                'success': False,
                'valid': False,
                'error': str(e)
            }
    
    def _check_domain_age(self, domain, whois_result):
        """Calculate domain age"""
        if not whois_result.get('success') or not whois_result.get('data'):
            return {'success': False, 'error': 'No WHOIS data available'}
        
        whois_data = whois_result['data']
        creation_date = whois_data.get('creation_date')
        
        if not creation_date:
            return {'success': False, 'error': 'No creation date found'}
        
        age_info = validator.calculate_domain_age(creation_date)
        if age_info:
            return {
                'success': True,
                'age_days': age_info['days'],
                'age_years': age_info['years'],
                'creation_date': creation_date
            }
        else:
            return {'success': False, 'error': 'Could not calculate domain age'}
    
    def _check_suspicious_indicators(self, domain, whois_result):
        """Check for suspicious indicators"""
        if not whois_result.get('success') or not whois_result.get('data'):
            return {'success': False, 'error': 'No WHOIS data available'}
        
        indicators = validator.check_suspicious_indicators(domain, whois_result['data'])
        
        return {
            'success': True,
            'indicators': indicators,
            'count': len(indicators)
        }
    
    def _check_blacklists(self, domain):
        """Check domain against blacklists"""
        if not rate_limiter.can_make_request('blacklist'):
            wait_time = rate_limiter.get_wait_time('blacklist')
            time.sleep(wait_time)
        
        # Get IP address for blacklist checking
        try:
            ip = socket.gethostbyname(domain)
        except:
            return {'success': False, 'error': 'Cannot resolve domain for blacklist check'}
        
        blacklist_results = {}
        
        # Check AbuseIPDB
        abuseipdb_key = config.get_api_key('abuseipdb')
        if abuseipdb_key:
            try:
                headers = {'Key': abuseipdb_key, 'Accept': 'application/json'}
                url = f'https://api.abuseipdb.com/api/v2/check'
                params = {'ipAddress': ip, 'maxAgeInDays': '90'}
                
                response = self.session.get(url, headers=headers, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    blacklist_results['abuseipdb'] = {
                        'listed': data['data']['abuseConfidenceScore'] > 0,
                        'score': data['data']['abuseConfidenceScore'],
                        'country': data['data'].get('countryCode')
                    }
            except Exception as e:
                logger.log_error(f"AbuseIPDB check failed for {domain}", e, "checker")
                blacklist_results['abuseipdb'] = {'error': str(e)}
        
        return {
            'success': True,
            'ip': ip,
            'results': blacklist_results
        }
    
    def _check_malware_databases(self, domain):
        """Check domain against malware databases"""
        if not rate_limiter.can_make_request('blacklist'):
            wait_time = rate_limiter.get_wait_time('blacklist')
            time.sleep(wait_time)
        
        virustotal_key = config.get_api_key('virustotal')
        if not virustotal_key:
            return {'success': False, 'error': 'VirusTotal API key not configured'}
        
        try:
            headers = {'x-apikey': virustotal_key}
            url = f'https://www.virustotal.com/vtapi/v2/url/report'
            params = {'apikey': virustotal_key, 'resource': domain}
            
            response = self.session.get(url, headers=headers, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'detected': data.get('positives', 0),
                    'total': data.get('total', 0),
                    'scan_date': data.get('scan_date'),
                    'permalink': data.get('permalink')
                }
            else:
                return {'success': False, 'error': f'API error: {response.status_code}'}
        except Exception as e:
            logger.log_error(f"VirusTotal check failed for {domain}", e, "checker")
            return {'success': False, 'error': str(e)}
    
    def _check_social_media_presence(self, domain):
        """Check for social media presence"""
        social_platforms = {
            'facebook': f'https://www.facebook.com/{domain}',
            'twitter': f'https://twitter.com/{domain}',
            'linkedin': f'https://www.linkedin.com/company/{domain}',
            'instagram': f'https://www.instagram.com/{domain}'
        }
        
        presence = {}
        
        for platform, url in social_platforms.items():
            try:
                response = self.session.head(url, timeout=5, allow_redirects=True)
                presence[platform] = response.status_code == 200
            except:
                presence[platform] = False
        
        return {
            'success': True,
            'presence': presence,
            'total_platforms': len(presence),
            'active_platforms': sum(presence.values())
        }
    
    def _calculate_risk_score(self, checks):
        """Calculate overall risk score (0-100)"""
        score = 0
        
        # Domain age (newer = higher risk)
        if checks.get('age', {}).get('success'):
            age_days = checks['age'].get('age_days', 0)
            if age_days < 30:
                score += 25
            elif age_days < 90:
                score += 15
            elif age_days < 365:
                score += 5
        
        # Suspicious indicators
        if checks.get('suspicious', {}).get('success'):
            indicators = checks['suspicious'].get('indicators', [])
            for indicator in indicators:
                if indicator['severity'] == 'high':
                    score += 20
                elif indicator['severity'] == 'medium':
                    score += 10
                else:
                    score += 5
        
        # Blacklist status
        if checks.get('blacklist', {}).get('success'):
            results = checks['blacklist'].get('results', {})
            for service, result in results.items():
                if result.get('listed'):
                    score += 15
        
        # Malware detection
        if checks.get('malware', {}).get('success'):
            detected = checks['malware'].get('detected', 0)
            total = checks['malware'].get('total', 1)
            if detected > 0:
                score += (detected / total) * 30
        
        # SSL certificate issues
        if checks.get('ssl', {}).get('success'):
            if not checks['ssl'].get('valid'):
                score += 20
            elif checks['ssl'].get('days_until_expiry', 0) < 30:
                score += 10
        
        return min(100, score)
    
    def _get_risk_level(self, score):
        """Convert risk score to risk level"""
        if score >= 80:
            return 'Critical'
        elif score >= 60:
            return 'High'
        elif score >= 40:
            return 'Medium'
        elif score >= 20:
            return 'Low'
        else:
            return 'Safe'

# Global instance
domain_checker = DomainChecker() 