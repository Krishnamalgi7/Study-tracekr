import streamlit as st
import time
from utils.ai_client import ClaudeAI


def app(storage):
    # --- Custom CSS for the Gemini Look ---
    # This removes extra padding and styles the chat input area
    st.markdown("""
        <style>
        /* Remove top padding to make it look like an app */
        .block-container {
            padding-top: 2rem !important;
            padding-bottom: 5rem !important;
        }

        /* Style the chat input to look floating and clean */
        .stChatInputContainer {
            padding-bottom: 20px;
            background: linear-gradient(to bottom, transparent, #f8fafc);
        }

        /* Hide the default Streamlit header decoration if visible */
        header {visibility: hidden;}
        </style>
    """, unsafe_allow_html=True)

    # --- Header Section ---
    st.markdown("""
        <h2 style='margin-bottom: 0px;'>✨ AI Study Companion</h2>
        <p style='color: #64748b; font-size: 0.9rem; margin-bottom: 30px;'>Ask me anything about your study plans or subjects.</p>
    """, unsafe_allow_html=True)

    # --- 1. Setup & Authentication ---
    user = st.session_state.get("user")
    if not user:
        st.info("🔒 Please log in to start chatting.")
        return

    # Initialize Chat History in Session State
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Initialize AI Client
    client = ClaudeAI()

    # --- 2. Display Chat History ---
    # If history is empty, show a Gemini-style welcome message
    if not st.session_state.messages:
        st.markdown("""
        <div style="text-align: center; margin-top: 50px; opacity: 0.7;">
            <div style="font-size: 60px;">👋</div>
            <h3>Hello! How can I help you study today?</h3>
            <p>Try asking: <i>"Create a schedule for Python"</i> or <i>"Explain Calculus"</i></p>
        </div>
        """, unsafe_allow_html=True)

    # Render existing messages
    for message in st.session_state.messages:
        # 'role' is either "user" or "assistant"
        with st.chat_message(message["role"], avatar="👤" if message["role"] == "user" else "✨"):
            st.markdown(message["content"])

    # --- 3. Chat Input & Logic ---
    # st.chat_input creates the fixed input bar at the bottom
    if prompt := st.chat_input("Ask a question..."):

        # A. Display User Message
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)

        # Add to history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # B. Display AI Response
        with st.chat_message("assistant", avatar="✨"):
            # Create a placeholder for the "typing" effect
            message_placeholder = st.empty()
            full_response = ""

            with st.spinner("Thinking..."):
                try:
                    # Get response from your existing client
                    response_text = client.ask(prompt)

                    # Optional: Simulate a typing stream effect (looks cooler)
                    for chunk in response_text.split():
                        full_response += chunk + " "
                        time.sleep(0.02)  # Small delay for typing effect
                        message_placeholder.markdown(full_response + "▌")

                    # Final render without cursor
                    message_placeholder.markdown(full_response)

                except Exception as e:
                    message_placeholder.error(f"Error: {str(e)}")
                    full_response = "Sorry, I encountered an error."

        # Add AI response to history
        st.session_state.messages.append({"role": "assistant", "content": full_response})