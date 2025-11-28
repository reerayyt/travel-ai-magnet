import streamlit as st
import openai
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Travel Strategy Generator", page_icon="🌎")

# Function to connect to Google Sheets
def save_email_to_sheet(email, budget, region, vibe):
    try:
        # Load credentials from Streamlit Secrets
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        # Create a dictionary from the secrets
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        
        # Open the sheet
        sheet = client.open("Travel Leads").sheet1
        sheet.append_row([email, budget, str(region), vibe])
        return True
    except Exception as e:
        st.error(f"Database Error: {e}")
        return False

# --- 2. THE APP DESIGN ---
st.title("🌎 AI Travel Strategy Generator")
st.markdown("### Find your next home base based on your vibe.")

with st.form("travel_form"):
    budget = st.select_slider("Monthly Budget (USD)", options=["$800-$1500", "$1500-$2500", "$2500-$4000", "$4000+"])
    region = st.multiselect("Preferred Regions", ["Latin America", "Europe", "SE Asia", "Africa/Middle East", "Anywhere"])
    vibe = st.text_area("Describe your perfect day (e.g., 'Surfing in the morning, fast wifi for work, party at night')")
    email = st.text_input("Where should we send the full guide? (Email)")
    
    submitted = st.form_submit_button("Generate My Strategy ✨")

# --- 3. THE LOGIC ---
if submitted:
    if not email:
        st.warning("Please enter your email to unlock the results.")
    elif not st.secrets.get("openai_key"):
        st.error("API Key missing. Please set it in Streamlit Secrets.")
    else:
        # Save to Google Sheet
        with st.spinner("Saving your preferences..."):
            save_success = save_email_to_sheet(email, budget, region, vibe)
        
        if save_success:
            # Run AI
            client = openai.Client(api_key=st.secrets["openai_key"])
            prompt = f"""
            User is an entrepreneur looking to travel/live abroad.
            Budget: {budget}
            Regions: {region}
            Vibe: {vibe}
            
            Recommend 2 specific cities. For each, give:
            1. City, Country
            2. "Why it works for you" (1-2 sentences)
            3. Estimated Cost of Living
            4. One hidden gem spot (cafe/coworking/nature)
            
            Keep it punchy, exciting, and formatted with markdown.
            """
            
            with st.spinner("Analyzing global data..."):
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}]
                )
                st.success("Strategy Generated!")
                st.markdown("---")
                st.markdown(response.choices[0].message.content)
                st.markdown("---")
                st.info("✅ We have added you to our VIP list. Check your email later for the full Playbook!")
