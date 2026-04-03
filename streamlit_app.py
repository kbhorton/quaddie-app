import streamlit as st
import datetime
import pandas as pd

# 1. Helper Functions
def deactivate_editing():
    st.session_state.editing = False
    # Clear the cache to ensure we get the newest data from Google
    st.cache_data.clear()

@st.cache_data(ttl=10) # Cache data for only 10 seconds
def get_data(csv_url):
    # Add a timestamp to bypass Google's cache
    timestamp = datetime.datetime.now().timestamp()
    return pd.read_csv(f"{csv_url}&cachebust={timestamp}")

st.set_page_config(page_title="Quaddie Tracker", page_icon="🏇")
st.title("🏇 Shared Quaddie Tracker")

# 2. Setup Connection
try:
    sheet_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
    sheet_id = sheet_url.split("/d/")[1].split("/")[0]
    csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    df = get_data(csv_url)
except Exception as e:
    st.error("Connection Error. Check your Secret URL and Sheet Headers.")
    st.stop()

# 3. Date Logic
today_date = datetime.date.today().isoformat()
# Ensure the Date column in your sheet is being read as a string for comparison
df['Date'] = df['Date'].astype(str)
today_entry = df[df['Date'] == today_date]

# 4. Display Logic
if not today_entry.empty and not st.session_state.get('editing'):
    row = today_entry.iloc[-1]
    st.success(f"✅ Picks Active for {row['Track']}")
    
    cols = st.columns(4)
    for i in range(4):
        with cols[i]:
            st.metric(f"Leg {i+1}", str(row[f"Leg{i+1}"]))
    
    if st.button("Edit / Update Picks"):
        st.session_state.editing = True
    
    if st.button("🔄 Force Refresh Data"):
        st.cache_data.clear()
        st.rerun()

else:
    # 5. Editor View
    st.info(f"Looking for picks for today: {today_date}")
    st.warning("⚠️ Manual Step Required")
    st.write("1. Open your sheet and add a row for today.")
    st.link_button("Open Google Sheet", sheet_url)
    
    st.write("2. Once saved in Google, click the button below:")
    st.button("I've finished entering picks", on_click=deactivate_editing, key="final_btn")

    # Debugging Section (Only shows if no picks found)
    if today_entry.empty:
        with st.expander("See what the app currently sees in your sheet"):
            st.write(df)
