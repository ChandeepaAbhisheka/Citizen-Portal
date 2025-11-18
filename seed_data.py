# from pymongo import MongoClient
# import os
# from dotenv import load_dotenv
# load_dotenv()

# client = MongoClient(os.getenv("MONGO_URI"))
# db = client["citizen_portal"]

# data = [
#     {"id": "service1", "name": "Transport Services", "questions": ["Renew License", "Register Vehicle"]},
#     {"id": "service2", "name": "Health Services", "questions": ["Vaccination", "Medical Certificate"]}
# ]
# db.services.insert_many(data)
# print("Database seeded successfully!")

from pymongo import MongoClient
import os
import json

# ---------------------------------------------
# Database Connection
# ---------------------------------------------
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)

db = client["citizen_portal"]
services_col = db["services"]

# Clear existing data
services_col.delete_many({})

# ---------------------------------------------
# Base Ministries With Real Subservices
# ---------------------------------------------
docs = [
    {
        "id": "ministry_it",
        "name": {
            "en": "Ministry of IT & Digital Affairs",
            "si": "තොරතුරු තාක්ෂණ අමාත්‍යංශය",
            "ta": "தகவல் தொழில்நுட்ப அமைச்சு"
        },
        "subservices": [
            {
                "id": "it_cert",
                "name": {
                    "en": "IT Certificates",
                    "si": "අයිටී සහතික",
                    "ta": "ஐடி சான்றிதழ்கள்"
                },
                "questions": [
                    {
                        "q": {
                            "en": "How to apply for an IT certificate?",
                            "si": "IT සහතිකයක් සඳහා අයදුම් කරන ආකාරය?",
                            "ta": "ஐடி சான்றிதழுக்கு எப்படி விண்ணப்பிப்பது?"
                        },
                        "answer": {
                            "en": "Fill the online form and upload your NIC.",
                            "si": "ඔන්ලයින් පෝරමය පුරවා NIC උඩුගත කරන්න.",
                            "ta": "ஆன்லைன் படிவத்தை நிரப்பி NIC ஐ பதிவேற்றுங்கள்."
                        },
                        "downloads": ["/static/forms/it_cert_form.pdf"],
                        "location": "https://maps.google.com/?q=Ministry+of+IT",
                        "instructions": "Visit the digital portal, register and submit your application."
                    }
                ]
            }
        ]
    },

    {
        "id": "ministry_education",
        "name": {
            "en": "Ministry of Education",
            "si": "අධ්‍යාපන අමාත්‍යංශය",
            "ta": "கல்வி அமைச்சு"
        },
        "subservices": [
            {
                "id": "schools",
                "name": {
                    "en": "Schools",
                    "si": "පාසල්",
                    "ta": "பள்ளிகள்"
                },
                "questions": [
                    {
                        "q": {
                            "en": "How to register a school?",
                            "si": "පාසලක් ලියාපදිංචි කරන ආකාරය?",
                            "ta": "பள்ளியை பதிவு செய்வது எப்படி?"
                        },
                        "answer": {
                            "en": "Complete the registration form and submit documents.",
                            "si": "ලියාපදිංචි පෝරමය පුරවා අවශ්‍ය ලේඛන ඉදිරිපත් කරන්න.",
                            "ta": "பதிவு படிவத்தை பூர்த்தி செய்து ஆவணங்களை சமர்ப்பிக்கவும்."
                        },
                        "downloads": ["/static/forms/school_reg.pdf"],
                        "location": "https://maps.google.com/?q=Ministry+of+Education",
                        "instructions": "Follow the guidelines on the education portal."
                    }
                ]
            },
            {
                "id": "exams",
                "name": {
                    "en": "Exams & Results",
                    "si": "විභාග & ප්‍රතිඵල",
                    "ta": "தேர்வுகள் மற்றும் முடிவுகள்"
                },
                "questions": [
                    {
                        "q": {
                            "en": "How to apply for the national exam?",
                            "si": "ජාතික විභාගයට අයදුම් කරන ආකාරය?",
                            "ta": "தேசிய தேர்விற்கு எப்படி விண்ணப்பிப்பது?"
                        },
                        "answer": {
                            "en": "Register via the examination portal.",
                            "si": "විභාග පෝර්ටලය හරහා ලියාපදිංචි වන්න.",
                            "ta": "தேர்வு போர்ட்டல் மூலம் பதிவு செய்யவும்."
                        },
                        "downloads": [],
                        "location": "",
                        "instructions": "Check exam schedule and applicable fees."
                    }
                ]
            }
        ]
    }
]

# ---------------------------------------------
# Auto-Generated Ministries To Reach 20
# ---------------------------------------------
remaining_ministries = [
    ("ministry_health", "Ministry of Health"),
    ("ministry_transport", "Ministry of Transport"),
    ("ministry_imm", "Ministry of Immigration"),
    ("ministry_foreign", "Ministry of Foreign Affairs"),
    ("ministry_finance", "Ministry of Finance"),
    ("ministry_labour", "Ministry of Labour"),
    ("ministry_public", "Ministry of Public Administration"),
    ("ministry_justice", "Ministry of Justice"),
    ("ministry_housing", "Ministry of Housing"),
    ("ministry_agri", "Ministry of Agriculture"),
    ("ministry_youth", "Ministry of Youth Affairs"),
    ("ministry_defence", "Ministry of Defence"),
    ("ministry_tourism", "Ministry of Tourism"),
    ("ministry_trade", "Ministry of Industry & Trade"),
    ("ministry_energy", "Ministry of Power & Energy"),
    ("ministry_water", "Ministry of Water Supply"),
    ("ministry_env", "Ministry of Environment"),
    ("ministry_culture", "Ministry of Culture"),
]

for mid, title in remaining_ministries:
    docs.append({
        "id": mid,
        "name": {
            "en": title,
            "si": title,
            "ta": title
        },
        "subservices": [
            {
                "id": "general",
                "name": {
                    "en": "General Services",
                    "si": "සාමාන්ය සේවාවන්",
                    "ta": "பொது சேவைகள்"
                },
                "questions": [
                    {
                        "q": {
                            "en": "What services are offered?",
                            "si": "ලබාදීමට ඇති සේවාවන් මොනවාද?",
                            "ta": "எந்த சேவைகள் வழங்கப்படுகின்றன?"
                        },
                        "answer": {
                            "en": "Please check the service list on the portal.",
                            "si": "පෝර්ටලයහි සේවා ලැයිස්තුව බලන්න.",
                            "ta": "போர்ட்டலில் சேவை பட்டியலைப் பார்க்கவும்."
                        },
                        "downloads": [],
                        "location": "",
                        "instructions": "Use the contact details on the portal for more information."
                    }
                ]
            }
        ]
    })

# Insert to MongoDB
services_col.insert_many(docs)

print("Seeded services:", services_col.count_documents({}))
