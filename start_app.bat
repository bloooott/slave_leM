@echo off
cd /d "C:\Users\saidb\OneDrive\Documents\project\job-agent"
git pull origin main
call venv\Scripts\activate
streamlit run app.py