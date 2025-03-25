import os
import google.generativeai as genai
import pymongo
import gridfs  # ✅ For storing PDF
import certifi
import textwrap
from datetime import datetime
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors

# ✅ Configure Gemini API Key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# ✅ MongoDB Connection with SSL Fix
MONGO_URI = os.getenv("MONGO_URI")
client = pymongo.MongoClient(MONGO_URI, tlsCAFile=certifi.where())
db = client["mental_health_chatbot"]
chat_collection = db["chat_history"]
reports_collection = db["reports"]
fs = gridfs.GridFS(db)  # ✅ GridFS initialization

# ✅ Fetch User's Chat History
def fetch_chat_history(user_id, limit=10):
    try:
        chat_history = list(chat_collection.find({"user_id": user_id}).sort("_id", -1).limit(limit))
        return [chat["message"] for chat in chat_history] if chat_history else []
    except pymongo.errors.ServerSelectionTimeoutError as e:
        return [f"❌ MongoDB Connection Error: {str(e)}"]

# ✅ Extract Primary Concern from Chat
def extract_primary_concern(user_id):
    chat_history = fetch_chat_history(user_id)
    if not chat_history:
        return "Not Mentioned"
    prompt = f"""You are an AI assistant analyzing a user's chat history with a mental health chatbot.Identify the primary concern or issue they are discussing (e.g., Anxiety, Depression, Stress, Loneliness).If no clear concern is found, return 'Not Mentioned'.Chat History:{chat_history}Primary Concern:"""
    try:
        model = genai.GenerativeModel(model_name="gemini-1.5-pro")
        response = model.generate_content(prompt)
        return response.text.strip().replace("Primary Concern:", "").strip() if response.text else "Not Mentioned"
    except Exception as e:
        return "Not Mentioned"

# ✅ Extract Name and Age from Chat
def extract_user_details(user_id):
    chat_history = fetch_chat_history(user_id)
    if not chat_history:
        return "Not Mentioned", "Not Mentioned"
    prompt = f"""You are an AI assistant. Extract the user's name and age (if mentioned) from this chat history.Chat: {chat_history}Reply in this format exactly: Name: <name>, Age: <age>. If not found, say 'Not Mentioned'."""
    try:
        model = genai.GenerativeModel(model_name="gemini-1.5-pro")
        response = model.generate_content(prompt)
        text = response.text.strip()
        name = text.split("Name:")[1].split(",")[0].strip() if "Name:" in text else "Not Mentioned"
        age = text.split("Age:")[1].strip() if "Age:" in text else "Not Mentioned"
        return name, age
    except Exception as e:
        return "Not Mentioned", "Not Mentioned"

# ✅ Generate Summary using Gemini API v1.5
def generate_chat_summary(user_id):
    chat_history = fetch_chat_history(user_id)
    if not chat_history:
        return "No conversation history found."
    prompt = f"""You are an AI assistant helping with mental health support.Below is the recent conversation of a user with a chatbot.Summarize the key points in a concise and professional manner, focusing on their emotions, concerns, and overall well-being.Chat History:{chat_history}Summary:"""
    try:
        model = genai.GenerativeModel(model_name="gemini-1.5-pro")
        response = model.generate_content(prompt)
        summary = response.text.strip()
        if summary.startswith("Summary:"):
            summary = summary.replace("Summary:", "").strip()
        return summary
    except Exception as e:
        return f"❌ Error generating summary: {str(e)}"

# ✅ Footer function
def draw_footer(canvas_obj, width, height):
    canvas_obj.setFont("Helvetica", 9)
    canvas_obj.setFillColor(colors.grey)
    canvas_obj.setStrokeColor(colors.lightgrey)
    canvas_obj.setLineWidth(0.5)
    canvas_obj.line(50, 70, width - 50, 70)
    canvas_obj.drawCentredString(width / 2, 60, "NeuroWell Pvt. Ltd. • Made by Tejash Tarun")
    canvas_obj.drawCentredString(width / 2, 45, "This is a summary report generated for counselor reference only.")

# ✅ Save PDF to GridFS
def save_pdf_to_gridfs(path, filename):
    with open(path, "rb") as f:
        data = f.read()
        existing = fs.find_one({"filename": filename})
        if existing:
            fs.delete(existing._id)
        fs.put(data, filename=filename)

# ✅ Main PDF generator
def create_pdf_report(user_id, user_name="Not Mentioned", user_age="Not Mentioned"):
    summary = generate_chat_summary(user_id)
    primary_concern = extract_primary_concern(user_id)
    if user_name == "Not Mentioned" or user_age == "Not Mentioned":
        user_name, user_age = extract_user_details(user_id)
    if "Error" in summary or "❌" in summary:
        return summary
    if primary_concern.startswith("Primary Concern:"):
        primary_concern = primary_concern.replace("Primary Concern:", "").strip()
    reports_dir = "reports"
    os.makedirs(reports_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    pdf_filename = f"{reports_dir}/Chat_Report_{user_id}_{timestamp}.pdf"
    try:
        c = canvas.Canvas(pdf_filename, pagesize=letter)
        width, height = letter
        # ✅ Title Header
        c.setFont("Helvetica-Bold", 24)
        c.setFillColor(colors.darkblue)
        c.drawCentredString(width / 2, height - 60, "🧠 NeuroWell Mental Health Report")
        # ✅ Timestamp
        c.setFont("Helvetica", 10)
        c.setFillColor(colors.black)
        c.drawRightString(width - 50, height - 75, f"Generated on: {datetime.now().strftime('%d %B %Y, %I:%M %p')}")
        # ✅ User Info Section
        y = height - 110
        c.setFont("Helvetica-Bold", 14)
        c.setFillColor(colors.black)
        c.drawString(70, y, "■ User Information")
        y -= 20
        c.setFont("Helvetica", 12)
        c.drawString(90, y, f"• User ID: {user_id}")
        y -= 18
        c.drawString(90, y, f"• Name: {user_name}")
        y -= 18
        c.drawString(90, y, f"• Age: {user_age}")
        y -= 18
        c.drawString(90, y, f"• Primary Concern: {primary_concern}")
        # ✅ Line Separator
        y -= 15
        c.setStrokeColor(colors.grey)
        c.setLineWidth(1)
        c.line(60, y, width - 60, y)
        y -= 30
        # ✅ Summary Title
        c.setFont("Helvetica-Bold", 14)
        c.setFillColor(colors.darkred)
        c.drawString(70, y, "■ Session Summary")
        y -= 25
        # ✅ Typewriter Summary with Wrapping
        c.setFont("Courier", 10)
        c.setFillColor(colors.black)
        usable_width = width - 180
        char_width = c.stringWidth("M", "Courier", 10)
        max_chars = int(usable_width / char_width)
        line_height = 15
        lines = summary.split("\n")
        for line in lines:
            wrapped_lines = textwrap.wrap(line, width=max_chars)
            for w_line in wrapped_lines:
                c.drawString(90, y, w_line)
                y -= line_height
                if y < 100:
                    draw_footer(c, width, height)
                    c.showPage()
                    y = height - 80
                    c.setFont("Courier", 10)
        # ✅ Watermark (on first page)
        c.setFont("Helvetica-Bold", 45)
        c.setFillColor(colors.lightgrey)
        c.saveState()
        c.translate(width / 2, height / 2)
        c.rotate(45)
        c.drawCentredString(0, 0, "NeuroWell")
        c.restoreState()
        # ✅ Final Footer
        draw_footer(c, width, height)
        c.save()
        filename = f"{user_id}_report.pdf"
        save_pdf_to_gridfs(pdf_filename, filename)  # ✅ Save in MongoDB
    except Exception as e:
        return f"❌ PDF Generation Error: {str(e)}"
    # ✅ Store metadata in MongoDB
    try:
        reports_collection.insert_one({
            "user_id": user_id,
            "user_name": user_name,
            "user_age": user_age,
            "primary_concern": primary_concern,
            "summary": summary,
            "pdf_path": pdf_filename,
            "timestamp": datetime.now()
        })
    except pymongo.errors.ServerSelectionTimeoutError as e:
        return f"❌ MongoDB Connection Error: {str(e)}"
    return filename