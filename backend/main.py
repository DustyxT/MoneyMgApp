from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
from routes import transactions, budget, statistics, profile

app = FastAPI(
    title="Manage Ur Wealth API",
    description="Backend API for the Manage Ur Wealth personal finance application",
    version="1.0.0"
)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.responses import JSONResponse
from fastapi.requests import Request

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print(f"Global error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"success": False, "message": "Internal Server Error", "detail": str(exc)},
    )

# Include routers
app.include_router(transactions.router)
app.include_router(budget.router)
app.include_router(statistics.router)
app.include_router(profile.router)

# Serve static files
from utils import get_base_path
FRONTEND_DIR = get_base_path() / "frontend"

@app.get("/")
def serve_frontend():
    return FileResponse(FRONTEND_DIR / "index.html")

@app.get("/styles.css")
def serve_css():
    return FileResponse(FRONTEND_DIR / "styles.css", media_type="text/css")

@app.get("/app.js")
def serve_js():
    return FileResponse(FRONTEND_DIR / "app.js", media_type="application/javascript")

@app.get("/health")
def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    import sys
    import os
    import traceback
    from pathlib import Path

    # Determine log path (next to executable or script)
    if getattr(sys, 'frozen', False):
        base_dir = Path(sys.executable).parent
    else:
        base_dir = Path(__file__).parent.parent

    log_file = base_dir / "debug.log"

    # Redirect stdout/stderr to debug.log
    # This fixes the "isatty" crash by providing actual file streams instead of None
    # and allows us to see why the app might be failing.
    sys.stdout = open(log_file, "w", buffering=1)
    sys.stderr = open(log_file, "w", buffering=1)

    print("--- Manage Ur Wealth Startup ---")
    
    try:
        # Run the application
        if getattr(sys, 'frozen', False):
            import webbrowser
            from threading import Timer
            
            def open_browser():
                print("Launching browser...")
                webbrowser.open("http://localhost:8000")
                
            # Open browser after a short delay
            Timer(2.0, open_browser).start()

        print("Starting Uvicorn server...")
        # Pass the app object directly to avoid import errors in PyInstaller
        uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
        
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        traceback.print_exc()
        # Keep process alive briefly to ensure log flush? 
        # No, file is line bufferedish.
    finally:
        print("Server stopped.")

