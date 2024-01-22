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
    df_three = pd.DataFrame(columns = ["TeamName", "Shots", "ShotsOnGoal", "Fouls", "Corners", "Offsides", "PossessionPercentage", "Competition", "Date", "Match"])
    df_four = pd.DataFrame(columns = ["Team 1", "Team 2", "Result", "Date", "Competition", "SearchString"])

    competitionName = "World Cup 2018, Qualifiers, Africa"
    #data_table = pd.read_csv('/Users/tedwards/Downloads/Match Results - World Cup Qualifiers 2014, South America.csv')
    count = 0
    r = requests.get("https://m.football-lineups.com/tourn/CAF-Africa-Qualifying-2018/fixture", headers=headers)
    if r.status_code == 200:
        soup = BeautifulSoup(r.content, 'html.parser')
        table = soup.find('table', {'class': 'table table-responsive table-condensed table-hover table-striped'})
        rows = table.find_all('tr')
        row_count = 0
        for row in rows:
            tableDatas = row.find_all("td")
            num_of_tds = len(tableDatas)
            
            if(num_of_tds > 3):
                count = 0
                gameDate, team_one, team_two, match_link = "", "", "", ""
                team_one_lineup = []
                team_one_goals = []
                team_one_stats = []
                team_two_lineup = []
                team_two_goals = []
                team_two_stats = []
                gotDate = False;
                for td in tableDatas:
                    if(td.has_attr('class')):
                        td_class = td.attrs['class'][0]
                        if(td_class == 'mobile-hiddenTD' and gotDate == False):
                            gameDate = td.contents[0].strip()
                            gotDate = True
                        elif(td_class == 'td_resul'):
                            first_link = td.find('a', href=True)
                            match_link = first_link['href']
                    if(td.has_attr('align')):
                        td_align_status = td.attrs['align'][0]
                        if(td_align_status == 'l'):
                            team_two = td.text.strip()
                        if(td_align_status == 'r' and not td.has_attr('class')):
                            team_one = td.text.strip()
            
                match_name = str(team_one) + " vs " + str(team_two)
                team_one_lineup.append(team_one)
                team_two_lineup.append(team_two)
                team_one_goals.append(team_one)
                team_two_goals.append(team_two)
                team_one_stats.append(team_one)
                team_two_stats.append(team_two)

                full_match_link = "https://m.football-lineups.com" + match_link
                if(row_count > 46):
                    r = requests.get(full_match_link, headers=headers)
                    if r.status_code == 200:
                        soup = BeautifulSoup(r.content, 'html.parser')
                        tables = soup.find_all('table')
                        has_stats_table = True
                        if (len(tables) == 5): has_stats_table = False
                        count = 0
                        for table in tables:
                            if count == 0:
                                rows = table.find_all('tr')
                                team_one_goal_count, team_two_goal_count = 0,0
                                for row in rows: 
                                    isGoalScoringRow = False
                                    teamOneScored = True
                                    playerWhoScored = ""
                                   
                                    tableDatas = row.find_all('td')
                                    for td in tableDatas:
                                        if(td.has_attr('align')):
                                            td_align_status = td.attrs['align'][0]
                                            if(td_align_status == 'l'):
                                                temp_name = td.find('a')
                                                if(temp_name): 
                                                    playerWhoScored = temp_name.text.strip()
                                                    teamOneScored = False
                                            if(td_align_status == 'r'): #Team One is Right
                                                temp_name = td.find('a')
                                                if(temp_name): 
                                                    playerWhoScored = temp_name.text.strip()
                                            if(td_align_status == 'c'):
                                                img = td.find('img')
                                                if(img):
                                                    img_title = img.attrs['title'][0]
                                                    print(img_title)
                                                    if(img_title == 'g' or img_title == 'p' or img_title == 'h'):
                                                          isGoalScoringRow = True
                                                          print("Found Goalscoring Row")       
                                    if(isGoalScoringRow):
                                        if(teamOneScored):
                                            print("Goal for Team One")
                                            print(playerWhoScored)
                                            if(team_one_goal_count < 9): team_one_goals.append(playerWhoScored)
                                            team_one_goal_count = team_one_goal_count + 1
                                        else:
                                            print("Goal for Team Two")
                                            print(playerWhoScored)
                                            if(team_two_goal_count < 9): team_two_goals.append(playerWhoScored)
                                            team_two_goal_count = team_two_goal_count + 1

                            if count == 1:
                                rows = table.find_all('tr')
                                for row in rows: 
                                    tableDatas = row.find_all('td')
                                    stats_count = 0
                                    for td in tableDatas:
                                        if(stats_count == 0):
                                            team_one_stats.append(td.text.strip())
                                        if(stats_count == 2):
                                            team_two_stats.append(td.text.strip())
                                        stats_count = stats_count +1
                            if count == 2 or count == 3 or count == 4 or count == 5 or (count > 0 and not has_stats_table):
                                rows = table.find_all('tr')
                                for row in rows: 
                                    tableDatas = row.find_all('td')
                                    stats_count = 0
                                    player_name = ""
                                    player_name, player_number = "", ""
                                    for td in tableDatas:
                                        if(stats_count == 0):
                                            player_number = td.text.strip()
                                        if(stats_count == 1):
                                            player_name = td.text.strip()
                                        stats_count = stats_count +1 
                                    if(stats_count > 0):
                                        full_player_name = player_number + " " + player_name
                                        if(count == 2 or count == 3):
                                            team_one_lineup.append(full_player_name)
                                        else:
                                            team_two_lineup.append(full_player_name)
                            count = count + 1
                        #if count == 0:
                        #Here we need to pad.
                        
                        number_of_goals = len(team_one_goals)
                        for i in range(10-number_of_goals):
                            team_one_goals.append("-")
                        team_one_goals.append(competitionName)
                        team_one_goals.append(gameDate)
                        team_one_goals.append(match_name)
                        
                        number_of_goals = len(team_two_goals)
                        for i in range(10-number_of_goals):
                            team_two_goals.append("-")
                        team_two_goals.append(competitionName)
                        team_two_goals.append(gameDate)
                        team_two_goals.append(match_name)
                        
                        stats_present = len(team_one_stats)
                        for i in range(7-stats_present):
                            team_one_stats.append("-")
                        team_one_stats.append(competitionName)
                        team_one_stats.append(gameDate)
                        team_one_stats.append(match_name)
                        
                        stats_present = len(team_two_stats)
                        for i in range(7-stats_present):
                            team_two_stats.append("-")
                        team_two_stats.append(competitionName)
                        team_two_stats.append(gameDate)
                        team_two_stats.append(match_name)
                        
                        num_players = len(team_one_lineup)
                        for i in range(32-num_players):
                            team_one_lineup.append("-")
                        team_one_lineup.append(competitionName)
                        team_one_lineup.append(gameDate)
                        team_one_lineup.append(match_name)
                        
                        num_players = len(team_two_lineup)
                        for i in range(32-num_players):
                            team_two_lineup.append("-")
                        team_two_lineup.append(competitionName)
                        team_two_lineup.append(gameDate)
                        team_two_lineup.append(match_name)
                            #Blank document. Need to pad all tables. 
                        
                        print("Lineups")
                        print(team_one_lineup)
                        print(team_two_lineup)
                        print("Stats")
                        print(team_one_stats)
                        print(team_two_stats)
                        print("Goals")
                        print(team_one_goals)
                        print(team_two_goals)
    
                        df.loc[len(df)] = team_one_lineup
                        df.loc[len(df)] = team_two_lineup
                        df_two.loc[len(df_two)] = team_one_goals
                        df_two.loc[len(df_two)] = team_two_goals
                        #df_three.loc[len(df_three)] = team_one_stats
                        #df_three.loc[len(df_three)] = team_two_stats
                row_count = row_count + 1

    return df, df_two#, df_three
#df, df_two, df_three = match_lineup_skysports_scrape()
df, df_two = match_lineup_skysports_scrape()
        
        
"""
    print(match_link)
for index, row in data_table.iterrows():
    r = requests.get(, headers=headers)
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
        print("accessed football-lineups")
        soup = BeautifulSoup(r.content, 'html.parser')
        soup = BeautifulSoup(r.content, 'html.parser')
        table = soup.find('table', {'class': 'table table-responsive table-condensed table-hover table-striped'})
        
        
        
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
"""