#!/usr/bin/env python3

import requests
import re
import time
from urllib.parse import quote_plus

def search_angela_massey():
    """Targeted search for Angela Massey's email"""
    
    print("🔍 Targeted Search for Angela Massey")
    print("=" * 40)
    
    # Common email patterns for Angela Massey
    email_patterns = [
        'angela.massey@',
        'amassey@',
        'angela@',
        'massey.angela@',
        'angela_massey@',
        'angela.massey@gmail.com',
        'angela.massey@yahoo.com',
        'angela.massey@hotmail.com',
        'angela.massey@outlook.com',
        'amassey@gmail.com',
        'amassey@yahoo.com',
        'amassey@hotmail.com',
        'amassey@outlook.com'
    ]
    
    # Search queries
    search_queries = [
        '"Angela Massey" email',
        '"Angela Massey" contact',
        '"Angela Massey" mailto:',
        '"Angela Massey" @',
        'angela.massey@',
        'amassey@',
        '"Angela Massey" gmail',
        '"Angela Massey" yahoo',
        '"Angela Massey" hotmail',
        '"Angela Massey" outlook',
        '"Angela Massey" professional email',
        '"Angela Massey" work email',
        '"Angela Massey" business contact'
    ]
    
    found_emails = []
    
    # Search Google
    print("🔍 Searching Google...")
    for query in search_queries[:5]:  # Limit to first 5 queries
        try:
            search_url = f"https://www.google.com/search?q={quote_plus(query)}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(search_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                # Extract emails from response
                email_matches = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', response.text)
                for email in email_matches:
                    if 'angela' in email.lower() or 'massey' in email.lower():
                        found_emails.append(email.lower())
            
            time.sleep(2)  # Be respectful
            
        except Exception as e:
            print(f"Error searching Google: {e}")
            continue
    
    # Search Bing
    print("🔍 Searching Bing...")
    for query in search_queries[:3]:
        try:
            search_url = f"https://www.bing.com/search?q={quote_plus(query)}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(search_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                email_matches = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', response.text)
                for email in email_matches:
                    if 'angela' in email.lower() or 'massey' in email.lower():
                        found_emails.append(email.lower())
            
            time.sleep(2)
            
        except Exception as e:
            print(f"Error searching Bing: {e}")
            continue
    
    # Remove duplicates and filter
    unique_emails = list(set(found_emails))
    filtered_emails = []
    
    for email in unique_emails:
        # Filter out common false positives
        if not any(exclude in email.lower() for exclude in [
            'example.com', 'test.com', 'noreply', 'no-reply', 'linkedin.com',
            'facebook.com', 'twitter.com', 'github.com'
        ]):
            filtered_emails.append(email)
    
    # Display results
    if filtered_emails:
        print(f"\n✅ Found {len(filtered_emails)} potential email(s) for Angela Massey:")
        for i, email in enumerate(filtered_emails, 1):
            print(f"  {i}. {email}")
        
        # Recommend the best one
        best_email = filtered_emails[0]
        print(f"\n🎯 Recommended email: {best_email}")
        
        # Try to verify the email
        print("\n🔍 Verifying email...")
        if verify_email_domain(best_email):
            print(f"✅ {best_email} - Domain verified")
        else:
            print(f"⚠️  {best_email} - Domain could not be verified")
            
    else:
        print("\n❌ No email addresses found for Angela Massey")
        print("\n💡 Alternative suggestions:")
        print("  - Try searching for 'Angela Massey' on professional directories")
        print("  - Check if she has a personal website")
        print("  - Look for her on other social media platforms")
        print("  - Use LinkedIn's messaging system to contact her directly")

def verify_email_domain(email):
    """Simple domain verification"""
    try:
        domain = email.split('@')[1]
        import socket
        socket.gethostbyname(domain)
        return True
    except:
        return False

if __name__ == "__main__":
    search_angela_massey() 