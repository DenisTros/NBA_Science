import streamlit as st
from PIL import Image

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

from urllib.request import urlopen
from bs4 import BeautifulSoup

import sys
sys.path.insert(0, './')

from src.scrapper import scrape_nba_finals

finals_table = scrape_nba_finals()

st.table(finals_table)