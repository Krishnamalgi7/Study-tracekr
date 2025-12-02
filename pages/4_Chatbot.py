import streamlit as st
from utils.ai_client import ClaudeAI

def app(storage):
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.subheader("AI Study Assistant")
    st.write("Ask anything related to your study plans, subjects, time management, or explanations.")

    client = ClaudeAI()

    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    user_input = st.text_area("Ask your question...")

    if st.button("Send"):
        if user_input.strip():
            st.session_state.chat_history.append(("You", user_input))
            response = client.ask(user_input)
            st.session_state.chat_history.append(("AI", response))
            st.rerun()

    for sender, msg in st.session_state.chat_history:
        if sender == "You":
            st.markdown(f"<div class='section-card' style='border-left:4px solid #60a5fa'><b>You:</b> {msg}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='section-card' style='border-left:4px solid #7c3aed'><b>AI:</b> {msg}</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
