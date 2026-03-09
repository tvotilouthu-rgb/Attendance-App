import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
import os

# --- CONFIGURATION ---
IST = pytz.timezone('Asia/Kolkata')
LOG_FILE = "attendance_log.csv"

# Staff Database - Updated with correct Names and Posts
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
    
    qr_id = st.text_input("Apna ID Card QR Scan Karein:")

    if qr_id:
        if qr_id in staff_db:
            user_info = staff_db[qr_id]
            name = user_info["name"]
            post = user_info["post"]
            
            st.success(f"Pehchaan: {name} ({post})")
            
            img_file = st.camera_input(f"{name}, apni selfie lein")
            
            if img_file:
                if st.button("Attendance Submit Karein"):
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
                    st.success(f"Dhanyawad {name}! Aapki attendance lag gayi hai.")
        else:
            st.error("Ghalat ID! Please sahi QR scan karein.")

# --- SECTION 2: ADMIN DASHBOARD (REPORTS) ---
else:
    st.title("📊 Admin Dashboard & Reports")
    
    if os.path.exists(LOG_FILE):
        try:
            df_all = pd.read_csv(LOG_FILE)
            tab1, tab2 = st.tabs(["📅 Daily Report", "📅 Monthly Report"])

            with tab1:
                selected_date = st.date_input("Tareekh Chunein:", datetime.now(IST).date())
                daily_df = df_all[df_all['Date'] == str(selected_date)]
                st.dataframe(daily_df, use_container_width=True)
                
                if not daily_df.empty:
                    st.download_button("📥 Download Daily CSV", daily_df.to_csv(index=False).encode('utf-8'), f"Daily_{selected_date}.csv", "text/csv")

            with tab2:
                all_months = df_all['Month'].unique().tolist()
                selected_month = st.selectbox("Mahina Chunein:", all_months)
                month_df = df_all[df_all['Month'] == selected_month]
                st.dataframe(month_df, use_container_width=True)
                
                if not month_df.empty:
                    st.download_button("📥 Download Monthly CSV", month_df.to_csv(index=False).encode('utf-8'), f"Monthly_{selected_month}.csv", "text/csv")
        except:
            st.error("Data error! CSV file ka header sahi karein.")
    else:
        st.info("Abhi tak koi data nahi mila.")
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
