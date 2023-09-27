import streamlit as st
from PIL import Image

image = Image.open('./data/nba.png')

st.markdown("<h1 style='text-align: center;'>NBA Dashboard</h1>", unsafe_allow_html=True)

st.image(image, caption='National Basketball Association')

st.markdown(
"""
## Summary

This is a dashboard that can help teams and players find interesting stats about past and current NBA seasons.

"""
)

st.markdown(
"""
## Index

- Teams
- Players
- NBA Finals

"""
)