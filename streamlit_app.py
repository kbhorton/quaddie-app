import streamlit as st
import datetime
import pandas as pd
import pytz # This handles the timezone

# 1. Helper Functions
def deactivate_editing():
    st.session_state.editing = False
    st.cache_data.clear()

@st.cache_data(ttl=10)
def get_data(csv_url):
    timestamp = datetime.date.today().isoformat()
    return pd.read_csv(f"{csv_url}&cachebust={timestamp}")

st.set_page_config(page_title="Quaddie Tracker", page_icon="🏇")
st.title("🏇 Shared Quaddie Tracker")

# 2. Setup Connection
try:
    sheet_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
    sheet_id = sheet_url.split("/d/")[1].split("/")[0]
    csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    df = get_data(csv_url)
except:
    st.error("Connection Error. Check your Secret URL.")
    st.stop()

# 3. FIX: Australian Timezone Logic
sydney_tz = pytz.timezone('Australia/Sydney')
now_sydney = datetime.datetime.now(sydney_tz)
today_date = now_sydney.strftime('%Y-%m-%d') # Correct AU Date

# 4. Filter Logic
df['Date'] = df['Date'].astype(str)
today_entry = df[df['Date'] == today_date]

# 5. Display Logic
if not today_entry.empty and not st.session_state.get('editing'):
    row = today_entry.iloc[-1]
    st.success(f"✅ Picks Active for {row['Track']} ({today_date})")
    
    cols = st.columns(4)
    for i in range(4):
        with cols[i]:
            st.metric(f"Leg {i+1}", str(row[f"Leg{i+1}"]))
    
    if st.button("Edit / Update Picks"):
        st.session_state.editing = True
else:
    st.info(f"Looking for picks for today (Sydney Time): {today_date}")
    st.link_button("Open Google Sheet", sheet_url)
    st.button("I've finished entering picks", on_click=deactivate_editing, key="final_v3")

    with st.expander("Debug: Current Sheet Data"):
        st.write(df)
