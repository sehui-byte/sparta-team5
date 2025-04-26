import os

import openai
import streamlit as st

os.environ["OPENAI_API_KEY"] = st.secrets["API_KEY"]


