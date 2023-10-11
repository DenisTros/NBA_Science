from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd
import requests
from PIL import Image
from io import BytesIO
import unidecode
import os
import sys
import unicodedata


def scrape_nba_finals(sample= 10):
    # URL to scrape
    url = "https://www.basketball-reference.com/playoffs/"

    html = urlopen(url)
            
    # create beautiful soup object from HTML
    soup = BeautifulSoup(html, features="html.parser")

    # use getText()to extract the headers into a list
    headers = [th.getText() for th in soup.findAll('tr', limit=2)[1].findAll('th')]

    # get rows from table
    rows = soup.findAll('tr')[2:]
    rows_data = [[td.getText() for td in rows[i].findAll('td')]
                        for i in range(len(rows))]
    # if you print row_data here you'll see an empty row
    # so, remove the empty row
    rows_data.pop(20)
    # for simplicity subset the data for only 39 seasons
    rows_data = rows_data[0:sample]

    last_year = 2023
    for i in range(0, len(rows_data)):
        rows_data[i].insert(0, last_year)
        last_year -=1


    nba_finals = pd.DataFrame(rows_data, columns = headers)

    return nba_finals

# create a function to scrape team performance for multiple years
def scrape_NBA_team_data(years = [2017, 2018]):
    
    final_df = pd.DataFrame(columns = ["Year", "Team", "W", "L",
                                       "W/L%", "GB", "PS/G", "PA/G",
                                       "SRS", "Playoffs",
                                       "Losing_season"])
    
    # loop through each year
    for y in years:
        # NBA season to scrape
        year = y
        
        # URL to scrape, notice f string:
        url = f"https://www.basketball-reference.com/leagues/NBA_{year}_standings.html"
        
        # collect HTML data
        html = urlopen(url)
        
        # create beautiful soup object from HTML
        soup = BeautifulSoup(html, features="html.parser")
        
        # use getText()to extract the headers into a list
        titles = [th.getText() for th in soup.findAll('tr', limit=2)[0].findAll('th')]
        
        # first, find only column headers
        headers = titles[1:titles.index("SRS")+1]
        
        # then, exclude first set of column headers (duplicated)
        titles = titles[titles.index("SRS")+1:]
        
        # next, row titles (ex: Boston Celtics, Toronto Raptors)
        try:
            row_titles = titles[0:titles.index("Eastern Conference")]
        except: row_titles = titles

        # remove the non-teams from this list
        for i in headers:
            row_titles.remove(i)

        divisions = ["Atlantic Division", "Central Division",
                     "Southeast Division", "Northwest Division",
                     "Pacific Division", "Southwest Division",
                     "Midwest Division"]
        
        [row_titles.remove(x) for x in row_titles if x in divisions ]

        # Separate east and west 
        east_titles = row_titles[:row_titles.index('Western Conference')]
        east_titles = [e.replace('*','') for e in east_titles] 
        west_titles = row_titles[row_titles.index('Western Conference')+1:]
        west_titles = [w.replace('*','') for w in west_titles]

        row_titles.remove("Western Conference")
        
        # next, grab all data from rows (avoid first row)
        rows = soup.findAll('tr')[1:]
        team_stats = [[td.getText() for td in rows[i].findAll('td')]
                    for i in range(len(rows))]
        
        # remove empty elements
        team_stats = [e for e in team_stats if e != []]

        # only keep needed rows
        team_stats = team_stats[0:len(row_titles)]
        
        # add team name to each row in team_stats
        for i in range(0, len(team_stats)):
            team_stats[i].insert(0, row_titles[i])
            team_stats[i].insert(0, year)
            
        # add team, year columns to headers
        headers.insert(0, "Team")
        headers.insert(0, "Year")
        
        # create a dataframe with all aquired info
        year_standings = pd.DataFrame(team_stats, columns = headers)
        
        # add a column to dataframe to indicate playoff appearance
        year_standings["Playoffs"] = ["Y" if "*" in ele else "N" for ele in year_standings["Team"]]
        # remove * from team names
        year_standings["Team"] = [ele.replace('*', '') for ele in year_standings["Team"]]
        # add losing season indicator (win % < .5)
        year_standings["Losing_season"] = ["Y" if float(ele) < .5 else "N" for ele in year_standings["W/L%"]]
        
        # append new dataframe to final_df
        final_df = pd.concat([final_df, year_standings], ignore_index=True)
        final_df = final_df.drop(columns=['Year'])

        east_df = final_df[final_df.Team.isin(east_titles)].sort_values(by='W',ascending=False)
        west_df = final_df[final_df.Team.isin(west_titles)].sort_values(by='W',ascending=False)
        
    # export to csv
    return east_df, west_df


def get_player_image_url(player):
    """ Return first result of google images for indicated player """

    url = f'https://www.google.com/search?q={player}&tbm=isch'
    content = requests.get(url).content
    soup = BeautifulSoup(content,'lxml')
    images = soup.findAll('img')
    final_url = images[1].get('src')
    return final_url

# Get player stats

def get_player_stats(player,season):

    """ Get player stats indicating name and season (year)"""

    url = f'https://www.basketball-reference.com/leagues/NBA_{season}_per_game.html'

    table_html = BeautifulSoup(urlopen(url),'html.parser').findAll('table')

    df = pd.read_html(str(table_html))[0]
    
    df = df[df.Player.apply(lambda x: x.lower()) == player.lower()]

    final_cols = ['Age', 'Tm','G','PTS','AST', 'TRB', 'STL','BLK','TOV',
                    'MP','FG%','3P%', '2P%', 'eFG%','FT%','PF','Player']
    
    df_player = df[final_cols].set_index('Player').T.reset_index()

    return df_player

# Data for radial plot

def generate_data_for_comparison(player_1_stats, player_2_stats):

    df_1 = player_1_stats
    df_2 = player_2_stats

    df_1.columns = ['index',df_1.index[0]]
    df_2.columns = ['index',df_2.index[0]]

    df_1 = df_1.set_index('index').T
    df_2 = df_2.set_index('index').T

    stats = ['PTS','AST','TRB','STL','BLK', 'TOV']

    df_1 = df_1[stats]
    df_2 = df_2[stats]

    df_1 = df_1.apply(pd.to_numeric, errors='coerce')
    df_2 = df_2.apply(pd.to_numeric, errors='coerce')

    return df_1, df_2