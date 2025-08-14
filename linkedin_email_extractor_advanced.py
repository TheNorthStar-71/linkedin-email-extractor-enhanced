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
    print("Selenium not available. Install with: pip install selenium")

class LinkedInEmailExtractorAdvanced:
    def __init__(self, use_selenium=True):
        self.use_selenium = use_selenium and SELENIUM_AVAILABLE
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        if self.use_selenium:
            self.driver = None
            self._setup_selenium()
    
    def _setup_selenium(self):
        """Setup Selenium WebDriver"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # Run in background
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            print("✅ Selenium WebDriver initialized")
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
            
            # Method 1: Try Selenium (if available)
            if self.use_selenium:
                email = self._extract_with_selenium(linkedin_url)
                if email:
                    return {"email": email, "method": "selenium"}
            
            # Method 2: Try to get the profile page directly
            email = self._scrape_profile_page(linkedin_url)
            if email:
                return {"email": email, "method": "direct_scraping"}
            
            # Method 3: Try to find contact information
            email = self._find_contact_info(linkedin_url)
            if email:
                return {"email": email, "method": "contact_info"}
            
            # Method 4: Try to extract from profile data
            email = self._extract_from_profile_data(linkedin_url)
            if email:
                return {"email": email, "method": "profile_data"}
            
            # Method 5: Try to find email in about section
            email = self._extract_from_about_section(linkedin_url)
            if email:
                return {"email": email, "method": "about_section"}
            
            return {"error": "No email found on this LinkedIn profile. The profile might be private or the email is not publicly visible."}
            
        except Exception as e:
            return {"error": f"Error extracting email: {str(e)}"}
        finally:
            if self.use_selenium and self.driver:
                self.driver.quit()
    
    def _extract_with_selenium(self, url):
        """Extract email using Selenium WebDriver"""
        try:
            print("🌐 Using Selenium to load page...")
            self.driver.get(url)
            
            # Wait for page to load
            time.sleep(3)
            
            # Try to find email in various locations
            email_selectors = [
                "//*[contains(text(), '@')]",
                "//a[contains(@href, 'mailto:')]",
                "//span[contains(text(), '@')]",
                "//div[contains(text(), '@')]",
                "//p[contains(text(), '@')]"
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
                contact_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Contact info') or contains(text(), 'Contact')]")
                contact_button.click()
                time.sleep(2)
                
                # Look for email in contact info
                email_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), '@')]")
                for element in email_elements:
                    text = element.text
                    email = self._extract_email_from_text(text)
                    if email:
                        return email
            except Exception:
                pass
            
            return None
            
        except Exception as e:
            print(f"Error with Selenium extraction: {e}")
            return None
    
    def _extract_from_about_section(self, url):
        """Try to extract email from the about section"""
        try:
            # Try to access about section
            about_url = url + '/overlay/about-this-profile/'
            response = self.session.get(about_url, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for email in about section
                email_elements = soup.find_all(text=re.compile(r'[\w\.-]+@[\w\.-]+\.\w+'))
                for element in email_elements:
                    email = self._extract_email_from_text(element)
                    if email:
                        return email
            
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
            r'[\w\.-]+\s*at\s*[\w\.-]+\s*dot\s*\w+'
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
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            return self._extract_email_from_text(response.text)
            
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
            response = self.session.get(url, timeout=10)
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
            r'facebook\.com$'
        ]
        
        for pattern in invalid_patterns:
            if re.search(pattern, email, re.IGNORECASE):
                return False
        
        return True

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 linkedin_email_extractor_advanced.py <linkedin_profile_url>")
        print("Example: python3 linkedin_email_extractor_advanced.py https://www.linkedin.com/in/johndoe/")
        sys.exit(1)
    
    linkedin_url = sys.argv[1]
    extractor = LinkedInEmailExtractorAdvanced()
    
    print("LinkedIn Email Extractor (Advanced)")
    print("=" * 40)
    
    result = extractor.extract_email_from_linkedin_url(linkedin_url)
    
    if "error" in result:
        print(f"❌ {result['error']}")
        sys.exit(1)
    else:
        print(f"✅ Email found: {result['email']}")
        print(f"📋 Method used: {result['method']}")

if __name__ == "__main__":
    main() 