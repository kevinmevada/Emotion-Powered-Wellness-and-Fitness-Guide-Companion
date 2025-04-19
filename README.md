# Emotion-Powered Wellness and Fitness Guide Companion

<p >
  <img src="https://img.shields.io/badge/Built%20With-Streamlit-ff4b4b?style=for-the-badge&logo=streamlit&logoColor=white">
  <img src="https://img.shields.io/badge/AI%20Powered-DeepFace-3b8ac4?style=for-the-badge&logo=python&logoColor=white">
  <img src="https://img.shields.io/github/license/kevinmevada/Emotion-Powered-Wellness-and-Fitness-Guide-Companion?style=for-the-badge">
  <img src="https://img.shields.io/github/last-commit/kevinmevada/Emotion-Powered-Wellness-and-Fitness-Guide-Companion?style=for-the-badge">
</p>


> 🚀 Your fitness journey just got personal. This AI-powered app curates workouts based on your **emotions or time availability**. Fitness meets feelings.

## 📚 Table of Contents

- Why This App?
- Installation
- Usage
- Dependencies
- Project Structure
- Contributing
- License
- Contact
- Acknowledgments

---

## 💡 Why This App?

Fitness isn’t just about muscle—it's about mood. This app detects your **emotions (Happy, Sad, Angry, Neutral)** and recommends workouts to match. Whether you're hyped or need a gentle stretch, this companion adapts to **you**.

✨ Think: **Spotify for workouts**, but powered by your face.

---

## 🏋️ Features

| Feature | Description |
|--------|-------------|
| 🎭 **Emotion-Based Workouts** | AI uses webcam + DeepFace to detect your mood and recommend a custom workout |
| ⏱ **Duration-Based Plans** | Pick from 15, 30, 45, or 60-minute sessions |
| 🔐 **Facial Authentication** | Secure login/signup with face recognition |
| 🎨 **Custom Themes** | Choose from Cyberpunk, Neon Glow, Forest Green & more |
| 📊 **Progress Dashboard** | Track your stats, streaks & earn badges like 🔥 and 🏋️ |
| 📧 **Email Notifications** | Automatically send workout plans to your inbox |
| 📱 **Responsive UI** | Card layout, hover effects, mobile optimized |

---

## 🛠 Installation

### 📋 Prerequisites

- 🐍 Python 3.8+
- 📷 Webcam (for emotion detection)
- 📧 SMTP credentials (Gmail works best)
- 📂 `mood_based_workouts_updated.csv` dataset (included)

### 📦 Steps

```bash
git clone https://github.com/kevinmevada/emotion-powered-wellness.git
cd emotion-powered-wellness

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

Create a `.env` file:

```env
SMTP_EMAIL=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

Then run:

```bash
streamlit run app.py
```

Visit: [http://localhost:8501](http://localhost:8501)

---

## 🚀 Usage

### 🧍 Sign Up & Log In

- Register with email, password + **facial scan**
- Log in with credentials + **face match**

### 🧠 Choose Your Mode

- **Emotion-Based** → Click "Scan Emotions"
- **Time-Based** → Select workout duration

### 📈 Dashboard & Sharing

- Track your streaks and stats
- Customize theme
- Share via email or link

---

## 📦 Dependencies

| Library         | Version  | Purpose                          |
|----------------|----------|----------------------------------|
| streamlit       | 1.28.0   | Web app frontend                 |
| deepface        | 0.0.79   | Emotion detection, face auth     |
| opencv-python   | 4.8.0    | Webcam feed                      |
| pandas          | 2.0.3    | Data management                  |
| numpy           | 1.24.3   | Numerical calculations           |
| bcrypt          | 4.0.1    | Secure password hashing          |
| python-dotenv   | 1.0.0    | Env variable handling            |
| smtplib         | stdlib   | Email handling                   |

⚠️ **Note:** Check DeepFace's [license](https://github.com/serengil/deepface) before commercial use.

---

## 🗂 Project Structure

```
emotion-powered-wellness/
├── app.py                         # Main Streamlit app
├── auth.py                        # Facial recognition + user auth
├── workout_recommendation.py     # Workout logic and email sender
├── database.py                    # SQLite logic
├── mood_based_workouts_updated.csv
├── .env                           # Email credentials (not tracked)
├── requirements.txt
├── README.md
├── LICENSE
├── .gitignore
└── assets/
    └── demo.gif                   # Demo animation
```

---

## 🤝 Contributing

We welcome contributors! Here’s how:

```bash
git checkout -b feature/my-feature
# make changes
git commit -m "Add my feature"
git push origin feature/my-feature
```

Then open a Pull Request.

📌 Don’t forget to update tests and docs.

---

## 📜 License

This project is open-source under the [MIT License](LICENSE). Feel free to use, modify, and share. Just keep the copyright.

---

## 📬 Contact

**Author**: Kevin Mevada  
📧 [mevadakevin@gmail.com](mailto:mevadakevin@gmail.com)  
🔗 [GitHub](https://github.com/kevinmevada) | [LinkedIn](https://linkedin.com/in/kevinmevada)

---

## 🙌 Acknowledgments

- 🧠 [DeepFace](https://github.com/serengil/deepface) — Emotion & face recognition
- 🛠 [Streamlit](https://streamlit.io) — Web app framework
- 🌍 Open Source Contributors — You rock!
- 💖 Users — Thanks for being a part of this journey!

---

_⭐ Star this repo if you like the project. Your support means everything!_

---
