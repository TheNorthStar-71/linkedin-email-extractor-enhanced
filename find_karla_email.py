#!/usr/bin/env python3

from ultra_fast_linkedin_email import UltraFastLinkedInEmailFinder

def find_karla_email():
    finder = UltraFastLinkedInEmailFinder()
    
    # Karla Castaneda's LinkedIn URL
    linkedin_url = "https://www.linkedin.com/in/karla-castaneda/"
    
    print("🔍 Finding Karla Castaneda's Email (Work Preferred)")
    print("=" * 50)
    
    # Based on the LinkedIn profile, Karla works at Ema Unlimited
    # Let's try with company information for better work email results
    person_info = {
        'name': 'Karla Castaneda',
        'username': 'karla-castaneda',
        'company': 'Ema Unlimited',
        'linkedin_url': linkedin_url
    }
    
    # Generate email candidates with company focus
    email_candidates = finder._generate_email_candidates(person_info)
    
    # Add company-specific patterns
    company_domain = 'emaunlimited.com'  # Common pattern
    name_parts = person_info['name'].lower().split()
    if len(name_parts) >= 2:
        first_name, last_name = name_parts[0], name_parts[-1]
        
        # Add work email patterns
        work_patterns = [
            f"{first_name}.{last_name}@{company_domain}",
            f"{first_name}{last_name}@{company_domain}",
            f"{first_name}_{last_name}@{company_domain}",
            f"{first_name}@{company_domain}",
            f"{last_name}.{first_name}@{company_domain}",
            f"{first_name[0]}{last_name}@{company_domain}",
            f"karla.castaneda@{company_domain}",
            f"karlacastaneda@{company_domain}",
            f"karla@{company_domain}",
        ]
        
        email_candidates.extend(work_patterns)
    
    print(f"👤 Searching for: {person_info['name']} at {person_info['company']}")
    print(f"🏢 Company domain: {company_domain}")
    
    # Use the finder's verification method
    with finder.session as session:
        verified_emails = []
        for email in email_candidates:
            result = finder._verify_email_fast(email)
            if result and result.get('can_receive'):
                verified_emails.append(email)
        
        # Rank emails (work emails first)
        ranked_emails = []
        for email in verified_emails:
            confidence = 0
            method = "found"
            
            # Boost confidence for work emails
            if company_domain in email:
                confidence += 80
                method = "work_email"
            elif any(provider in email for provider in ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com']):
                confidence += 60
                method = "personal_email"
            
            # Name matching
            if any(part in email.lower() for part in ['karla', 'castaneda']):
                confidence += 30
            
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
            
            for i, email_info in enumerate(ranked_emails, 1):
                status = "🏢 WORK" if "work" in email_info['method'] else "📧 PERSONAL"
                print(f"  {i}. {email_info['email']} ({email_info['confidence']}%) - {status}")
            
            # Recommend work email if available
            work_emails = [e for e in ranked_emails if "work" in e['method']]
            if work_emails:
                print(f"\n🎯 RECOMMENDED (Work): {work_emails[0]['email']}")
            else:
                print(f"\n🎯 RECOMMENDED (Personal): {ranked_emails[0]['email']}")
        else:
            print("\n❌ No verified emails found")
            print("💡 Try using LinkedIn messaging to contact Karla directly")

if __name__ == "__main__":
    find_karla_email() 