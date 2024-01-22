#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec  8 13:01:42 2023

@author: tedwards
"""

import requests
from requests import get
from bs4 import BeautifulSoup
import pandas as pd
import unicodedata, unidecode
import re


def format_string(s):
    # Remove the first 6 characters
    formatted = s[6:]
    # Replace underscores with spaces
    formatted = formatted.replace('_', ' ')
    return formatted

def extract_date(s):
    # Find all occurrences of text within parentheses
    matches = re.findall(r'\(([^)]+)\)', s)
    # Return the first match, or an empty string if no match is found
    return matches[0] if matches else ""

def remove_after_parenthesis(s):
    # Split the string at '(' and take the first part
    return s.split('(')[0].strip()


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
r = requests.get("https://en.wikipedia.org/wiki/Football_at_the_2020_Summer_Olympics_%E2%80%93_Men%27s_tournament_final", headers=headers)
competitionName = "Olympics, 2020"
print(r.status_code)
if r.status_code == 200:
    print("accessed Wiki page")
    soup = BeautifulSoup(r.content, 'html.parser')
    match_boxes = soup.find_all('div', {'class': 'footballbox'})
    lineups = soup.find_all('table', {'width': '100%'})
    for lineup, box in zip(lineups,match_boxes):
        team_one_lineup = []
        team_one_goals = []
        team_two_lineup = []
        team_two_goals = []
        match_name = ""
        lineup_table = lineup.find_all('table')
        date = box.find('div', {'class': 'fdate'})
        if(date): 
            print("The date of the match.")
            date = extract_date(date.text.strip())
            print(date)
        goal_event_box = box.find('table', {'class': 'fevent'})
        if(goal_event_box):
            print("In Goal Event Box")
            team_names = goal_event_box.find_all('span', {'itemprop': 'name'})
            team_names_count = 0
            team_one, team_two = "",""
            for team in team_names:
                if(team_names_count == 0):
                    team_one_lineup.append(team.text.strip())
                    team_one_goals.append(team.text.strip())
                    team_one = team.text.strip()
                    #print("Team One Name:")
                    #print(team.text.strip())
                if(team_names_count == 1):
                    team_two_lineup.append(team.text.strip())
                    team_two_goals.append(team.text.strip())
                    team_two = team.text.strip()
                    #print("Team Two Name:")
                    #print(team.text.strip())
                team_names_count = team_names_count + 1
            match_name = team_one + " vs " + team_two
            print(match_name)
            away_goals = goal_event_box.find('td', {'class': 'fagoal'})
            home_goals = goal_event_box.find('td', {'class': 'fhgoal'})
            
            print("Away Goal Scorers")
            goals_count = 0
            one_goal_away = False
            for child in away_goals.children:
                if child.name == 'a' and goals_count == 0:
                    #Here we are in the case of one goal scorer
                    one_goal_away = True
                    goalscorer_name = away_goals.find('a', href=True)
                    goalscorer_name_parsed = goalscorer_name['title']
                    goalscorer_name_parsed = remove_after_parenthesis(goalscorer_name_parsed)
                    team_two_goals.append(goalscorer_name_parsed)
                    print(goalscorer_name_parsed)
                    
            if one_goal_away == False:
                away_goalscorers = away_goals.find_all('li')
                for goalscorer in away_goals:
                    #goalscorer_name = goalscorer.find('a', href=True)
                    for goalscorer_name in goalscorer.find_all('a', href=True):
                    #if(goalscorer_name):
                        #goalscorer_name_parsed = format_string(goalscorer_name['href'])
                       
                        goalscorer_name_parsed = goalscorer_name['title']
    
                        if(goalscorer_name_parsed != "Penalty kick (association football)" and goalscorer_name_parsed != "Own goal"):
                            goalscorer_name_parsed = remove_after_parenthesis(goalscorer_name_parsed)
                            print(goalscorer_name_parsed)
                            #print(goalscorer_name.text.strip())
                            team_two_goals.append(goalscorer_name_parsed)
            print("Home Goal Scorers")
            goals_count = 0
            one_goal_home = False
            for child in home_goals.children:
                if child.name == 'a' and goals_count == 0:
                    one_goal_home = True
                    goalscorer_name = home_goals.find('a', href=True)
                    goalscorer_name_parsed = goalscorer_name['title']
                    goalscorer_name_parsed = remove_after_parenthesis(goalscorer_name_parsed)
                    team_one_goals.append(goalscorer_name_parsed)
                    print(goalscorer_name_parsed)
        
            if one_goal_home == False:
                home_goalscorers = home_goals.find_all('li')
                for goalscorer in home_goals:
                    #goalscorer_name = goalscorer.find('a', href=True)
                    #if(goalscorer_name):
                    for goalscorer_name in goalscorer.find_all('a', href=True):
                        #goalscorer_name_parsed = format_string(goalscorer_name['href'])
                        goalscorer_name_parsed = goalscorer_name['title']
                        if(goalscorer_name_parsed != "Penalty kick (association football)" and goalscorer_name_parsed != "Own goal"):
                            goalscorer_name_parsed = remove_after_parenthesis(goalscorer_name_parsed)
                            print(goalscorer_name_parsed)
                            #print(goalscorer_name.text.strip())
                            team_one_goals.append(goalscorer_name_parsed)
        lineup_count = 0
        for ls in lineup_table:
            lineup_data = ls.find_all('tr')
            player_count = 0
            for row in lineup_data:
                if(lineup_count == 0):
                    internal_count = 0
                    player_number, player_name = "",""
                    for td in row.find_all('td'):
                        if(player_count != 0 or player_count != 11):
                            if(internal_count == 1):
                                player_number = td.text.strip()
                            if(internal_count == 2):
                                player_name = td.text.strip()
                            internal_count = internal_count + 1
                    if(player_number != "" and player_name != ""):
                        full_player_name = player_number + " " + player_name
                        full_player_name = remove_after_parenthesis(full_player_name)
                        team_one_lineup.append(full_player_name)
                        print(full_player_name)
                if(lineup_count == 1): 
                    internal_count = 0
                    player_number, player_name = "",""
                    for td in row.find_all('td'):
                        if(player_count != 0 or player_count != 11):
                            if(internal_count == 1):
                                player_number = td.text.strip()
                            if(internal_count == 2):
                                player_name = td.text.strip()
                            internal_count = internal_count + 1
                    if(player_number != "" and player_name != ""):
                        full_player_name = player_number + " " + player_name
                        full_player_name = remove_after_parenthesis(full_player_name)
                        team_two_lineup.append(full_player_name)
                        print(full_player_name)
                #rint("Lineup:")
                #print(row.text.strip())
            player_count = player_count + 1
            lineup_count = lineup_count + 1
        number_of_players = len(team_one_lineup) +3
        for i in range(35-number_of_players):
            team_one_lineup.append("-")
        number_of_players = len(team_two_lineup) +3
        for i in range(35-number_of_players):
            team_two_lineup.append("-")
        
        number_of_goals = len(team_one_goals)
        for i in range(10-number_of_goals):
            team_one_goals.append("-")
        number_of_goals = len(team_two_goals)
        for i in range(10-number_of_goals):
            team_two_goals.append("-")
        
        
        team_one_lineup.append(competitionName)
        team_one_lineup.append(date)
        team_one_lineup.append(match_name)
        team_two_lineup.append(competitionName)
        team_two_lineup.append(date)
        team_two_lineup.append(match_name)
        
        team_one_goals.append(competitionName)
        team_one_goals.append(date)
        team_one_goals.append(match_name)
        team_two_goals.append(competitionName)
        team_two_goals.append(date)
        team_two_goals.append(match_name)
        print(team_one_lineup)
        print(team_one_goals)
        df.loc[len(df)] = team_one_lineup
        df.loc[len(df)] = team_two_lineup
        df_two.loc[len(df_two)] = team_one_goals
        df_two.loc[len(df_two)] = team_two_goals
        
   
    print(len(lineups))
    print(len(match_boxes))