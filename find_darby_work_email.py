#!/usr/bin/env python3

import requests
import re
import time
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from ultra_fast_linkedin_email import UltraFastLinkedInEmailFinder

class LinkedInCompanyScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
    
    def get_company_info(self, linkedin_url):
        """Scrape LinkedIn profile to get current company information"""
        try:
            print(f"🔍 Scraping LinkedIn profile: {linkedin_url}")
            
            # Add delay to avoid rate limiting
            time.sleep(2)
            
            response = self.session.get(linkedin_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for company information in various places
            company_info = self._extract_company_info(soup)
            
            if company_info:
                print(f"✅ Found company: {company_info['company']}")
                if company_info.get('domain'):
                    print(f"🌐 Company domain: {company_info['domain']}")
                return company_info
            else:
                print("❌ Could not extract company information")
                return None
                
        except Exception as e:
            print(f"❌ Error scraping LinkedIn: {e}")
            return None
    
    def _extract_company_info(self, soup):
        """Extract company information from LinkedIn page"""
        company_info = {}
        
        # Method 1: Look for current position/company in the main content
        selectors = [
            '[data-section="currentPositionsDetails"]',
            '[data-section="experience"]',
            '.experience__company-name',
            '.pv-entity__company-name',
            '.experience-group__company-name',
            '.pv-text-details__right-panel',
            '.text-body-medium',
            '.pv-text-details__left-panel'
        ]
        
        for selector in selectors:
            elements = soup.select(selector)
            for element in elements:
                text = element.get_text(strip=True)
                if text and len(text) > 2 and len(text) < 100:
                    # Look for company-like text
                    if any(word in text.lower() for word in ['inc', 'llc', 'corp', 'company', 'ltd', 'group', 'associates']):
                        company_info['company'] = text
                        break
                    # Or if it looks like a company name (capitalized words)
                    elif text[0].isupper() and ' ' in text:
                        company_info['company'] = text
                        break
        
        # Method 2: Look for company in the header area
        if not company_info.get('company'):
            header_selectors = [
                '.pv-text-details__left-panel',
                '.pv-top-card__company-name',
                '.pv-top-card__company-summary-info'
            ]
            
            for selector in header_selectors:
                elements = soup.select(selector)
                for element in elements:
                    text = element.get_text(strip=True)
                    if text and len(text) > 2 and len(text) < 100:
                        company_info['company'] = text
                        break
        
        # Method 3: Look for any text that might be a company name
        if not company_info.get('company'):
            # Search for patterns that look like company names
            text_elements = soup.find_all(text=True)
            for text in text_elements:
                text = text.strip()
                if text and len(text) > 3 and len(text) < 50:
                    # Look for company indicators
                    if any(indicator in text.lower() for indicator in ['inc', 'llc', 'corp', 'company', 'ltd', 'group']):
                        company_info['company'] = text
                        break
        
        # Try to extract domain from company name
        if company_info.get('company'):
            domain = self._extract_domain_from_company(company_info['company'])
            if domain:
                company_info['domain'] = domain
        
        return company_info if company_info.get('company') else None
    
    def _extract_domain_from_company(self, company_name):
        """Try to guess domain from company name"""
        # Remove common suffixes
        name = company_name.lower()
        name = re.sub(r'\s+(inc|llc|corp|company|ltd|group|associates|partners|solutions|systems|technologies|tech|software|consulting|consultants|services|agency|marketing|media|communications|international|global|worldwide|america|usa|us)\s*$', '', name)
        
        # Clean up the name
        name = re.sub(r'[^\w\s]', '', name)
        name = name.strip()
        
        # Convert to domain format
        domain = name.replace(' ', '').replace('&', 'and') + '.com'
        
        return domain

def find_darby_work_email():
    scraper = LinkedInCompanyScraper()
    finder = UltraFastLinkedInEmailFinder()
    
    # Darby Wright's LinkedIn URL
    linkedin_url = "https://www.linkedin.com/in/darby-wright-6ba805172/"
    
    print("🔍 Finding Darby Wright's Work Email")
    print("=" * 50)
    
    # First, scrape the LinkedIn profile to get company info
    company_info = scraper.get_company_info(linkedin_url)
    
    if not company_info:
        print("❌ Could not extract company information from LinkedIn")
        print("💡 Try using LinkedIn messaging to contact Darby directly")
        return
    
    # Generate work email candidates
    person_name = "Darby Wright"
    company_name = company_info['company']
    company_domain = company_info.get('domain', 'company.com')
    
    print(f"👤 Person: {person_name}")
    print(f"🏢 Company: {company_name}")
    print(f"🌐 Domain: {company_domain}")
    
    # Generate work email patterns
    name_parts = person_name.lower().split()
    first_name, last_name = name_parts[0], name_parts[-1]
    
    work_email_candidates = [
        f"{first_name}.{last_name}@{company_domain}",
        f"{first_name}{last_name}@{company_domain}",
        f"{first_name}_{last_name}@{company_domain}",
        f"{last_name}.{first_name}@{company_domain}",
        f"{first_name[0]}{last_name}@{company_domain}",
        f"{first_name}{last_name[0]}@{company_domain}",
        f"darby.wright@{company_domain}",
        f"darbywright@{company_domain}",
        f"darby@{company_domain}",
        f"dwright@{company_domain}",
        f"wright@{company_domain}",
    ]
    
    print(f"🔍 Generated {len(work_email_candidates)} work email candidates")
    
    # Verify work emails
    verified_work_emails = []
    with finder.session as session:
        for email in work_email_candidates:
            result = finder._verify_email_fast(email)
            if result and result.get('can_receive'):
                verified_work_emails.append(email)
    
    # Rank work emails
    ranked_work_emails = []
    for email in verified_work_emails:
        confidence = 0
        
        # Name matching
        if any(part in email.lower() for part in ['darby', 'wright']):
            confidence += 40
        
        # Domain matching
        if company_domain in email:
            confidence += 50
        
        # Format validation
        if re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            confidence += 20
        
        if confidence > 0:
            ranked_work_emails.append({
                'email': email,
                'confidence': confidence
            })
    
    # Sort by confidence
    ranked_work_emails.sort(key=lambda x: x['confidence'], reverse=True)
    
    # Display results
    if ranked_work_emails:
        print(f"\n✅ Found {len(ranked_work_emails)} verified work email(s):")
        
        for i, email_info in enumerate(ranked_work_emails, 1):
            print(f"  {i}. {email_info['email']} ({email_info['confidence']}%) - 🏢 WORK")
        
        print(f"\n🎯 RECOMMENDED (Work): {ranked_work_emails[0]['email']}")
        
        if len(ranked_work_emails) > 1:
            print(f"📧 Alternative (Work): {ranked_work_emails[1]['email']}")
    else:
        print("\n❌ No verified work emails found")
        print("💡 Try using LinkedIn messaging to contact Darby directly")

if __name__ == "__main__":
    import re
    find_darby_work_email() 