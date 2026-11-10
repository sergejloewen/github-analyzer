import streamlit as st
import requests

st.text_input("Enter GitHub username:", key="username_input")

st.button("Analyze", key="analyze_button")

st.write(requests.response.json())
