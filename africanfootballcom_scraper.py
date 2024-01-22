#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov  3 11:16:53 2023

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
    r = requests.get('https://africanfootball.com/group-standings/864/2019-Africa-Cup-of-Nations-Qualifiers', headers=headers)
    competitionName = "African Cup of Nations, Qualifiers, 2019"
    print(r.status_code)
    if r.status_code == 200:
        print("accessed site")
        soup = BeautifulSoup(r.content, 'html.parser')
        gen_table = soup.find_all('table', {'class': 'table table-condensed no-margin'})
        for table in gen_table:
            rows = table.find_all('tr')
            for row in rows:
                tableDatas = row.find_all("td")
                num_of_tds = len(tableDatas)
                
                if(num_of_tds < 6):
                    count = 0
                    gameDate, team_one, team_two, score = 0,0,0,0
                    #gotDate = False;
                    print("Start")
                    for td in tableDatas:
                        print(td.text.strip())
                        if(count == 0):
                            gameDate = td.text.strip()
                        if(count == 1):
                            team_one = td.text.strip()
                        if(count == 2):
                            t_score = td.text.strip()
                            score =  re.sub(r'\s+', '', t_score)
                        if(count == 3):
                            team_two = td.text.strip()
                        count = count + 1
                    print("End")
                    searchString = str(team_one) + " vs " + str(team_two) + " on " + str(gameDate) + " " + str(competitionName)
                    entry = [team_one, team_two, score, gameDate, competitionName, searchString]
                    df.loc[len(df)] = entry
    return df
df = match_results_scrape()