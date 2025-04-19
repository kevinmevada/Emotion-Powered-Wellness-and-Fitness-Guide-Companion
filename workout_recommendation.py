import numpy as np
import streamlit as st
import cv2
import pandas as pd
from collections import Counter
from deepface import DeepFace
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv
import time
from database import save_workout_plan, get_workout_plans, save_progress, get_progress

# Load environment variables
load_dotenv()
SENDER_EMAIL = os.getenv('SMTP_EMAIL')
SENDER_PASSWORD = os.getenv('SMTP_PASSWORD')

# Load workout dataset
@st.cache_data
def load_workout_data():
    try:
        df = pd.read_csv("mood_based_workouts_updated.csv")  # Ensure file exists or provide path
        df['type'] = df['Sets']
        df['name'] = df['Exercise']
        df['link'] = df['Video_Link']
        df['duration'] = df.apply(lambda row: (
            5 if any(x in row['name'].lower() for x in ['sprint', 'hiit', 'battle rope', 'rowing'])
            else 2 if any(x in row['name'].lower() for x in ['plank', 'side plank']) or 'sec' in row['type']
            else 3
        ), axis=1)
        return df[['name', 'type', 'link', 'duration']]
    except FileNotFoundError:
        st.error("Workout dataset not found. Please ensure 'mood_based_workouts_updated.csv' exists.")
        return pd.DataFrame()

df = load_workout_data()
if df.empty:
    st.stop()

# Function to send email
def send_email(to_email, subject, content):
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(content, 'html'))
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, to_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        st.error(f"Failed to send email: {str(e)}")
        return False

# Colorful, professional email template
def generate_email_template(subject, username, plan_id, workouts, duration_info=None, emotions=None):
    # Theme settings
    primary_color = '#C0392B'  # Vibrant red
    secondary_color = '#000000'  # Pure black
    accent_color = '#FFFFFF'  # White
    background_color = '#1C2526'  # Dark charcoal
    font_heading = 'Poppins'
    font_body = 'Roboto'

    # Dynamic content
    title = subject
    intro_text = f"Hello {username},"
    if emotions:
        body_text = f"Your workout plan, tailored to your emotions ({', '.join(emotions)}), is ready to energize your day!"
    else:
        body_text = f"Your {duration_info}-minute workout plan (actual duration: {workouts['duration'].sum()} minutes) is set to boost your fitness!"

    content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@600&family=Roboto:wght@400;500&display=swap" rel="stylesheet">
    <style>
        body {{
            margin: 0;
            padding: 0;
            font-family: '{font_body}', 'Helvetica', 'Arial', sans-serif;
            background-color: {background_color};
            color: #FFFFFF;
        }}
        .outer-container {{
            width: 100%;
            background: {background_color};
            padding: 20px 0;
        }}
        .inner-container {{
            max-width: 900px;
            margin: 0 auto;
            background: #2D2D2D;
            border-radius: 10px;
            border: 2px solid {primary_color};
        }}
        .header {{
            padding: 0;
            text-align: center;
            background: {secondary_color};
        }}
        .header img {{
            width: 100%;
            height: auto;
            border-radius: 10px 10px 0 0;
            display: block;
        }}
        .content {{
            padding: 35px;
        }}
        h1 {{
            font-family: '{font_heading}', 'Helvetica', sans-serif;
            color: {primary_color};
            font-size: 26px;
            margin: 0 0 20px;
            text-align: center;
            font-weight: 500;
        }}
        p {{
            font-size: 16px;
            line-height: 1.6;
            margin: 0 0 15px;
            color: #D3D3D3;
        }}
        ul {{
            list-style: none;
            padding: 0;
            margin: 0 0 25px;
        }}
        li {{
            font-size: 18px;
            margin: 15px 0;
            display: block;
        }}
        li span {{
            color: {accent_color}; /* Match numbers to white text */
            margin-right: 10px;
        }}
        a {{
            color: {accent_color}; /* White links */
            text-decoration: none;
            font-weight: 500;
        }}
        a:hover {{
            text-decoration: underline;
        }}
        .button {{
            display: inline-block;
            padding: 12px 30px;
            background: {primary_color};
            color: {accent_color};
            text-align: center;
            border-radius: 5px;
            font-size: 16px;
            font-weight: 500;
            margin: 20px auto;
            display: block;
            width: fit-content;
            text-decoration: none;
            transition: background 0.3s ease;
        }}
        .button:hover {{
            background: #E74C3C;
        }}
        .footer {{
            background: {secondary_color};
            padding: 20px;
            text-align: center;
            font-size: 12px;
            color: #D3D3D3;
            border-top: 2px solid {primary_color};
            border-radius: 0 0 10px 10px;
        }}
        .footer a {{
            color: #E74C3C;
            text-decoration: none;
            font-weight: 500;
        }}
        .footer a:hover {{
            text-decoration: underline;
        }}
        @media only screen and (max-width: 900px) {{
            .inner-container {{
                max-width: 95%;
                margin: 0 auto;
            }}
            .content {{
                padding: 20px;
            }}
            h1 {{
                font-size: 22px;
            }}
            p, li {{
                font-size: 16px;
            }}
            .button {{
                padding: 10px 25px;
                font-size: 14px;
            }}
            .header img {{
                border-radius: 8px 8px 0 0;
            }}
        }}
    </style>
</head>
<body>
    <table class="outer-container" width="100%" cellpadding="0" cellspacing="0">
        <tr>
            <td>
                <table class="inner-container" width="100%" cellpadding="0" cellspacing="0">
                    <tr>
                        <td class="header">
                            <img src="https://images.unsplash.com/photo-1593079831268-3381b0db4a77?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80" alt="Fitness Header" />
                        </td>
                    </tr>
                    <tr>
                        <td class="content">
                            <h1>{title}</h1>
                            <p>{intro_text}</p>
                            <p>{body_text}</p>
                            <ul>
                                {''.join([f"""
                                <li>
                                    <span>{index + 1}.</span> <a href='{row['link']}'>{row['name']} ({row['type']}) - {row['duration']} min</a>
                                </li>
                                """ for index, (_, row) in enumerate(workouts.iterrows())])}
                            </ul>
                            <span class="button">Start Your Workout</span>
                        </td>
                    </tr>
                    <tr>
                        <td class="footer">
                            <p>Created by Kevin Mevada</p>
                            <p><a href="https://github.com/kevinmevada">GitHub</a> | <a href="https://linkedin.com/in/kevinmevada">LinkedIn</a></p>
                            <p>© 2025 Emotion Powered Wellness and Fitness Guide Companion. All Rights Reserved.</p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""
    # Save for debugging
    with open("email_content.html", "w", encoding="utf-8") as f:
        f.write(content)
    return content

# Emotion detection with DeepFace
def detect_emotion():
    emotions = []
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        st.error("No webcam detected. Please connect a webcam and try again.")
        return []
    timeout = 20
    start_time = time.time()
    with st.spinner("Detecting emotions..."):
        while time.time() - start_time < timeout:
            ret, frame = cap.read()
            if not ret:
                st.error("Failed to capture video. Please check your webcam.")
                break
            try:
                result = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=True)
                emotion = result[0]['dominant_emotion'].capitalize()
                if emotion in ['Happy', 'Sad', 'Angry', 'Neutral']:
                    emotions.append(emotion)
            except Exception as e:
                st.warning(f"Emotion detection error: {e}")
                pass
            if len(emotions) >= 10:
                break
    cap.release()
    cv2.destroyAllWindows()
    return list(dict.fromkeys(emotions))[:3]

# Recommend workouts based on emotions
def recommend_workouts(detected_emotions):
    df = pd.read_csv("mood_based_workouts_updated.csv")
    df['Mood'] = df['Mood'].str.replace(r"[\[\]']", "", regex=True).str.strip().str.lower()
    recommended = []
    for emotion in detected_emotions:
        emotion = emotion.lower().strip()
        mood_df = df[df['Mood'] == emotion]
        for _, row in mood_df.iterrows():
            workout = {
                'Exercise': row['Exercise'],
                'Sets': row['Sets'],
                'Video_Link': row['Video_Link'],
                'Duration': row['Duration']
            }
            recommended.append(workout)
    return recommended[:20]

# Recommend workouts by duration
def recommend_workouts_by_duration(target_duration):
    selected = pd.DataFrame()
    remaining_time = target_duration
    available_workouts = df.copy()
    while remaining_time > 0 and not available_workouts.empty:
        workout = available_workouts.sample(n=1)
        workout_duration = workout['duration'].iloc[0]
        if workout_duration <= remaining_time:
            selected = pd.concat([selected, workout], ignore_index=True)
            remaining_time -= workout_duration
        available_workouts = available_workouts.drop(workout.index)
    total_duration = selected['duration'].sum()
    while total_duration > target_duration and not selected.empty:
        selected = selected.iloc[:-1]
        total_duration = selected['duration'].sum()
    return selected.reset_index(drop=True)

# Emotion-based workout recommendation
def workout_recommendation():
    st.markdown(
        """
        <style>
        .header-container {
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            margin-bottom: 10px;
        }
        .header-container h1 {
            text-align: center;
            margin: 0;
            padding: 10px 0;
        }
        .button-container {
            display: flex;
            justify-content: center;
            align-items: center;
            margin: 10px 0;
        }
        .button-container .stButton>button {
            width: 200px;
            text-align: center;
            padding: 10px 20px;
            font-size: 18px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    with st.container():
        st.markdown("<div class='header-container'>", unsafe_allow_html=True)
        st.markdown("<h1>Emotion-Based Workouts</h1>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<div class='button-container'>", unsafe_allow_html=True)
        if st.button('Scan Emotions', key='emotion_button'):
            detected_emotions = detect_emotion()
            if detected_emotions:
                st.success("Emotions detected!")
                st.session_state['emotions_detected'] = True
                st.session_state['detected_emotions'] = detected_emotions
                recommended_workouts = recommend_workouts(detected_emotions)
                st.session_state['emotion_recommended_workouts'] = pd.DataFrame(recommended_workouts).rename(columns={
                    'Exercise': 'name',
                    'Sets': 'type',
                    'Video_Link': 'link',
                    'Duration': 'duration'
                })
                user_id = st.session_state.get('user_id')
                if user_id and not st.session_state['emotion_recommended_workouts'].empty:
                    st.session_state['emotion_plan_id'] = save_workout_plan(user_id, 'emotion', st.session_state['emotion_recommended_workouts'])
            else:
                st.warning("No emotions detected. Try again.")
        st.markdown("</div>", unsafe_allow_html=True)

    if 'emotion_recommended_workouts' in st.session_state and not st.session_state['emotion_recommended_workouts'].empty:
        recommended_workouts = st.session_state['emotion_recommended_workouts']
        detected_emotions = st.session_state.get('detected_emotions', [])
        st.markdown(f"<h3 style='text-align: center;'>Detected Emotions: {', '.join(detected_emotions)}</h3>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center;'>Your Workout Plan</h3>", unsafe_allow_html=True)
        st.write("---")
        for i, row in recommended_workouts.iterrows():
            st.markdown(f"""
                <div class='workout-card'>
                    <h4><a href="{row['link']}" target="_blank">{i + 1}. {row['name']}</a></h4>
                    <p>Sets: {row['type']}</p>
                    <p>Duration: {row['duration']} min</p>
                </div>
            """, unsafe_allow_html=True)

        user_email = st.session_state.get('email')
        user_id = st.session_state.get('user_id')
        plan_id = st.session_state.get('emotion_plan_id')
        
        if user_id and plan_id:
            if st.button("Share Plan", key='share_emotion'):
                st.code(f"https://your-app-url.com/plan/{plan_id}")
            
            if user_email and st.button("Email Plan", key='email_emotion'):
                username = st.session_state.get('username', 'User')
                # Debug session state
                st.write(f"Debug: Emotion-based email - Email={user_email}, Username={username}, PlanID={plan_id}")
                st.write(f"Debug: Emotions={', '.join(detected_emotions)}")
                st.write("Debug: Email content saved to 'email_content.html'")
                subject = "Your Emotion-Based Workout Plan 💪"
                content = generate_email_template(
                    subject=subject,
                    username=username,
                    plan_id=plan_id,
                    workouts=recommended_workouts,
                    emotions=detected_emotions
                )
                if send_email(user_email, subject, content):
                    st.success("Plan sent to your email!")
                else:
                    st.error("Failed to send email. Check debug logs")
            
            if st.button("Mark as Completed", key='complete_emotion'):
                feedback = st.text_area("Optional feedback:", key='feedback_emotion')
                save_progress(user_id, plan_id, True, feedback)
                st.success("Workout marked as completed!")

# Duration-based workout recommendation
def duration_based_workouts():
    st.markdown("<h1 style='text-align: center;'>Duration-Based Workouts</h1>", unsafe_allow_html=True)
    duration_options = [15, 30, 45, 60]
    target_duration = st.selectbox("Workout Duration (minutes)", duration_options, key='duration_select')
    
    if 'duration_recommended_workouts' not in st.session_state:
        st.session_state['duration_recommended_workouts'] = None
    if 'duration_plan_id' not in st.session_state:
        st.session_state['duration_plan_id'] = None

    if st.button("Generate Plan", key='generate_duration'):
        recommended_workouts = recommend_workouts_by_duration(target_duration)
        total_duration = recommended_workouts['duration'].sum()
        st.session_state['duration_recommended_workouts'] = recommended_workouts
        if recommended_workouts.empty:
            st.warning("No workouts could be selected.")
        else:
            user_id = st.session_state.get('user_id')
            if user_id:
                plan_id = save_workout_plan(user_id, 'duration', recommended_workouts)
                st.session_state['duration_plan_id'] = plan_id
            st.markdown(f"<h3 style='text-align: center;'>Your {target_duration}-Minute Workout Plan</h3>", unsafe_allow_html=True)
            st.write("---")
            for i, row in recommended_workouts.iterrows():
                st.markdown(f"""
                    <div class='workout-card'>
                        <h4><a href="{row['link']}" target="_blank">{i + 1}. {row['name']}</a></h4>
                        <p>Sets: {row['type']}</p>
                        <p>Duration: {row['duration']} min</p>
                    </div>
                """, unsafe_allow_html=True)

    recommended_workouts = st.session_state.get('duration_recommended_workouts')
    plan_id = st.session_state.get('duration_plan_id')
    user_email = st.session_state.get('email')
    user_id = st.session_state.get('user_id')

    if recommended_workouts is not None and not recommended_workouts.empty:
        if user_id and plan_id:
            if st.button("Share Plan", key='share_duration'):
                st.code(f"https://your-app-url.com/plan/{plan_id}")
            
            if user_email and st.button("Email Plan", key='email_duration'):
                username = st.session_state.get('username', 'User')
                # Debug session state
                st.write(f"Debug: Duration-based email - Email={user_email}, Username={username}, PlanID={plan_id}")
                st.write(f"Debug: Duration={target_duration}, Total Duration={recommended_workouts['duration'].sum()}")
                st.write("Debug: Email content saved to 'email_content.html'")
                subject = f"Your {target_duration}-Minute Workout Plan 💪"
                content = generate_email_template(
                    subject=subject,
                    username=username,
                    plan_id=plan_id,
                    workouts=recommended_workouts,
                    duration_info=target_duration
                )
                if send_email(user_email, subject, content):
                    st.success("Plan sent to your email!")
                else:
                    st.error("Failed to send email. Check debug logs")
            
            if st.button("Mark as Completed", key='complete_duration'):
                feedback = st.text_area("Optional feedback:", key='feedback_duration')
                save_progress(user_id, plan_id, True, feedback)
                st.success("Workout marked as completed!")

# Workout history
def workout_history():
    st.markdown("<h1 style='text-align: center;'>Workout History</h1>", unsafe_allow_html=True)
    user_id = st.session_state.get('user_id')
    if user_id:
        plans = get_workout_plans(user_id)
        if not plans:
            st.info("No workout plans yet. Start one now!")
        else:
            for plan in plans:
                workouts = pd.read_json(plan['data'])
                st.markdown(f"""
                    <div class='stCard'>
                        <h4>{plan['type'].capitalize()} Plan - {plan['created_at']}</h4>
                        <ul>
                            {''.join([f"<li>{row['name']} ({row['type']}) - {row['duration']} min</li>" for _, row in workouts.iterrows()])}
                        </ul>
                    </div>
                """, unsafe_allow_html=True)

# Progress dashboard
def progress_dashboard():
    st.markdown("<h1 style='text-align: center;'>Progress Dashboard</h1>", unsafe_allow_html=True)
    user_id = st.session_state.get('user_id')
    if user_id:
        progress = get_progress(user_id)
        if not progress:
            st.info("No progress recorded yet.")
        else:
            completed = sum(1 for p in progress if p['completed'])
            streak = 0
            last_date = None
            for p in sorted(progress, key=lambda x: x['completed_at']):
                date = p['completed_at'].split()[0]
                if p['completed'] and (last_date is None or (pd.to_datetime(date) - pd.to_datetime(last_date)).days == 1):
                    streak += 1
                else:
                    streak = 1 if p['completed'] else 0
                last_date = date
            
            st.markdown(f"""
                <div class='stCard'>
                    <h3>Your Stats</h3>
                    <p>Workouts Completed: {completed}</p>
                    <p>Current Streak: {streak} days</p>
                    <p>Badges: {'🏋️' if completed >= 5 else ''}{'🔥' if streak >= 3 else ''}</p>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<h3>Recent Activity</h3>", unsafe_allow_html=True)
            for p in progress[:5]:
                plan = get_workout_plans(user_id)
                plan_data = next((x for x in plan if x['id'] == p['plan_id']), None)
                plan_name = plan_data['type'].capitalize() if plan_data else "Unknown"
                st.markdown(f"""
                    <div class='stCard'>
                        <p>{plan_name} Plan - {p['completed_at']}</p>
                        <p>Status: {'Completed' if p['completed'] else 'Not Completed'}</p>
                        <p>Feedback: {p['feedback'] or 'None'}</p>
                    </div>
                """, unsafe_allow_html=True)