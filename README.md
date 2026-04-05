# DevOps AI Agent

AI-powered system monitoring agent with ML-based anomaly detection and 
LLM reasoning.

## What it does
- Monitors CPU, RAM, disk in real time using psutil
- Detects anomalies using Isolation Forest (falls back to thresholds 
  while training)
- Sends anomalies to Gemini API for root cause analysis + fix suggestions
- Stores incident memory across sessions
- Live Streamlit dashboard

## Setup
1. Clone the repo
2. `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and add your Gemini API key 
   (free at aistudio.google.com)
4. `python main.py` — terminal agent
5. `streamlit run dashboard.py` — live dashboard

## Stack
Python · psutil · scikit-learn · Gemini API · Streamlit
