import os
import json
from typing import Optional
from fastapi import FastAPI, Request, HTTPException
from autocar_client import AutoCarClient

app = FastAPI()

# Load Route Map
ROUTE_MAP = {}
route_map_path = "route_map.json"
if os.path.exists(route_map_path):
    with open(route_map_path, "r") as f:
        ROUTE_MAP = json.load(f)

client = AutoCarClient()

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/.well-known/isli-manifest")
async def manifest():
    import yaml
    manifest_path = "isli-skill.yaml"
    if os.path.exists(manifest_path):
        with open(manifest_path, "r") as f:
            return yaml.safe_load(f)
    raise HTTPException(status_code=404, detail="Manifest not found")

@app.post("/login")
async def login(request: Request):
    payload = await request.json()
    email = payload.get("email")
    password = payload.get("password")
    
    if not email or not password:
        raise HTTPException(status_code=400, detail="Missing email or password")
        
    result = client.login(email, password)
    return result

@app.post("/{tool_name}")
async def handle_tool(tool_name: str, request: Request):
    if tool_name not in ROUTE_MAP:
        raise HTTPException(status_code=404, detail=f"Unknown tool: {tool_name}")
    
    config = ROUTE_MAP[tool_name]
    payload = await request.json()
    
    access_token = payload.get("access_token")
    if not access_token:
        return {"success": False, "message": "Missing 'access_token' in payload. Please login first."}
    
    # Construct endpoint path
    endpoint = config["path"]
    if "{id}" in endpoint:
        if "id" not in payload:
            return {"success": False, "message": "Missing required parameter: id"}
        endpoint = endpoint.replace("{id}", str(payload["id"]))
    
    # Data is 'data' field or None
    data = payload.get("data")
    
    result = client.request(config["method"], endpoint, data, access_token)
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8101)
