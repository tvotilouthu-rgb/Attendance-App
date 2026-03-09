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
    
    # Do options: Manual ya Scanner
    choice = st.radio("Attendance Kaise Lagayein?", ["QR Scanner Se", "Manual ID Likh Kar"])
    
    qr_id = ""
    
    if choice == "QR Scanner Se":
        st.info("Scanner abhi aapki selfie camera ko use karega. QR code ko camera ke samne layein.")
        # Streamlit ka standard camera input jo scan ke liye bhi kaam karega
        scan_img = st.camera_input("QR Code Scan Karein")
        if scan_img:
            st.warning("Scanner logic processing... Abhi ke liye niche apni ID confirm karein.")
            qr_id = st.text_input("Scanner ne kya ID padhi? (Yahan confirm karein):")
    else:
        qr_id = st.text_input("Apna ID Card Number Likhein (e.g. AHD-TIL-01):")

    if qr_id:
        if qr_id in staff_db:
            user_info = staff_db[qr_id]
            name = user_info["name"]
            post = user_info["post"]
            st.success(f"Pehchaan: {name} ({post})")
            
            # Selfie for Attendance
            img_file = st.camera_input(f"{name}, apni selfie lein")
            
            if img_file:
                if st.button("Final Submit Karein"):
                    now = datetime.now(IST)
                    new_entry = {
                        "Date": str(now.date()),
                        "ID": qr_id,
                        "Name": name,
                        "Post": post,
                        "Status": "Present",
                        "Time": now.strftime("%H:%M:%S"),
                        "Month": now.strftime("%B %Y")
                    }
                    df = pd.DataFrame([new_entry])
                    if not os.path.exists(LOG_FILE):
                        df.to_csv(LOG_FILE, index=False)
                    else:
                        df.to_csv(LOG_FILE, mode='a', header=False, index=False)
                    st.balloons()
                    st.success(f"Attendance Lag Gayi!")
        else:
            st.error("Ghalat ID! Sahi ID dalein.")
