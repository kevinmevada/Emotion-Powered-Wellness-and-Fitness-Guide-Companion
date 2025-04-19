import streamlit as st
from auth import login_page, signup_page, logout_button
from workout_recommendation import workout_recommendation, duration_based_workouts, workout_history, progress_dashboard
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Define predefined themes with safe defaults
THEMES = {
    "Cyberpunk": {
        "primary_color": "#00C6FF",
        "secondary_color": "#0072FF",
        "font_style": "Poppins",
        "background": "radial-gradient(circle at top left, #0A0A0A, #141414, #1E1E1E)"
    },
    "Neon Glow": {
        "primary_color": "#FF00FF",
        "secondary_color": "#00FFFF",
        "font_style": "Roboto",
        "background": "radial-gradient(circle at top left, #1E1E1E, #2E2E2E, #3E3E3E)"
    },
    "Sunset Vibes": {
        "primary_color": "#FF5733",
        "secondary_color": "#FFC300",
        "font_style": "Montserrat",
        "background": "radial-gradient(circle at top left, #2C3E50, #4A6FA5, #8E9AAF)"
    },
    "Forest Green": {
        "primary_color": "#228B22",
        "secondary_color": "#32CD32",
        "font_style": "Open Sans",
        "background": "radial-gradient(circle at top left, #0A2E0A, #1A4A1A, #2A6A2A)"
    }
}

# Available web-safe fonts
FONT_OPTIONS = [
    "Poppins", "Roboto", "Montserrat", "Open Sans", "Arial", "Helvetica", "Times New Roman", "Courier New"
]

# Function to validate hex color
def is_valid_hex_color(color):
    return isinstance(color, str) and len(color) == 7 and color.startswith("#") and all(c in "0123456789ABCDEFabcdef" for c in color[1:])

# Function to apply custom theme with fallback
def apply_custom_theme(theme):
    primary_color = theme.get("primary_color", "#00C6FF")
    secondary_color = theme.get("secondary_color", "#0072FF")
    font_style = theme.get("font_style", "Poppins") if theme.get("font_style") in FONT_OPTIONS else "Poppins"
    background = theme.get("background", "radial-gradient(circle at top left, #0A0A0A, #141414, #1E1E1E)")
    
    if not is_valid_hex_color(primary_color):
        primary_color = "#00C6FF"
    if not is_valid_hex_color(secondary_color):
        secondary_color = "#0072FF"
    
    try:
        st.markdown(f"""
            <style>
            .stApp {{
                background: {background};
                color: #E0E0E0 !important;
                font-family: '{font_style}', sans-serif;
            }}
            .css-1d391kg {{
                background: rgba(20, 20, 20, 0.6);
                color: #FFFFFF;
                padding: 25px;
                border-radius: 14px;
                box-shadow: inset 0 0 15px rgba(0, 255, 255, 0.15);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(0, 255, 255, 0.3);
            }}
            .stButton>button {{
                background: linear-gradient(135deg, {primary_color}, {secondary_color});
                color: white;
                border: none;
                border-radius: 10px;
                padding: 14px 24px;
                font-size: 17px;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 1.2px;
                transition: all 0.3s ease-in-out;
                box-shadow: 0px 0px 8px rgba(0, 198, 255, 0.4);
            }}
            .stButton>button:hover {{
                background: linear-gradient(135deg, {secondary_color}, {primary_color});
                box-shadow: 0px 0px 15px rgba(0, 198, 255, 0.8);
                transform: scale(1.05);
            }}
            h1, h2, h3, h4, h5, h6 {{
                color: {primary_color} !important;
                text-transform: uppercase;
                letter-spacing: 2px;
                font-weight: 700;
            }}
            .stCard, .workout-card {{
                background: rgba(255, 255, 255, 0.1);
                padding: 20px;
                border-radius: 12px;
                box-shadow: inset 0 0 10px rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(8px);
                border: 1px solid rgba(255, 255, 255, 0.2);
                transition: all 0.3s ease-in-out;
            }}
            .stCard:hover, .workout-card:hover {{
                transform: scale(1.05);
                box-shadow: 0px 0px 20px rgba(0, 198, 255, 0.6);
            }}
            .stTextInput>div>div>input {{
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(0, 255, 255, 0.3);
                color: white;
                border-radius: 8px;
                padding: 12px;
                font-size: 16px;
                transition: all 0.3s ease-in-out;
            }}
            .stTextInput>div>div>input:focus {{
                box-shadow: 0px 0px 8px rgba(0, 198, 255, 0.6);
                border: 1px solid rgba(0, 198, 255, 0.6);
            }}
            .stColorPicker {{
                background: rgba(255, 255, 255, 0.05);
                border-radius: 8px;
                padding: 10px;
            }}
            .footer {{
                text-align: center;
                padding: 20px;
                margin-top: 50px;
                color: {primary_color};
            }}
            .footer a {{
                color: {primary_color};
                text-decoration: none;
                margin: 0 10px;
            }}
            .footer a:hover {{
                text-decoration: underline;
            }}
            @media (max-width: 600px) {{
                .stButton>button {{
                    padding: 10px 16px;
                    font-size: 14px;
                }}
                .stCard, .workout-card {{
                    padding: 15px;
                }}
            }}
            </style>
            """, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Failed to apply theme: {e}")
        apply_custom_theme(THEMES["Cyberpunk"])

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = None
if 'email' not in st.session_state:
    st.session_state['email'] = None
if 'emotions_detected' not in st.session_state:
    st.session_state['emotions_detected'] = False
if 'selected_theme' not in st.session_state:
    st.session_state['selected_theme'] = "Cyberpunk"
if 'user_id' not in st.session_state:
    st.session_state['user_id'] = None
if 'custom_theme' not in st.session_state:
    st.session_state['custom_theme'] = None

# Apply the selected theme with fallback
try:
    if st.session_state['selected_theme'] == "Custom" and st.session_state['custom_theme']:
        apply_custom_theme(st.session_state['custom_theme'])
    else:
        apply_custom_theme(THEMES[st.session_state['selected_theme']])
except Exception:
    st.session_state['selected_theme'] = "Cyberpunk"
    apply_custom_theme(THEMES["Cyberpunk"])

# Sidebar for navigation
st.sidebar.title("Navigation")
if st.session_state.get('logged_in'):
    st.sidebar.markdown(f"<div class='card'><h3>Welcome, {st.session_state['username']}!</h3></div>", unsafe_allow_html=True)
    logout_button()
    choice = st.sidebar.radio("Choose an option", [
        "Emotion-Based Workouts",
        "Duration-Based Workouts",
        "Workout History",
        "Progress Dashboard",
        "Profile",
        "Customize Theme"
    ])
else:
    choice = st.sidebar.radio("Choose an option", ["Login", "Sign Up"])

# Pages
if choice == "Login":
    login_page()
elif choice == "Sign Up":
    signup_page()
elif choice == "Emotion-Based Workouts" and st.session_state.get('logged_in'):
    workout_recommendation()
elif choice == "Duration-Based Workouts" and st.session_state.get('logged_in'):
    duration_based_workouts()
elif choice == "Workout History" and st.session_state.get('logged_in'):
    workout_history()
elif choice == "Progress Dashboard" and st.session_state.get('logged_in'):
    progress_dashboard()
elif choice == "Profile" and st.session_state.get('logged_in'):
    st.title("Profile")
    st.markdown(f"""
        <div class='card'>
            <h3>Your Profile</h3>
            <p>Username: {st.session_state['username']}</p>
            <p>Email: {st.session_state['email']}</p>
        </div>
    """, unsafe_allow_html=True)
elif choice == "Customize Theme" and st.session_state.get('logged_in'):
    st.title("Customize Theme")
    
    theme_options = list(THEMES.keys()) + ["Custom"]
    selected_theme = st.selectbox("Choose a theme", theme_options, index=theme_options.index(st.session_state['selected_theme']))
    
    if selected_theme == "Custom":
        st.markdown("<h3>Create Your Custom Theme</h3>", unsafe_allow_html=True)
        with st.form(key="custom_theme_form"):
            primary_color = st.color_picker("Primary Color", value="#00C6FF", key="primary_color")
            secondary_color = st.color_picker("Secondary Color", value="#0072FF", key="secondary_color")
            font_style = st.selectbox("Font Style", FONT_OPTIONS, index=FONT_OPTIONS.index("Poppins"), key="font_style")
            background_color = st.color_picker("Background Color", value="#1E1E1E", key="background_color")
            submit_button = st.form_submit_button("Save and Apply Custom Theme")
            
            if submit_button:
                if not is_valid_hex_color(primary_color) or not is_valid_hex_color(secondary_color) or not is_valid_hex_color(background_color):
                    st.error("Invalid color format. Please use the color picker.")
                elif font_style not in FONT_OPTIONS:
                    st.error("Invalid font selected.")
                else:
                    custom_theme = {
                        "primary_color": primary_color,
                        "secondary_color": secondary_color,
                        "font_style": font_style,
                        "background": background_color
                    }
                    st.session_state['custom_theme'] = custom_theme
                    st.session_state['selected_theme'] = "Custom"
                    try:
                        apply_custom_theme(custom_theme)
                        st.success("Custom theme applied successfully!")
                    except Exception as e:
                        st.error(f"Failed to apply custom theme: {e}")
                        st.session_state['selected_theme'] = "Cyberpunk"
                        apply_custom_theme(THEMES["Cyberpunk"])
    else:
        if st.button("Apply Theme", key="apply_predefined_theme"):
            st.session_state['selected_theme'] = selected_theme
            try:
                apply_custom_theme(THEMES[selected_theme])
                st.success(f"Theme updated to {selected_theme}!")
            except Exception as e:
                st.error(f"Failed to apply theme: {e}")
                st.session_state['selected_theme'] = "Cyberpunk"
                apply_custom_theme(THEMES["Cyberpunk"])

# Footer
st.markdown("""
    <div class="footer">
        <p>Made with ❤️ by Kevin Mevada </p>
        <p>
            <a href="https://github.com/kevinmevada" target="_blank">GitHub</a> |
            <a href="https://linkedin.com/in/kevinmevada" target="_blank">LinkedIn</a>
        </p>
    </div>
""", unsafe_allow_html=True)