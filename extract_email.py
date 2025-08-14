#!/usr/bin/env python3

import sys
import os

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from linkedin_email_extractor_internet import InternetEmailExtractor
    INTERNET_AVAILABLE = True
except ImportError:
    INTERNET_AVAILABLE = False

try:
    from linkedin_email_extractor_robust import LinkedInEmailExtractorRobust
    ROBUST_AVAILABLE = True
except ImportError:
    ROBUST_AVAILABLE = False

try:
    from linkedin_email_extractor_advanced import LinkedInEmailExtractorAdvanced
    ADVANCED_AVAILABLE = True
except ImportError:
    ADVANCED_AVAILABLE = False

try:
    from linkedin_email_extractor import LinkedInEmailExtractor
    BASIC_AVAILABLE = True
except ImportError:
    BASIC_AVAILABLE = False

def main():
    print("🔗 LinkedIn Email Extractor")
    print("=" * 40)
    print()
    
    # Check which extractors are available
    if not INTERNET_AVAILABLE and not ROBUST_AVAILABLE and not ADVANCED_AVAILABLE and not BASIC_AVAILABLE:
        print("❌ Error: No email extractors available!")
        print("Please make sure you have the required dependencies installed:")
        print("pip install -r requirements.txt")
        return
    
    # Get LinkedIn URL from user
    while True:
        linkedin_url = input("Enter LinkedIn profile URL: ").strip()
        
        if not linkedin_url:
            print("❌ Please enter a valid LinkedIn URL")
            continue
        
        if 'linkedin.com' not in linkedin_url or '/in/' not in linkedin_url:
            print("❌ Please enter a valid LinkedIn profile URL (should contain 'linkedin.com/in/')")
            continue
        
        break
    
    print()
    print("🔍 Extracting email...")
    print()
    
    # Try internet search first, then robust, then advanced, then basic
    result = None
    
    if INTERNET_AVAILABLE:
        try:
            print("🌐 Using internet search extractor (searches entire web)...")
            extractor = InternetEmailExtractor()
            result = extractor.extract_email_from_linkedin_url(linkedin_url)
        except Exception as e:
            print(f"⚠️  Internet search extractor failed: {e}")
    
    if not result and ROBUST_AVAILABLE:
        try:
            print("🔧 Trying robust extractor with anti-detection measures...")
            extractor = LinkedInEmailExtractorRobust()
            result = extractor.extract_email_from_linkedin_url(linkedin_url)
        except Exception as e:
            print(f"⚠️  Robust extractor failed: {e}")
    
    if not result and ADVANCED_AVAILABLE:
        try:
            print("🔧 Trying advanced extractor...")
            extractor = LinkedInEmailExtractorAdvanced()
            result = extractor.extract_email_from_linkedin_url(linkedin_url)
        except Exception as e:
            print(f"⚠️  Advanced extractor failed: {e}")
    
    if not result and BASIC_AVAILABLE:
        try:
            print("🔧 Trying basic extractor...")
            extractor = LinkedInEmailExtractor()
            result = extractor.extract_email_from_linkedin_url(linkedin_url)
        except Exception as e:
            print(f"⚠️  Basic extractor failed: {e}")
    
    if not result:
        print("❌ No extractors worked. Please check your dependencies.")
        return
    
    # Display result
    print()
    if "error" in result:
        print(f"❌ {result['error']}")
        print()
        print("💡 Tips:")
        print("- Make sure the LinkedIn profile is public")
        print("- The email might not be publicly visible")
        print("- Try a different LinkedIn profile")
    else:
        print(f"✅ Email found: {result['email']}")
        print(f"📋 Method used: {result['method']}")
        
        if 'all_emails' in result and len(result['all_emails']) > 1:
            print(f"📧 All emails found: {', '.join(result['all_emails'])}")
        
        if 'verified' in result and result['verified']:
            print("✅ Email verified and can receive messages")
        elif 'verified' in result and not result['verified']:
            print("⚠️  Email not verified but format is valid")
        
        if 'verification_results' in result and result['verification_results']:
            print("\n📊 Verification Results:")
            for v_result in result['verification_results'][:5]:  # Show first 5
                status = "✅" if v_result['can_receive'] else "❌"
                print(f"  {status} {v_result['email']}: {v_result['reason']}")
        
        if 'sources_searched' in result:
            print(f"🔍 Sources searched: {', '.join(result['sources_searched'])}")
        
        print()
        print("🎉 Success! You can now contact this person directly.")

if __name__ == "__main__":
    main() 