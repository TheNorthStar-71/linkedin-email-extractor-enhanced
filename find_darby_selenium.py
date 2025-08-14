#!/usr/bin/env python3

import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from ultra_fast_linkedin_email import UltraFastLinkedInEmailFinder

class LinkedInSeleniumScraper:
    def __init__(self):
        self.driver = None
        self._setup_driver()
    
    def _setup_driver(self):
        """Setup Chrome driver with anti-detection options"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        except Exception as e:
            print(f"❌ Error setting up Chrome driver: {e}")
            print("💡 Make sure Chrome is installed and chromedriver is available")
            self.driver = None
    
    def get_company_info(self, linkedin_url):
        """Scrape LinkedIn profile using Selenium to get company information"""
        if not self.driver:
            print("❌ Chrome driver not available")
            return None
        
        try:
            print(f"🔍 Scraping LinkedIn profile with Selenium: {linkedin_url}")
            
            self.driver.get(linkedin_url)
            time.sleep(3)  # Wait for page to load
            
            # Try to find company information in various selectors
            company_info = self._extract_company_info()
            
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
        finally:
            if self.driver:
                self.driver.quit()
    
    def _extract_company_info(self):
        """Extract company information from LinkedIn page"""
        company_info = {}
        
        # Try multiple selectors for company information
        selectors = [
            '.pv-text-details__left-panel',
            '.pv-top-card__company-name',
            '.pv-top-card__company-summary-info',
            '[data-section="currentPositionsDetails"]',
            '[data-section="experience"]',
            '.experience__company-name',
            '.pv-entity__company-name',
            '.experience-group__company-name',
            '.text-body-medium',
            '.pv-text-details__right-panel',
            '.pv-entity__secondary-title',
            '.pv-entity__company-summary-info'
        ]
        
        for selector in selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    text = element.text.strip()
                    if text and len(text) > 2 and len(text) < 100:
                        # Look for company-like text
                        if any(word in text.lower() for word in ['inc', 'llc', 'corp', 'company', 'ltd', 'group', 'associates', 'partners', 'solutions', 'systems', 'technologies', 'tech', 'software', 'consulting', 'consultants', 'services', 'agency', 'marketing', 'media', 'communications']):
                            company_info['company'] = text
                            break
                        # Or if it looks like a company name (capitalized words)
                        elif text[0].isupper() and ' ' in text and len(text.split()) <= 4:
                            company_info['company'] = text
                            break
                
                if company_info.get('company'):
                    break
                    
            except Exception as e:
                continue
        
        # If still no company found, try to get any text that might be a company
        if not company_info.get('company'):
            try:
                # Get all text from the page and look for company patterns
                page_text = self.driver.find_element(By.TAG_NAME, 'body').text
                lines = page_text.split('\n')
                
                for line in lines:
                    line = line.strip()
                    if line and len(line) > 3 and len(line) < 50:
                        # Look for company indicators
                        if any(indicator in line.lower() for indicator in ['inc', 'llc', 'corp', 'company', 'ltd', 'group', 'associates', 'partners', 'solutions', 'systems', 'technologies', 'tech', 'software', 'consulting', 'consultants', 'services', 'agency', 'marketing', 'media', 'communications']):
                            company_info['company'] = line
                            break
                        # Or if it looks like a company name (capitalized words, reasonable length)
                        elif line[0].isupper() and ' ' in line and len(line.split()) <= 4 and len(line) > 5:
                            company_info['company'] = line
                            break
            except Exception as e:
                pass
        
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
    scraper = LinkedInSeleniumScraper()
    finder = UltraFastLinkedInEmailFinder()
    
    # Darby Wright's LinkedIn URL
    linkedin_url = "https://www.linkedin.com/in/darby-wright-6ba805172/"
    
    print("🔍 Finding Darby Wright's Work Email (Selenium Method)")
    print("=" * 60)
    
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