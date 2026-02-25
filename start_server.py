#!/usr/bin/env python
"""
Simple backend server starter with error output visible.
"""
import os
import sys
import traceback
from pathlib import Path

# Add backend/src to path
backend_src = Path(__file__).parent / "backend" / "src"
sys.path.insert(0, str(backend_src))

# Set environment variables
os.environ.setdefault('DATABASE_URL', 'sqlite:///./todoapp.db')
os.environ.setdefault('BETTER_AUTH_SECRET', 'your-super-secret-better-auth-key-here-make-it-long-and-random')

if __name__ == "__main__":
    print("=" * 50)
    print("Starting Backend Server...")
    print("=" * 50)
    
    try:
        from fastapi import FastAPI
        from fastapi.middleware.cors import CORSMiddleware
        
        app = FastAPI(
            title="Hackathon-Todo API",
            description="REST API for the Hackathon-Todo application",
            version="1.0.0"
        )
        
        # Add CORS middleware
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        @app.get("/")
        def read_root():
            return {"message": "Hackathon-Todo API is running!", "endpoints": ["/", "/health", "/api/v1/tasks"]}
        
        @app.get("/health")
        def health_check():
            return {"status": "healthy", "database": "sqlite"}
        
        # Try to include the tasks router
        try:
            from routes import tasks
            app.include_router(tasks.router, prefix="/api/v1", tags=["tasks"])
            print("[OK] Tasks router loaded")
        except Exception as e:
            print(f"[WARN] Tasks router not loaded: {e}")
        
        print("[OK] FastAPI app created")
        print("[OK] Starting uvicorn on http://0.0.0.0:4000")
        print("=" * 50)
        
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=4000, reload=False, log_level="info")
        
    except Exception as e:
        print(f"[ERROR] Error starting server: {e}")
        traceback.print_exc()
        sys.exit(1)
