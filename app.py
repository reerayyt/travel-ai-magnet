import streamlit as st
import openai
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- 1. CONFIG & STYLING ---
st.set_page_config(page_title="Global Lifestyle Strategy", page_icon="📈", layout="centered")

# Custom CSS: Green "WhatsApp" button + Cleaner UI + Metrics styling
st.markdown("""
<style>
    div.stButton > button:first-child {
        background-color: #25D366;
        color: white;
        font-size: 20px;
        font-weight: bold;
        border-radius: 8px;
        width: 100%;
        border: none;
        padding: 10px;
    }
    div.stButton > button:first-child:hover {
        background-color: #128C7E;
        color: white;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #25D366;
        margin-bottom: 10px;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Function to connect to Google Sheets
def save_lead_to_sheet(phone, income_source, current_burn, budget, region, vibe):
    try:
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        sheet = client.open("Travel Leads").sheet1
        # Saving all data points
        sheet.append_row([phone, income_source, current_burn, budget, str(region), vibe])
        return True
    except Exception as e:
        return False

# --- 2. THE APP HEADER ---
st.title("🚀 The Global Lifestyle Architect")
st.markdown("""
**Scale your runway. Upgrade your network.**
Use AI to find the perfect base where you can lower your burn rate, avoid isolation, and connect with other high-level earners.
""")
st.markdown("---")

# --- 3. THE FORM ---
with st.form("travel_form"):
    
    st.markdown("### 1. The Business Case")
    col1, col2 = st.columns(2)
    
    with col1:
        # ICP Dropdown
        income_source = st.selectbox(
            "How do you make money?", 
            ["Agency / Freelance", "Crypto / Trading", "Content Creator", "Software / SaaS", "E-Commerce", "Remote Job"]
        )
    
    with col2:
        # The Anchor for Savings Calculation
        current_burn = st.number_input("Current Monthly Expenses (Home)", min_value=1000, value=4000, step=500, help="Total cost to live in your current city (Rent, Food, etc).")

    st.markdown("### 2. The Lifestyle Design")
    col3, col4 = st.columns(2)
    
    with col3:
        budget = st.select_slider("Target Monthly Budget (Abroad)", options=["<$1.5k", "$1.5k-$2.5k", "$2.5k-$4k", "$4k+"])
    
    with col4:
        region = st.multiselect("Region Preference", ["Latin America", "Europe", "SE Asia", "Africa", "No Preference"])
    
    st.write("")
    vibe = st.text_area("What is your vision?", placeholder="e.g. I need a strong crypto community, modern gym, and EST time zone alignment.")
    
    st.markdown("### 3. Unlock Your Roadmap")
    phone = st.text_input("WhatsApp Number (with Country Code)", placeholder="e.g. +1 305-555-0123")
    
    st.caption("🔒 We'll send the full detailed breakdown to your WhatsApp.")
    
    # Submit Button
    submitted = st.form_submit_button("Generate My Runway Strategy 💸")

# --- 4. THE LOGIC ---
if submitted:
    if not phone:
        st.error("Please enter your WhatsApp number to receive the guide!")
    elif len(phone) < 7:
        st.warning("Please include your country code (e.g. +1).")
    elif not st.secrets.get("openai_key"):
        st.error("System Error: API Key missing.")
    else:
        # Save to Google Sheet
        save_lead_to_sheet(phone, income_source, current_burn, budget, region, vibe)
        
        # Run AI
        with st.spinner("Calculating runway extension and analyzing network density..."):
            client = openai.Client(api_key=st.secrets["openai_key"])
            
            # --- HIGH-VALUE ICP PROMPT ---
            prompt = f"""
            Act as a business strategist and relocation expert for a high-net-worth individual.
            
            USER PROFILE:
            - Income Source: {income_source} (Tailor networking advice to this industry)
            - Current Burn Rate: ${current_burn}/month (Use this to calculate savings)
            - Target Budget: {budget}
            - Vision: {vibe}
            - Region: {region}
            
            TASK:
            Recommend 2 specific cities that optimize their runway and network.
            
            CRITICAL SAFETY PROTOCOL:
            If recommending Colombia (Medellin/Bogota), insert a bold "⚠️ SECURITY WARNING" about current targeting of tourists/Americans. Be realistic.
            
            OUTPUT FORMAT (Markdown):
            
            ## 📍 City 1: [City, Country]
            
            **💸 The Runway Calculator:**
            * Est. Cost of Living: [Amount]
            * **Monthly Savings:** [${current_burn} - Est Cost]
            * **Annual Capital Unlocked:** [Multiply Monthly Savings by 12] (Reinvest this into your {income_source} business)
            
            **🤝 The Network Protocol (Avoid Isolation):**
            * **Earner Density Score:** [1-10 Score of how many online entrepreneurs are here]
            * **Where to Live:** [Specific Neighborhood] (Best for avoiding isolation)
            * **The "Day 1" Action:** "Go to [Specific Coworking/Cafe] on your first day to meet other [Income Source] pros."
            
            **🛡️ Safety & Reality:**
            * Safety Score: [X/10]
            * The "Real Talk" warning: [Honest downsides]
            
            ---
            (Repeat for City 2)
            
            **🚀 Strategist's Note:**
            End with a punchy, motivating closing about taking action.
            """
            # --- PROMPT END ---
            
            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}]
                )
                
                # Display results
                st.success("Strategy Generated. Here is your blueprint:")
                st.markdown(response.choices[0].message.content)
                
                # Next Step CTA
                with st.expander("🎁 Bonus: Get the 'Zero-to-Launch' Travel Playbook"):
                    st.write("Don't figure it out alone. Download the step-by-step guide to booking your first flight for free and setting up your base.")
                    # REPLACE WITH YOUR REAL LINK
                    st.markdown("[👉 Download Playbook Here](https://docs.google.com/)")
                    
            except Exception as e:
                st.error(f"AI Error: {e}")
