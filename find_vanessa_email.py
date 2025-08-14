#!/usr/bin/env python3

from ultra_fast_linkedin_email import UltraFastLinkedInEmailFinder

def find_vanessa_email():
    finder = UltraFastLinkedInEmailFinder()
    
    # Vanessa Ramirez's LinkedIn URL
    linkedin_url = "https://www.linkedin.com/in/vanessa-ramirez-96135798/"
    
    print("🔍 Finding Vanessa Ramirez's Email (Work Preferred)")
    print("=" * 50)
    
    # Extract person info from URL
    person_info = finder._extract_person_info(linkedin_url)
    if not person_info:
        print("❌ Could not extract person info from LinkedIn URL")
        return
    
    print(f"👤 Found: {person_info['name']}")
    
    # Generate email candidates
    email_candidates = finder._generate_email_candidates(person_info)
    
    # Add common company domains for Vanessa (we'll try multiple possibilities)
    name_parts = person_info['name'].lower().split()
    if len(name_parts) >= 2:
        first_name, last_name = name_parts[0], name_parts[-1]
        
        # Common company domains to try
        company_domains = [
            'company.com',  # Generic
            'vanessa-ramirez.com',  # Personal domain possibility
            'ramirez.com',  # Family domain possibility
        ]
        
        # Add work email patterns
        for domain in company_domains:
            work_patterns = [
                f"{first_name}.{last_name}@{domain}",
                f"{first_name}{last_name}@{domain}",
                f"{first_name}_{last_name}@{domain}",
                f"{first_name}@{domain}",
                f"{last_name}.{first_name}@{domain}",
                f"{first_name[0]}{last_name}@{domain}",
                f"vanessa.ramirez@{domain}",
                f"vanessaramirez@{domain}",
                f"vanessa@{domain}",
            ]
            email_candidates.extend(work_patterns)
    
    print(f"🔍 Generated {len(email_candidates)} email candidates")
    
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
            if any(domain in email for domain in ['company.com', 'vanessa-ramirez.com', 'ramirez.com']):
                confidence += 80
                method = "work_email"
            elif any(provider in email for provider in ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com']):
                confidence += 60
                method = "personal_email"
            
            # Name matching
            if any(part in email.lower() for part in ['vanessa', 'ramirez']):
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
            
            for i, email_info in enumerate(ranked_emails[:10], 1):  # Show top 10
                status = "🏢 WORK" if "work" in email_info['method'] else "📧 PERSONAL"
                print(f"  {i}. {email_info['email']} ({email_info['confidence']}%) - {status}")
            
            # Recommend best email
            work_emails = [e for e in ranked_emails if "work" in e['method']]
            if work_emails:
                print(f"\n🎯 RECOMMENDED (Work): {work_emails[0]['email']}")
            else:
                print(f"\n🎯 RECOMMENDED (Personal): {ranked_emails[0]['email']}")
        else:
            print("\n❌ No verified emails found")
            print("💡 Try using LinkedIn messaging to contact Vanessa directly")

if __name__ == "__main__":
    find_vanessa_email() 