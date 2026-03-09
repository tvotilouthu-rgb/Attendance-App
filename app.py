import streamlit as st
import pandas as pd
from datetime import datetime
import os
import pytz
from PIL import Image

# --- SETTINGS & STAFF DATABASE ---
FIXED_LOCATION = "VETERINARY HOSPITAL, TILOUTHU"
LOG_FILE = "Attendance_Data.csv"
IST = pytz.timezone('Asia/Kolkata')

# Staff Data (QR ID match karne ke liye)
staff_db = {
    "AHD-TIL-01": {"name": "Dr. Sanjay Kumar", "post": "T.V.O.", "pin": "1001"},
    "AHD-TIL-02": {"name": "Pramod Kumar Pandey", "post": "D.E.O.", "pin": "2002"},
    "AHD-TIL-03": {"name": "Satyanarayan Pandey", "post": "Peon", "pin": "3003"},
    "AHD-TIL-04": {"name": "Raja Kumar", "post": "Peon (Outsourced)", "pin": "4004"}
}

st.set_page_config(page_title="AHD Smart Attendance", layout="centered")

# --- NAVIGATION ---
menu = st.sidebar.radio("Menu", ["Attendance Lagayein", "Monthly Report (Admin)"])

# --- SECTION 1: ATTENDANCE LOGIC ---
if menu == "Attendance Lagayein":
    st.title(f"🏛️ {FIXED_LOCATION}")
    st.info(f"📅 Date: {datetime.now(IST).strftime('%d-%m-%Y')}")

    # 1. QR Scan Mode
    st.subheader("📷 QR Code Scan Karein")
    qr_img = st.camera_input("Apna ID Card QR dikhayein")

    if qr_img:
        # Note: Professional apps mein 'pyzbar' use hota hai background mein, 
        # yahan demo ke liye hum user ko ID manually confirm karne denge ya 
        # aap image upload karke read kar sakte hain. 
        # Abhi ke liye hum easy flow rakhte hain:
        
        id_from_qr = st.selectbox("ID Confirm Karein:", ["--Select ID--"] + list(staff_db.keys()))
        
        if id_from_qr != "--Select ID--":
            user_info = staff_db[id_from_qr]
            st.success(f"Pehchaan: {user_info['name']} ({user_info['post']})")
            
            # 2. Selfie (Biometric Feel)
            st.subheader("🤳 Ek Selfie Lein")
            selfie = st.camera_input("Attendance ke liye photo khinchein", key="selfie_capture")
            
            if selfie:
                col1, col2 = st.columns(2)
                
                def log_data(status):
                    now = datetime.now(IST)
                    new_entry = {
                        "ID": id_from_qr,
                        "Name": user_info['name'],
                        "Post": user_info['post'],
                        "Status": status,
                        "Time": now.strftime("%H:%M:%S"),
                        "Date": now.strftime("%Y-%m-%d"),
                        "Month": now.strftime("%B-%Y"), # Monthly filter ke liye
                        "Location": FIXED_LOCATION
                    }
                    df = pd.DataFrame([new_entry])
                    df.to_csv(LOG_FILE, mode='a', header=not os.path.exists(LOG_FILE), index=False)
                    st.balloons()
                    st.success(f"Done! {user_info['name']} ka {status} record ho gaya.")

                with col1:
                    if st.button("✅ Check-In (Aaye)"):
                        log_data("IN")
                with col2:
                    if st.button("❌ Check-Out (Gaye)"):
                        log_data("OUT")

# --- SECTION 2: MONTHLY REPORT ---
else:
    st.title("📊 Admin Dashboard")
    
    if os.path.exists(LOG_FILE):
        df_all = pd.read_csv(LOG_FILE)
        
        # Month Filter
        all_months = df_all['Month'].unique().tolist()
        selected_month = st.selectbox("Mahina Chunein:", all_months)
        
        # Staff Filter
        all_staff = df_all['Name'].unique().tolist()
        selected_staff = st.multiselect("Staff Chunein (Khali chhodne par sabka dikhega):", all_staff)
        
        # Filtering Data
        report_df = df_all[df_all['Month'] == selected_month]
        if selected_staff:
            report_df = report_df[report_df['Name'].isin(selected_staff)]
        
        st.write(f"### {selected_month} ki Report")
        st.dataframe(report_df)
        
        # Download Excel/CSV Button
        csv = report_df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Report (CSV)", data=csv, file_name=f"Attendance_{selected_month}.csv", mime='text/csv')
    else:
        st.warning("Abhi tak koi data record nahi hua hai.")

