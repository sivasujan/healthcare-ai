"""Streamlit UI that talks to the MediAssist backend.

This app provides quick access to key backend APIs documented in
the repo (auth, symptom analysis, chat). It's intended as a
starter integration — extend to cover more endpoints as needed.

Run:
    streamlit run streamlit_app.py

Prerequisites:
 - Backend running at http://localhost:8000 (see run.ps1 in repo)
 - Python packages from `requirements.txt`
"""

import json
import requests
import streamlit as st


API_DEFAULT = "http://localhost:8000/api"


def api_post(base, path, token, payload):
    url = base.rstrip("/") + path
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return requests.post(url, headers=headers, json=payload, timeout=30)


def api_get(base, path, token, params=None):
    url = base.rstrip("/") + path
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return requests.get(url, headers=headers, params=params, timeout=30)


def login_ui(base):
    st.subheader("Login")
    email = st.text_input("Email", value="test@example.com")
    password = st.text_input("Password", type="password", value="Test@12345")
    if st.button("Login"):
        try:
            resp = api_post(base, "/auth/login", token=None, payload={"email": email, "password": password})
            data = resp.json()
            if resp.ok and data.get("data"):
                token = data["data"].get("access_token") or data["data"].get("token")
                st.session_state["access_token"] = token
                st.success("Logged in")
            else:
                st.error(data.get("message") or f"Login failed: {resp.status_code}")
        except Exception as e:
            st.error(f"Login error: {e}")


def symptom_ui(base):
    st.subheader("Symptom Analyzer")
    symptoms = st.text_area("Symptoms (comma-separated or free text)")
    age = st.number_input("Age", min_value=0, max_value=120, value=30)
    gender = st.selectbox("Gender", ["male", "female", "other"], index=0)
    if st.button("Analyze Symptoms"):
        if not symptoms:
            st.warning("Enter symptoms first")
            return
        payload = {
            "symptoms": symptoms,
            "age": age,
            "gender": gender,
        }
        try:
            token = st.session_state.get("access_token")
            resp = api_post(base, "/symptom/analyze", token=token, payload=payload)
            data = resp.json()
            if resp.ok:
                st.json(data.get("data") or data)
            else:
                st.error(data.get("message") or f"Error: {resp.status_code}")
        except Exception as e:
            st.error(f"Request failed: {e}")


def chat_ui(base):
    st.subheader("Chat (non-streaming)")
    chat_msg = st.text_input("Message")
    if st.button("Send"):
        if not chat_msg:
            st.warning("Type a message")
            return
        try:
            token = st.session_state.get("access_token")
            resp = api_post(base, "/chat/send", token=token, payload={"message": chat_msg})
            data = resp.json()
            if resp.ok:
                st.json(data.get("data") or data)
            else:
                st.error(data.get("message") or f"Error: {resp.status_code}")
        except Exception as e:
            st.error(f"Chat request failed: {e}")


def main():
    st.set_page_config(page_title="MediAssist — Streamlit UI", layout="wide")
    st.title("MediAssist — Streamlit integration")

    with st.sidebar:
        st.header("Settings")
        base = st.text_input("API base URL", value=API_DEFAULT)
        if "access_token" not in st.session_state:
            st.session_state["access_token"] = None
        st.markdown("---")
        st.write("Demo credentials:")
        st.write("- Email: test@example.com\n- Password: Test@12345")

    col1, col2 = st.columns(2)
    with col1:
        login_ui(base)
        st.markdown("---")
        symptom_ui(base)

    with col2:
        chat_ui(base)
        st.markdown("---")
        st.subheader("Quick health check")
        if st.button("Run emergency check sample"):
            sample = {"symptoms": "chest pain, shortness of breath", "age": 60}
            try:
                token = st.session_state.get("access_token")
                resp = api_post(base, "/emergency/check", token=token, payload=sample)
                st.json(resp.json().get("data") or resp.json())
            except Exception as e:
                st.error(f"Emergency check failed: {e}")


if __name__ == "__main__":
    main()
