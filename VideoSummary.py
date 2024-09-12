import streamlit as st
import google.generativeai as genai
import PyPDF2
import tempfile
import time

GOOGLE_API_KEY = "AIzaSyBikV0v1ltCUIsVoLProMqJgx88fXNr6T0"
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

# Function to get chatbot response
def get_bot_response(user_input, context=""):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = f"User message: {user_input}\nContext from document: {context}\nRespond appropriately."
        response = model.generate_content([prompt])
        return response.text
    except Exception as e:
        st.error(f"Error generating response: {e}")
        return "Sorry, something went wrong."

# Function to read the contents of a PDF file
def read_pdf(file):
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        return ""

# Streamlit app interface
st.title("AI Chatbot with Document Upload")

st.write("""
Welcome to the AI Chatbot! You can upload documents (PDFs, text files), and the bot will use the content to respond.
""")

# Chat history to keep track of conversation
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []
    st.session_state["document_context"] = ""

# Document uploader for PDFs and text files
uploaded_file = st.file_uploader("Upload Document", type=['pdf', 'txt'])

# If a document is uploaded, process it
if uploaded_file is not None:
    if uploaded_file.type == "application/pdf":
        context = read_pdf(uploaded_file)
    elif uploaded_file.type == "text/plain":
        context = uploaded_file.read().decode("utf-8")

    # Save the context of the document for chatbot responses
    st.session_state["document_context"] = context
    st.success("Document uploaded successfully!")
    st.write("Document Content:")
    st.write(context)

# User input form
user_input = st.text_input("You:", key="input")

# Submit button to send user input
if st.button("Send"):
    if user_input:
        document_context = st.session_state.get("document_context", "")

        # Add a spinner to show the API call is being processed
        with st.spinner('Generating response...'):
            start_time = time.time()
            bot_response = get_bot_response(user_input, context=document_context)
            end_time = time.time()

            # Store the conversation in chat history
            st.session_state["chat_history"].append({"user": user_input, "bot": bot_response})

            # Measure the time taken for the response
            st.success(f"Response generated in {round(end_time - start_time, 2)} seconds.")

        # Clear the input field after sending
        st.session_state["input"] = ""

# Display the chat history
if st.session_state["chat_history"]:
    for chat in st.session_state["chat_history"]:
        st.write(f"You: {chat['user']}")
        st.write(f"Bot: {chat['bot']}")
        st.write("---")
