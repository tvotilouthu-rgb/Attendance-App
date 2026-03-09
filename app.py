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

# --- MAIN MENU ---
menu = st.sidebar.radio("Navigation", ["Attendance Lagayein", "Admin Dashboard"])

# --- SECTION 1: ATTENDANCE ---
if menu == "Attendance Lagayein":
    st.title("🏥 First Class Veterinary Hospital, Tilouthu")
    
    choice = st.radio("Attendance Kaise Lagayein?", ["QR Scanner Se", "Manual ID Likh Kar"])
    qr_id = ""
    
    if choice == "QR Scanner Se":
        scan_img = st.camera_input("QR Code Scan Karein")
        if scan_img:
            qr_id = st.text_input("ID confirm karein:")
    else:
        qr_id = st.text_input("Apna ID Card Code Dalein (e.g. AHD-TIL-01):").strip()

    if qr_id in staff_db:
        user_info = staff_db[qr_id]
        name = user_info["name"]
        post = user_info["post"]
        st.success(f"Pehchaan: {name} ({post})")
        
        img_file = st.camera_input(f"{name}, apni selfie lein")
        
        if img_file:
            if st.button("Attendance Submit Karein"):
                now = datetime.now(IST)
                today = str(now.date())
                current_time = now.strftime("%H:%M:%S")
                
                # Check if already punched in today
                if os.path.exists(LOG_FILE):
                    df = pd.read_csv(LOG_FILE)
                    # Aaj ki entries filter karein
                    today_entry = df[(df['ID'] == qr_id) & (df['Date'] == today)]
                    
                    if not today_entry.empty and pd.isna(today_entry.iloc[-1]['Out_Time']):
                        # Agar In_Time hai par Out_Time khali hai, toh Out_Time bharo
                        df.loc[today_entry.index[-1], 'Out_Time'] = current_time
                        df.to_csv(LOG_FILE, index=False)
                        st.warning(f"Out-Time Lag Gaya: {current_time}")
                    else:
                        # Nayi In_Time entry
                        new_row = {"Date": today, "ID": qr_id, "Name": name, "Post": post, "In_Time": current_time, "Out_Time": None, "Month": now.strftime("%B %Y")}
                        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                        df.to_csv(LOG_FILE, index=False)
                        st.success(f"In-Time Lag Gaya: {current_time}")
                else:
                    # Pehli baar file banana
                    new_row = {"Date": today, "ID": qr_id, "Name": name, "Post": post, "In_Time": current_time, "Out_Time": None, "Month": now.strftime("%B %Y")}
                    pd.DataFrame([new_row]).to_csv(LOG_FILE, index=False)
                    st.success(f"In-Time Lag Gaya: {current_time}")
                st.balloons()

# --- SECTION 2: ADMIN DASHBOARD ---
else:
    st.title("📊 Admin Dashboard")
    if os.path.exists(LOG_FILE):
        df_all = pd.read_csv(LOG_FILE)
        st.dataframe(df_all, use_container_width=True)
        csv = df_all.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download All Reports", csv, "Attendance_Report.csv", "text/csv")
    else:
        st.info("Koi data nahi mila.")
