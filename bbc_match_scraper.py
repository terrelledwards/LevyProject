#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov  2 14:27:07 2023

@author: tedwards
"""

import requests
from requests import get
from bs4 import BeautifulSoup
import pandas as pd
import unicodedata, unidecode
import re

def match_results_scrape():
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9',
    'DNT': '1',  # Do Not Track Request Header
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
    }
    df = pd.DataFrame(columns = ["Team 1", "Team 2", "Result", "Date", "Competition", "SearchString"])
    r = requests.get('https://www.bbc.com/sport/football/27187112', headers=headers)
    competitionName = "African Cup of Nations, Qualifiers, 2015"
    print(r.status_code)
    if r.status_code == 200:
        print("accessed site")
        soup = BeautifulSoup(r.content, 'html.parser')
        lines = soup.find_all('li')
        pattern = r"\/"
        pattern_two = r"()"
        for line in lines:
            temp = line.text.strip()
            if re.search(pattern, temp):
                index_of_colon = temp.index(":")
                temp_two = temp[index_of_colon:]
                gameDate = temp[:index_of_colon]
                index_of_dash = temp_two.index("-")
                team_one = temp_two[1:index_of_dash-2]
                team_two = ""
                if temp_two.find("(") != -1:
                    index_of_bracket = temp_two.index("(")
                    team_two = temp_two[index_of_dash+2:index_of_bracket-1]
                else:
                    team_two = temp_two[index_of_dash+2:]
                score = temp_two[index_of_dash-1] + ":" + temp_two[index_of_dash+1]
                #print(gameDate)
                #print(team_one)
                #print(score)
                #print(team_two)
                print(temp)
                searchString = str(team_one) + " vs " + str(team_two) + " on " + str(gameDate) + " " + str(competitionName)
                entry = [team_one, team_two, score, gameDate, competitionName, searchString]
                df.loc[len(df)] = entry
            
    return df
df = match_results_scrape()
    
    