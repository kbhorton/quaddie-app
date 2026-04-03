import streamlit as st
import datetime
import pandas as pd
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Quaddie Tracker", page_icon="🏇")

# 1. Connect to Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

def get_data():
    # Adding a random parameter helps force a fresh read from Google
    return conn.read(ttl=0) 

st.title("🏇 Shared Quaddie Tracker")

today_date = datetime.date.today().isoformat()

# Try to get data, if it fails (empty sheet), create a blank starting point
try:
    df = get_data()
except:
    df = pd.DataFrame(columns=["Date", "Track", "Leg1", "Leg2", "Leg3", "Leg4"])

# Filter for today's entries
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

# 3. The Input Form
if st.session_state.get('editing'):
    with st.form("quaddie_form"):
        track_val = "" if today_entry.empty else today_entry.iloc[-1]['Track']
        track = st.text_input("Track Name", value=track_val)
        
        c1, c2, c3, c4 = st.columns(4)
        l1 = c1.text_input("Leg 1", key="in1")
        l2 = c2.text_input("Leg 2", key="in2")
        l3 = c3.text_input("Leg 3", key="in3")
        l4 = c4.text_input("Leg 4", key="in4")
        
        if st.form_submit_button("Save to Cloud"):
            # Create the new row
            new_row = pd.DataFrame([{
                "Date": today_date, "Track": track,
                "Leg1": l1, "Leg2": l2, "Leg3": l3, "Leg4": l4
            }])
            
            # Add new row to existing data
            updated_df = pd.concat([df, new_row], ignore_index=True)
            
            # Overwrite the sheet with the updated list
            conn.update(data=updated_df)
            
            st.success("Saved! Refreshing...")
            st.session_state.editing = False
            st.rerun()
