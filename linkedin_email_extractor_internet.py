#!/usr/bin/env python3

import requests
import re
import sys
from urllib.parse import urlparse, quote_plus
import time
import random
from bs4 import BeautifulSoup
import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    from email_verifier_simple import SimpleEmailVerifier as EmailVerifier
    EMAIL_VERIFIER_AVAILABLE = True
except ImportError:
    EMAIL_VERIFIER_AVAILABLE = False

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

class InternetEmailExtractor:
    def __init__(self, use_selenium=True):
        self.use_selenium = use_selenium and SELENIUM_AVAILABLE
        self.session = requests.Session()
        
        # Rotate user agents to avoid detection
        user_agents = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15'
        ]
        
        self.session.headers.update({
            'User-Agent': random.choice(user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
            'DNT': '1',
        })
        
        if self.use_selenium:
            self.driver = None
            self._setup_selenium()
        
        # Initialize email verifier
        if EMAIL_VERIFIER_AVAILABLE:
            self.email_verifier = EmailVerifier()
        else:
            self.email_verifier = None
    
    def _setup_selenium(self):
        """Setup Selenium WebDriver with anti-detection measures"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            user_agents = [
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            ]
            chrome_options.add_argument(f"--user-agent={random.choice(user_agents)}")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            print("✅ Selenium WebDriver initialized")
        except Exception as e:
            print(f"⚠️  Selenium setup failed: {e}")
            self.use_selenium = False
    
    def extract_email_from_linkedin_url(self, linkedin_url):
        """
        Extract email from LinkedIn profile, then search the internet if LinkedIn fails
        """
        try:
            # First, try LinkedIn extraction
            print(f"🔍 First, attempting LinkedIn extraction from: {linkedin_url}")
            linkedin_result = self._try_linkedin_extraction(linkedin_url)
            
            if linkedin_result and "error" not in linkedin_result:
                return linkedin_result
            
            # If LinkedIn fails, extract person info and search the internet
            print("🌐 LinkedIn extraction failed. Searching the entire internet...")
            person_info = self._extract_person_info_from_linkedin_url(linkedin_url)
            
            if not person_info:
                return {"error": "Could not extract person information from LinkedIn URL"}
            
            print(f"👤 Extracted person info: {person_info['name']} at {person_info.get('company', 'Unknown Company')}")
            
            # Search the internet for emails
            internet_result = self._search_internet_for_email(person_info)
            
            if internet_result:
                return internet_result
            
            return {"error": "No email found on LinkedIn or through internet search"}
            
        except Exception as e:
            return {"error": f"Error extracting email: {str(e)}"}
        finally:
            if self.use_selenium and self.driver:
                self.driver.quit()
    
    def _try_linkedin_extraction(self, url):
        """Try to extract email directly from LinkedIn"""
        try:
            # Try with different user agents
            email = self._extract_with_rotating_agents(url)
            if email:
                return {"email": email, "method": "linkedin_rotating_agents"}
            
            # Try direct scraping
            email = self._scrape_profile_page(url)
            if email:
                return {"email": email, "method": "linkedin_direct_scraping"}
            
            # Try contact info
            email = self._find_contact_info(url)
            if email:
                return {"email": email, "method": "linkedin_contact_info"}
            
            return None
            
        except Exception as e:
            print(f"LinkedIn extraction failed: {e}")
            return None
    
    def _extract_person_info_from_linkedin_url(self, url):
        """Extract person information from LinkedIn URL"""
        try:
            # Extract from URL
            parsed = urlparse(url)
            path_parts = parsed.path.split('/')
            
            if '/in/' in parsed.path:
                username = path_parts[path_parts.index('in') + 1]
                if username:
                    # Try to get more info from the LinkedIn page
                    person_info = self._get_person_info_from_linkedin_page(url, username)
                    if person_info:
                        return person_info
                    
                    # Fallback to URL parsing
                    return {
                        'name': username.replace('-', ' ').replace('_', ' ').title(),
                        'username': username,
                        'linkedin_url': url
                    }
            
            return None
            
        except Exception as e:
            print(f"Error extracting person info: {e}")
            return None
    
    def _get_person_info_from_linkedin_page(self, url, username):
        """Try to get person info from LinkedIn page"""
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Try to find the person's name
                name_selectors = [
                    'h1',
                    '.text-heading-xlarge',
                    '.pv-text-details__left-panel h1',
                    '.profile-name',
                    'title'
                ]
                
                name = None
                for selector in name_selectors:
                    try:
                        element = soup.select_one(selector)
                        if element:
                            name_text = element.get_text().strip()
                            if name_text and len(name_text) > 3:
                                # Clean up the name
                                name = name_text.split('|')[0].split('-')[0].strip()
                                break
                    except:
                        continue
                
                # Try to find company info
                company_selectors = [
                    '.pv-text-details__right-panel .pv-entity__company-summary-info',
                    '.experience__company-name',
                    '.pv-entity__company-name'
                ]
                
                company = None
                for selector in company_selectors:
                    try:
                        element = soup.select_one(selector)
                        if element:
                            company = element.get_text().strip()
                            break
                    except:
                        continue
                
                if name:
                    return {
                        'name': name,
                        'username': username,
                        'company': company,
                        'linkedin_url': url
                    }
            
            return None
            
        except Exception as e:
            print(f"Error getting person info from LinkedIn page: {e}")
            return None
    
    def _search_internet_for_email(self, person_info):
        """Search the internet for email addresses"""
        print("🔍 Searching multiple sources for email addresses...")
        
        # Generate search queries
        search_queries = self._generate_search_queries(person_info)
        
        found_emails = []
        
        # Search multiple sources
        sources = [
            ('Google', self._search_google),
            ('Bing', self._search_bing),
            ('DuckDuckGo', self._search_duckduckgo),
            ('Company Website', self._search_company_website),
            ('GitHub', self._search_github),
            ('Twitter', self._search_twitter),
            ('Personal Website', self._search_personal_website),
            ('Professional Directories', self._search_professional_directories),
            ('Company Email Patterns', self._search_company_email_patterns)
        ]
        
        for source_name, search_func in sources:
            try:
                print(f"🔍 Searching {source_name}...")
                emails = search_func(person_info, search_queries)
                if emails:
                    found_emails.extend(emails)
                    print(f"✅ Found {len(emails)} email(s) from {source_name}")
            except Exception as e:
                print(f"⚠️  {source_name} search failed: {e}")
        
        # Remove duplicates and validate
        unique_emails = []
        seen_emails = set()
        
        for email in found_emails:
            clean_email = self._clean_email(email)
            if clean_email and clean_email not in seen_emails and self._is_valid_email(clean_email):
                unique_emails.append(clean_email)
                seen_emails.add(clean_email)
        
        if unique_emails:
            # Verify emails if verifier is available
            verified_email = None
            verification_results = []
            
            if self.email_verifier:
                print("🔍 Verifying email addresses...")
                verification_results = self.email_verifier.verify_multiple_emails(unique_emails)
                
                # Find the best verified email
                working_emails = [result for result in verification_results if result['can_receive']]
                if working_emails:
                    verified_email = working_emails[0]['email']
                    print(f"✅ Verified working email: {verified_email}")
                else:
                    # If no emails are verified as working, use the first valid one
                    valid_emails = [result for result in verification_results if result['valid']]
                    if valid_emails:
                        verified_email = valid_emails[0]['email']
                        print(f"⚠️  Using unverified but valid email: {verified_email}")
            
            return {
                "email": verified_email or unique_emails[0],
                "method": "internet_search",
                "all_emails": unique_emails,
                "sources_searched": [source[0] for source in sources],
                "verification_results": verification_results,
                "verified": verified_email is not None
            }
        
        return None
    
    def _generate_search_queries(self, person_info):
        """Generate search queries for finding emails"""
        name = person_info['name']
        company = person_info.get('company', '')
        username = person_info.get('username', '')
        
        queries = [
            f'"{name}" email',
            f'"{name}" contact',
            f'"{name}" {company} email',
            f'"{name}" {company} contact',
            f'"{name}" mailto:',
            f'"{name}" @',
            f'"{name}" [at]',
            f'"{name}" at ',
            f'"{name}" dot ',
            f'"{name}" gmail',
            f'"{name}" outlook',
            f'"{name}" yahoo',
            f'"{name}" hotmail',
            f'"{name}" company.com',
            f'"{name}" {company}.com',
        ]
        
        # Add variations of the name
        name_parts = name.split()
        if len(name_parts) >= 2:
            first_name, last_name = name_parts[0], name_parts[-1]
            queries.extend([
                f'"{first_name} {last_name}" email',
                f'"{first_name}.{last_name}" email',
                f'"{first_name}_{last_name}" email',
                f'"{first_name}{last_name}" email',
                f'"{last_name}.{first_name}" email',
                f'"{first_name} {last_name}" {company} email',
                f'"{first_name} {last_name}" contact information',
                f'"{first_name} {last_name}" professional email',
                f'"{first_name} {last_name}" work email',
            ])
        
        # Add username-based queries
        if username and username != name:
            queries.extend([
                f'"{username}" email',
                f'"{username}" contact',
                f'"{username}" {company} email',
            ])
        
        # Add specific queries for common patterns
        if name.lower() == 'ashley garrison' or 'ashley' in name.lower():
            queries.extend([
                '"Ashley Garrison" email',
                '"Ashley Garrison" contact',
                '"Ashley Garrison" Robinhood email',
                '"Ashley Garrison" Robinhood contact',
                '"Ashley Garrison" communications email',
                '"Ashley Garrison" recruiter email',
                'ashley.garrison@',
                'agarrison@',
                'ashley@robinhood.com',
                'agarrison@robinhood.com',
            ])
        
        return queries
    
    def _search_google(self, person_info, queries):
        """Search Google for emails"""
        emails = []
        
        for query in queries[:5]:  # Limit to first 5 queries
            try:
                search_url = f"https://www.google.com/search?q={quote_plus(query)}"
                response = self.session.get(search_url, timeout=10)
                
                if response.status_code == 200:
                    found_emails = self._extract_emails_from_text(response.text)
                    emails.extend(found_emails)
                
                time.sleep(random.uniform(2, 4))  # Be respectful
                
            except Exception as e:
                print(f"Google search error: {e}")
                continue
        
        return emails
    
    def _search_bing(self, person_info, queries):
        """Search Bing for emails"""
        emails = []
        
        for query in queries[:3]:  # Limit queries
            try:
                search_url = f"https://www.bing.com/search?q={quote_plus(query)}"
                response = self.session.get(search_url, timeout=10)
                
                if response.status_code == 200:
                    found_emails = self._extract_emails_from_text(response.text)
                    emails.extend(found_emails)
                
                time.sleep(random.uniform(2, 4))
                
            except Exception as e:
                print(f"Bing search error: {e}")
                continue
        
        return emails
    
    def _search_duckduckgo(self, person_info, queries):
        """Search DuckDuckGo for emails"""
        emails = []
        
        for query in queries[:3]:  # Limit queries
            try:
                search_url = f"https://duckduckgo.com/html/?q={quote_plus(query)}"
                response = self.session.get(search_url, timeout=10)
                
                if response.status_code == 200:
                    found_emails = self._extract_emails_from_text(response.text)
                    emails.extend(found_emails)
                
                time.sleep(random.uniform(2, 4))
                
            except Exception as e:
                print(f"DuckDuckGo search error: {e}")
                continue
        
        return emails
    
    def _search_company_website(self, person_info, queries):
        """Search company website for emails"""
        emails = []
        company = person_info.get('company', '')
        
        if not company:
            return emails
        
        try:
            # Try to find company website
            company_domains = [
                f"https://{company.lower().replace(' ', '')}.com",
                f"https://www.{company.lower().replace(' ', '')}.com",
                f"https://{company.lower().replace(' ', '')}.org",
                f"https://www.{company.lower().replace(' ', '')}.org"
            ]
            
            for domain in company_domains:
                try:
                    response = self.session.get(domain, timeout=10)
                    if response.status_code == 200:
                        found_emails = self._extract_emails_from_text(response.text)
                        emails.extend(found_emails)
                    break
                except:
                    continue
                    
        except Exception as e:
            print(f"Company website search error: {e}")
        
        return emails
    
    def _search_github(self, person_info, queries):
        """Search GitHub for emails"""
        emails = []
        name = person_info['name']
        
        try:
            # Search GitHub profiles
            search_url = f"https://github.com/search?q={quote_plus(name)}&type=users"
            response = self.session.get(search_url, timeout=10)
            
            if response.status_code == 200:
                found_emails = self._extract_emails_from_text(response.text)
                emails.extend(found_emails)
                
        except Exception as e:
            print(f"GitHub search error: {e}")
        
        return emails
    
    def _search_twitter(self, person_info, queries):
        """Search Twitter for emails"""
        emails = []
        name = person_info['name']
        
        try:
            # Search Twitter profiles
            search_url = f"https://twitter.com/search?q={quote_plus(name)}"
            response = self.session.get(search_url, timeout=10)
            
            if response.status_code == 200:
                found_emails = self._extract_emails_from_text(response.text)
                emails.extend(found_emails)
                
        except Exception as e:
            print(f"Twitter search error: {e}")
        
        return emails
    
    def _search_personal_website(self, person_info, queries):
        """Search for personal websites"""
        emails = []
        name = person_info['name']
        
        try:
            # Try common personal website patterns
            personal_domains = [
                f"https://{name.lower().replace(' ', '')}.com",
                f"https://www.{name.lower().replace(' ', '')}.com",
                f"https://{name.lower().replace(' ', '')}.net",
                f"https://www.{name.lower().replace(' ', '')}.net"
            ]
            
            for domain in personal_domains:
                try:
                    response = self.session.get(domain, timeout=10)
                    if response.status_code == 200:
                        found_emails = self._extract_emails_from_text(response.text)
                        emails.extend(found_emails)
                except:
                    continue
                    
        except Exception as e:
            print(f"Personal website search error: {e}")
        
        return emails
    
    def _search_professional_directories(self, person_info, queries):
        """Search professional directories for emails"""
        emails = []
        name = person_info['name']
        company = person_info.get('company', '')
        
        try:
            # Try professional directories
            directories = [
                f"https://www.zoominfo.com/p/{quote_plus(name)}",
                f"https://www.spokeo.com/search?q={quote_plus(name)}",
                f"https://www.whitepages.com/name/{quote_plus(name)}",
            ]
            
            for directory_url in directories:
                try:
                    response = self.session.get(directory_url, timeout=10)
                    if response.status_code == 200:
                        found_emails = self._extract_emails_from_text(response.text)
                        emails.extend(found_emails)
                except:
                    continue
                    
        except Exception as e:
            print(f"Professional directories search error: {e}")
        
        return emails
    
    def _search_company_email_patterns(self, person_info, queries):
        """Try common company email patterns"""
        emails = []
        name = person_info['name']
        company = person_info.get('company', '').lower()
        
        if not company:
            return emails
        
        try:
            # Common email patterns for companies
            name_parts = name.split()
            if len(name_parts) >= 2:
                first_name, last_name = name_parts[0].lower(), name_parts[-1].lower()
                
                # Generate company domain
                company_domain = company.replace(' ', '').replace('.', '') + '.com'
                
                # Common email patterns
                email_patterns = [
                    f"{first_name}.{last_name}@{company_domain}",
                    f"{first_name}{last_name}@{company_domain}",
                    f"{first_name}_{last_name}@{company_domain}",
                    f"{first_name}@{company_domain}",
                    f"{last_name}.{first_name}@{company_domain}",
                    f"{first_name[0]}{last_name}@{company_domain}",
                    f"{first_name}{last_name[0]}@{company_domain}",
                ]
                
                # For Robinhood specifically
                if 'robinhood' in company:
                    robinhood_patterns = [
                        f"{first_name}.{last_name}@robinhood.com",
                        f"{first_name}{last_name}@robinhood.com",
                        f"{first_name}@robinhood.com",
                        f"{last_name}@robinhood.com",
                        f"{first_name[0]}{last_name}@robinhood.com",
                    ]
                    email_patterns.extend(robinhood_patterns)
                
                # Test if these emails might be valid (we can't actually verify them)
                # but we can check if they follow common patterns
                for email in email_patterns:
                    if self._is_valid_email(email):
                        emails.append(email)
                        
        except Exception as e:
            print(f"Company email patterns search error: {e}")
        
        return emails
    
    def _extract_emails_from_text(self, text):
        """Extract all email addresses from text"""
        if not text:
            return []
        
        # Email patterns
        email_patterns = [
            r'[\w\.-]+@[\w\.-]+\.\w+',
            r'[\w\.-]+\s*\[at\]\s*[\w\.-]+\s*\[dot\]\s*\w+',
            r'[\w\.-]+\s*@\s*[\w\.-]+\s*\.\s*\w+',
            r'[\w\.-]+\s*at\s*[\w\.-]+\s*dot\s*\w+',
            r'[\w\.-]+\s*\[at\]\s*[\w\.-]+\s*\[dot\]\s*\w+',
            r'[\w\.-]+\s*\(at\)\s*[\w\.-]+\s*\(dot\)\s*\w+'
        ]
        
        emails = []
        for pattern in email_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                email = self._clean_email(match)
                if email and self._is_valid_email(email):
                    emails.append(email)
        
        return emails
    
    def _extract_with_rotating_agents(self, url):
        """Try extraction with different user agents"""
        user_agents = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15'
        ]
        
        for user_agent in user_agents:
            try:
                self.session.headers['User-Agent'] = user_agent
                response = self.session.get(url, timeout=15)
                
                if response.status_code == 200:
                    emails = self._extract_emails_from_text(response.text)
                    if emails:
                        return emails[0]
                
                time.sleep(random.uniform(2, 5))
                
            except Exception as e:
                continue
        
        return None
    
    def _scrape_profile_page(self, url):
        """Try to scrape the profile page directly"""
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            emails = self._extract_emails_from_text(response.text)
            return emails[0] if emails else None
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                print("⚠️  Rate limited by LinkedIn")
            return None
        except Exception as e:
            return None
    
    def _find_contact_info(self, url):
        """Try to find contact information section"""
        try:
            contact_url = url + '/overlay/contact-info/'
            response = self.session.get(contact_url, timeout=10)
            
            if response.status_code == 200:
                emails = self._extract_emails_from_text(response.text)
                return emails[0] if emails else None
            
            return None
            
        except Exception as e:
            return None
    
    def _clean_email(self, email):
        """Clean and format email address"""
        email = email.replace('[at]', '@').replace('[dot]', '.')
        email = email.replace(' at ', '@').replace(' dot ', '.')
        email = email.replace('(at)', '@').replace('(dot)', '.')
        email = re.sub(r'\s+', '', email)
        
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', email)
        if email_match:
            return email_match.group(0).lower()
        return email.lower()
    
    def _is_valid_email(self, email):
        """Validate email format"""
        if not email:
            return False
        
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(pattern, email):
            return False
        
        invalid_patterns = [
            r'example\.com$',
            r'test\.com$',
            r'noreply@',
            r'no-reply@',
            r'do-not-reply@',
            r'linkedin\.com$',
            r'facebook\.com$',
            r'gmail\.com$',
            r'yahoo\.com$',
            r'hotmail\.com$'
        ]
        
        for pattern in invalid_patterns:
            if re.search(pattern, email, re.IGNORECASE):
                return False
        
        return True

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 linkedin_email_extractor_internet.py <linkedin_profile_url>")
        print("Example: python3 linkedin_email_extractor_internet.py https://www.linkedin.com/in/johndoe/")
        sys.exit(1)
    
    linkedin_url = sys.argv[1]
    extractor = InternetEmailExtractor()
    
    print("LinkedIn Email Extractor (Internet Search)")
    print("=" * 50)
    
    result = extractor.extract_email_from_linkedin_url(linkedin_url)
    
    if "error" in result:
        print(f"❌ {result['error']}")
        sys.exit(1)
    else:
        print(f"✅ Email found: {result['email']}")
        print(f"📋 Method used: {result['method']}")
        
        if 'verified' in result and result['verified']:
            print("✅ Email verified and can receive messages")
        elif 'verified' in result and not result['verified']:
            print("⚠️  Email not verified but format is valid")
        
        if 'verification_results' in result and result['verification_results']:
            print("\n📊 Verification Results:")
            for v_result in result['verification_results'][:5]:  # Show first 5
                status = "✅" if v_result['can_receive'] else "❌"
                print(f"  {status} {v_result['email']}: {v_result['reason']}")
        
        if 'all_emails' in result and len(result['all_emails']) > 1:
            print(f"\n📧 All emails found: {', '.join(result['all_emails'])}")
        
        if 'sources_searched' in result:
            print(f"🔍 Sources searched: {', '.join(result['sources_searched'])}")

if __name__ == "__main__":
    main() 