#!/usr/bin/env python3

from ultra_fast_linkedin_email import UltraFastLinkedInEmailFinder

def find_darby_email():
    finder = UltraFastLinkedInEmailFinder()
    
    # Darby Wright's LinkedIn URL
    linkedin_url = "https://www.linkedin.com/in/darby-wright-6ba805172/"
    
    print("🔍 Finding Darby Wright's Email (Work Preferred)")
    print("=" * 50)
    
    # Use correct name and try to find company info
    person_info = {
        'name': 'Darby Wright',
        'username': 'darby-wright-6ba805172',
        'linkedin_url': linkedin_url
    }
    
    print(f"👤 Searching for: {person_info['name']}")
    
    # Generate email candidates with common providers
    email_candidates = finder._generate_email_candidates(person_info)
    
    # Add specific patterns for Darby Wright
    name_parts = person_info['name'].lower().split()
    if len(name_parts) >= 2:
        first_name, last_name = name_parts[0], name_parts[-1]
        
        # Common email patterns for Darby Wright
        specific_patterns = [
            f"{first_name}.{last_name}@",
            f"{first_name}{last_name}@",
            f"{first_name}_{last_name}@",
            f"{last_name}.{first_name}@",
            f"{first_name[0]}{last_name}@",
            f"{first_name}{last_name[0]}@",
            f"darby.wright@",
            f"darbywright@",
            f"darby@",
        ]
        
        # Add common providers
        providers = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com']
        for pattern in specific_patterns:
            for provider in providers:
                email_candidates.append(pattern + provider)
    
    print(f"🔍 Generated {len(email_candidates)} email candidates")
    
    # Use the finder's verification method
    with finder.session as session:
        verified_emails = []
        for email in email_candidates:
            result = finder._verify_email_fast(email)
            if result and result.get('can_receive'):
                verified_emails.append(email)
        
        # Rank emails
        ranked_emails = []
        for email in verified_emails:
            confidence = 0
            method = "found"
            
            # Name matching
            if any(part in email.lower() for part in ['darby', 'wright']):
                confidence += 40
            
            # Domain quality
            domain = email.split('@')[1]
            if domain in finder.verified_domains:
                confidence += 50
            
            # Format validation
            if re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
                confidence += 20
            
            if confidence > 0:
                ranked_emails.append({
                    'email': email,
                    'confidence': confidence,
                    'method': method
                })
        
        # Sort by confidence
        ranked_emails.sort(key=lambda x: x['confidence'], reverse=True)
        
        # Display results
        if ranked_emails:
            print(f"\n✅ Found {len(ranked_emails)} verified email(s):")
            
            for i, email_info in enumerate(ranked_emails[:10], 1):  # Show top 10
                print(f"  {i}. {email_info['email']} ({email_info['confidence']}%)")
            
            print(f"\n🎯 RECOMMENDED: {ranked_emails[0]['email']}")
            
            if len(ranked_emails) > 1:
                print(f"📧 Alternative: {ranked_emails[1]['email']}")
        else:
            print("\n❌ No verified emails found")
            print("💡 Try using LinkedIn messaging to contact Darby directly")

if __name__ == "__main__":
    import re
    find_darby_email() 