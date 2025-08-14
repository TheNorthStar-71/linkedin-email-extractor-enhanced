#!/usr/bin/env python3

import requests
import re
import sys
from urllib.parse import urlparse
import time
import random
from bs4 import BeautifulSoup
import json
import os

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

class LinkedInEmailExtractorRobust:
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
            
            # Random user agent
            user_agents = [
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            ]
            chrome_options.add_argument(f"--user-agent={random.choice(user_agents)}")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            print("✅ Selenium WebDriver initialized with anti-detection measures")
        except Exception as e:
            print(f"⚠️  Selenium setup failed: {e}")
            self.use_selenium = False
    
    def extract_email_from_linkedin_url(self, linkedin_url):
        """
        Extract email from a LinkedIn profile URL using multiple methods
        """
        try:
            # Validate LinkedIn URL
            if not self._is_valid_linkedin_url(linkedin_url):
                return {"error": "Invalid LinkedIn URL. Please provide a valid LinkedIn profile URL."}
            
            print(f"🔍 Attempting to extract email from: {linkedin_url}")
            
            # Add random delay to avoid rate limiting
            time.sleep(random.uniform(1, 3))
            
            # Method 1: Try Selenium (if available)
            if self.use_selenium:
                email = self._extract_with_selenium(linkedin_url)
                if email:
                    return {"email": email, "method": "selenium"}
            
            # Method 2: Try with different user agents
            email = self._extract_with_rotating_agents(linkedin_url)
            if email:
                return {"email": email, "method": "rotating_agents"}
            
            # Method 3: Try to get the profile page directly
            email = self._scrape_profile_page(linkedin_url)
            if email:
                return {"email": email, "method": "direct_scraping"}
            
            # Method 4: Try to find contact information
            email = self._find_contact_info(linkedin_url)
            if email:
                return {"email": email, "method": "contact_info"}
            
            # Method 5: Try to extract from profile data
            email = self._extract_from_profile_data(linkedin_url)
            if email:
                return {"email": email, "method": "profile_data"}
            
            # Method 6: Try to find email in about section
            email = self._extract_from_about_section(linkedin_url)
            if email:
                return {"email": email, "method": "about_section"}
            
            # Method 7: Try to find email in activity section
            email = self._extract_from_activity_section(linkedin_url)
            if email:
                return {"email": email, "method": "activity_section"}
            
            return {"error": "No email found on this LinkedIn profile. The profile might be private, the email is not publicly visible, or LinkedIn is blocking our requests."}
            
        except Exception as e:
            return {"error": f"Error extracting email: {str(e)}"}
        finally:
            if self.use_selenium and self.driver:
                self.driver.quit()
    
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
                    email = self._extract_email_from_text(response.text)
                    if email:
                        return email
                
                # Add delay between requests
                time.sleep(random.uniform(2, 5))
                
            except Exception as e:
                print(f"Error with user agent {user_agent[:20]}...: {e}")
                continue
        
        return None
    
    def _extract_with_selenium(self, url):
        """Extract email using Selenium WebDriver"""
        try:
            print("🌐 Using Selenium to load page...")
            self.driver.get(url)
            
            # Wait for page to load
            time.sleep(random.uniform(3, 6))
            
            # Try to find email in various locations
            email_selectors = [
                "//*[contains(text(), '@')]",
                "//a[contains(@href, 'mailto:')]",
                "//span[contains(text(), '@')]",
                "//div[contains(text(), '@')]",
                "//p[contains(text(), '@')]",
                "//li[contains(text(), '@')]"
            ]
            
            for selector in email_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    for element in elements:
                        text = element.text
                        email = self._extract_email_from_text(text)
                        if email:
                            return email
                except Exception:
                    continue
            
            # Try to find contact info button and click it
            try:
                contact_selectors = [
                    "//button[contains(text(), 'Contact info')]",
                    "//button[contains(text(), 'Contact')]",
                    "//a[contains(text(), 'Contact info')]",
                    "//a[contains(text(), 'Contact')]"
                ]
                
                for selector in contact_selectors:
                    try:
                        contact_button = self.driver.find_element(By.XPATH, selector)
                        contact_button.click()
                        time.sleep(2)
                        
                        # Look for email in contact info
                        email_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), '@')]")
                        for element in email_elements:
                            text = element.text
                            email = self._extract_email_from_text(text)
                            if email:
                                return email
                        break
                    except Exception:
                        continue
            except Exception:
                pass
            
            return None
            
        except Exception as e:
            print(f"Error with Selenium extraction: {e}")
            return None
    
    def _extract_from_activity_section(self, url):
        """Try to extract email from the activity section"""
        try:
            # Try to access activity section
            activity_url = url + '/recent-activity/shares/'
            response = self.session.get(activity_url, timeout=10)
            
            if response.status_code == 200:
                return self._extract_email_from_text(response.text)
            
            return None
            
        except Exception as e:
            print(f"Error extracting from activity section: {e}")
            return None
    
    def _extract_from_about_section(self, url):
        """Try to extract email from the about section"""
        try:
            # Try to access about section
            about_url = url + '/overlay/about-this-profile/'
            response = self.session.get(about_url, timeout=10)
            
            if response.status_code == 200:
                return self._extract_email_from_text(response.text)
            
            return None
            
        except Exception as e:
            print(f"Error extracting from about section: {e}")
            return None
    
    def _extract_email_from_text(self, text):
        """Extract email from text using multiple patterns"""
        if not text:
            return None
        
        # Email patterns
        email_patterns = [
            r'[\w\.-]+@[\w\.-]+\.\w+',
            r'[\w\.-]+\s*\[at\]\s*[\w\.-]+\s*\[dot\]\s*\w+',
            r'[\w\.-]+\s*@\s*[\w\.-]+\s*\.\s*\w+',
            r'[\w\.-]+\s*at\s*[\w\.-]+\s*dot\s*\w+',
            r'[\w\.-]+\s*\[at\]\s*[\w\.-]+\s*\[dot\]\s*\w+',
            r'[\w\.-]+\s*\(at\)\s*[\w\.-]+\s*\(dot\)\s*\w+'
        ]
        
        for pattern in email_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                email = self._clean_email(match)
                if self._is_valid_email(email):
                    return email
        
        return None
    
    def _is_valid_linkedin_url(self, url):
        """Check if the URL is a valid LinkedIn profile URL"""
        try:
            parsed = urlparse(url)
            return 'linkedin.com' in parsed.netloc and '/in/' in parsed.path
        except:
            return False
    
    def _scrape_profile_page(self, url):
        """Try to scrape the profile page directly"""
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            return self._extract_email_from_text(response.text)
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                print("⚠️  Rate limited by LinkedIn. Try again later or use a different approach.")
            else:
                print(f"HTTP Error: {e}")
            return None
        except Exception as e:
            print(f"Error scraping profile page: {e}")
            return None
    
    def _find_contact_info(self, url):
        """Try to find contact information section"""
        try:
            # Try to access contact info page
            contact_url = url + '/overlay/contact-info/'
            response = self.session.get(contact_url, timeout=10)
            
            if response.status_code == 200:
                return self._extract_email_from_text(response.text)
            
            return None
            
        except Exception as e:
            print(f"Error finding contact info: {e}")
            return None
    
    def _extract_from_profile_data(self, url):
        """Try to extract from profile JSON data"""
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            # Look for JSON data in the page
            json_pattern = r'<script type="application/ld\+json">(.*?)</script>'
            json_matches = re.findall(json_pattern, response.text, re.DOTALL)
            
            for json_str in json_matches:
                try:
                    data = json.loads(json_str)
                    email = self._extract_email_from_json(data)
                    if email:
                        return email
                except json.JSONDecodeError:
                    continue
            
            return None
            
        except Exception as e:
            print(f"Error extracting from profile data: {e}")
            return None
    
    def _extract_email_from_json(self, data):
        """Recursively search for email in JSON data"""
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, str) and '@' in value:
                    email = self._extract_email_from_text(value)
                    if email:
                        return email
                elif isinstance(value, (dict, list)):
                    result = self._extract_email_from_json(value)
                    if result:
                        return result
        elif isinstance(data, list):
            for item in data:
                result = self._extract_email_from_json(item)
                if result:
                    return result
        return None
    
    def _clean_email(self, email):
        """Clean and format email address"""
        # Remove common obfuscation patterns
        email = email.replace('[at]', '@').replace('[dot]', '.')
        email = email.replace(' at ', '@').replace(' dot ', '.')
        email = email.replace('(at)', '@').replace('(dot)', '.')
        email = re.sub(r'\s+', '', email)  # Remove whitespace
        
        # Extract email using regex
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', email)
        if email_match:
            return email_match.group(0).lower()
        return email.lower()
    
    def _is_valid_email(self, email):
        """Validate email format"""
        if not email:
            return False
        
        # Basic email validation
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(pattern, email):
            return False
        
        # Check for common invalid patterns
        invalid_patterns = [
            r'example\.com$',
            r'test\.com$',
            r'noreply@',
            r'no-reply@',
            r'do-not-reply@',
            r'linkedin\.com$',
            r'facebook\.com$',
            r'gmail\.com$',  # Often used as placeholder
            r'yahoo\.com$',  # Often used as placeholder
            r'hotmail\.com$'  # Often used as placeholder
        ]
        
        for pattern in invalid_patterns:
            if re.search(pattern, email, re.IGNORECASE):
                return False
        
        return True

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 linkedin_email_extractor_robust.py <linkedin_profile_url>")
        print("Example: python3 linkedin_email_extractor_robust.py https://www.linkedin.com/in/johndoe/")
        sys.exit(1)
    
    linkedin_url = sys.argv[1]
    extractor = LinkedInEmailExtractorRobust()
    
    print("LinkedIn Email Extractor (Robust)")
    print("=" * 40)
    
    result = extractor.extract_email_from_linkedin_url(linkedin_url)
    
    if "error" in result:
        print(f"❌ {result['error']}")
        print()
        print("💡 Tips:")
        print("- LinkedIn may be blocking automated requests")
        print("- Try using the interactive script instead")
        print("- Make sure the profile is public")
        print("- The email might not be publicly visible")
        sys.exit(1)
    else:
        print(f"✅ Email found: {result['email']}")
        print(f"📋 Method used: {result['method']}")

if __name__ == "__main__":
    main() 