import streamlit as st
import pandas as pd
import joblib
import sqlalchemy
import psycopg2

st.title("🔍 Environment Diagnostic Tool")

st.success("If you see this, Streamlit, Pandas, and Joblib are working!")

try:
    from sqlalchemy import create_engine
    st.success("SQLAlchemy is correctly installed!")
except Exception as e:
    st.error(f"SQLAlchemy Error: {e}")

try:
    import psycopg2
    st.success("psycopg2-binary is correctly installed!")
except Exception as e:
    st.error(f"Database Driver Error: {e}")

# Check if secrets are present
if "DB_URL" in st.secrets:
    st.success("Database Secret found!")
else:
    st.warning("Database Secret 'DB_URL' is missing in Streamlit Settings.")

# Check if model file exists
import os
if os.path.exists('credit_model.joblib'):
    st.success("Model file 'credit_model.joblib' detected!")
else:
    st.error("Model file not found in the root directory!")
