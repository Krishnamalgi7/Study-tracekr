import streamlit as st
import time
import re
from utils.ai_client import ClaudeAI


def render_message_content(content):
    """Render message with proper code block handling."""
    try:
        # Split content by code blocks (triple backticks)
        parts = re.split(r'```(\w*)\n?(.*?)```', content, flags=re.DOTALL)

        for i, part in enumerate(parts):
            if i % 3 == 0:
                # Regular text - handle inline code
                if part.strip():
                    # Replace inline code `text` with HTML
                    part = re.sub(r'`([^`\n]+)`', r'<code>\1</code>', part)
                    st.markdown(part, unsafe_allow_html=True)
            elif i % 3 == 2:
                # Code block content
                language = parts[i - 1] if parts[i - 1] else 'python'
                if part.strip():
                    st.code(part.strip(), language=language)
    except Exception as e:
        # Fallback to simple markdown if parsing fails
        st.markdown(content)


def app(storage):
    # --- Modern CSS Styling ---
    st.markdown("""
        <style>
        /* Hide Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .stDeployButton {display: none;}

        /* Main container */
        .block-container {
            padding-top: 1rem !important;
            max-width: 1200px !important;
        }

        /* Chat messages */
        .stChatMessage {
            padding: 1.5rem !important;
            border-radius: 16px !important;
            margin-bottom: 1.5rem !important;
            box-shadow: 0 2px 12px rgba(0,0,0,0.06) !important;
        }

        /* User messages - purple gradient */
        .stChatMessage[data-testid*="user"] {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        }

        .stChatMessage[data-testid*="user"] p {
            color: white !important;
        }

        /* Assistant messages - white */
        .stChatMessage[data-testid*="assistant"] {
            background: white !important;
            border: 1px solid #e2e8f0 !important;
        }

        /* Chat input */
        .stChatInput textarea {
            border-radius: 24px !important;
            border: 2px solid #e2e8f0 !important;
            padding: 12px 20px !important;
            font-size: 1rem !important;
        }

        .stChatInput textarea:focus {
            border-color: #667eea !important;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
        }

        /* Code blocks */
        code {
            background: #f1f5f9 !important;
            padding: 3px 8px !important;
            border-radius: 6px !important;
            font-size: 0.9em !important;
            color: #1e293b !important;
        }

        /* Suggestion chips */
        .suggestion-chip {
            display: inline-block;
            padding: 10px 20px;
            margin: 8px;
            background: white;
            border: 2px solid #e2e8f0;
            border-radius: 24px;
            font-size: 0.95rem;
            color: #475569;
            transition: all 0.3s ease;
            box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        }

        .suggestion-chip:hover {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-color: transparent;
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
        }

        /* Float animation */
        @keyframes float {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-10px); }
        }

        .float-animation {
            animation: float 4s ease-in-out infinite;
        }
        </style>
    """, unsafe_allow_html=True)

    # --- Authentication Check ---
    user = st.session_state.get("user")
    if not user:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("""
                <div style="text-align: center;">
                    <div style="font-size: 80px; margin-bottom: 1rem;">🔒</div>
                    <h2 style="color: #1e293b;">Authentication Required</h2>
                    <p style="color: #64748b;">Please log in to start chatting.</p>
                </div>
            """, unsafe_allow_html=True)
        return

    # --- Header ---
    col1, col2 = st.columns([5, 1])

    with col1:
        message_count = len(st.session_state.get("messages", [])) // 2
        st.markdown(f"""
            <div style="display: flex; align-items: center; gap: 1rem; padding: 0.5rem 0;">
                <div style="font-size: 2rem;">✨</div>
                <div>
                    <div style="font-size: 1.5rem; font-weight: 700; color: #1e293b;">AI Study Companion</div>
                    <div style="font-size: 0.9rem; color: #64748b;">Powered by AI • {message_count} messages</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        if st.button("🗑️ Clear", key="clear_chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

    st.divider()

    # --- Initialize ---
    if "messages" not in st.session_state:
        st.session_state.messages = []

    client = ClaudeAI()

    # --- Welcome Screen or Chat History ---
    if not st.session_state.messages:
        st.markdown("<br><br>", unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1, 3, 1])
        with col2:
            st.markdown("""
                <div style="text-align: center;">
                    <div class="float-animation" style="font-size: 100px; margin-bottom: 1rem;">
                        🎓
                    </div>
                    <h1 style="font-size: 2.5rem; font-weight: 800; 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 1rem;">
                        Hello, Scholar!
                    </h1>
                    <p style="color: #64748b; font-size: 1.2rem; margin-bottom: 2rem;">
                        Ready to unlock your learning potential?
                    </p>
                </div>
            """, unsafe_allow_html=True)

            st.markdown("""
                <div style="text-align: center; margin-top: 2rem;">
                    <div class="suggestion-chip">📚 Create study schedule</div>
                    <div class="suggestion-chip">🧮 Explain concepts</div>
                    <div class="suggestion-chip">💡 Practice questions</div><br>
                    <div class="suggestion-chip">📝 Homework help</div>
                    <div class="suggestion-chip">🎯 Study tips</div>
                </div>
            """, unsafe_allow_html=True)
    else:
        # Display chat history
        for message in st.session_state.messages:
            avatar = "👤" if message["role"] == "user" else "✨"
            with st.chat_message(message["role"], avatar=avatar):
                if message["role"] == "assistant":
                    render_message_content(message["content"])
                else:
                    st.markdown(message["content"])

    # --- Chat Input ---
    if prompt := st.chat_input("Ask me anything about your studies..."):

        # User message
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)

        st.session_state.messages.append({"role": "user", "content": prompt})

        # AI response
        with st.chat_message("assistant", avatar="✨"):
            message_placeholder = st.empty()

            with message_placeholder.container():
                st.markdown("💭 *Thinking...*")

            try:
                response_text = client.ask(prompt)

                # Show typing effect
                full_response = ""
                words = response_text.split()

                for i, word in enumerate(words):
                    full_response += word + " "
                    if i % 5 == 0:
                        with message_placeholder.container():
                            st.markdown(full_response + "▌")
                        time.sleep(0.03)

                # Final render with code blocks
                message_placeholder.empty()
                with message_placeholder.container():
                    render_message_content(response_text)

            except Exception as e:
                error_msg = f"❌ Error: {str(e)}"
                message_placeholder.error(error_msg)
                response_text = error_msg

        # Save to history
        st.session_state.messages.append({
            "role": "assistant",
            "content": response_text
        })
        st.rerun()