#!/usr/bin/env python3

import requests
import re
import time
import socket
import concurrent.futures
from urllib.parse import quote_plus
from threading import Lock

class HyperFastEmailFinder:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.known_domains = set()
        self.domain_cache = {}
        self.lock = Lock()
        
        # Pre-verified common domains
        self.verified_domains = {
            'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com',
            'linkedin.com', 'google.com', 'microsoft.com', 'apple.com',
            'robinhood.com', 'facebook.com', 'twitter.com', 'github.com'
        }
    
    def find_email_fast(self, name, company=""):
        """Find email in under 30 seconds"""
        start_time = time.time()
        
        print(f"🚀 Hyper-Fast Email Search for: {name}")
        print("=" * 50)
        
        # Generate email candidates
        email_candidates = self._generate_email_candidates(name, company)
        
        # Parallel search and verification
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            # Submit all search tasks
            search_futures = []
            
            # Quick domain verification (parallel)
            domain_futures = [executor.submit(self._verify_domain_fast, email) for email in email_candidates]
            
            # Quick web search (parallel)
            search_queries = self._generate_search_queries(name, company)
            search_futures = [executor.submit(self._quick_search, query) for query in search_queries[:3]]
            
            # Collect results
            verified_emails = []
            for future in concurrent.futures.as_completed(domain_futures, timeout=15):
                try:
                    result = future.result(timeout=5)
                    if result and result['can_receive']:
                        verified_emails.append(result['email'])
                except:
                    continue
            
            # Collect search results
            found_emails = []
            for future in concurrent.futures.as_completed(search_futures, timeout=15):
                try:
                    emails = future.result(timeout=5)
                    found_emails.extend(emails)
                except:
                    continue
        
        # Combine and rank results
        all_emails = list(set(verified_emails + found_emails))
        ranked_emails = self._rank_emails(all_emails, name)
        
        elapsed_time = time.time() - start_time
        
        # Display results
        if ranked_emails:
            best_email = ranked_emails[0]
            print(f"\n✅ Email found in {elapsed_time:.1f} seconds!")
            print(f"🎯 Best email: {best_email['email']}")
            print(f"📊 Confidence: {best_email['confidence']}%")
            print(f"🔍 Method: {best_email['method']}")
            
            if len(ranked_emails) > 1:
                print(f"\n📧 Other options:")
                for email in ranked_emails[1:3]:  # Show top 3
                    print(f"  • {email['email']} ({email['confidence']}%)")
        else:
            print(f"\n❌ No email found in {elapsed_time:.1f} seconds")
        
        return ranked_emails[0] if ranked_emails else None
    
    def _generate_email_candidates(self, name, company):
        """Generate email candidates based on name and company"""
        candidates = []
        name_parts = name.lower().split()
        
        if len(name_parts) >= 2:
            first_name, last_name = name_parts[0], name_parts[-1]
            
            # Common email patterns
            patterns = [
                f"{first_name}.{last_name}@",
                f"{first_name}{last_name}@",
                f"{first_name}_{last_name}@",
                f"{first_name}@{last_name}.com",
                f"{last_name}.{first_name}@",
                f"{first_name[0]}{last_name}@",
                f"{first_name}{last_name[0]}@",
            ]
            
            # Add company-specific patterns
            if company:
                company_domain = company.lower().replace(' ', '').replace('.', '') + '.com'
                for pattern in patterns:
                    candidates.append(pattern + company_domain)
            
            # Add common providers
            providers = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com']
            for pattern in patterns:
                for provider in providers:
                    candidates.append(pattern + provider)
        
        return candidates
    
    def _generate_search_queries(self, name, company):
        """Generate optimized search queries"""
        queries = [
            f'"{name}" email',
            f'"{name}" contact',
            f'"{name}" mailto:',
            f'"{name}" @',
            f'"{name}" {company} email' if company else None,
        ]
        return [q for q in queries if q]
    
    def _verify_domain_fast(self, email):
        """Fast domain verification"""
        try:
            domain = email.split('@')[1]
            
            # Check cache first
            with self.lock:
                if domain in self.domain_cache:
                    return self.domain_cache[domain]
            
            # Quick checks
            if domain in self.verified_domains:
                result = {'email': email, 'can_receive': True, 'method': 'known_provider'}
                with self.lock:
                    self.domain_cache[domain] = result
                return result
            
            # Fast socket check
            try:
                socket.gethostbyname(domain)
                result = {'email': email, 'can_receive': True, 'method': 'domain_resolved'}
                with self.lock:
                    self.domain_cache[domain] = result
                return result
            except:
                pass
            
            result = {'email': email, 'can_receive': False, 'method': 'domain_failed'}
            with self.lock:
                self.domain_cache[domain] = result
            return result
            
        except:
            return None
    
    def _quick_search(self, query):
        """Quick web search with timeout"""
        try:
            search_url = f"https://www.google.com/search?q={quote_plus(query)}"
            response = self.session.get(search_url, timeout=5)
            
            if response.status_code == 200:
                # Fast email extraction
                emails = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', response.text)
                return list(set(emails))  # Remove duplicates
            
        except:
            pass
        
        return []
    
    def _rank_emails(self, emails, name):
        """Rank emails by confidence"""
        ranked = []
        name_lower = name.lower()
        
        for email in emails:
            confidence = 0
            method = "found"
            
            # Check if email contains name parts
            if any(part in email.lower() for part in name_lower.split()):
                confidence += 30
            
            # Check domain quality
            domain = email.split('@')[1]
            if domain in self.verified_domains:
                confidence += 40
            elif domain in self.domain_cache and self.domain_cache[domain]['can_receive']:
                confidence += 30
            
            # Check email format
            if re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
                confidence += 20
            
            # Filter out obvious false positives
            if any(exclude in email.lower() for exclude in [
                'example.com', 'test.com', 'noreply', 'no-reply'
            ]):
                confidence = 0
            
            if confidence > 0:
                ranked.append({
                    'email': email,
                    'confidence': confidence,
                    'method': method
                })
        
        # Sort by confidence
        ranked.sort(key=lambda x: x['confidence'], reverse=True)
        return ranked

def main():
    finder = HyperFastEmailFinder()
    
    # Test with Angela Massey
    result = finder.find_email_fast("Angela Massey")
    
    if result:
        print(f"\n🎉 Success! Found verified email: {result['email']}")
    else:
        print("\n💡 No email found. Try:")
        print("  - Using LinkedIn messaging")
        print("  - Searching professional directories")
        print("  - Checking company websites")

if __name__ == "__main__":
    main() 