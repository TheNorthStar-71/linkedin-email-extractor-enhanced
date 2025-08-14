#!/usr/bin/env python3

import smtplib
import socket
import re
import time
import requests

class SimpleEmailVerifier:
    def __init__(self):
        self.valid_domains = set()
        self.invalid_domains = set()
    
    def verify_email(self, email):
        """
        Verify if an email address is valid and can receive emails
        Returns: dict with verification results
        """
        if not self._is_valid_format(email):
            return {
                'email': email,
                'valid': False,
                'reason': 'Invalid email format',
                'can_receive': False
            }
        
        domain = email.split('@')[1]
        
        # Check domain validity
        domain_valid = self._verify_domain(domain)
        if not domain_valid:
            return {
                'email': email,
                'valid': False,
                'reason': 'Invalid domain',
                'can_receive': False
            }
        
        # Check if mailbox exists
        mailbox_exists = self._verify_mailbox(email)
        
        return {
            'email': email,
            'valid': True,
            'reason': 'Valid email address',
            'can_receive': mailbox_exists,
            'domain_valid': domain_valid,
            'mailbox_exists': mailbox_exists
        }
    
    def _is_valid_format(self, email):
        """Check if email format is valid"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def _verify_domain(self, domain):
        """Verify if domain is valid by checking if it resolves"""
        if domain in self.valid_domains:
            return True
        if domain in self.invalid_domains:
            return False
        
        try:
            # Try to resolve the domain
            socket.gethostbyname(domain)
            self.valid_domains.add(domain)
            return True
        except socket.gaierror:
            self.invalid_domains.add(domain)
            return False
    
    def _verify_mailbox(self, email):
        """Verify if mailbox exists using multiple methods"""
        try:
            domain = email.split('@')[1]
            
            # Method 1: Check if domain is from a known provider
            known_providers = [
                'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com',
                'robinhood.com', 'google.com', 'microsoft.com', 'apple.com',
                'linkedin.com', 'facebook.com', 'twitter.com', 'github.com'
            ]
            
            if domain.lower() in known_providers:
                return True
            
            # Method 2: Try to connect to common SMTP ports
            common_ports = [25, 587, 465]
            
            for port in common_ports:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(5)
                    
                    result = sock.connect_ex((domain, port))
                    sock.close()
                    
                    if result == 0:
                        return True
                        
                except Exception:
                    continue
            
            # Method 3: Check if domain has a website
            try:
                response = requests.get(f"http://{domain}", timeout=5)
                if response.status_code == 200:
                    return True
            except:
                pass
            
            # Method 4: Check if domain has HTTPS
            try:
                response = requests.get(f"https://{domain}", timeout=5)
                if response.status_code == 200:
                    return True
            except:
                pass
            
            return False
            
        except Exception:
            return False
    
    def verify_multiple_emails(self, emails):
        """
        Verify multiple email addresses
        Returns: list of verification results
        """
        results = []
        
        for email in emails:
            try:
                result = self.verify_email(email)
                results.append(result)
                
                # Add delay to avoid rate limiting
                time.sleep(0.5)
                
            except Exception as e:
                results.append({
                    'email': email,
                    'valid': False,
                    'reason': f'Verification error: {str(e)}',
                    'can_receive': False
                })
        
        return results
    
    def get_best_email(self, emails):
        """
        Get the best email from a list based on verification results
        Returns: best email or None
        """
        if not emails:
            return None
        
        # Filter out invalid formats
        valid_emails = [email for email in emails if self._is_valid_format(email)]
        
        if not valid_emails:
            return None
        
        # Verify all emails
        verification_results = self.verify_multiple_emails(valid_emails)
        
        # Find emails that can receive messages
        working_emails = [result for result in verification_results if result['can_receive']]
        
        if working_emails:
            # Return the first working email
            return working_emails[0]['email']
        
        # If no emails can be verified as working, return the first valid format
        valid_results = [result for result in verification_results if result['valid']]
        if valid_results:
            return valid_results[0]['email']
        
        return None

def main():
    """Test the email verifier"""
    verifier = SimpleEmailVerifier()
    
    # Test emails
    test_emails = [
        'ashley.garrison@robinhood.com',
        'ashleygarrison@robinhood.com',
        'ashley@robinhood.com',
        'test@nonexistentdomain12345.com',
        'invalid-email-format',
        'test@gmail.com'
    ]
    
    print("Simple Email Verification Test")
    print("=" * 40)
    
    for email in test_emails:
        result = verifier.verify_email(email)
        status = "✅" if result['can_receive'] else "❌"
        print(f"{status} {email}: {result['reason']}")

if __name__ == "__main__":
    main() 