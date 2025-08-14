#!/usr/bin/env python3

import requests
import re
import time
from urllib.parse import quote_plus
from ultra_fast_linkedin_email import UltraFastLinkedInEmailFinder

class InternetWorkEmailFinder:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
    
    def search_for_work_email(self, person_name, linkedin_url):
        """Search the internet for work email addresses"""
        print(f"🔍 Searching internet for {person_name}'s work email")
        
        # Extract username from LinkedIn URL
        username = linkedin_url.split('/in/')[-1].rstrip('/')
        print(f"👤 LinkedIn username: {username}")
        
        # Generate search queries
        search_queries = [
            f'"{person_name}" email',
            f'"{person_name}" contact',
            f'"{person_name}" work email',
            f'"{person_name}" business email',
            f'"{person_name}" @',
            f'"{person_name}" linkedin email',
            f'"{username}" email',
            f'"{person_name}" company email',
        ]
        
        found_emails = []
        
        for query in search_queries:
            try:
                print(f"🔍 Searching: {query}")
                
                # Search Google
                google_results = self._search_google(query)
                emails = self._extract_emails_from_text(google_results)
                found_emails.extend(emails)
                
                # Search Bing
                bing_results = self._search_bing(query)
                emails = self._extract_emails_from_text(bing_results)
                found_emails.extend(emails)
                
                time.sleep(1)  # Be respectful
                
            except Exception as e:
                print(f"❌ Error searching: {e}")
                continue
        
        # Remove duplicates and filter
        unique_emails = list(set(found_emails))
        filtered_emails = [email for email in unique_emails if self._is_valid_work_email(email, person_name)]
        
        return filtered_emails
    
    def _search_google(self, query):
        """Search Google for the query"""
        try:
            search_url = f"https://www.google.com/search?q={quote_plus(query)}"
            response = self.session.get(search_url, timeout=10)
            return response.text
        except Exception as e:
            print(f"❌ Google search error: {e}")
            return ""
    
    def _search_bing(self, query):
        """Search Bing for the query"""
        try:
            search_url = f"https://www.bing.com/search?q={quote_plus(query)}"
            response = self.session.get(search_url, timeout=10)
            return response.text
        except Exception as e:
            print(f"❌ Bing search error: {e}")
            return ""
    
    def _extract_emails_from_text(self, text):
        """Extract email addresses from text"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        return emails
    
    def _is_valid_work_email(self, email, person_name):
        """Check if email is likely a work email for the person"""
        # Skip obvious non-work emails
        if any(domain in email.lower() for domain in ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'aol.com']):
            return False
        
        # Skip common spam/placeholder emails
        if any(word in email.lower() for word in ['example.com', 'test.com', 'placeholder.com', 'domain.com']):
            return False
        
        # Check if email contains person's name
        name_parts = person_name.lower().split()
        email_lower = email.lower()
        
        # At least one name part should be in the email
        if any(part in email_lower for part in name_parts):
            return True
        
        return False

def find_darby_work_email():
    finder = InternetWorkEmailFinder()
    email_verifier = UltraFastLinkedInEmailFinder()
    
    # Darby Wright's information
    person_name = "Darby Wright"
    linkedin_url = "https://www.linkedin.com/in/darby-wright-6ba805172/"
    
    print("🔍 Finding Darby Wright's Work Email (Internet Search)")
    print("=" * 60)
    
    # Search for work emails
    found_emails = finder.search_for_work_email(person_name, linkedin_url)
    
    if not found_emails:
        print("❌ No work emails found through internet search")
        print("💡 Try using LinkedIn messaging to contact Darby directly")
        return
    
    print(f"\n🔍 Found {len(found_emails)} potential work emails")
    
    # Verify emails
    verified_emails = []
    with email_verifier.session as session:
        for email in found_emails:
            print(f"🔍 Verifying: {email}")
            result = email_verifier._verify_email_fast(email)
            if result and result.get('can_receive'):
                verified_emails.append(email)
                print(f"✅ Verified: {email}")
            else:
                print(f"❌ Failed: {email}")
    
    # Rank emails
    ranked_emails = []
    for email in verified_emails:
        confidence = 0
        
        # Name matching
        name_parts = person_name.lower().split()
        if any(part in email.lower() for part in name_parts):
            confidence += 40
        
        # Domain quality (non-personal domains)
        domain = email.split('@')[1]
        if domain not in ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com']:
            confidence += 50
        
        # Format validation
        if re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            confidence += 20
        
        if confidence > 0:
            ranked_emails.append({
                'email': email,
                'confidence': confidence
            })
    
    # Sort by confidence
    ranked_emails.sort(key=lambda x: x['confidence'], reverse=True)
    
    # Display results
    if ranked_emails:
        print(f"\n✅ Found {len(ranked_emails)} verified work email(s):")
        
        for i, email_info in enumerate(ranked_emails, 1):
            print(f"  {i}. {email_info['email']} ({email_info['confidence']}%) - 🏢 WORK")
        
        print(f"\n🎯 RECOMMENDED (Work): {ranked_emails[0]['email']}")
        
        if len(ranked_emails) > 1:
            print(f"📧 Alternative (Work): {ranked_emails[1]['email']}")
    else:
        print("\n❌ No verified work emails found")
        print("💡 Try using LinkedIn messaging to contact Darby directly")

if __name__ == "__main__":
    import re
    find_darby_work_email() 