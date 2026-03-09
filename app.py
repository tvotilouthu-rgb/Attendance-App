import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
import os
from PIL import Image

# --- CONFIGURATION ---
IST = pytz.timezone('Asia/Kolkata')
LOG_FILE = "attendance_log.csv"

# Staff Database (IDs and Names)
staff_db = {
    "AHD-TIL-01": "Pramod Kumar",
    "AHD-TIL-02": "Staff Member 2",
    "AHD-TIL-03": "Staff Member 3"
}

st.set_page_config(page_title="AHD Tilouthu Attendance", layout="wide")

# --- MAIN MENU ---
menu = st.sidebar.radio("Navigation", ["Attendance Lagayein", "Admin Dashboard"])

# --- SECTION 1: ATTENDANCE ---
if menu == "Attendance Lagayein":
    st.title("🏥 First Class Veterinary Hospital, Tilouthu")
    st.subheader("QR Scan & Attendance System")

    qr_id = st.text_input("Apna ID Card QR Scan Karein ya Likhein:")

    if qr_id:
        if qr_id in staff_db:
            name = staff_db[qr_id]
            st.success(f"Pehchaan: {name}")
            
            # Camera for Selfie
            img_file = st.camera_input(f"{name}, apni selfie lein")
            
            if img_file:
                if st.button("Attendance Submit Karein"):
                    now = datetime.now(IST)
                    new_entry = {
                        "Date": str(now.date()),
                        "ID": qr_id,
                        "Name": name,
                        "Status": "Present",
                        "Time": now.strftime("%H:%M:%S"),
                        "Month": now.strftime("%B %Y")
                    }
                    
                    # Save to CSV
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

            # --- TAB 1: DAILY REPORT ---
            with tab1:
                selected_date = st.date_input("Tareekh Chunein:", datetime.now(IST).date())
                daily_df = df_all[df_all['Date'] == str(selected_date)]
                
                st.write(f"### {selected_date} ki Attendance List")
                st.dataframe(daily_df, use_container_width=True)
                
                if not daily_df.empty:
                    csv_daily = daily_df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Download Daily CSV",
                        data=csv_daily,
                        file_name=f"Daily_Attendance_{selected_date}.csv",
                        mime='text/csv',
                    )

            # --- TAB 2: MONTHLY REPORT ---
            with tab2:
                all_months = df_all['Month'].unique().tolist()
                selected_month = st.selectbox("Mahina Chunein:", all_months)
                
                month_df = df_all[df_all['Month'] == selected_month]
                
                st.write(f"### {selected_month} ki Poori Report")
                st.dataframe(month_df, use_container_width=True)
                
                if not month_df.empty:
                    csv_month = month_df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Download Monthly CSV",
                        data=csv_month,
                        file_name=f"Monthly_Attendance_{selected_month}.csv",
                        mime='text/csv',
                    )
        except Exception as e:
            st.error(f"Data padhne mein galti hui. CSV file check karein.")
    else:
        st.info("Abhi tak koi data record nahi hua hai.")
