# scripts/add_documents.py
from ai.gemini_rag import GeminiRAGSystem

# Initialize RAG system
rag = GeminiRAGSystem()

# Sri Lankan Government Services Documents
documents = [
    # PASSPORT SERVICES
    {
        'text': '''Passport Application Process in Sri Lanka:

To apply for a Sri Lankan passport, you need the following documents:
1. Original Birth Certificate with certified copy
2. National Identity Card (NIC) - original and photocopy
3. Two recent passport-size photographs (white background, 35mm x 45mm)
4. Previous passport (if renewing)
5. Marriage certificate (if name changed after marriage)

Application Process:
- Visit the Department of Immigration and Emigration
- Obtain application form or download from website
- Complete form accurately
- Submit with required documents
- Pay applicable fees

Fees (as of 2024):
- Normal processing (16 pages): Rs. 3,000
- Normal processing (32 pages): Rs. 4,000  
- Normal processing (64 pages): Rs. 6,000
- Express processing: Additional Rs. 3,000

Processing Time:
- Normal: 7-10 working days
- Express: 3-5 working days

Office Locations:
- Colombo: Punchi Borella, "Suhurupaya"
- Kandy: Immigration Office, Kandy
- Matara: Immigration Office, Matara
- Jaffna: Immigration Office, Jaffna

Contact: +94 11 532 9000
Website: www.immigration.gov.lk''',
        'source': 'https://immigration.gov.lk/passport-application',
        'title': 'Passport Application Guide - Department of Immigration'
    },
    
    # TAX SERVICES
    {
        'text': '''Tax Filing in Sri Lanka - Inland Revenue Department:

Individual Income Tax:
- All individuals earning above threshold must file tax returns
- Deadline: November 30th annually
- Tax-free threshold: Rs. 3,000,000 per year

Required Documents:
1. Income statements from all sources
2. Bank statements
3. Investment details
4. Previous year's tax returns
5. TIN (Tax Identification Number)

How to File:
- Online: www.ird.gov.lk/RAMIS
- In-person: Visit nearest Inland Revenue office
- Through a tax consultant

Tax Rates for Individuals (2024):
- Up to Rs. 3,000,000: Tax-free
- Rs. 3,000,001 - Rs. 3,500,000: 6%
- Rs. 3,500,001 - Rs. 4,000,000: 12%
- Above Rs. 4,000,000: 18%

Corporate Tax:
- Deadline: December 31st
- Rate: 30% (varies by industry)

Value Added Tax (VAT):
- Registration required if annual turnover exceeds Rs. 12 million
- Standard rate: 18%
- Submit monthly returns

Contact:
- Hotline: 1962
- Email: info@ird.gov.lk
- Website: www.ird.gov.lk''',
        'source': 'https://ird.gov.lk/tax-filing',
        'title': 'Tax Filing Guide - Inland Revenue Department'
    },
    
    # NATIONAL ID CARD
    {
        'text': '''National Identity Card (NIC) Application - Sri Lanka:

Eligibility:
- All Sri Lankan citizens aged 16 and above
- Compulsory for all citizens

First-Time Application:

Required Documents:
1. Original Birth Certificate
2. Two recent passport-size photographs
3. Proof of residence (utility bill, bank statement)
4. Grama Niladhari certificate

Process:
- Visit your Divisional Secretariat (Kachcheri)
- Fill Form A (available at office)
- Provide fingerprints and photograph
- Submit documents

Fee: Free for first-time applicants
Processing Time: 2-4 weeks

Replacement/Corrections:

For Lost/Damaged NIC:
- File police report
- Visit Divisional Secretariat with police report
- Fill replacement form
- Fee: Rs. 200

For Name/Address Change:
- Marriage certificate (for name change)
- Proof of new address
- Fee: Rs. 100

New NIC (2024 onwards):
- Biometric smart card
- Valid for 10 years
- Contains chip with personal data

Contact:
- Commissioner General of Registrations
- Hotline: +94 11 269 5641
- Website: www.rgd.gov.lk''',
        'source': 'https://rgd.gov.lk/nic-application',
        'title': 'NIC Application Process - Department of Registration'
    },
    
    # DRIVING LICENSE
    {
        'text': '''Driving License Application - Sri Lanka:

Learner's Permit:

Requirements:
- Minimum age: 18 years
- Medical certificate
- Two passport-size photographs
- Copy of NIC

Process:
1. Visit nearest Motor Traffic Department office
2. Obtain application form
3. Submit with documents and fee (Rs. 500)
4. Take written examination (Highway Code)
5. If passed, receive learner's permit (valid 6 months)

Full License Application:

After holding learner's permit:
1. Complete minimum learning period (1 month for cars, 3 months for heavy vehicles)
2. Book driving test (Rs. 500)
3. Attend driving test at approved location
4. If passed, submit for license issuance

Required Documents:
- Valid learner's permit
- Medical certificate
- Competency certificate from driving school
- Two photographs
- Fee: Rs. 2,000 (5 years) or Rs. 4,000 (10 years)

License Categories:
- A1: Motorcycles under 100cc
- A: Motorcycles over 100cc
- B1: Three-wheelers
- B: Light vehicles (cars, vans)
- C1: Light goods vehicles
- C: Heavy vehicles
- D: Buses
- G: Articulated vehicles

Renewal:
- Can renew up to 1 year before expiry
- After 6 months overdue: Re-exam required
- Fee: Rs. 2,000 (5 years)

Contact:
- Commissioner of Motor Traffic
- Hotline: 1969
- Website: www.motortraffic.gov.lk''',
        'source': 'https://motortraffic.gov.lk/driving-license',
        'title': 'Driving License Guide - Department of Motor Traffic'
    },
    
    # BIRTH CERTIFICATE
    {
        'text': '''Birth Certificate Registration - Sri Lanka:

Initial Registration (within 3 months):

Required Information:
- Child's details (name, date, time, place of birth)
- Parents' details (names, NIC numbers, addresses)
- Hospital birth notification (if hospital birth)
- Two witnesses (if home birth)

Process:
1. Visit Registrar of Births office in the area of birth
2. Complete Form 1 (Registration of Birth)
3. Provide hospital notification or witness statements
4. Submit within 3 months of birth

Fee: Free if registered within 3 months

Late Registration (after 3 months):

- Requires Magistrate's order
- Additional documentation needed
- Court appearance may be required
- Fees apply (varies)

Obtaining Certified Copy:

Who Can Apply:
- Person named in certificate (if over 18)
- Parents
- Legal guardians
- Authorized representatives

Required:
- Application form
- Copy of NIC
- Fee: Rs. 100 per copy

Processing Time:
- Normal: 7 working days
- Express: 1-2 working days (additional fee: Rs. 500)

Collection:
- In person at issuing office
- By registered post (additional fee)

Name Changes/Corrections:
- Deed poll required
- Gazette notification
- Processing through Registrar General's Department

Contact:
- Registrar General's Department
- Hotline: +94 11 269 5641
- Website: www.rgd.gov.lk''',
        'source': 'https://rgd.gov.lk/birth-certificate',
        'title': 'Birth Certificate Guide - Registrar General Department'
    },
    
    # MARRIAGE CERTIFICATE
    {
        'text': '''Marriage Registration - Sri Lanka:

Types of Marriage Registration:

1. General Marriage (Civil)
2. Kandyan Marriage
3. Muslim Marriage
4. Tesawalamai Marriage

General Marriage Registration:

Notice of Marriage:
- Must give notice at least 14 days before marriage
- Both parties must appear personally
- Required documents:
  * NIC copies
  * Birth certificates
  * If divorced: Divorce decree
  * If widowed: Death certificate of spouse
  * If foreign national: Passport and legal documents

Registration Process:
1. Submit notice of intended marriage to Registrar
2. Notice displayed for 14 days (objection period)
3. If no objections, marriage can proceed
4. Marriage conducted by Marriage Registrar or authorized person
5. Register signed by couple, witnesses, and registrar

Fee: Rs. 1,000

Obtaining Marriage Certificate:

Required:
- Application form
- Couple's NIC copies
- Fee: Rs. 100 per certified copy

Processing Time: 7-10 working days

Marriage Requirements:
- Minimum age: 18 years
- Not related within prohibited degrees
- Not already married (unless prior marriage dissolved)
- Sound mind and given consent freely

Registration Offices:
- District Registrar offices island-wide
- Divisional Secretariats

Overseas Marriages:
- Must be registered at Sri Lankan embassy/consulate
- Or registered in Sri Lanka within 3 months of return

Contact:
- Registrar General's Department
- Hotline: +94 11 269 5641
- Website: www.rgd.gov.lk''',
        'source': 'https://rgd.gov.lk/marriage-registration',
        'title': 'Marriage Registration Guide - Registrar General Department'
    }
]

# Add documents to RAG system
print(f"\n📚 Adding {len(documents)} government service documents...")
count = rag.add_documents(documents)
print(f"✅ Successfully added {count} documents to knowledge base!")

# Test the system
print("\n🧪 Testing system with sample queries...\n")

test_queries = [
    "How do I apply for a passport?",
    "What is the tax filing deadline?",
    "How do I get a National ID card?",
    "What documents do I need for a driving license?",
    "How do I register a birth certificate?"
]

for query in test_queries:
    print(f"❓ {query}")
    result = rag.answer_query(query)
    print(f"💡 {result['answer'][:150]}...")
    print(f"📊 Confidence: {result['confidence']}, Sources: {len(result['sources'])}\n")

print("="*60)
stats = rag.get_stats()
print(f"✅ Total documents in system: {stats['total_documents']}")
print("="*60)