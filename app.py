import os

from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from google import genai

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Get Gemini API key
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise RuntimeError(
        "GEMINI_API_KEY is missing. "
        "Please create a .env file and add your Gemini API key."
    )

# Create Gemini client
client = genai.Client(api_key=api_key)


# --------------------------------------------------
# SYSTEM PROMPT
# --------------------------------------------------

SYSTEM_PROMPT = """
You are StudyMate AI, a friendly and helpful academic
and technical study assistant.

Your purpose is to help students understand technical
and academic subjects clearly.

Rules:
1. Explain concepts in simple language.
2. Give examples when useful.
3. Use headings and bullet points when appropriate.
4. Be polite and encouraging.
5. If the question is unclear, ask for clarification.
6. Do not pretend to know information you do not know.
7. Focus on helping the student learn.
"""


# --------------------------------------------------
# CONVERSATION STORAGE
# --------------------------------------------------

conversations = {}

# Keep the latest 12 messages
MAX_MESSAGES = 12


# --------------------------------------------------
# HOME PAGE
# --------------------------------------------------

@app.route("/")
def home():
    return render_template("index.html")


# --------------------------------------------------
# CHAT API
# --------------------------------------------------

@app.route("/chat", methods=["POST"])
def chat():

    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "error": "Invalid request."
            }), 400

        message = data.get("message", "").strip()

        conversation_id = data.get(
            "conversation_id",
            "default"
        )

        if not message:
            return jsonify({
                "error": "Please enter a message."
            }), 400

        # Create conversation if it doesn't exist
        if conversation_id not in conversations:
            conversations[conversation_id] = []

        history = conversations[conversation_id]

        # Add user's message
        history.append({
            "role": "user",
            "content": message
        })

        # Context-window management
        recent_history = history[-MAX_MESSAGES:]

        # Convert history into a prompt
        conversation_text = ""

        for item in recent_history:
            role = item["role"]
            content = item["content"]

            if role == "user":
                conversation_text += f"User: {content}\n"

            else:
                conversation_text += f"Assistant: {content}\n"

        # Final prompt
        prompt = f"""
{SYSTEM_PROMPT}

Here is the recent conversation:

{conversation_text}

Now respond to the latest user message.
"""

        # Gemini API request
        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt
        )

        assistant_reply = response.text

        # Save assistant response
        history.append({
            "role": "assistant",
            "content": assistant_reply
        })

        # Keep only recent messages
        if len(history) > MAX_MESSAGES:
            conversations[conversation_id] = (
                history[-MAX_MESSAGES:]
            )

        return jsonify({
            "response": assistant_reply,
            "conversation_id": conversation_id
        })

    except Exception as e:

        print("=" * 60)
        print("GEMINI API ERROR:")
        print(type(e).__name__)
        print(str(e))
        print("=" * 60)

        return jsonify({
            "error":
            "Sorry, the AI service is currently unavailable. "
            "Please try again."
        }), 500


# --------------------------------------------------
# RUN SERVER
# --------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)