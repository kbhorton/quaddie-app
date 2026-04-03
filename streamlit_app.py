import streamlit as st
import datetime
import pandas as pd

# 1. Function to handle the button click
def deactivate_editing():
    st.session_state.editing = False

st.set_page_config(page_title="Quaddie Tracker", page_icon="🏇")

st.title("🏇 Shared Quaddie Tracker")

# 2. Get your Sheet ID from your Secrets
sheet_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
sheet_id = sheet_url.split("/d/")[1].split("/")[0]
csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"

# 3. Load Data
def get_data():
    # We add a timestamp to the URL to bypass Google's cache
    return pd.read_csv(f"{csv_url}&cachebust={datetime.datetime.now().timestamp()}")

today_date = datetime.date.today().isoformat()

try:
    df = get_data()
except:
    st.error("Could not read the Google Sheet. Check your URL in Secrets.")
    st.stop()

# Filter for today's entries
today_entry = df[df['Date'] == today_date]

# 4. Display Logic
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

# 5. The Editor View
if st.session_state.get('editing'):
    st.warning("⚠️ Manual Step Required")
    st.write("Click the button below to open your sheet and type your picks directly.")
    
    st.link_button("Open Google Sheet", sheet_url)
    
    st.info("Once you have saved your picks in the spreadsheet, click the button below.")
    
    # We use a unique key here to avoid the duplicate ID error
    st.button("I've finished entering picks", on_click=deactivate_editing, key="finish_button_v2")
