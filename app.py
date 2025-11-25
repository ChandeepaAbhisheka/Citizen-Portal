# from flask import Flask, jsonify, render_template
# from flask_cors import CORS
# from pymongo import MongoClient
# import os
# from dotenv import load_dotenv

# load_dotenv()

# app = Flask(__name__)
# CORS(app)

# #connect to MongoDB(database)
# MONGO_URI = os.getenv("MONGO_URI")
# client = MongoClient(MONGO_URI)
# db = client['citizen_portal']
# services_col = db['services']

# @app.route('/')
# def home():
#     return render_template('index.html')

# @app.route("/api/services")
# def get_services():
#     #print("DB count:", services_col.count_documents({}))
#     services = list(services_col.find({}, {"_id":0}))
#     #print("Returned docs:", services)
#     return jsonify(services)


# if __name__ == '__main__':
#     app.run(debug=True)

import os
import traceback # ADDED: To see real errors
from flask import Flask, jsonify, render_template, request, session, redirect, send_file
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from pymongo import MongoClient
from typing import List, Dict, Any
from datetime import datetime
from io import StringIO, BytesIO
import csv
from dotenv import load_dotenv

# --- Import AI System ---
GeminiComplete = None
try:
    from ai.gemini_complete import GeminiComplete  # type: ignore
    print("✅ Imported GeminiComplete from ai/")
except ImportError:
    try:
        from gemini_complete import GeminiComplete  # type: ignore
        print("✅ Imported GeminiComplete from root")
    except ImportError:
        print("❌ ERROR: Could not find gemini_complete.py")

load_dotenv()
app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = os.getenv("FLASK_SECRET", "dev-secret")
CORS(app)

# Rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
db = None
services_col = None
eng_col = None
admins_col = None
try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    db = client["citizen_portal"]
    services_col = db["services"]
    eng_col = db["engagements"]
    admins_col = db["admins"]
    # Test connection
    client.server_info()
    print("✅ Connected to MongoDB")

    # FORCE UPDATE the admin user
    username = "admin"
    new_password = os.getenv("ADMIN_PWD", "admin123")

    admins_col.update_one(
        {"username": username},
        {"$set": {"password": new_password}},
        upsert=True # This creates it if it doesn't exist
    )
except Exception as e:
    print(f"⚠️ MongoDB Warning: {e}")

# Initialize AI System
print("🚀 Initializing AI System...")
try:
    if GeminiComplete:
        rag_system = GeminiComplete()
        print("✓ AI System ready!")
    else:
        rag_system = None
        print("⚠️ AI System NOT loaded (Missing file)")
except Exception as e:
    print(f"❌ AI Init Failed: {e}")
    rag_system = None

# --- Helpers ---
def admin_required(fn):
    from functools import wraps
    @wraps(fn)
    def wrapper(*a, **kw):
        if not session.get("admin_logged_in"):
            return jsonify({"error":"unauthorized"}), 401
        return fn(*a, **kw)
    return wrapper

# Simple fallback knowledge base (since we aren't doing full Vector Search in app.py yet)
knowledge_base_text = """
To apply for a passport in Sri Lanka, you need: Birth certificate, National ID card, and two passport photos. Visit the Department of Immigration.
Tax filing deadline in Sri Lanka is November 30 for individuals. You can file online at ird.gov.lk
To get a National ID card, visit your Divisional Secretariat with birth certificate and proof of residence.
"""

# Initialize knowledge base as list for indexing documents
knowledge_base = []

# --- Public routes ---
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/services")
def get_services():
    if db is None or services_col is None: return jsonify([])
    docs = list(services_col.find({}, {"_id":0}))
    return jsonify(docs)

@app.route("/api/service/<service_id>")
def get_service(service_id):
    if db is None or services_col is None: return jsonify({})
    doc = services_col.find_one({"id": service_id}, {"_id":0})
    return jsonify(doc or {})

@app.route("/api/engagement", methods=["POST"])
def log_engagement():
    """Log user engagement to MongoDB"""
    if db is None or eng_col is None: return jsonify({"status": "skipped (no db)"})
    try:
        payload = request.json or {}
        
        # safely parse age
        age_val = payload.get("age")
        age = None
        if age_val is not None and age_val != "":
            try:
                age = int(age_val)
            except (ValueError, TypeError):
                age = None

        doc = {
            "user_id": payload.get("user_id") or None,
            "age": age,
            "job": payload.get("job"),
            "desires": payload.get("desires") or [],
            "question_clicked": payload.get("question_clicked"),
            "service": payload.get("service"),
            "source": payload.get("source", "web"),
            "timestamp": datetime.utcnow()
        }
        
        eng_col.insert_one(doc)
        print(f"📝 Engagement logged")
        return jsonify({"status": "ok", "success": True})
    
    except Exception as e:
        print(f"❌ Engagement error: {str(e)}")
        return jsonify({"error": str(e)}), 500

# --- Admin site ---
@app.route("/admin")
def admin_page():
    if not session.get("admin_logged_in"):
        return redirect("/admin/login")
    return render_template("admin.html")

@app.route("/admin/manage")
@admin_required
def manage_page():
    return render_template("manage.html")

@app.route("/api/admin/manage/data")
@admin_required
def admin_manage_data():
    """Get admin management dashboard data"""
    data = {
        "database": "connected" if db is not None else "offline",
        "ai_system": "online" if rag_system else "offline",
        "total_engagements": eng_col.count_documents({}) if eng_col is not None else 0,
        "total_services": services_col.count_documents({}) if services_col is not None else 0,
        "knowledge_base_size": len(knowledge_base),
        "timestamp": datetime.utcnow().isoformat()
    }
    return jsonify(data)

@app.route("/admin/login", methods=["GET","POST"])
def admin_login():
    if request.method == "GET":
        return render_template("admin.html")
    data = request.form
    username = data.get("username")
    password = data.get("password")
    
    if db is None or admins_col is None: return "Database error", 500
    
    admin = admins_col.find_one({"username": username})
    if admin and admin.get("password") == password:
        session["admin_logged_in"] = True
        session["admin_user"] = username
        return redirect("/admin")
    return "Login failed", 401

@app.route("/api/admin/logout", methods=["POST"])
@admin_required
def admin_logout():
    session.clear()
    return jsonify({"status":"logged out"})

# --- MISSING ADMIN ROUTES (Paste this before "AI ENDPOINTS") ---

@app.route("/api/admin/insights")
@admin_required
def admin_insights():
    # 1. Age Groups
    age_groups = {"<18":0,"18-25":0,"26-40":0,"41-60":0,"60+":0}
    try:
        if eng_col is not None:
            for e in eng_col.find({}, {"age":1}):
                age = e.get("age")
                if not age: continue
                if age < 18: age_groups["<18"] += 1
                elif age <= 25: age_groups["18-25"] += 1
                elif age <= 40: age_groups["26-40"] += 1
                elif age <= 60: age_groups["41-60"] += 1
                else: age_groups["60+"] += 1
    except Exception: pass

    # 2. Services & Questions
    services = {}
    questions = {}
    if eng_col is not None:
        for e in eng_col.find({}, {"service":1, "question_clicked":1}):
            s = e.get("service") or "Unknown"
            q = e.get("question_clicked") or "Direct Chat"
            services[s] = services.get(s,0) + 1
            questions[q] = questions.get(q,0) + 1

    return jsonify({
        "age_groups": age_groups,
        "services": services,
        "questions": questions
    })

@app.route('/api/admin/index-documents', methods=['POST'])
def index_documents():
    """Add documents to knowledge base"""
    try:
        data = request.get_json()
        documents = data.get('documents', [])
        
        for doc in documents:
            knowledge_base.append(doc)
        
        return jsonify({
            "message": f"Successfully indexed {len(documents)} documents",
            "count": len(documents),
            "total": len(knowledge_base)
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/admin/engagements")
@admin_required
def admin_engagements():
    items = []
    if eng_col is not None:
        for e in eng_col.find().sort("timestamp",-1).limit(100):
            e["_id"] = str(e["_id"])
            e["timestamp"] = e.get("timestamp").isoformat() if e.get("timestamp") else ""
            items.append(e)
    return jsonify(items)

# ============================================
# ADMIN SERVICES MANAGEMENT
# ============================================

@app.route("/api/admin/services", methods=["GET", "POST"])
@admin_required
def admin_services():
    """Get all services or create/update a service"""
    if request.method == "GET":
        # Return all services
        if db is None or services_col is None:
            return jsonify([])
        docs = list(services_col.find({}, {"_id": 0}))
        return jsonify(docs)
    
    # POST method
    if db is None or services_col is None:
        return jsonify({"error": "Database offline"}), 500
    
    payload = request.json or {}
    service_id = payload.get("id")
    
    if not service_id:
        return jsonify({"error": "id required"}), 400
    
    # Prepare service document
    service_doc = {
        "id": service_id,
        "name": payload.get("name", ""),
        "questions": payload.get("questions", [])
    }
    
    try:
        # Upsert: update if exists, insert if not
        services_col.update_one(
            {"id": service_id},
            {"$set": service_doc},
            upsert=True
        )
        return jsonify({"status": "ok", "message": "Service saved successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/admin/services/<service_id>", methods=["DELETE"])
@admin_required
def delete_service(service_id):
    """Delete a service"""
    if db is None or services_col is None:
        return jsonify({"error": "Database offline"}), 500
    
    try:
        result = services_col.delete_one({"id": service_id})
        if result.deleted_count > 0:
            return jsonify({"status": "deleted", "message": "Service deleted successfully"})
        else:
            return jsonify({"error": "Service not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ============================================
# AI ENDPOINTS (FIXED)
# ============================================

@app.route('/api/ai/search', methods=['POST'])
# @limiter.limit("20 per minute") # Commented out for debugging to avoid 429 errors
def ai_search():
    """AI-powered search using Gemini"""
    query = None
    try:
        data = request.get_json()
        if not data: return jsonify({"error": "No JSON data"}), 400
        
        query = (data.get('query') or '').strip()
        
        # --- FIX 1: Detect Ghost Input from n8n/Postman ---
        if "{{" in query or query == "":
            print(f"⚠️ INVALID INPUT BLOCKED: {query}")
            return jsonify({
                "answer": "Error: Invalid query format. Please send real text, not variables.",
                "success": False
            })
        
        print(f"🔍 Received query: {query}")

        if not rag_system:
            return jsonify({"answer": "AI System is offline.", "success": False})

        # --- FIX 2: Use the class we actually have (GeminiComplete) ---
        # Note: GeminiComplete.generate_answer takes (query, context)
        # Since we don't have the Vector DB search here, we pass the static KB for now.
        result = rag_system.generate_answer(query, knowledge_base_text)

        print(f"📊 Result: {result.get('success')}")
        
        # Log to MongoDB if available
        if db is not None:
            try:
                db.ai_searches.insert_one({
                    "query": query,
                    "timestamp": datetime.utcnow(),
                    "success": result.get('success', False)
                })
            except Exception: pass
        
        return jsonify(result)
    
    except Exception as e:
        # --- FIX 3: Unmask the error ---
        print(f"❌ CRITICAL API ERROR: {str(e)}")
        traceback.print_exc() # This prints the full error to your terminal
        
        return jsonify({
            "error": "Search failed",
            "message": str(e),
            "query": query or "unknown"
        }), 500

@app.route('/api/ai/chat', methods=['POST'])
def ai_chat():
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        history = data.get('history', [])
        
        if not message: return jsonify({"error": "Message required"}), 400
        if not rag_system: return jsonify({"error": "AI offline"}), 500

        # Call GeminiComplete chat
        result = rag_system.chat(message, history)
        return jsonify(result)
    
    except Exception as e:
        print(f"❌ Chat error: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "ai_system": "online" if rag_system else "offline",
        "database": "connected" if db is not None else "offline",
        "timestamp": datetime.utcnow().isoformat()
    })

if __name__ == "__main__":
    # Create default admin if DB works
    if db is not None and admins_col is not None and admins_col.count_documents({}) == 0:
        admins_col.insert_one({"username":"admin", "password": os.getenv("ADMIN_PWD","admin123")})
        print("👤 Default admin created")
        
    app.run(debug=True, host="0.0.0.0", port=int(os.getenv("PORT",5000)))