from pymongo import MongoClient
import os
from dotenv import load_dotenv
load_dotenv()

client = MongoClient(os.getenv("MONGO_URI"))
db = client["citizen_portal"]

data = [
    {"id": "service1", "name": "Transport Services", "questions": ["Renew License", "Register Vehicle"]},
    {"id": "service2", "name": "Health Services", "questions": ["Vaccination", "Medical Certificate"]}
]
db.services.insert_many(data)
print("Database seeded successfully!")
