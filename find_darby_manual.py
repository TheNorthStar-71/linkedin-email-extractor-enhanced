#!/usr/bin/env python3

import re
from ultra_fast_linkedin_email import UltraFastLinkedInEmailFinder

def find_darby_work_email():
    finder = UltraFastLinkedInEmailFinder()
    
    # Darby Wright's information
    person_name = "Darby Wright"
    linkedin_url = "https://www.linkedin.com/in/darby-wright-6ba805172/"
    
    print("🔍 Finding Darby Wright's Work Email (Manual Company Search)")
    print("=" * 65)
    
    # Common company domains to try (based on typical companies)
    company_domains = [
        # Tech companies
        'google.com', 'microsoft.com', 'apple.com', 'amazon.com', 'meta.com', 'facebook.com',
        'netflix.com', 'twitter.com', 'linkedin.com', 'salesforce.com', 'adobe.com', 'oracle.com',
        'ibm.com', 'intel.com', 'cisco.com', 'vmware.com', 'nvidia.com', 'amd.com',
        
        # Consulting firms
        'mckinsey.com', 'bain.com', 'bcg.com', 'deloitte.com', 'pwc.com', 'ey.com', 'kpmg.com',
        'accenture.com', 'capgemini.com', 'infosys.com', 'tcs.com', 'wipro.com',
        
        # Financial services
        'goldmansachs.com', 'morganstanley.com', 'jpmorgan.com', 'bankofamerica.com', 'wellsfargo.com',
        'citigroup.com', 'blackrock.com', 'fidelity.com', 'vanguard.com', 'schwab.com',
        
        # Healthcare/Pharma
        'pfizer.com', 'johnsonandjohnson.com', 'merck.com', 'novartis.com', 'roche.com',
        'astrazeneca.com', 'gsk.com', 'sanofi.com', 'bayer.com', 'abbvie.com',
        
        # Retail/Consumer
        'walmart.com', 'target.com', 'costco.com', 'home depot.com', 'lowes.com',
        'starbucks.com', 'mcdonalds.com', 'coca-cola.com', 'pepsico.com', 'nestle.com',
        
        # Manufacturing
        'ge.com', 'siemens.com', 'bosch.com', 'philips.com', '3m.com', 'honeywell.com',
        'caterpillar.com', 'deere.com', 'boeing.com', 'airbus.com',
        
        # Media/Entertainment
        'disney.com', 'warnerbros.com', 'paramount.com', 'sony.com', 'nbcuniversal.com',
        'viacom.com', 'comcast.com', 'att.com', 'verizon.com', 'tmobile.com',
        
        # Generic company patterns
        'company.com', 'corp.com', 'inc.com', 'llc.com', 'ltd.com'
    ]
    
    # Generate email patterns for Darby Wright
    name_parts = person_name.lower().split()
    first_name, last_name = name_parts[0], name_parts[-1]
    
    email_patterns = [
        f"{first_name}.{last_name}@",
        f"{first_name}{last_name}@",
        f"{first_name}_{last_name}@",
        f"{last_name}.{first_name}@",
        f"{first_name[0]}{last_name}@",
        f"{first_name}{last_name[0]}@",
        f"darby.wright@",
        f"darbywright@",
        f"darby@",
        f"dwright@",
        f"wright@",
        f"d.wright@",
        f"darby.w@",
    ]
    
    print(f"👤 Person: {person_name}")
    print(f"🔍 Testing {len(company_domains)} company domains")
    print(f"📧 Using {len(email_patterns)} email patterns")
    
    # Generate all email candidates
    email_candidates = []
    for pattern in email_patterns:
        for domain in company_domains:
            email_candidates.append(pattern + domain)
    
    print(f"🔍 Generated {len(email_candidates)} email candidates")
    
    # Verify emails in batches
    verified_emails = []
    batch_size = 50
    
    with finder.session as session:
        for i in range(0, len(email_candidates), batch_size):
            batch = email_candidates[i:i+batch_size]
            print(f"🔍 Verifying batch {i//batch_size + 1}/{(len(email_candidates) + batch_size - 1)//batch_size}")
            
            for email in batch:
                try:
                    result = finder._verify_email_fast(email)
                    if result and result.get('can_receive'):
                        verified_emails.append(email)
                        print(f"✅ Found: {email}")
                except Exception as e:
                    continue
    
    # Rank emails
    ranked_emails = []
    for email in verified_emails:
        confidence = 0
        
        # Name matching
        if any(part in email.lower() for part in ['darby', 'wright']):
            confidence += 40
        
        # Domain quality (prefer well-known companies)
        domain = email.split('@')[1]
        if domain in ['google.com', 'microsoft.com', 'apple.com', 'amazon.com', 'meta.com', 'salesforce.com', 'adobe.com']:
            confidence += 60
        elif domain in ['mckinsey.com', 'bain.com', 'bcg.com', 'deloitte.com', 'pwc.com', 'ey.com', 'kpmg.com']:
            confidence += 55
        elif domain in ['goldmansachs.com', 'morganstanley.com', 'jpmorgan.com', 'blackrock.com']:
            confidence += 55
        elif domain not in ['company.com', 'corp.com', 'inc.com', 'llc.com', 'ltd.com']:
            confidence += 50
        
        # Format validation
        if re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            confidence += 20
        
        if confidence > 0:
            ranked_emails.append({
                'email': email,
                'confidence': confidence,
                'domain': domain
            })
    
    # Sort by confidence
    ranked_emails.sort(key=lambda x: x['confidence'], reverse=True)
    
    # Display results
    if ranked_emails:
        print(f"\n✅ Found {len(ranked_emails)} verified work email(s):")
        
        for i, email_info in enumerate(ranked_emails[:10], 1):  # Show top 10
            print(f"  {i}. {email_info['email']} ({email_info['confidence']}%) - 🏢 {email_info['domain']}")
        
        print(f"\n🎯 RECOMMENDED (Work): {ranked_emails[0]['email']}")
        
        if len(ranked_emails) > 1:
            print(f"📧 Alternative (Work): {ranked_emails[1]['email']}")
    else:
        print("\n❌ No verified work emails found")
        print("💡 Try using LinkedIn messaging to contact Darby directly")

if __name__ == "__main__":
    import re
    find_darby_work_email() 