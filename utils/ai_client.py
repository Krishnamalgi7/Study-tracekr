import os
import requests
import streamlit as st

class ClaudeAI:
    def __init__(self):
        key = None
        try:
            key = st.secrets.get("groq_api_key") if hasattr(st, "secrets") else None
        except Exception:
            key = None
        if not key:
            key = os.getenv("GROQ_API_KEY")
        self.api_key = key
        self.url = "https://api.groq.com/openai/v1/chat/completions"
        env_model = os.getenv("GROQ_MODEL") or None
        self.preferred_model = env_model

    def _post(self, model, prompt):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 400
        }
        try:
            res = requests.post(self.url, headers=headers, json=payload, timeout=30)
            return res
        except Exception as e:
            return e

    def ask(self, prompt):
        if not self.api_key:
            return "Groq API key missing. Add it to .env or Streamlit secrets."

        tried = []
        # Build fallback candidate list (preferred model first if provided)
        candidates = []
        if self.preferred_model:
            candidates.append(self.preferred_model)
        candidates.extend([
            "llama-3.1-8b-instant",
            "llama-3.1-70b-versatile",
            "mixtral-8x7b",
            "gemma-2b"
        ])
        # Deduplicate while preserving order
        seen = set()
        candidates = [m for m in candidates if not (m in seen or seen.add(m))]

        last_error_text = None
        for model in candidates:
            tried.append(model)
            resp = self._post(model, prompt)
            if isinstance(resp, Exception):
                last_error_text = f"Request failed: {resp}"
                continue
            if resp.status_code == 200:
                try:
                    body = resp.json()
                    # safe parse of typical chat completion shape
                    if "choices" in body and len(body["choices"])>0:
                        content = body["choices"][0].get("message", {}).get("content") or body["choices"][0].get("delta", {}).get("content")
                        if content:
                            return content
                    # fallback attempt to extract other structures
                    if "text" in body:
                        return body["text"]
                    return "Received unexpected successful response format from Groq."
                except Exception as e:
                    last_error_text = f"Response parse error: {e}"
                    continue
            else:
                # try parse JSON error body
                try:
                    err = resp.json()
                    msg = None
                    if isinstance(err, dict) and "error" in err:
                        # Groq/OpenAI style
                        msg = err["error"].get("message") if isinstance(err["error"], dict) else str(err["error"])
                        code = err["error"].get("code") if isinstance(err["error"], dict) else None
                    else:
                        msg = str(err)
                        code = None
                except Exception:
                    msg = resp.text
                    code = None

                last_error_text = f"API Error with model {model}: {msg}"

                # if model specifically decommissioned, try next candidate
                if code == "model_decommissioned" or (isinstance(msg, str) and "decommissioned" in msg.lower()):
                    continue
                else:
                    # for other errors return that error immediately
                    return last_error_text

        # none succeeded
        return (
            "All attempted models failed. Tried models: "
            + ", ".join(tried)
            + ".\nLast error: "
            + (last_error_text or "unknown")
            + "\n\nRecommendation: open your Groq console, check available models and set the exact model name in your .env as GROQ_MODEL or in Streamlit secrets. Example .env entry:\nGROQ_MODEL=llama-3.1-8b-instant"
        )
