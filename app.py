import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- SETTINGS & STAFF DATABASE ---
FIXED_LOCATION = "VETERINARY HOSPITAL, TILOUTHU"
LOG_FILE = "Attendance_Data.csv"

# Staff Data with PINs (Aap PIN badal sakte hain)
staff_db = {
    "Dr. Sanjay Kumar": {"post": "T.V.O.", "pin": "1001"},
    "Pramod Kumar Pandey": {"post": "D.E.O.", "pin": "2002"},
    "Satyanarayan Pandey": {"post": "Peon", "pin": "3003"},
    "Raja Kumar": {"post": "Peon (Outsourced)", "pin": "4004"}
}

# --- APP UI ---
st.set_page_config(page_title="Secure Attendance", layout="centered")
st.title(f"🏛️ {FIXED_LOCATION}")
st.info(f"📍 Location: {FIXED_LOCATION} | 📅 Date: {datetime.now().strftime('%d-%m-%Y')}")

# 1. Name Selection
selected_name = st.selectbox("Apna Naam Select Karein:", ["--Select Name--"] + list(staff_db.keys()))

if selected_name != "--Select Name--":
    # 2. PIN Input (Password mode)
    user_pin = st.text_input("Apna 4-Digit PIN Darj Karein:", type="password", help="Security ke liye apna PIN dalein")
    
    col1, col2 = st.columns(2)
    
    # 3. Validation Logic
    if user_pin == staff_db[selected_name]["pin"]:
        st.success(f"Pehchaan Sahi Hai: {selected_name} ({staff_db[selected_name]['post']})")
        
        def log_attendance(status):
            now = datetime.now()
            new_entry = {
                "Name": selected_name,
                "Post": staff_db[selected_name]["post"],
                "Status": "IN" if status == "In" else "OUT",
                "Time": now.strftime("%H:%M:%S"),
                "Date": now.strftime("%Y-%m-%d"),
                "Location": FIXED_LOCATION
            }
            df = pd.DataFrame([new_entry])
            df.to_csv(LOG_FILE, mode='a', header=not os.path.exists(LOG_FILE), index=False)
            st.balloons() # Thoda celebration!
            st.info(f"Kamyabi! {status} time record ho gaya hai.")

        with col1:
            if st.button("✅ Check-In (Aaye)", use_container_width=True):
                log_attendance("In")
        with col2:
            if st.button("❌ Check-Out (Gaye)", use_container_width=True):
                log_attendance("Out")
                
    elif user_pin != "":
        st.error("Galat PIN! Kripya sahi PIN dalein.")

# --- ADMIN SECTION ---
st.divider()
if st.expander("Admin: Aaj ka Attendance Record Dekhein"):
    password = st.text_input("Admin Password:", type="password")
    if password == "admin123": # Sirf admin hi data dekh sakega
        if os.path.exists(LOG_FILE):
            data = pd.read_csv(LOG_FILE)
            st.dataframe(data.sort_values(by="Time", ascending=False))
        else:

            st.warning("Abhi tak koi record nahi hai.")



