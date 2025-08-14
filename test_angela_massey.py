#!/usr/bin/env python3

import sys
import os

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from linkedin_email_extractor_internet import InternetEmailExtractor

def main():
    linkedin_url = "https://www.linkedin.com/in/angela-massey-4747346/"
    extractor = InternetEmailExtractor()
    
    print("LinkedIn Email Extractor (Internet Search) - Angela Massey Test")
    print("=" * 60)
    
    # Manually set person info for Angela Massey
    # We'll try different variations since we don't know her exact company
    person_info_variations = [
        {
            'name': 'Angela Massey',
            'username': 'angela-massey-4747346',
            'company': '',  # Try without company first
            'linkedin_url': linkedin_url
        },
        {
            'name': 'Angela Massey',
            'username': 'angela-massey-4747346',
            'company': 'LinkedIn',  # Try with LinkedIn as company
            'linkedin_url': linkedin_url
        },
        {
            'name': 'Angela Massey',
            'username': 'angela-massey-4747346',
            'company': 'Technology',  # Try with generic tech company
            'linkedin_url': linkedin_url
        }
    ]
    
    for i, person_info in enumerate(person_info_variations, 1):
        print(f"\n🔍 Attempt {i}: {person_info['name']} at {person_info['company'] or 'Unknown Company'}")
        
        # Search the internet for emails
        result = extractor._search_internet_for_email(person_info)
        
        if result:
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
            
            break
        else:
            print("❌ No email found with this person info")
    
    if not any(extractor._search_internet_for_email(info) for info in person_info_variations):
        print("\n❌ No email found for Angela Massey through any search attempts")

if __name__ == "__main__":
    main() 