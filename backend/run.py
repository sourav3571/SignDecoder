
from app.main import app

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["app", "models"],
        reload_excludes=["venv"],
        log_level="info"
    )
