import streamlit as st
import base64
import os
import pandas as pd
import random
import gspread
from google.oauth2.service_account import Credentials

# -------------------- Page Config --------------------
st.set_page_config(
    page_title="Engineering Personality Test | IEEE ZC",
    page_icon="🧩",
    layout="centered"
)

# -------------------- Google Sheets Connection --------------------
@st.cache_resource(ttl=60)
def get_google_sheet():
    """Connects to Google Sheets using Streamlit Secrets."""
    try:
        secrets = st.secrets["gcp_service_account"]
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        creds = Credentials.from_service_account_info(secrets, scopes=scopes)
        client = gspread.authorize(creds)
        
        sheet_url = st.secrets["private_sheet_url"]
        return client.open_by_url(sheet_url).sheet1
    except Exception as e:
        st.error(f"❌ Connection Error: {e}")
        return None

def load_data():
    """Fetches data using get_all_values."""
    sheet = get_google_sheet()
    col_names = ["Name", "Major", "Timestamp"]
    
    if sheet:
        try:
            raw_data = sheet.get_all_values()
            if not raw_data:
                return pd.DataFrame(columns=col_names)
            
            if raw_data[0] and raw_data[0][0] == "Name":
                raw_data = raw_data[1:]
            
            df = pd.DataFrame(raw_data, columns=col_names)
            return df
        except Exception as e:
            return pd.DataFrame(columns=col_names)
    return pd.DataFrame(columns=col_names)

def save_data(name, major):
    """Saves a new result to Google Sheets."""
    sheet = get_google_sheet()
    if sheet:
        try:
            timestamp = str(pd.Timestamp.now())
            sheet.append_row([name, major, timestamp])
        except Exception as e:
            st.error(f"Could not save data: {e}")

# -------------------- Helper to Load Local Image --------------------
def get_img_as_base64(file):
    try:
        with open(file, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except:
        return None

img_tag = ""
if os.path.exists("IEEE.jpg"):
    img_b64 = get_img_as_base64("IEEE.jpg")
    if img_b64:
        img_tag = f'<img src="data:image/jpeg;base64,{img_b64}" class="logo-img">'
else:
    img_tag = '<div style="text-align:center; font-size:40px; margin-bottom:10px;">IEEE ZC 🦅</div>'

# -------------------- 15 Personality Questions --------------------
# Logic:
# CIE = Connection/Social | ENV = Harmony/Nature | NANO = Detail/Precision
# REE = Energy/Efficiency | AERO = Freedom/Big Picture

raw_questions = [
    {
        "q": "1. Your friend is feeling down. How do you help?",
        "options": [
            {"text": "I talk it out with them. Communication fixes everything.", "type": "CIE"},
            {"text": "I take them for a walk outside to get some fresh air.", "type": "ENV"},
            {"text": "I analyze exactly what went wrong to find the root cause.", "type": "NANO"}
        ]
    },
    {
        "q": "2. You have to travel to a new city. You prefer:",
        "options": [
            {"text": "The fastest method possible. I hate waiting.", "type": "AERO"},
            {"text": "Something efficient that doesn't waste money or energy.", "type": "REE"},
            {"text": "Video calling instead. Why travel when we have the internet?", "type": "CIE"}
        ]
    },
    {
        "q": "3. You walk into a messy room. You immediately:",
        "options": [
            {"text": "Start organizing the small things perfectly into drawers.", "type": "NANO"},
            {"text": "Open the windows to let the bad air out.", "type": "ENV"},
            {"text": "Clean it as fast as possible so I can conserve my energy for later.", "type": "REE"}
        ]
    },
    {
        "q": "4. If you could have a superpower, it would be:",
        "options": [
            {"text": "Flight. I want to see the world from above.", "type": "AERO"},
            {"text": "Telepathy. I want to know what everyone is thinking.", "type": "CIE"},
            {"text": "Healing. I want to fix living things.", "type": "ENV"}
        ]
    },
    {
        "q": "5. What kind of games do you like to play?",
        "options": [
            {"text": "Open-world exploration games with no boundaries.", "type": "AERO"},
            {"text": "Strategy games where I manage resources and energy.", "type": "REE"},
            {"text": "Puzzle games that require extreme attention to detail.", "type": "NANO"}
        ]
    },
    {
        "q": "6. You are at a crowded party. You are:",
        "options": [
            {"text": "Introducing people to each other; I'm the connector.", "type": "CIE"},
            {"text": "Making sure the vibe isn't toxic and everyone is comfortable.", "type": "ENV"},
            {"text": "Noticing the tiny details in the decor that no one else sees.", "type": "NANO"}
        ]
    },
    {
        "q": "7. Your car breaks down in the middle of nowhere. You:",
        "options": [
            {"text": "Check the battery or fuel immediately.", "type": "REE"},
            {"text": "Check the GPS to see how far the destination is.", "type": "AERO"},
            {"text": "Check your phone signal to call for help.", "type": "CIE"}
        ]
    },
    {
        "q": "8. You receive a gift. You would love:",
        "options": [
            {"text": "A plant or something organic.", "type": "ENV"},
            {"text": "A Swiss watch with complex tiny gears.", "type": "NANO"},
            {"text": "A solar-powered power bank that never runs out.", "type": "REE"}
        ]
    },
    {
        "q": "9. What is your biggest fear?",
        "options": [
            {"text": "Being trapped in a small box.", "type": "AERO"},
            {"text": "Being misunderstood or ignored.", "type": "CIE"},
            {"text": "Watching something beautiful wither and die.", "type": "ENV"}
        ]
    },
    {
        "q": "10. You have a big problem to solve. You:",
        "options": [
            {"text": "Break it down into tiny little pieces.", "type": "NANO"},
            {"text": "Keep pushing through until the job is done.", "type": "REE"},
            {"text": "Take a step back to look at the big picture.", "type": "AERO"}
        ]
    },
    {
        "q": "11. Your communication style is:",
        "options": [
            {"text": "Constant updates. I like staying linked.", "type": "CIE"},
            {"text": "Calm and natural. No stress.", "type": "ENV"},
            {"text": "Precise and short. I don't like fluff.", "type": "NANO"}
        ]
    },
    {
        "q": "12. You wake up in the morning. The first thing you need is:",
        "options": [
            {"text": "Energy. Coffee or breakfast immediately.", "type": "REE"},
            {"text": "To get out the door. I hate staying still.", "type": "AERO"},
            {"text": "To check my notifications and messages.", "type": "CIE"}
        ]
    },
    {
        "q": "13. You are cooking dinner. You focus on:",
        "options": [
            {"text": "Using organic, healthy ingredients.", "type": "ENV"},
            {"text": "Measuring everything exactly (Molecular Gastronomy style).", "type": "NANO"},
            {"text": "Meal prepping efficiently for the whole week.", "type": "REE"}
        ]
    },
    {
        "q": "14. You look up at the sky. You think:",
        "options": [
            {"text": "I want to go up there.", "type": "AERO"},
            {"text": "I wonder how many invisible signals are passing through.", "type": "CIE"},
            {"text": "I hope it doesn't rain and ruin the garden.", "type": "ENV"}
        ]
    },
    {
        "q": "15. What is your ultimate goal in life?",
        "options": [
            {"text": "To achieve perfection in my craft.", "type": "NANO"},
            {"text": "To create a sustainable life.", "type": "REE"},
            {"text": "To be free.", "type": "AERO"}
        ]
    }
]

# -------------------- Session State & Randomization --------------------
if "submitted" not in st.session_state:
    st.session_state.submitted = False
if "user_name" not in st.session_state:
    st.session_state.user_name = ""

# Shuffle options ONCE per session
if "shuffled_questions" not in st.session_state:
    shuffled = []
    for item in raw_questions:
        q_copy = item.copy()
        q_copy["options"] = random.sample(item["options"], len(item["options"]))
        shuffled.append(q_copy)
    st.session_state.shuffled_questions = shuffled

# -------------------- Global Styling --------------------
st.markdown("""
<style>
    .stApp {
        background: radial-gradient(circle at 50% 10%, #0a192f 0%, #020c1b 100%);
        color: #ccd6f6;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .sticky-header-container {
        position: fixed; top: 0; left: 0; width: 100%; height: 60px;
        background: rgba(2, 12, 27, 0.95); backdrop-filter: blur(10px);
        z-index: 999999; border-bottom: 1px solid rgba(100, 255, 218, 0.2);
        display: flex; align-items: center; justify-content: center;
        box-shadow: 0 4px 20px rgba(0,0,0,0.5);
    }
    .header-text {
        color: #64ffda; font-weight: bold; font-size: 1.2rem; letter-spacing: 1px;
    }
    .block-container { padding-top: 80px !important; }
    h1, h2, h3 { color: #64ffda !important; text-shadow: 0 0 10px rgba(100, 255, 218, 0.3); }
    .logo-container { display: flex; justify-content: center; margin-bottom: 20px; }
    .logo-img {
        width: 160px; border-radius: 50%; animation: float 4s ease-in-out infinite;
        box-shadow: 0 0 20px rgba(100, 255, 218, 0.2);
    }
    @keyframes float {
        0% { transform: translateY(0px); } 50% { transform: translateY(-10px); } 100% { transform: translateY(0px); }
    }
    .question-box {
        background: rgba(17, 34, 64, 0.6); border-left: 4px solid #64ffda;
        border-radius: 8px; padding: 20px; margin-bottom: 15px;
        font-size: 1.1rem; font-weight: bold; color: #e6f1ff;
    }
    .stTextInput input {
        background-color: rgba(17, 34, 64, 0.8); color: #64ffda;
        border: 1px solid #64ffda; border-radius: 8px; text-align: center; font-size: 1.2rem;
    }
    .stRadio div[role="radiogroup"] > label {
        background: rgba(255,255,255,0.03); padding: 15px; border-radius: 10px;
        margin-bottom: 8px; border: 1px solid transparent; transition: all 0.2s; cursor: pointer;
    }
    .stRadio div[role="radiogroup"] > label:hover {
        background: rgba(100, 255, 218, 0.1); border-color: #64ffda; color: #64ffda !important;
    }
    div[data-testid="stFormSubmitButton"] button {
        background: transparent; color: #64ffda !important; border: 2px solid #64ffda;
        border-radius: 8px; padding: 10px 30px; font-weight: bold; transition: 0.3s; width: 100%;
    }
    div[data-testid="stFormSubmitButton"] button:hover {
        background: rgba(100, 255, 218, 0.1); box-shadow: 0 0 15px rgba(100, 255, 218, 0.3);
        transform: scale(1.02);
    }
    .stButton button { border-radius: 8px; font-weight: bold; }
    .winner-title { font-size: 3rem; font-weight: 800; color: #64ffda; text-align: center; margin-bottom: 10px; }
    .winner-desc { font-size: 1.2rem; color: #8892b0; max-width: 600px; margin: 0 auto; text-align: center; }
    .link-btn {
        display: block; width: fit-content; margin: 20px auto; background: #64ffda;
        color: #0a192f !important; padding: 12px 30px; border-radius: 5px;
        text-decoration: none; font-weight: bold; transition: 0.3s; text-align: center;
    }
    .link-btn:hover { transform: scale(1.05); box-shadow: 0 0 20px rgba(100, 255, 218, 0.5); }
    #MainMenu, footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# -------------------- Sticky Header --------------------
if not st.session_state.submitted:
    st.markdown("""
    <div class="sticky-header-container">
        <div class="header-text">IEEE ZC &nbsp;|&nbsp; ENGINEERING QUIZ</div>
    </div>
    """, unsafe_allow_html=True)

# -------------------- Main Content --------------------
main_placeholder = st.empty()

# 1. State: User Has NOT Submitted
if not st.session_state.submitted:
    with main_placeholder.container():
        st.markdown(f'<div class="logo-container">{img_tag}</div>', unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center;'>Which Engineering Major Are You?</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #8892b0; margin-bottom: 30px;'>📡 CIE? 🌍 ENV? 🔬 NANO? ⚡ REE? or 🚀 AERO?</p>", unsafe_allow_html=True)

        # --- STEP 1: ASK FOR NAME & SHOW LEADERBOARD ---
        if st.session_state.user_name == "":
            st.markdown("### First, tell us who you are:")
            name_input = st.text_input("Enter your full name")
            
            col1, col2, col3 = st.columns([1,1,1])
            with col2:
                if st.button("Start Quiz 🚀", use_container_width=True):
                    if name_input.strip() != "":
                        st.session_state.user_name = name_input
                        st.rerun()
                    else:
                        st.error("Please enter your name to proceed!")
            
            # --- LEADERBOARD AT START ---
            st.markdown("---")
            st.markdown("### 📊 Previous Responders")
            
            df = load_data()
            if not df.empty and "Major" in df.columns:
                counts = df["Major"].value_counts()
                st.bar_chart(counts, color="#64ffda")
                st.dataframe(df[["Name", "Major"]].tail(10).iloc[::-1], use_container_width=True, hide_index=True)
            else:
                st.caption("Be the first to answer!")

        # --- STEP 2: SHOW QUIZ FORM (Only if Name is set) ---
        else:
            st.info(f"Welcome, **{st.session_state.user_name}**! Let's find your path.")
            
            with st.form("quiz_form"):
                for i, q_data in enumerate(st.session_state.shuffled_questions):
                    st.markdown(f'<div class="question-box">{q_data["q"]}</div>', unsafe_allow_html=True)
                    option_texts = [opt["text"] for opt in q_data["options"]]
                    st.radio(label=f"q_{i}", options=option_texts, index=None, key=f"q_{i}", label_visibility="collapsed")
                    st.write("") 

                st.markdown("---")
                submitted = st.form_submit_button("✨ Reveal My Destiny ✨")
                
                if submitted:
                    answered_count = 0
                    current_questions = st.session_state.shuffled_questions
                    for i in range(len(current_questions)):
                        if st.session_state.get(f"q_{i}"):
                            answered_count += 1
                    
                    if answered_count < len(current_questions):
                        st.error(f"⚠️ You missed some questions! Please answer all {len(current_questions)}. (Answered: {answered_count})")
                    else:
                        st.session_state.submitted = True
                        st.rerun()

# 2. State: User Submitted (RESULT VIEW)
else:
    with main_placeholder.container():
        st.markdown(f'<div class="logo-container">{img_tag}</div>', unsafe_allow_html=True)

        scores = {"CIE": 0, "ENV": 0, "NANO": 0, "REE": 0, "AERO": 0}
        current_questions = st.session_state.shuffled_questions
        for i, q_data in enumerate(current_questions):
            user_answer_text = st.session_state.get(f"q_{i}")
            if user_answer_text:
                for opt in q_data["options"]:
                    if opt["text"] == user_answer_text:
                        scores[opt["type"]] += 1
                        break

        max_score = max(scores.values())
        top_matches = [k for k, v in scores.items() if v == max_score]
        winner = top_matches[0]
        
        if "saved" not in st.session_state:
            save_data(st.session_state.user_name, winner)
            st.session_state.saved = True

        st.markdown('<div class="result-text">', unsafe_allow_html=True)
        
        if winner == "CIE":
            st.markdown('<div class="winner-title">📡 CIE</div>', unsafe_allow_html=True)
            st.markdown(f"### {st.session_state.user_name}, You are a CIE Engineer!")
            st.markdown("""<div class="winner-desc">You are the <b>Connector</b>.<br>You thrive on patterns, signals, and linking the unseen. You don't just see the world; you see the web that holds it together.</div>""", unsafe_allow_html=True)

        elif winner == "ENV":
            st.markdown('<div class="winner-title">🌍 ENV</div>', unsafe_allow_html=True)
            st.markdown(f"### {st.session_state.user_name}, You are an Environmental Engineer!")
            st.markdown("""<div class="winner-desc">You are the <b>Guardian</b>.<br>You are driven by balance, life, and sustainability. You see the fragility of our home and have the will to protect it.</div>""", unsafe_allow_html=True)

        elif winner == "NANO":
            st.markdown('<div class="winner-title">🔬 NANO</div>', unsafe_allow_html=True)
            st.markdown(f"### {st.session_state.user_name}, You are a Nanoengineer!")
            st.markdown("""<div class="winner-desc">You are the <b>Architect</b>.<br>You look deeper than anyone else. You understand that the biggest changes come from the smallest details.</div>""", unsafe_allow_html=True)

        elif winner == "REE":
            st.markdown('<div class="winner-title">⚡ REE</div>', unsafe_allow_html=True)
            st.markdown(f"### {st.session_state.user_name}, You are a Renewable Energy Engineer!")
            st.markdown("""<div class="winner-desc">You are the <b>Innovator</b>.<br>You are drawn to flow, power, and transformation. You believe in a future that fuels itself without destruction.</div>""", unsafe_allow_html=True)

        elif winner == "AERO":
            st.markdown('<div class="winner-title">🚀 AERO</div>', unsafe_allow_html=True)
            st.markdown(f"### {st.session_state.user_name}, You are an Aerospace Engineer!")
            st.markdown("""<div class="winner-desc">You are the <b>Explorer</b>.<br>You refuse to be bound by gravity. You look up at the horizon and see a challenge, not a limit.</div>""", unsafe_allow_html=True)
            
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("""<br><a href="https://forms.gle/DUW3KsYfNpg53ahK6" target="_blank" class="link-btn">📝 Sign Up For Your Major Introduction Session Here</a>""", unsafe_allow_html=True)
        
        if st.button("🔄 Play Again", use_container_width=True):
            st.session_state.submitted = False
            st.session_state.user_name = ""
            if "saved" in st.session_state: del st.session_state.saved
            if "shuffled_questions" in st.session_state: del st.session_state.shuffled_questions
            for key in list(st.session_state.keys()):
                if key.startswith("q_"): del st.session_state.key
            st.rerun()