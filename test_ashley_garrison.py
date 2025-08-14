#!/usr/bin/env python3

import sys
import os

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from linkedin_email_extractor_internet import InternetEmailExtractor

def main():
    linkedin_url = "https://www.linkedin.com/in/ashleygarrison1/"
    extractor = InternetEmailExtractor()
    
    print("LinkedIn Email Extractor (Internet Search) - Ashley Garrison Test")
    print("=" * 60)
    
    # Manually set person info for Ashley Garrison
    person_info = {
        'name': 'Ashley Garrison',
        'username': 'ashleygarrison1',
        'company': 'Robinhood',
        'linkedin_url': linkedin_url
    }
    
    print(f"👤 Testing with person info: {person_info['name']} at {person_info['company']}")
    
    # Search the internet for emails
    result = extractor._search_internet_for_email(person_info)
    
    if result:
        print(f"✅ Email found: {result['email']}")
        print(f"📋 Method used: {result['method']}")
        
        if 'all_emails' in result and len(result['all_emails']) > 1:
            print(f"📧 All emails found: {', '.join(result['all_emails'])}")
        
        if 'sources_searched' in result:
            print(f"🔍 Sources searched: {', '.join(result['sources_searched'])}")
    else:
        print("❌ No email found through internet search")

if __name__ == "__main__":
    main() 