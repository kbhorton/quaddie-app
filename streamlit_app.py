import streamlit as st
import datetime
import pandas as pd

st.set_page_config(page_title="Quaddie Tracker", page_icon="🏇")

st.title("🏇 Shared Quaddie Tracker")

# 1. Get your Sheet ID from the URL
# If your URL is https://docs.google.com/spreadsheets/d/1ABC123/edit, your ID is 1ABC123
sheet_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
sheet_id = sheet_url.split("/d/")[1].split("/")[0]
csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"

def get_data():
    return pd.read_csv(csv_url)

today_date = datetime.date.today().isoformat()

# Load Data
try:
    df = get_data()
except:
    st.error("Could not read the Google Sheet. Check your URL in Secrets.")
    st.stop()

today_entry = df[df['Date'] == today_date]

# 2. Display Logic
if not today_entry.empty and not st.session_state.get('editing'):
    row = today_entry.iloc[-1]
    st.success(f"Picks active for {row['Track']}")
    
    cols = st.columns(4)
    for i in range(4):
        with cols[i]:
            st.metric(f"Leg {i+1}", str(row[f"Leg{i+1}"]))
    
    if st.button("Edit / Update Picks"):
        st.session_state.editing = True
else:
    if today_entry.empty:
        st.info("No picks entered for today.")
    st.session_state.editing = True

# 3. Instruction for Saving
if st.session_state.get('editing'):
    st.warning("⚠️ Manual Step Required")
    st.write("Because Google is strict about security, the easiest way to save your picks is to click the button below to open your sheet and type them in directly. Your friends will see them here instantly once you refresh.")
    
    st.link_button("Open Google Sheet to Enter Picks", sheet_url)
    
    st.info("Type the Date, Track, and Horse Numbers into the next available row.")
    
    if st.button("I've finished entering picks"):
        st.session_state.editing = False
        st.rerun()
