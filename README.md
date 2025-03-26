# 🧠 NeuroWell – AI-Driven Mental Health Simulation System

**NeuroWell** is an AI-powered **mental health chatbot and therapy simulator**, combining emotional intelligence, AI-generated reports, and immersive relaxation simulations to support user well-being. Designed as more than a chatbot, NeuroWell is a **complete mental health assistant**, ideal for users needing instant emotional support, report-based escalation, and calming therapy tools.

---

## 🚀 Why NeuroWell?

In a world filled with stress and anxiety, NeuroWell offers:

- ✅ Emotionally intelligent LLM-based chatbot (Gemini/Groq)
- ✅ Automated PDF mental health reports
- ✅ Visual relaxation simulation (games, sounds)
- ✅ Scalable, secure backend with real-time inference
- ✅ Therapist-ready user data and summaries

---

## 📌 Features

### 🔹 AI Mental Health Chatbot
- Built with **Gemini 1.5 Pro** + **LangChain**
- Detects and responds to **stress, anxiety, sadness, and depression**
- Empathetic, supportive, and non-robotic tone
- Option to forward request to a counselor

### 🔹 PDF Report Generation
- Name, Age, Primary Concern extracted via LLM
- Summary of chat session
- Automatically stored in **MongoDB (GridFS)**

### 🔹 Relaxation Simulation Tools (Frontend)
- 🎮 Relaxation mini-games
- 🎧 Calming sound players (rain, waves, forest)
- 🧘 Breathing & mindfulness UI
- Acts as an **AI-first therapy simulation**

### 🔹 Secure Storage & Access
- MongoDB + GridFS for secure file handling
- Reports are downloadable by counselors via REST API

---

## 🧰 Tools Used  
[![PyCharm](https://img.shields.io/badge/PyCharm-143?style=for-the-badge&logo=pycharm&logoColor=white&color=black)](https://www.jetbrains.com/pycharm/)  
[![Postman](https://img.shields.io/badge/Postman-FF6C37?style=for-the-badge&logo=postman&logoColor=white)](https://www.postman.com/)  
[![Jupyter](https://img.shields.io/badge/Jupyter-F37626?style=for-the-badge&logo=jupyter&logoColor=white)](https://jupyter.org/)  
[![Git](https://img.shields.io/badge/Git-F05032?style=for-the-badge&logo=git&logoColor=white)](https://git-scm.com/)  
[![GitHub](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/)

---

## 🛠️ Tech Stack

![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-4EA94B?style=for-the-badge&logo=mongodb&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Gemini API](https://img.shields.io/badge/Gemini-FF6C37?style=for-the-badge&logo=google&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-5E8FFF?style=for-the-badge&logo=langchain&logoColor=white)
![Render](https://img.shields.io/badge/Render-Deployed-0078D4?style=for-the-badge&logo=render&logoColor=white)

---

## 📂 Folder Structure

<pre> NeuroWell/ ├── llama.py # 🧠 FastAPI chatbot logic ├── generate_report.py # 📄 LLM-driven PDF report generator ├── requirements.txt # 📦 Python dependencies ├── .env.example # 🔐 Sample environment config ├── start.sh # 🚀 Start script for Render ├── Data/ # 📁 Sample PDF files ├── chroma_db/ # 🧠 Chroma vector DB storage ├── Frontend/ # 🎮 UI with relaxation games and sounds └── README.md # 📘 Project documentation </pre>




---

## ⚙️ Setup & Installation

### 🔹 1. Clone the Repository

```bash
git clone https://github.com/your-username/NeuroWell.git
cd NeuroWell
```

🔹 2. Create a Virtual Environment

python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

🔹 3. Install Dependencies

pip install -r requirements.txt

🔹 4. Set Environment Variables

Create a .env file and add:
```bash
GEMINI_API_KEY=your_gemini_key
MONGO_URI=your_mongodb_uri
GROQ_API_KEY=optional
```
    You can use .env.example as a template

🔹 5. Start the FastAPI Server
```bash 
python llama.py
# OR with Uvicorn
./start.sh
```
🔄 API Endpoints
🧠 POST /chat
``` bash
{
  "user_id": "user123",
  "message": "I'm feeling very anxious and sad lately."
}
```
    Returns an empathetic AI response

    Stores chat history in MongoDB

    Detects emotion (stress, anxiety, etc.)

📄 GET /report/:userId

    Returns a downloadable PDF mental health report

    Includes user name, age, chat summary, and primary concern

🎮 Relaxation Simulation Add-On (Frontend)

    📍 Embedded in the dashboard

    🎧 Includes sound players (rain, ocean, forest)

    🎮 Includes breathing circles, anti-stress clickers

    💡 Designed to feel immersive like therapy simulation, not just frontend

🧪 Sample Test
```bash
curl -X POST https://neurowell-backend.onrender.com/chat \
     -H "Content-Type: application/json" \
     -d '{"user_id": "test123", "message": "I feel overwhelmed with life."}'
```
🔮 Future Scope

    Counselor dashboard to review reports

    Real-time escalation to human therapists

    Sentiment-based recommendation engine

    Integration with smart wearables for emotional tracking

✨ Contributors
Name	Role
Tejash Tarun	AI Backend, Report System, Gemini Integration
Team	User Auth Backend, Frontend Relaxation UI
📎 Useful Links
Component	Link
🌐 Frontend	coming soon
⚙️ Backend API	https://neurowell-backend.onrender.com/chat
📄 PDF Report	https://neurowell-backend.onrender.com/report/:userId
📜 License

This project is licensed under the MIT License.
