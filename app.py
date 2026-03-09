import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
import os

# --- CONFIGURATION ---
IST = pytz.timezone('Asia/Kolkata')
LOG_FILE = "attendance_log.csv"

# Staff Database
staff_db = {
    "AHD-TIL-01": {"name": "Dr. Sanjay Kumar", "post": "T.V.O."},
    "AHD-TIL-02": {"name": "Pramod Kumar Pandey", "post": "D.E.O."},
    "AHD-TIL-03": {"name": "Satyanarayan Pandey", "post": "Peon"},
    "AHD-TIL-04": {"name": "Raja Kumar", "post": "Peon (Outsourced)"}
}

st.set_page_config(page_title="AHD Tilouthu Attendance", layout="wide")

menu = st.sidebar.radio("Navigation", ["Attendance Lagayein", "Admin Dashboard"])

if menu == "Attendance Lagayein":
    st.title("🏥 First Class Veterinary Hospital, Tilouthu")
    
    # Scanner hamesha screen par rahega
    img_file = st.camera_input("Scanner/Selfie: Apne QR Code ya Chehre ki photo lein")
    
    qr_id = st.text_input("Apna ID Card Code Dalein (e.g. AHD-TIL-01):").strip()

    if qr_id in staff_db:
        user_info = staff_db[qr_id]
        st.success(f"Pehchaan: {user_info['name']} ({user_info['post']})")
        
        if img_file and st.button("Attendance Register Karein"):
            now = datetime.now(IST)
            today = str(now.date())
            current_time = now.strftime("%H:%M:%S")
            
            if os.path.exists(LOG_FILE):
                df = pd.read_csv(LOG_FILE)
                # Aaj ki entry check karein
                mask = (df['ID'] == qr_id) & (df['Date'] == today)
                
                if mask.any() and pd.isna(df.loc[mask, 'Out_Time']).any():
                    # Out_Time update karein
                    df.loc[mask & pd.isna(df['Out_Time']), 'Out_Time'] = current_time
                    st.warning(f"Out-Time Lag Gaya: {current_time}")
                else:
                    # Nayi In-Time entry
                    new_row = {
                        "Date": today, 
                        "ID": qr_id, 
                        "Name": user_info['name'], 
                        "Post": user_info['post'], 
                        "In_Time": current_time, 
                        "Out_Time": None, 
                        "Month": now.strftime("%B %Y")
                    }
                    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                    st.success(f"In-Time Lag Gaya: {current_time}")
                
                df.to_csv(LOG_FILE, index=False)
                st.balloons()
            else:
                # Agar file na ho toh nayi banayein
                new_row = {"Date": today, "ID": qr_id, "Name": user_info['name'], "Post": user_info['post'], "In_Time": current_time, "Out_Time": None, "Month": now.strftime("%B %Y")}
                pd.DataFrame([new_row]).to_csv(LOG_FILE, index=False)
                st.success(f"File Ban Gayi aur In-Time Lag Gaya!")

else:
    st.title("📊 Admin Dashboard")
    if os.path.exists(LOG_FILE):
        df_all = pd.read_csv(LOG_FILE)
        st.dataframe(df_all, use_container_width=True)
