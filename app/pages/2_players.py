import streamlit as st
from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd
import requests
from PIL import Image
from io import BytesIO
from st_aggrid import AgGrid, GridOptionsBuilder
import matplotlib.pyplot as plt
import plotly.express as px

import sys
sys.path.insert(0, './')
from src.scrapper import get_player_image_url, get_player_stats, generate_data_for_comparison
from src.plots import plot_comparison

st.set_page_config(
    page_title="Players",
    page_icon="🏀",
    layout="wide",
)

st.markdown("""
# Players' stats comparison 🏀  
""")

season = st.selectbox('Select first player:',
                    (2020,2021,2022))


c1, c2,c3 = st.columns(3)
with c1:
    player_1 = st.selectbox(
                    'Select first player:',
                    ('Lebron James','Kevin Durant','Stephen Curry','Giannis Antetokounmpo'))
    url = get_player_image_url(player_1)
    im = Image.open(requests.get(url, stream=True).raw)
    st.image(im)

    player_1_stats = get_player_stats(player_1,season)

with c3:
    player_2 = st.selectbox(
                    'Select second player:',
                    ('Stephen Curry','Kevin Durant','Giannis Antetokounmpo','Lebron James'))
    url = get_player_image_url(player_2)
    im = Image.open(requests.get(url, stream=True).raw)
    st.image(im)

    player_2_stats = get_player_stats(player_2,season)

with c2:
    
    player_comparison_table = player_1_stats.merge(player_2_stats,on='index')

    AgGrid(
            player_comparison_table,
            gridOptions=GridOptionsBuilder.from_dataframe(player_comparison_table).build(),
            fit_columns_on_grid_load=True
        )

# Plots

if player_2_stats.shape[1] == 2:
        
    col1, col2 = st.columns(2)

    with col2:

        # Radial chart
        df_1, df_2 = player_1_stats.copy(), player_2_stats.copy()
        df_1_radial, df_2_radial = generate_data_for_comparison(df_1, df_2)
        radar = plot_comparison(df_1_radial, df_2_radial, [player_1,player_2])
        st.pyplot(radar)

    with col1:
            
        # Bar chart
        players_df = player_1_stats.merge(player_2_stats,on='index').set_index('index').T.reset_index()
        players_df = players_df[['Player','PTS','AST','TRB','STL','BLK','TOV','MP','PF']]
        players_df = players_df.melt(id_vars='Player', var_name='Stats', value_name='Averages')
        players_df.Averages = players_df.Averages.apply(pd.to_numeric, errors='coerce')

        fig = px.bar(players_df, x='Stats', y='Averages', color='Player',barmode='group',
                    labels={'Stats': 'Stats', 'Averages': 'Averages'},
                    title='NBA Season Stats by Player',
                    text='Averages',
                    category_orders={'Stats': players_df['Stats'].tolist()})

        # Customize layout and appearance
        fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')
        fig.update_layout(xaxis_title='Stats', yaxis_title='Averages')
        fig.update_xaxes(tickangle=0)  # Rotate x-axis labels if needed
        fig.update_layout(legend=dict(
            yanchor="top",
            y=1.3,
            xanchor="left",
            x=0.4
        ))

        st.plotly_chart(fig,use_container_width=True)
else:
    st.markdown('One of the selected players did not participate in that season')

