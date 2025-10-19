#!/bin/bash
# Start Backend Server
cd "C:/Users/srina/OneDrive/Documents/Downloads/Stealth-Reecovery-20251010T154256Z-1-001/Stealth-Reecovery"
C:/Python313/python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
