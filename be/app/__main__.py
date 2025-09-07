#!/usr/bin/env python3
"""
Entry point for running the app directly with: python -m app
"""
import os
import uvicorn

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    print(f"🚀 Starting server on port {port}")
    uvicorn.run("app.main:app", host="0.0.0.0", port=port)
