import streamlit as st
from database import init_db, create_user, authenticate, save_face_embedding, get_face_embedding, get_db_connection
from deepface import DeepFace
import cv2
import numpy as np
import time

# Initialize the database
init_db()

# Capture face embedding with timeout
def capture_face_embedding():
    st.write("Please look at the camera for Face ID registration...")
    cap = cv2.VideoCapture(0)
    embedding = None
    video_placeholder = st.empty()
    timeout = 30
    start_time = time.time()

    while time.time() - start_time < timeout:
        ret, frame = cap.read()
        if not ret:
            st.error("Failed to capture video. Please check your webcam.")
            break
        video_placeholder.image(frame, channels="BGR", use_container_width=True)

        try:
            embedding = DeepFace.represent(frame, model_name="Facenet", enforce_detection=True)
            if embedding:
                st.success("Face captured successfully!")
                break
        except Exception:
            pass
    else:
        st.error("Face capture timed out. Please try again.")

    cap.release()
    cv2.destroyAllWindows()
    return embedding[0]["embedding"] if embedding else None

# Verify face embedding with timeout
def verify_face_embedding(user_id):
    st.write("Please look at the camera for Face ID verification...")
    cap = cv2.VideoCapture(0)
    verified = False
    video_placeholder = st.empty()
    timeout = 30
    start_time = time.time()

    conn = get_db_connection()
    result = conn.execute("SELECT embedding FROM face_embeddings WHERE user_id = ?", (user_id,)).fetchone()
    conn.close()

    if result:
        stored_embedding_bytes = result["embedding"]
        stored_embedding = np.frombuffer(stored_embedding_bytes, dtype=np.float64)

        while time.time() - start_time < timeout:
            ret, frame = cap.read()
            if not ret:
                st.error("Failed to capture video. Please check your webcam.")
                break
            video_placeholder.image(frame, channels="BGR", use_container_width=True)

            try:
                embedding = DeepFace.represent(frame, model_name="Facenet", enforce_detection=True)
                if embedding:
                    current_embedding = np.array(embedding[0]["embedding"])
                    distance = np.linalg.norm(current_embedding - stored_embedding)

                    if distance < 10:
                        st.success("Face ID verified successfully!")
                        verified = True
                        break
                    else:
                        st.warning("Face not matched. Try again...")
            except Exception as e:
                st.warning("Face not detected. Please stay in the frame.")

        if not verified:
            st.error("Face verification timed out.")
    else:
        st.error("No Face ID data found for this user.")

    cap.release()
    cv2.destroyAllWindows()
    return verified

# Login Page
def login_page():
    st.title("Login")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

    if submitted:
        user = authenticate(username, password)
        if user:
            if verify_face_embedding(user['id']):
                st.session_state['logged_in'] = True
                st.session_state['username'] = user['username']
                st.session_state['email'] = user['email']
                st.session_state['user_id'] = user['id']
                st.success("Logged in successfully!")
                st.rerun()
            else:
                st.error("Face ID verification failed.")
        else:
            st.error("Invalid username or password.")

# Signup Page
def signup_page():
    st.title("Sign Up")
    with st.form("signup_form"):
        new_username = st.text_input("Choose a Username")
        new_email = st.text_input("Enter your Email")
        new_password = st.text_input("Choose a Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        submitted = st.form_submit_button("Sign Up")

    if submitted:
        if new_password != confirm_password:
            st.error("Passwords do not match.")
        elif not new_email or "@" not in new_email:
            st.error("Please enter a valid email.")
        else:
            face_embedding = capture_face_embedding()
            if face_embedding:
                result = create_user(new_username, new_email, new_password)
                if result == True:
                    conn = get_db_connection()
                    user_id = conn.execute("SELECT id FROM users WHERE username = ?", (new_username,)).fetchone()["id"]
                    save_face_embedding(user_id, face_embedding)
                    conn.close()
                    st.success("Account created successfully! Please log in.")
                else:
                    st.error(result)
            else:
                st.error("Face ID registration failed.")

# Logout Button
def logout_button():
    if st.sidebar.button("Logout"):
        st.session_state['logged_in'] = False
        st.session_state['username'] = None
        st.session_state['email'] = None
        st.session_state['user_id'] = None
        st.session_state['emotions_detected'] = False
        st.success("Logged out successfully!")
        st.rerun()