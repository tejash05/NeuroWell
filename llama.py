import os
import uvicorn
import certifi
from dotenv import load_dotenv
import motor.motor_asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_groq import ChatGroq
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import PromptTemplate
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader

from generate_report import create_pdf_report

# ✅ Load environment variables
load_dotenv()

# ✅ Initialize FastAPI App
app = FastAPI()

# ✅ MongoDB Connection
MONGO_URI = os.getenv("MONGO_URI")
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI, tlsCAFile=certifi.where())
db = client["mental_health_chatbot"]
chat_collection = db["chat_history"]
reports_collection = db["reports"]


# ✅ Request Schema
class ChatRequest(BaseModel):
    user_id: str
    message: str


# ✅ Initialize LLaMA3 Model
def initialize_llm():
    return ChatGroq(
        groq_api_key=os.getenv("GROQ_API_KEY"),
        model_name="llama3-8b-8192",
        max_tokens=75,
        temperature=0.2
    )


# ✅ Create ChromaDB Vector Store
def create_vector_db():
    db_path = "chroma_db"
    if not os.path.exists(db_path):
        loader = DirectoryLoader("Data", glob="*.pdf", loader_cls=PyPDFLoader)
        documents = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        texts = text_splitter.split_documents(documents)
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        vector_db = Chroma.from_documents(texts, embeddings, persist_directory=db_path,
                                          collection_name="mental_health_chatbot")
        vector_db.persist()
    else:
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        vector_db = Chroma(persist_directory=db_path, embedding_function=embeddings,
                           collection_name="mental_health_chatbot")
    return vector_db


# ✅ Setup QA Chain
def setup_qa_chain(vector_db, llm):
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    retriever = vector_db.as_retriever()

    prompt_template = """Your name is Neuro AI, a caring mental health support companion and answer short.
- NEVER say you are an AI or talk about not having emotions.
- Always acknowledge user’s feelings with warmth and empathy.
- Your tone is supportive, comforting, and friendly.
- If the user expresses stress, sadness, anxiety, or asks for help — respond with emotional care and offer to connect to a counselor.

Chat History:{chat_history}
Context:{context}
User: {question}
Neuro AI:"""

    prompt = PromptTemplate(
        input_variables=["chat_history", "context", "question"],
        template=prompt_template
    )

    return ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        return_source_documents=False,
        combine_docs_chain_kwargs={"prompt": prompt}
    )


# ✅ Emotion Detection
def analyze_emotion(text):
    keywords = {
        "stressed": ["stress", "overwhelmed", "pressure", "tense"],
        "anxious": ["anxious", "worried", "nervous", "panic"],
        "sad": ["sad", "lonely", "heartbroken", "upset"],
        "depressed": ["depressed", "hopeless", "nothing matters", "empty"]
    }
    text = text.lower()
    for emotion, words in keywords.items():
        if any(word in text for word in words):
            return emotion
    return "neutral"


# ✅ AI Comfort Response
def generate_comforting_response(emotion, llm):
    if emotion == "neutral":
        return "I'm glad to hear that! Let me know if there's anything else I can help with."

    system_prompt = f"""You are a mental health chatbot providing emotional support.
- The user feels {emotion}.
- Acknowledge their emotions warmly.
- Offer reassurance and support.
- NEVER talk about yourself or say 'I don't have feelings.'
- Provide a concise and empathetic response."""

    response = llm.invoke(system_prompt)
    return response.content.strip()


# ✅ Initialize components
vector_db = create_vector_db()
llm = initialize_llm()
qa_chain = setup_qa_chain(vector_db, llm)


# ✅ Chat Endpoint
@app.post("/chat")
async def chatbot_response(request: ChatRequest):
    user_id = request.user_id
    user_input = request.message.strip().lower()
    if not user_input:
        raise HTTPException(status_code=400, detail="❌ Provide a valid input.")

    await chat_collection.insert_one({"user_id": user_id, "message": user_input})

    chat_history = await chat_collection.find({"user_id": user_id}).sort("_id", -1).limit(3).to_list(None)
    chat_texts = [{"role": "user", "content": chat["message"]} for chat in chat_history]

    counselor_status = await reports_collection.find_one({"user_id": user_id})
    if counselor_status and counselor_status.get("requested", False):
        return {
            "response": "Your request has already been forwarded to our counselor. They will reach out to you soon."
        }

    if "connect me" in user_input or "meet" in user_input:
        pdf_path = create_pdf_report(user_id)
        await reports_collection.insert_one({
            "user_id": user_id,
            "summary": "User requested counselor connection",
            "requested": True,
            "pdf_path": pdf_path,
            "timestamp": datetime.now()
        })
        return {
            "response": f"✅ Your request has been forwarded to our counselor. Here's the report: [Download Report]({pdf_path})."
        }

    emotion = analyze_emotion(user_input)
    if emotion != "neutral":
        return {"response": generate_comforting_response(emotion, llm)}

    response = qa_chain({"question": user_input, "chat_history": chat_texts})
    return {"response": response['answer']}


# ✅ Start server
if __name__ == "__main__":
    uvicorn.run("llama:app", host="0.0.0.0", port=8020, reload=True)
