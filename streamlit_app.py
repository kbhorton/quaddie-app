import streamlit as st
import datetime
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# Basic Page Setup
st.set_page_config(page_title="Quaddie Tracker", page_icon="🏇")

# 1. Connect to Google Sheets
# Note: You will link your URL in the Streamlit Cloud settings later
conn = st.connection("gsheets", type=GSheetsConnection)

def get_data():
    return conn.read(ttl="1m") # Refresh data every minute

st.title("🏇 Shared Quaddie Tracker")

today_date = datetime.date.today().isoformat()
df = get_data()

# Filter for today's entries
today_entry = df[df['Date'] == today_date]

# 2. Display Logic
if not today_entry.empty:
    row = today_entry.iloc[-1] # Get the most recent entry for today
    st.success(f"Picks active for {row['Track']}")
    
    cols = st.columns(4)
    for i in range(4):
        with cols[i]:
            st.metric(f"Leg {i+1}", str(row[f"Leg{i+1}"]))
    
    if st.button("Edit / Update Picks"):
        st.session_state.editing = True
else:
    st.info("No picks entered for today.")
    st.session_state.editing = True

# 3. The Input Form
if st.session_state.get('editing'):
    with st.form("quaddie_form"):
        track = st.text_input("Track Name", placeholder="e.g. Randwick")
        c1, c2, c3, c4 = st.columns(4)
        l1 = c1.text_input("Leg 1", key="in1")
        l2 = c2.text_input("Leg 2", key="in2")
        l3 = c3.text_input("Leg 3", key="in3")
        l4 = c4.text_input("Leg 4", key="in4")
        
        if st.form_submit_button("Save to Cloud"):
            new_row = pd.DataFrame([{
                "Date": today_date, "Track": track,
                "Leg1": l1, "Leg2": l2, "Leg3": l3, "Leg4": l4
            }])
            # This sends the data to your Google Sheet
            conn.create(data=new_row)
            st.success("Saved! Refresh the page to see updates.")
            st.session_state.editing = False
