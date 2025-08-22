import os
from google import generativeai as genai
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import pickle
import logging
from functools import lru_cache
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Gemini client
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    logger.error("Gemini API key not set in .env file")
    raise ValueError("Gemini API key not set in .env file")

try:
    genai.configure(api_key=GEMINI_API_KEY)
    client = genai.GenerativeModel('gemini-1.5-pro')
except Exception as e:
    logger.error(f"Failed to initialize Gemini client: {e}")
    raise

# Absolute path to output folder
OUTPUT_DIR = r"E:\Personal Project\AI Projects\AI-Tutor-APP-ME-and-Tony\AJ-AI-TUTOR\AJ-AI-Tutor\Server\app\output"
#OUTPUT_DIR = os.getenv("OUTPUT_DIR", "/code/app/output")  

# Load embedding model and RAG data
try:
    embed_model = SentenceTransformer('all-MiniLM-L6-v2')
    index = faiss.read_index(os.path.join(OUTPUT_DIR, "textbook_index.faiss"))
    with open(os.path.join(OUTPUT_DIR, "text_chunks.pkl"), "rb") as f:
        text_chunks = pickle.load(f)
except Exception as e:
    logger.error(f"Error loading RAG data: {e}")
    raise

@lru_cache(maxsize=100)
def is_python_question(query, threshold=0.7):
    python_keywords = [
        'python', 'list', 'dict', 'function', 'loop', 'variable', 'string', 'class',
        'import', 'lambda', 'def', 'tuple', 'set', 'int', 'float', 'bool', 'syntax',
        'error', 'numbers', 'numeric', 'arithmetic', 'types', 'math', 'operators',
        'if', 'elif', 'else', 'while', 'for', 'break', 'continue', 'input', 'print',
        'type', 'conversion', 'indexing', 'slicing', 'concatenation', 'password'
    ]
    query_lower = query.lower()
    keyword_match = any(keyword in query_lower for keyword in python_keywords)
    
    q_emb = embed_model.encode([query], convert_to_numpy=True)
    avg_emb = np.mean(embed_model.encode(python_keywords, convert_to_numpy=True), axis=0)
    similarity = np.dot(q_emb, avg_emb.T) / (np.linalg.norm(q_emb) * np.linalg.norm(avg_emb))
    
    return keyword_match or similarity > threshold

def retrieve_relevant_context(query, top_k=3, min_similarity=0.5):
    try:
        q_emb = embed_model.encode([query], convert_to_numpy=True)
        D, I = index.search(q_emb, top_k)
        retrieved_chunks = []
        for i, dist in zip(I[0], D[0]):
            similarity = 1 - (dist / 2.0)
            if similarity >= min_similarity:
                chunk = text_chunks[i]
                text = chunk.get("text", "")
                page = chunk.get("page", "?")
                retrieved_chunks.append(f"[Page {page}]\n{text}")
        return "\n---\n".join(retrieved_chunks) if retrieved_chunks else "No relevant textbook content found."
    except Exception as e:
        logger.error(f"Error retrieving context: {e}")
        return "Error retrieving context."

def generate_rag_prompt(question, context):
    prompt = f"""
        You are a warm, patient, and knowledgeable AI tutor, like a great teacher who explains things clearly and makes learning enjoyable. 
        Your job is to help the student understand their textbook content deeply using the given context, but you can also use your own expertise to add helpful details, real-world applications, and analogies.

        Here’s how to respond:
        1. Start by naturally acknowledging the relevant textbook content. Summarize it in your own words without quoting mechanically.
        2. Give a clear, friendly explanation as if you’re teaching a curious student. Expand on the topic with examples, analogies, and practical applications. 
        3. If code examples make sense, include them in a natural way with helpful comments.
        4. Smoothly integrate textbook page references into your sentences (e.g., “On page 6, your textbook promises to explain…”), but don’t list them in a rigid block.
        5. Keep the tone warm, encouraging, and approachable—avoid sounding like a rigid template.
        6. End by encouraging the student to explore further in the textbook for deeper understanding.
        7. For multi-step concepts or processes, explain step by step in simple terms.
        8. If the question is outside the textbook or Python syllabus, politely explain that you focus on the syllabus content and guide the student back to relevant topics.

        
        When explaining concepts like programming or theory:
        - Begin with a simple **definition in one sentence**.
        - Use **an analogy** (e.g., LEGOs, family trees) to make it relatable.
        - If applicable, include a **visual hierarchy or structure** in text form (like a class diagram or flow).
        - For programming topics, add **one main example** that demonstrates the concept in a beginner-friendly way, including **comments explaining each part**.
        - Briefly mention **related variations or types** (like different kinds of inheritance), even if you don’t dive deep. **Whenever you mention these types (single inheritance, multiple inheritance, multilevel inheritance, hybrid inheritance), write them in bold using Markdown** so they stand out.
        - If needed, show an **extra mini-example** for advanced cases, but keep it short and clear.
        - Reassure the learner that it’s okay if it feels abstract at first, and encourage **practice and experimentation**.
        

        Context from the textbook:
        {context}

        Student’s question:
        {question}

        Now craft a helpful, teacher-like answer.
        """
    return prompt


def get_tutor_reply_with_rag(question):
    try:
        question_lower = question.lower()
        if "who are you" in question_lower or "what are you" in question_lower or "yourself" in question_lower:
            return (
                "I am your AI tutor, designed to help you navigate and understand your textbook syllabus "
                "by intelligently reading through your PDF and providing clear, concise explanations tailored to your questions."
            )

        context = retrieve_relevant_context(question)
        prompt = generate_rag_prompt(question, context)
        response = client.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        logger.error(f"Error getting tutor reply: {e}")
        return f"⚠️ An error occurred: {e}"




