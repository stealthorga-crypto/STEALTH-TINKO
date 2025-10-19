#!/bin/bash
cd "/c/Users/srina/OneDrive/Documents/Downloads/Stealth-Reecovery-20251010T154256Z-1-001/Stealth-Reecovery"
export PYTHONPATH="$(pwd):$PYTHONPATH"
C:/Python313/python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
