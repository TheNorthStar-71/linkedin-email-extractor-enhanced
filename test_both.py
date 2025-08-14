#!/usr/bin/env python3

from ultra_fast_linkedin_email import UltraFastLinkedInEmailFinder

def test_both():
    finder = UltraFastLinkedInEmailFinder()
    
    # Test cases
    test_cases = [
        {
            'name': 'Angela Massey',
            'url': 'https://www.linkedin.com/in/angela-massey-4747346/'
        },
        {
            'name': 'Ashley Garrison',
            'url': 'https://www.linkedin.com/in/ashleygarrison1/'
        }
    ]
    
    print("⚡ Ultra-Fast Email Finder - Performance Test")
    print("=" * 50)
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n🔍 Test {i}: {case['name']}")
        print("-" * 30)
        
        result = finder.find_email_from_linkedin(case['url'])
        
        if result:
            print(f"✅ SUCCESS: {result['email']} ({result['confidence']}% confidence)")
        else:
            print("❌ No email found")
    
    print(f"\n🎉 All tests completed!")

if __name__ == "__main__":
    test_both() 