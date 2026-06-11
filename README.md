# AutoCar API Skill (USR v2.0)

An ISLI-compatible Python skill built on the **Universal Skill Runtime (USR) v2.0**. This skill runs as a Dockerized HTTP microservice and allows AI agents to interact with the AutoCar Software API.

## 🚀 Features

- **Explicit Tools**: Over 45+ distinct tools (e.g., `create_customer`, `list_invoices`, `get_work_order`) for clear discovery by AI agents.
- **Dockerized Architecture**: Runs as a standalone microservice.
- **USR v2.0 Compliant**: Implements the `isli-skill.yaml` manifest and standard endpoints.
- **Internal Session Management**: Securely maps ISLI users to AutoCar API tokens using an internal SQLite database.

## 📁 Directory Structure

```
autocar-api/
├── isli-skill.yaml      # USR v2.0 Manifest
├── Dockerfile           # Container definition
├── requirements.txt     # Python dependencies
├── app.py               # Flask Web Server
├── autocar_client.py    # API Logic
├── SKILL.md             # Gemini CLI Documentation
└── README.md            # GitHub Documentation
```

## 🛠 Deployment (ISLI Registry)

1. Push this folder to a public GitHub repository.
2. The ISLI Core will:
   - Clone the repository.
   - Build the Docker image using the provided `Dockerfile`.
   - Inject a `JWT_SECRET` for internal authentication.
   - Expose the tools defined in `isli-skill.yaml`.

## ⚙️ Configuration

- **Port**: 8000
- **Default API URL**: `https://auto.wan.ma` (can be overridden via `AUTOCAR_API_URL` env var).
- **Persistence**: Session data is stored in `/app/data/skill_sessions.db` inside the container.

## 📄 License
MIT
