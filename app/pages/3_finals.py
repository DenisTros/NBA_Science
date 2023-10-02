import streamlit as st
from PIL import Image
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from urllib.request import urlopen
from bs4 import BeautifulSoup
from st_aggrid import AgGrid
import sys
sys.path.insert(0, './')
from src.scrapper import scrape_nba_finals

# Page configuration
st.set_page_config(
    page_title="Finals",
    page_icon="🏀",
    layout="wide",
)

# Intro
st.title('NBA Playoffs leaders in the last 10 years')

# Get Finals MVP data
df = scrape_nba_finals()

df.drop(columns=['Lg'],inplace=True)

# Final table
AgGrid(df)