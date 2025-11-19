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
from flask import Flask, jsonify, render_template, request, session, redirect, send_file 
from flask_cors import CORS 
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from pymongo import MongoClient 
from typing import cast, List, Dict, Any
from pymongo.cursor import Cursor
from bson import ObjectId 
from datetime import datetime 
from io import StringIO, BytesIO 
import csv 
from dotenv import load_dotenv 

# Import our Gemini RAG system
from ai.gemini_rag import GeminiRAGSystem

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

# MongoDB connection (replace with your Atlas URI) 
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/") 
client = MongoClient(MONGO_URI) 
db = client["citizen_portal"] 
services_col = db["services"] 
eng_col = db["engagements"] 
admins_col = db["admins"] 

# Initialize Gemini RAG System
print("🚀 Initializing AI System...")
rag_system = GeminiRAGSystem()
print("✓ AI System ready!")

# --- Helpers --- 
def admin_required(fn): 
    from functools import wraps 
    @wraps(fn) 
    def wrapper(*a, **kw): 
        if not session.get("admin_logged_in"): 
            return jsonify({"error":"unauthorized"}), 401 
        return fn(*a, **kw) 
    return wrapper 
        
# --- Public routes --- 
@app.route("/") 
def home(): 
    return render_template("index.html") 

@app.route("/api/services") 
def get_services(): 
    docs = list(services_col.find({}, {"_id":0})) 
    return jsonify(docs) 

@app.route("/api/service/<service_id>") 
def get_service(service_id): 
    doc = services_col.find_one({"id": service_id}, {"_id":0}) 
    return jsonify(doc or {}) 

@app.route("/api/engagement", methods=["POST"]) 
def log_engagement(): 
    payload = request.json or {} 
    # safely parse age: avoid passing None/invalid values to int()
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
        "timestamp": datetime.utcnow() 
    } 
    eng_col.insert_one(doc) 
    return jsonify({"status":"ok"}) 

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

@app.route("/admin/login", methods=["GET","POST"]) 
def admin_login(): 
    if request.method == "GET": 
        return render_template("admin.html")  # admin page has the login modal 
    data = request.form 
    username = data.get("username") 
    password = data.get("password") 
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
 
# Admin API: insights and user management 
@app.route("/api/admin/insights") 
@admin_required 
def admin_insights(): 
    # Age groups 
    age_groups = {"<18":0,"18-25":0,"26-40":0,"41-60":0,"60+":0} 
    for e in eng_col.find({}, {"age":1}): 
        age = e.get("age") 
        if not age: 
            continue 
        try: 
            age = int(age) 
            if age < 18: 
                age_groups["<18"] += 1 
            elif age <= 25: 
                age_groups["18-25"] += 1 
            elif age <= 40: 
                age_groups["26-40"] += 1 
            elif age <= 60: 
                age_groups["41-60"] += 1 
            else: 
                age_groups["60+"] += 1 
        except Exception: 
            continue 
 
    # Jobs 
    jobs = {} 
    for e in eng_col.find({}, {"job":1}): 
        j = (e.get("job") or "Unknown").strip() 
        jobs[j] = jobs.get(j,0) + 1 
 
    # Services and questions 
    services = {} 
    questions = {} 
    desires = {} 
    for e in eng_col.find({}, {"service":1, "question_clicked":1, "desires":1}): 
        s = e.get("service") or "Unknown" 
        q = e.get("question_clicked") or "Unknown" 
        ds = e.get("desires") or [] 
        services[s] = services.get(s,0) + 1 
        questions[q] = questions.get(q,0) + 1 
        for d in ds: 
            desires[d] = desires.get(d,0) + 1 
 
    # Suggest premium help: users with repeated engagements on same desire or question
    pipeline = [ 
        {"$group": {"_id": {"user":"$user_id","question":"$question_clicked"}, "count":{"$sum":1}}}, 
        {"$match": {"count": {"$gte": 2}}} 
    ] 
    repeated = list(eng_col.aggregate(pipeline)) 
    premium_suggestions = [ 
        {"user": r["_id"]["user"], "question": r["_id"]["question"], "count": r["count"]} 
        for r in repeated if r["_id"]["user"] 
    ] 
 
    return jsonify({ 
        "age_groups": age_groups, 
        "jobs": jobs, 
        "services": services, 
        "questions": questions, 
        "desires": desires, 
        "premium_suggestions": premium_suggestions 
    }) 

# Admin CRUD for services (create/update/delete)
@app.route("/api/admin/services", methods=["GET", "POST"])
@admin_required
def admin_services():
    if request.method == "GET":
        # Return all services
        services = list(services_col.find({}, {"_id": 0}))
        return jsonify(services)

    # POST → create or update
    payload = request.json or {}
    sid = payload.get("id")

    if not sid:
        return jsonify({"error": "Service ID is required"}), 400

    services_col.update_one(
        {"id": sid},
        {"$set": payload},
        upsert=True
    )

    return jsonify({"status": "ok"})

@app.route("/api/admin/engagements") 
@admin_required 
def admin_engagements(): 
    items = [] 
    for e in eng_col.find().sort("timestamp",-1).limit(500): 
        e["_id"] = str(e["_id"]) 
        e["timestamp"] = e.get("timestamp").isoformat() if e.get("timestamp") else None 
        items.append(e) 
    return jsonify(items) 
 
@app.route("/api/admin/export_csv") 
@admin_required 
def export_csv(): 
    cursor = eng_col.find() 
    si = StringIO() 
    cw = csv.writer(si) 
    cw.writerow(["user_id","age","job","desire","question","service","timestamp"]) 
    for e in cursor: 
        cw.writerow([ 
            e.get("user_id"), e.get("age"), e.get("job"), 
            ",".join(e.get("desires") or []), 
            e.get("question_clicked"), e.get("service"), 
            e.get("timestamp").isoformat() if e.get("timestamp") else "" 
        ]) 
    csv_bytes = si.getvalue().encode("utf-8") 
    return send_file( 
        BytesIO(csv_bytes), 
        mimetype="text/csv", 
        as_attachment=True, 
        download_name="engagements.csv" 
    ) 
 

@app.route("/api/admin/services/<service_id>", methods=["DELETE"]) 
@admin_required 
def delete_service(service_id): 
    services_col.delete_one({"id": service_id}) 
    return jsonify({"status":"deleted"}) 

@app.route('/api/admin/index-documents', methods=['POST'])
def index_documents():
    """
    Admin endpoint to add documents to knowledge base
    
    Request body:
    {
        "documents": [
            {
                "text": "Document content here",
                "source": "https://example.com",
                "title": "Document Title"
            }
        ]
    }
    """
    try:
        # TODO: Add admin authentication
        
        data = request.get_json()
        documents = data.get('documents', [])
        
        if not documents:
            return jsonify({"error": "No documents provided"}), 400
        
        # Add to RAG system
        count = rag_system.add_documents(documents)
        
        return jsonify({
            "message": f"Successfully indexed {count} documents",
            "count": count
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/admin/search-analytics', methods=['GET'])
def search_analytics():
    """Get search analytics for admin"""
    try:
        # Get all searches
        searches = list(db.ai_searches.find({}).sort('timestamp', -1).limit(100))
        
        # Calculate metrics
        total = len(searches)
        high_confidence = sum(1 for s in searches if s.get('confidence') == 'high')
        
        return jsonify({
            "total_searches": total,
            "high_confidence_rate": (high_confidence / total * 100) if total > 0 else 0,
            "recent_searches": searches[:20]
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- Placeholders for AI integration (vector DB, embeddings) 

# @app.route("/api/ai/search", methods=["POST"]) 
# def ai_search(): 
#     # Placeholder: in future, accept textual query, get embeddings, search
#     # a vector DB (FAISS/Pinecone), and return relevant docs + generated answer via LLM.
#     return jsonify({"message":"AI search not configured. Add vector DB + LLM."}) 



# ============================================
# AI ENDPOINTS
# ============================================

@app.route('/api/ai/search', methods=['POST'])
@limiter.limit("20 per minute")
def ai_search():
    """
    AI-powered search endpoint using Gemini
    
    Request body:
    {
        "query": "How do I apply for a passport?"
    }
    """
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({"error": "Query is required"}), 400
        
        if len(query) < 3:
            return jsonify({"error": "Query too short"}), 400
        
        # Get answer from Gemini RAG
        result = rag_system.answer_query(query, n_results=5)
        
        # Log the search
        db.ai_searches.insert_one({
            'query': query,
            'timestamp': datetime.utcnow(),
            'confidence': result['confidence'],
            'sources_count': result['retrieved_docs'],
            'ip_address': request.remote_addr
        })
        
        return jsonify(result)
    
    except Exception as e:
        app.logger.error(f"AI search error: {str(e)}")
        return jsonify({
            "error": "Search failed",
            "message": "Please try again or contact support"
        }), 500

@app.route('/api/ai/chat', methods=['POST'])
@limiter.limit("30 per minute")
def ai_chat():
    """
    Interactive chat with Gemini
    
    Request body:
    {
        "message": "Hello!",
        "history": [{"role": "user", "content": "Hi"}]  # optional
    }
    """
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        history = data.get('history', [])
        
        if not message:
            return jsonify({"error": "Message is required"}), 400
        
        result = rag_system.chat(message, history)
        
        return jsonify({
            "response": result['response'],
            "history": result['history']
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/ai/stats', methods=['GET'])
def ai_stats():
    """Get AI system statistics"""
    try:
        stats = rag_system.get_stats()
        
        # Add search statistics
        total_searches = db.ai_searches.count_documents({})
        recent_searches = list(db.ai_searches.find({}).sort('timestamp', -1).limit(10))
        
        return jsonify({
            **stats,
            'total_searches': total_searches,
            'recent_queries': [s['query'] for s in recent_searches]
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# ============================================
# HEALTH CHECK
# ============================================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "ai_system": "operational",
        "database": "connected",
        "timestamp": datetime.utcnow().isoformat()
    })

@app.route('/api/webhook/n8n/scrape', methods=['POST'])
def n8n_scrape_webhook():
    """
    Webhook for N8N to trigger document scraping
    
    Request body:
    {
        "urls": [
            {"url": "https://example.com", "type": "html", "title": "Page Title"}
        ]
    }
    """
    try:
        data = request.get_json()
        urls = data.get('urls', [])
        
        if not urls:
            return jsonify({"error": "No URLs provided"}), 400
        
        # Import scraper
        from scripts.document_scrapper import DocumentScraper
        scraper = DocumentScraper()
        
        # Scrape and index
        count = scraper.scrape_and_index(urls)
        
        return jsonify({
            "success": True,
            "count": count,
            "message": f"Successfully scraped and indexed {count} documents"
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/webhook/n8n/query', methods=['POST'])
def n8n_query_webhook():
    """
    Webhook for N8N to query the AI system
    
    Request body:
    {
        "query": "How do I apply for a passport?",
        "user_id": "telegram_12345"
    }
    """
    try:
        data = request.get_json()
        query = data.get('query', '')
        user_id = data.get('user_id', 'anonymous')
        
        if not query:
            return jsonify({"error": "Query is required"}), 400
        
        # Get answer
        result = rag_system.answer_query(query)
        
        # Log engagement
        db.engagements.insert_one({
            'user_id': user_id,
            'query': query,
            'timestamp': datetime.utcnow(),
            'source': 'n8n_webhook',
            'confidence': result['confidence']
        })
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
if __name__ == "__main__": 
    # ensure at least one admin user exists (dev convenience) 
    if admins_col.count_documents({}) == 0: 
        admins_col.insert_one({"username":"admin", "password": os.getenv("ADMIN_PWD","admin123")}) 
    app.run(debug=True, host="0.0.0.0", port=int(os.getenv("PORT",5000))) 