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

# Initialize the Gemini client with your API key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    logger.error("Gemini API key not set in .env file")
    raise ValueError("Gemini API key not set in .env file")

try:
    genai.configure(api_key=GEMINI_API_KEY)
    client = genai.GenerativeModel('gemini-1.5-pro')  # Using gemini-1.5-pro
except Exception as e:
    logger.error(f"Failed to initialize Gemini client: {e}")
    raise

# Load embedding model and RAG data
try:
    embed_model = SentenceTransformer('all-MiniLM-L6-v2')
    index = faiss.read_index("../output/textbook_index.faiss")
    with open("../output/text_chunks.pkl", "rb") as f:
        text_chunks = pickle.load(f)
except Exception as e:
    logger.error(f"Error loading RAG data: {e}")
    raise

# 🔍 Improved keyword-based and semantic filter
@lru_cache(maxsize=100)
def is_python_question(query, threshold=0.7):
    """Check if the query is Python-related using keywords and semantic similarity."""
    python_keywords = [
        'python', 'list', 'dict', 'function', 'loop', 'variable', 'string', 'class',
        'import', 'lambda', 'def', 'tuple', 'set', 'int', 'float', 'bool', 'syntax',
        'error', 'numbers', 'numeric', 'arithmetic', 'types', 'math', 'operators',
        'if', 'elif', 'else', 'while', 'for', 'break', 'continue', 'input', 'print',
        'type', 'conversion', 'indexing', 'slicing', 'concatenation', 'password'
    ]
    query_lower = query.lower()
    keyword_match = any(keyword in query_lower for keyword in python_keywords)
    
    # Semantic check using embedding similarity
    q_emb = embed_model.encode([query], convert_to_numpy=True)
    avg_emb = np.mean(embed_model.encode(python_keywords, convert_to_numpy=True), axis=0)
    similarity = np.dot(q_emb, avg_emb.T) / (np.linalg.norm(q_emb) * np.linalg.norm(avg_emb))
    
    return keyword_match or similarity > threshold

def retrieve_relevant_context(query, top_k=3, min_similarity=0.5):
    """Retrieve relevant textbook chunks with similarity filtering."""
    try:
        q_emb = embed_model.encode([query], convert_to_numpy=True)
        D, I = index.search(q_emb, top_k)
        retrieved_chunks = []
        for i, dist in zip(I[0], D[0]):
            # Convert L2 distance to cosine similarity (approximation)
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

# 💬 Create the prompt with textbook context
def generate_rag_prompt(question, context):
    prompt = f"""
You are a helpful and patient Python tutor. Use the following textbook excerpts to answer the question. If the context is insufficient, provide a general answer but note the limitation.

Context:
{context}

Question:
{question}

Requirements:
- Provide a detailed explanation based on the context, supplemented by relevant general knowledge if needed.
- Include working, well-commented Python code if applicable.
- List references to textbook pages from the context and general concepts used.
- Format the response with sections: Explanation, Code (if applicable), References.
- Keep the response concise and focused on the question.

Example output:
AI Python Tutor says:
Explanation
This code/example demonstrates a key Python concept. We start by [briefly describe the initial step or purpose, e.g., defining a variable or using a function], which is essential for [explain its purpose, e.g., storing data or performing a task]. The [describe a main structure, e.g., loop or conditional] allows [explain what it does, e.g., repeating an action or making a decision], as referenced in the textbook context. If needed, general Python knowledge is added to clarify [e.g., syntax or behavior]. This helps you learn [list learning outcomes, e.g., variable usage, control flow].

Code
# Example code for the concept
[insert generic or topic-specific code here, e.g., variable = 10]
[describe what the code does, e.g., a = input("Enter value: ")]
[explain the logic, e.g., if a > 0: print("Positive")]

References

[Page X]: [Description of textbook reference, e.g., introduction to variables].
General: [List relevant concepts, e.g., variables, input/output, conditionals].
"""
    return prompt

# 🎯 Ask the model with context + question
def get_tutor_reply_with_rag(question):
    try:
        context = retrieve_relevant_context(question)
        prompt = generate_rag_prompt(question, context)
        response = client.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        logger.error(f"Error getting tutor reply: {e}")
        return f"⚠️ An error occurred: {e}"

# 🖥️ Interactive CLI
def main():
    print("""
🤖 Welcome to AI Python Tutor with RAG!
Ask Python-related questions based on the textbook "Python Programming".
Example questions:
- What is a Python list?
- How do I write a function in Python?
- Can you show me a Python password game?
Type 'exit' to quit.
""")
    while True:
        user_question = input("Your question: ").strip()
        if user_question.lower() == "exit":
            print("👋 Goodbye!")
            break
        if not user_question:
            print("\n🚫 Please enter a valid question.\n")
            print("-" * 40 + "\n")
            continue
        if not is_python_question(user_question):
            print("\n🚫 Please ask a Python-related question. Try 'What is a Python list?' or 'How do I write a loop?'.\n")
            print("-" * 40 + "\n")
            continue

        reply = get_tutor_reply_with_rag(user_question)
        print("\nAI Python Tutor says:\n")
        print(reply)
        print("\n" + "-" * 40 + "\n")

if __name__ == "__main__":
    main()