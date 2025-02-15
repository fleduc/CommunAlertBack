from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import auth, users, alerts, messages
print("✅ FastAPI démarre")

app = FastAPI(title="CommunAlert API")

# Configurer CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("✅ Importation des routes AUTH")
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])

print("✅ Importation des routes USERS")
app.include_router(users.router, prefix="/api/users", tags=["users"])

print("✅ Importation des routes ALERTS")
app.include_router(alerts.router, prefix="/api/alerts", tags=["alerts"])

print("✅ Importation des routes MESSAGES")
app.include_router(messages.router, prefix="/api/alerts/{alert_id}/messages", tags=["messages"])


@app.get("/")
def read_root():
    return {"message": "Bienvenue sur CommunAlert API"}
