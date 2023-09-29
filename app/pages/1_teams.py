import streamlit as st
from PIL import Image
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from urllib.request import urlopen
from bs4 import BeautifulSoup
from st_aggrid import AgGrid, GridOptionsBuilder
import sys
sys.path.insert(0, './')
from src.scrapper import scrape_NBA_team_data

st.set_page_config(
    page_title="Teams",
    page_icon="🏀",
    layout="wide",

)


# Intro
st.title('NBA Eastern and Western conference standings by year')

# Select years:
# Crea una tabla para cada conferencia por cada año que selecciones
selected_years = st.multiselect(
    'Select the years you want to see',
        list(range(1990,2024,1)))


# Get teams data
for year in selected_years:
    west, east = scrape_NBA_team_data([year])

    st.markdown(
        f"""
        ### Year: {year}
        """
    )
    c1, c2 = st.columns(2)

    with c1:
        AgGrid(
                west.head(50),
                gridOptions=GridOptionsBuilder.from_dataframe(west).build(),
            )

    with c2:
        AgGrid(east)

# Agregar graficos por equipo