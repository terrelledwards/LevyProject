#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 15 13:13:57 2023

@author: tedwards
"""

import requests
from requests import get
from bs4 import BeautifulSoup
import pandas as pd
import unicodedata, unidecode
import re


def match_lineup_skysports_scrape():
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9',
    'DNT': '1',  # Do Not Track Request Header
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
    }
    df = pd.DataFrame(columns = ["TeamName", "Starter_1" , "Starter_2", "Starter_3", "Starter_4", "Starter_5", "Starter_6", "Starter_7", "Starter_8", "Starter_9", "Starter_10", "Starter_11", "Sub_1", "Sub_2", "Sub_3", "Sub_4", "Sub_5", "Unused_1","Unused_2","Unused_3","Unused_4","Unused_5","Unused_6","Unused_7","Unused_8","Unused_9","Unused_10","Unused_11", "Unused_12","Unused_13","Unused_14","Unused_15","Competition", "Date", "Match"])
    df_two = pd.DataFrame(columns = ["TeamName", "Goal_1", "Goal_2", "Goal_3", "Goal_4", "Goal_5", "Goal_6", "Goal_7", "Goal_8", "Goal_9", "Competition", "Date", "Match" ])
    competitionName = "World Cup 2014, Qualifiers, Europe"
    data_table = pd.read_csv('/Users/tedwards/Downloads/Match Results - World Cup Qualifiers 2014, Europe.csv')
    count = 0
    for index, row in data_table.iterrows():
        match_date = row[4]
        match_name = row[1] + " vs " + row[2]
        search_string = row[6]
        google_string = search_string + "match lineups sky sports"
        google_link = "https://www.google.com/search?q=" + google_string
        r = requests.get(google_link, headers=headers)
        match_link = ""
        print(r.status_code)
        if r.status_code == 200: 
            print("accessed google")
            soup = BeautifulSoup(r.content, 'html.parser')
            first_link_div = soup.find('div', {'class': 'yuRUbf'})
            first_link = first_link_div.find('a', href=True)
            match_link = first_link['href']
            print(match_link)
       
        r = requests.get(match_link, headers=headers)  
        print(r.status_code)
        if r.status_code == 200:
            print("accessed sky")
            soup = BeautifulSoup(r.content, 'html.parser')
            columns = soup.find_all('div', {'class': 'sdc-site-team-lineup__col'})
            for col in columns:
                team_row = []
                team_goals = []
                subs = []
                bench = []
                team_name = col.find('h4', {'class': 'sdc-site-team-lineup__team-name'})
                team_row.append(team_name.text.strip())
                team_goals.append(team_name.text.strip())

                starting_lineup = col.find('dl', {'class': 'sdc-site-team-lineup__players'})
                numbers = starting_lineup.find_all('dt')
                names = starting_lineup.find_all('dd')
                for number, name in zip(numbers, names):
                    starting_initial = name.find('span', {'class': 'sdc-site-team-lineup__player-initial'})
                    player_surname = name.find('span', {'class': 'sdc-site-team-lineup__player-surname'})
                    #print(number.text.strip())
                    player_string = ""
                    if(starting_initial):
                        #print(starting_initial.text.strip())
                        #print(player_surname.text.strip())
                        player_string = number.text.strip() + " " + starting_initial.text.strip() + " " + player_surname.text.strip()
                    else:
                        #print(player_surname.text.strip())
                        player_string = number.text.strip() + " "  + player_surname.text.strip()

                    team_row.append(player_string)
                    goal_scorer_check = name.find('span', {'class': 'sdc-site-team-lineup__item-event-icon sdc-site-team-lineup__item-event-icon--goal'})
                    if(goal_scorer_check):
                        team_goals.append(player_string)
                #Bench Check
                substitutes = col.find('dl', {'class': 'sdc-site-team-lineup__players sdc-site-team-lineup__players--subs'})
                numbers_sub = substitutes.find_all('dt')
                names_sub = substitutes.find_all('dd')
                for number, name in zip(numbers_sub, names_sub):
                    starting_initial = name.find('span', {'class': 'sdc-site-team-lineup__player-initial'})
                    player_surname = name.find('span', {'class': 'sdc-site-team-lineup__player-surname'})
                    #print(number.text.strip())
                    player_string = ""
                    if(starting_initial):
                        #print(starting_initial.text.strip())
                        #print(player_surname.text.strip())
                        player_string = number.text.strip() + " " + starting_initial.text.strip() + " " + player_surname.text.strip()
                    else:
                        #print(player_surname.text.strip())
                        player_string = number.text.strip() + " "  + player_surname.text.strip()
                    events_indicator = name.find('ul', {'class': 'sdc-site-team-lineup__events'})
                    if(events_indicator):
                        subs.append(player_string)
                    else: 
                        bench.append(player_string)
                    goal_scorer_check = name.find('span', {'class': 'sdc-site-team-lineup__item-event-icon sdc-site-team-lineup__item-event-icon--goal'})
                    if(goal_scorer_check):
                        team_goals.append(player_string)
                number_of_subs = len(subs)
                for i in range(5-number_of_subs):
                    subs.append("-")
                team_row = team_row + subs + bench
                number_of_players = len(team_row) +3
                for i in range(35-number_of_players):
                    team_row.append("-")
                    
                
                number_of_goals = len(team_goals)
                for i in range(10-number_of_goals):
                    team_goals.append("-")
                #Here we need to pad until the end
                
                #Final things to append
                team_goals.append(competitionName)
                team_goals.append(match_date)
                team_goals.append(match_name)
                team_row.append(competitionName)
                team_row.append(match_date)
                team_row.append(match_name)
                
                print(team_row)
                print(team_goals)
                df.loc[len(df)] = team_row
                df_two.loc[len(df_two)] = team_goals
    return df, df_two

df, df_two = match_lineup_skysports_scrape()
    