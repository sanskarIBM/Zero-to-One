import streamlit as st
import requests

st.title("Self-Healing Test Automation Dashboard")

with st.form("element_form"):
    element_id = st.text_input("Element ID", "elem42")
    submitted = st.form_submit_button("Show Healing Actions & Analytics")

if submitted:
    healings = requests.get(f"http://127.0.0.1:5000/get_healings/{element_id}").json()
    analytics = requests.get(f"http://127.0.0.1:5000/analytics/element/{element_id}").json()
    st.subheader("Healing Actions")
    st.json(healings)
    st.subheader("Element Analytics")
    st.json(analytics)

if st.button("Suggest Locator"):
    suggestion = requests.get(f"http://127.0.0.1:5000/suggest_locator/{element_id}").json()
    st.subheader("Suggested Locator")
    st.json(suggestion)
