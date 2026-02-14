import streamlit as st
import pandas as pd
import joblib
from sqlalchemy import create_engine
from datetime import datetime

# 1. Load the Model
# Ensure 'credit_model.joblib' is in your main folder
model = joblib.load('credit_model.joblib')

# 2. Database Connection
# Make sure DB_URL is set in your Streamlit/HuggingFace Secrets
def get_connection():
    return create_engine(st.secrets["DB_URL"])

# --- UI LAYOUT ---
st.set_page_config(page_title="Bank Default Monitor", layout="wide")
st.title("🏦 Bank Default & Business Overview Monitor")

tab1, tab2 = st.tabs(["Prediction Tool", "Business Dashboard"])

with tab1:
    st.header("New Loan Application")
    
    with st.form("prediction_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            amount = st.number_input("Loan Amount", min_value=0)
            duration = st.number_input("Duration (Months)", min_value=0)
            age = st.number_input("Applicant Age", min_value=18)
            chk_acct = st.selectbox("Checking Account Status", [ '< 0 €','0–200 €','≥ 200 €','No checking account'])
            
        with col2:
            saving_acct = st.selectbox("Savings Account Status", ['< 100 €','100–500 €','500–1000 €','≥ 1000 €','No / unknown savings'])
            credit_his = st.selectbox("Credit History Score", ['No previous credit / all paid','All credits paid duly','Existing credits paid duly','Delay in payments','Critical account'])
            property_type = st.selectbox("Property Type", [ 'Real estate', 'Life insurance / building society', 'Car or other property', 'No / unknown property'])
            
        submit = st.form_submit_button("Predict Risk")

    if submit:
        # Prepare data for prediction
        input_data = pd.DataFrame([[age, amount, duration, chk_acct, saving_acct, credit_his, property_type]],
                                 columns=['age','amount','duration','chk_acct','saving_acct',  'credit_his','property'])
        
        # Make Prediction
        prediction = model.predict(input_data)[0]
        result_text = "High Risk (Default)" if prediction == 2 else "Low Risk (Success)"
        
        # Display Result
        if prediction == 2:
            st.error(f"Prediction: {result_text}")
        else:
            st.success(f"Prediction: {result_text}")
            
        # 3. Save to Database
        try:
            engine = get_connection()
            df_to_save = input_data.copy()
            df_to_save['prediction_result'] = result_text
            df_to_save.to_sql('loan_predictions', engine, if_exists='append', index=False)
            st.info("Record saved to database successfully!")
        except Exception as e:
            st.warning(f"Database error: {e}")

with tab2:
    st.header("Historical Overview")
    try:
        engine = get_connection()
        history_df = pd.read_sql("SELECT * FROM loan_predictions ORDER BY prediction_time DESC", engine)
        
        if not history_df.empty:
            # Metrics
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Applications", len(history_df))
            c2.metric("Avg Loan Amount", f"${history_df['amount'].mean():,.2f}")
            c3.metric("Default Rate", f"{(history_df['prediction_result'] == 'High Risk (Default)').mean():.1%}")
            
            # Data Table
            st.dataframe(history_df)
        else:
            st.write("No data found in database.")
    except Exception as e:

        st.error(f"Could not load dashboard: {e}")
