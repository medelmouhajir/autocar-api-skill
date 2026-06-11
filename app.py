import os
import json
import jwt
import sqlite3
from flask import Flask, request, jsonify, g
from autocar_client import AutoCarClient

app = Flask(__name__)

# Config
DB_PATH = os.getenv("DB_PATH", "/app/data/skill_sessions.db")
JWT_SECRET = os.getenv("JWT_SECRET")  # Provided by ISLI Core during installation

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DB_PATH)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        db.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                isli_user_id TEXT PRIMARY KEY,
                access_token TEXT,
                refresh_token TEXT,
                user_email TEXT
            )
        ''')
        db.commit()

# Initialize DB
init_db()

def verify_isli_auth(f):
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("X-Internal-Auth")
        if not auth_header:
            return jsonify({"success": False, "message": "Missing X-Internal-Auth header"}), 401
        
        # Strip 'Bearer ' if present
        token = auth_header.split(" ")[1] if auth_header.startswith("Bearer ") else auth_header
        
        try:
            if JWT_SECRET:
                payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            else:
                # Fallback for dev: extract 'sub' without verification if no secret is set
                payload = jwt.decode(token, options={"verify_signature": False})
            
            request.isli_user_id = payload.get("sub")
            if not request.isli_user_id:
                 return jsonify({"success": False, "message": "Invalid JWT: missing 'sub' (User ID)"}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({"success": False, "message": "Internal JWT expired"}), 401
        except Exception as e:
            return jsonify({"success": False, "message": f"Auth verification failed: {str(e)}"}), 401
        
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

# Load Route Map
ROUTE_MAP = {}
if os.path.exists("route_map.json"):
    with open("route_map.json", "r") as f:
        ROUTE_MAP = json.load(f)
elif os.path.exists("autocar-api/route_map.json"):
    with open("autocar-api/route_map.json", "r") as f:
        ROUTE_MAP = json.load(f)

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

@app.route("/.well-known/isli-manifest", methods=["GET"])
def manifest():
    try:
        import yaml
        manifest_path = "isli-skill.yaml"
        if not os.path.exists(manifest_path):
            manifest_path = "autocar-api/isli-skill.yaml"
        with open(manifest_path, "r") as f:
            content = yaml.safe_load(f)
        return jsonify(content)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/login", methods=["POST"])
@verify_isli_auth
def login():
    payload = request.json
    email = payload.get("email")
    password = payload.get("password")
    
    client = AutoCarClient()
    # Temporary mock db for the client's internal use during this request
    temp_db = {}
    result = client.login(email, password, temp_db)
    
    if result.get("success"):
        # Store in SQLite
        db = get_db()
        db.execute('''
            INSERT OR REPLACE INTO sessions (isli_user_id, access_token, refresh_token, user_email)
            VALUES (?, ?, ?, ?)
        ''', (request.isli_user_id, temp_db["accessToken"], temp_db["refreshToken"], temp_db["userEmail"]))
        db.commit()
        
    return jsonify(result)

@app.route("/<tool_name>", methods=["POST"])
@verify_isli_auth
def handle_tool(tool_name):
    if tool_name not in ROUTE_MAP:
        return jsonify({"success": False, "message": f"Unknown tool: {tool_name}"}), 404
    
    config = ROUTE_MAP[tool_name]
    payload = request.json or {}
    
    # Get tokens from DB
    db = get_db()
    row = db.execute("SELECT * FROM sessions WHERE isli_user_id = ?", (request.isli_user_id,)).fetchone()
    
    if not row:
        return jsonify({"success": False, "message": "User not authenticated. Please login first."}), 401
    
    # Prepare client db from sqlite row
    client_db = {
        "accessToken": row["access_token"],
        "refreshToken": row["refresh_token"]
    }
    
    # Construct endpoint path (handle parameter substitution if any)
    endpoint = config["path"]
    if "{id}" in endpoint:
        if "id" not in payload:
            return jsonify({"success": False, "message": "Missing required parameter: id"}), 400
        endpoint = endpoint.replace("{id}", str(payload["id"]))
    
    # Data is either the whole payload or specifically the 'data' field
    data = payload.get("data") if "data" in payload else None
    
    client = AutoCarClient()
    result = client.request(config["method"], endpoint, data, client_db)
    
    # If tokens changed (refresh happened), update DB
    if client_db["accessToken"] != row["access_token"]:
        db.execute('''
            UPDATE sessions SET access_token = ?, refresh_token = ?
            WHERE isli_user_id = ?
        ''', (client_db["accessToken"], client_db["refreshToken"], request.isli_user_id))
        db.commit()
        
    return jsonify(result)

if __name__ == "__main__":
    app.run(port=8000)
