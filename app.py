import streamlit as st
import openai
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- 1. CONFIG & STYLING ---
st.set_page_config(page_title="Nomad Matchmaker", page_icon="✈️", layout="centered")

# Custom CSS for the button and cleaner look
st.markdown("""
<style>
    div.stButton > button:first-child {
        background-color: #25D366; /* WhatsApp Green color */
        color: white;
        font-size: 20px;
        border-radius: 10px;
        width: 100%;
        border: none;
    }
    div.stButton > button:first-child:hover {
        background-color: #128C7E;
        color: white;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Function to connect to Google Sheets
def save_lead_to_sheet(phone, budget, region, vibe):
    try:
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        sheet = client.open("Travel Leads").sheet1
        # Saving Phone, Budget, Region, Vibe
        sheet.append_row([phone, budget, str(region), vibe])
        return True
    except Exception as e:
        return False

# --- 2. THE APP HEADER ---
st.image("https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?q=80&w=2021&auto=format&fit=crop", use_container_width=True)

st.title("✈️ The Nomad Matchmaker")
st.write("Stop guessing where to go next. Tell us your vibe, and our AI will build your perfect travel profile.")
st.markdown("---")

# --- 3. THE FORM ---
with st.form("travel_form"):
    
    col1, col2 = st.columns(2)
    
    with col1:
        budget = st.select_slider("💰 Monthly Budget (USD)", options=["<$1k", "$1k-$2k", "$2k-$3k", "$3k-$5k", "$5k+"])
    
    with col2:
        region = st.multiselect("🗺️ Preferred Regions", ["Latin America", "Europe", "SE Asia", "Africa", "No Preference"])
    
    st.write("")
    vibe = st.text_area("✨ What is your vibe?", placeholder="e.g. I need fast wifi, surf breaks, and good coffee. Not too crowded.")
    
    st.write("")
    st.markdown("### 📱 Unlock Your Strategy")
    phone = st.text_input("WhatsApp Number (with Country Code)", placeholder="e.g. +1 305-555-0123")
    
    st.caption("By submitting your number, you agree that we may contact you via WhatsApp with travel tips and guides.")
    
    # Submit Button
    submitted = st.form_submit_button("Find My Perfect City 🚀")

# --- 4. THE LOGIC ---
if submitted:
    if not phone:
        st.error("Please enter your WhatsApp number to receive the guide!")
    elif len(phone) < 7:
        st.warning("Please make sure to include your country code (e.g. +1 for USA, +44 for UK)")
    elif not st.secrets.get("openai_key"):
        st.error("System Error: API Key missing.")
    else:
        # Save to Google Sheet
        save_lead_to_sheet(phone, budget, region, vibe)
        
        # Run AI
        with st.spinner("Analyzing crime rates, wifi speeds, and cost of living..."):
            client = openai.Client(api_key=st.secrets["openai_key"])
            
            # --- UPDATED PROMPT WITH SAFETY PROTOCOL ---
            prompt = f"""
            Act as a veteran digital nomad and security expert.
            User Input: Budget {budget}, Regions {region}, Vibe {vibe}.
            
            Task: Recommend 2 specific cities.
            
            CRITICAL SAFETY PROTOCOL:
            1. If you recommend ANY city in Colombia (especially Medellin/Bogota), you MUST include a warning block starting with "⚠️ SECURITY WARNING:" explaining that Americans/tourists are currently being targeted and dating apps can be dangerous. Be
