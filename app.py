import streamlit as st
import openai
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- 1. CONFIG & STYLING ---
st.set_page_config(page_title="Global Lifestyle AI", page_icon="🌍", layout="centered")

# Custom CSS for the WhatsApp button and cleaner look
st.markdown("""
<style>
    div.stButton > button:first-child {
        background-color: #25D366;
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
        # Just return False if it fails, don't crash the app
        return False

# --- 2. THE APP HEADER ---
# (Image removed as requested)

st.title("🌍 The Global Lifestyle Architect")
st.write("Design your ideal life abroad. Whether you are looking for cheaper living, better quality of life, or a new adventure, use AI to find your perfect base.")
st.markdown("---")

# --- 3. THE FORM ---
with st.form("travel_form"):
    
    col1, col2 = st.columns(2)
    
    with col1:
        budget = st.select_slider("💰 Monthly Budget (USD)", options=["<$1k", "$1k-$2k", "$2k-$3k", "$3k-$5k", "$5k+"])
    
    with col2:
        region = st.multiselect("🗺️ Preferred Regions", ["Latin America", "Europe", "SE Asia", "Africa", "No Preference"])
    
    st.write("")
    vibe = st.text_area("✨ What is your vision?", placeholder="e.g. I need a modern apartment, strong crypto community, and proximity to nature.")
    
    st.write("")
    st.markdown("### 📱 Unlock Your Strategy")
    phone = st.text_input("WhatsApp Number (with Country Code)", placeholder="e.g. +1 305-555-0123")
    
    st.caption("By submitting your number, you agree that we may contact you via WhatsApp with travel tips and guides.")
    
    # Submit Button
    submitted = st.form_submit_button("Find My Global Base 🚀")

# --- 4. THE LOGIC ---
if submitted:
    if not phone:
        st.error("Please enter your WhatsApp number to receive the guide!")
    elif len(phone) < 7:
        st.warning("Please make sure to include your country code (e.g. +1 for USA, +44 for UK)")
    elif not st.secrets.get("openai_key"):
        st.error("System Error: API Key missing. Check Streamlit Secrets.")
    else:
        # Save to Google Sheet
        save_lead_to_sheet(phone, budget, region, vibe)
        
        # Run AI
        with st.spinner("Analyzing cost of living, safety data, and lifestyle matches..."):
            client = openai.Client(api_key=st.secrets["openai_key"])
            
            # --- PROMPT START ---
            prompt = f"""
            Act as a high-net-worth relocation consultant and security expert.
            User Input: Budget {budget}, Regions {region}, Vision {vibe}.
            
            Task: Recommend 2 specific cities for this entrepreneur to globalize their lifestyle.
            
            CRITICAL SAFETY PROTOCOL:
            1. If you recommend ANY city in Colombia (especially Medellin/Bogota), you MUST include a warning block starting with "⚠️ SECURITY WARNING:" explaining that Americans/Westerners are currently being targeted and dating apps can be dangerous. Be realistic about crime rates.
            2. For all other cities, include a "Safety Score" (1-10) and a brief mention of specific risks (pickpockets, scams, etc).
            
            Format output as Markdown:
            
            ## 🌴 City Name, Country
            **The Vibe:** [One sentence summary]
            
            | Feature | Rating/Cost |
            | :--- | :--- |
            | 💸 Est. Cost | [Amount] |
            | 🛡️ Safety Score | [X/10] |
            | 🚀 Best for | [Key Benefit] |
            
            **The Strategy:** [Why this fits their lifestyle vision]
            
            (If Colombia: Insert WARNING text here)
            
            ---
            (Repeat for City 2)
            
            End with a professional, encouraging closing statement.
            """
            # --- PROMPT END ---
            
            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}]
                )
                
                # Display results
                st.success("Analysis Complete. Here are your top recommendations:")
                st.markdown(response.choices[0].message.content)
                
                # Next Step
                with st.expander("🎁 Bonus: Download the full Travel Hacking Playbook"):
                    st.write("Get the PDF guide that explains exactly how to book the flights to these cities for free.")
                    # REPLACE THIS LINK BELOW WITH YOUR REAL GOOGLE DOC LINK
                    st.markdown("[👉 Download Playbook Here](https://docs.google.com/)")
                    
            except Exception as e:
                st.error(f"AI Error: {e}")
