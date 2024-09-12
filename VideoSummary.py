import streamlit as st
from pydub import AudioSegment
import tempfile
import os
import google.generativeai as genai

# Configure the Google API key using st.secrets
GOOGLE_API_KEY = "AIzaSyBikV0v1ltCUIsVoLProMqJgx88fXNr6T0"
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY


# Function to get chatbot response
def get_bot_response(user_input):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content([
            "This is a chatbot conversation. Please respond to the user's message:",
            user_input
        ])
        return response.text
    except Exception as e:
        st.error(f"Error generating response: {e}")
        return "Sorry, something went wrong."

# Streamlit app interface
st.title("AI Chatbot")

st.write("""
Welcome to the AI Chatbot! Type your message below, and the AI will respond to you.
""")

# Chat history to keep track of conversation
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

# User input form
user_input = st.text_input("You:", key="input")

# Submit button to send user input
if st.button("Send"):
    if user_input:
        # Get the chatbot's response
        bot_response = get_bot_response(user_input)

        # Store the conversation in chat history
        st.session_state["chat_history"].append({"user": user_input, "bot": bot_response})

        # Clear the input field after sending
        st.session_state["input"] = ""

# Display the chat history
if st.session_state["chat_history"]:
    for chat in st.session_state["chat_history"]:
        st.write(f"You: {chat['user']}")
        st.write(f"Bot: {chat['bot']}")
        st.write("---")
