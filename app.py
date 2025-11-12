from flask import Flask, jsonify, render_template
from flask_cors import CORS
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

#connect to MongoDB(database)
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client['mydatabase']

@app.route('/')
def home():
    return render_template('index.html')

@app.route("/api/services")
def get_services():
    services_collection = db['services']
    services = list(services_collection.find({}, {'_id': 0}))
    return jsonify(services)

if __name__ == '__main__':
    app.run(debug=True)