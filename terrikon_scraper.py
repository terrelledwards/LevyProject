#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 30 13:24:32 2023

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
    df = pd.DataFrame(columns = ["TeamName", "Starter_1" , "Starter_2", "Starter_3", "Starter_4", "Starter_5", "Starter_6", "Starter_7", "Starter_8", "Starter_9", "Starter_10", "Starter_11", "Sub_1", "Sub_2", "Sub_3", "Sub_4", "Sub_5", "Unused_1","Unused_2","Unused_3","Unused_4","Unused_5","Unused_6","Unused_7","Unused_8","Unused_9","Unused_10","Unused_11", "Unused_12","Unused_13","Unused_14","Unused_15","Competition", "Date", "Match"])
    df_two = pd.DataFrame(columns = ["TeamName", "Goal_1", "Goal_2", "Goal_3", "Goal_4", "Goal_5", "Goal_6", "Goal_7", "Goal_8", "Goal_9", "Goal_10", "Competition", "Date", "Match" ])

    r = requests.get('https://terrikon.com/en/worldcup-u20-2023', headers=headers)
    competitionName = "U-20 World Cup 2023"
    print(r.status_code)
    if r.status_code == 200:
        print("accessed site")
        soup = BeautifulSoup(r.content, 'html.parser')
        tables = soup.find_all('table', {'class': 'gameresult'})
        for table in tables:
            rows = table.find_all("tr")
            for row in rows:
                
                teams = row.find_all('td', {'class': 'team'})
                team_one = teams[0].text.strip()
                team_two = teams[1].text.strip()
                
                
                team_one = team_one + " U-20"
                team_two = team_two + " U-20"
                
                
                score = row.find('td', {'class': 'score'})
                first_link = score.find('a', href=True)
                score = score.text.strip()
                match_link = first_link['href']
                gameDate = row.find('td', {'class': 'date'})
                gameDate = gameDate.text.strip()
                match_date = gameDate
                match_name = team_one + " vs " + team_two
                full_match_link = "https://terrikon.com" + match_link
                r = requests.get(full_match_link, headers=headers)
                print(r.status_code)
                if r.status_code == 200:
                    soup = BeautifulSoup(r.content, 'html.parser')
                    goals_head_div = soup.find('div', {'class': 'txt'})
                    goals_divs = goals_head_div.find_all('div')
                    team_one_lineup = []
                    team_one_goals = []
                    team_two_lineup = []
                    team_two_goals = []
                    team_one_lineup.append(team_one)
                    team_one_goals.append(team_one)
                    team_two_lineup.append(team_two)
                    team_two_goals.append(team_two)
                    count = 0
                    for div in goals_divs:
                        if(div.has_attr('style')):
                            div_style_status = div.attrs['style'][0]
                            print(div_style_status)
                            goals_split_pattern = r"\D+(?=\d+')"
                            if(div_style_status == 'f'):
                                print("Start Count",count)
                                if(count == 0):
                                    print("Team One Goals")
                                    goals_team_one = div.text.strip()
                                    goal_scorers = re.findall(goals_split_pattern, goals_team_one)
                                    goal_scorers = [scorer.strip() for scorer in goal_scorers]  # Remove any trailing whitespace
                                    print(goal_scorers)
                                    for scorer in goal_scorers:
                                        team_one_goals.append(scorer)                        
                                    print(goals_team_one)
                                if(count == 1):
                                    print("Team Two Goals")
                                    goals_team_two = div.text.strip()
                                    goal_scorers = re.findall(goals_split_pattern, goals_team_two)
                                    goal_scorers = [scorer.strip() for scorer in goal_scorers]  # Remove any trailing whitespace
                                    print(goal_scorers)
                                    for scorer in goal_scorers:
                                        team_two_goals.append(scorer)
                                    print(goals_team_two)
                                count = count + 1
                                print("End count", count)
                    lineups_div = soup.find('div', {'class': 'game-lineups'})
                    if(lineups_div):
                        lineups = lineups_div.find_all('p')
                        count = 0
                        for lineup in lineups:
                            if count == 0:
                                team_one_lineup_data = lineup.text.strip()
                                print(team_one_lineup_data)
                                # Remove Yellow Cards and following
                                data = re.split("Yellow Cards:", team_one_lineup_data)[0]
                                
                                # Remove parentheses and their contents
                                data = re.sub(r"\(.*?\)", "", data)
                                
                                # Split into starting lineup, substitution, and bench
                                parts = re.split("Substitution:|Bench:", data)
                                
                                starting_lineup = parts[0].split(",")[0:]  # Skip the "Ukraine U20:" part
                                substitution = parts[1].split(",") if len(parts) > 1 else []
                                bench = parts[2].split(",") if len(parts) > 2 else []
                                
                                # Strip whitespace and filter empty strings
                                starting_lineup = [player.strip() for player in starting_lineup if player.strip()]
                                checker_for_first = 0
                                for player in starting_lineup:
                                    if(checker_for_first == 0):
                                        print(player)
                                        temp = player.split(":")
                                        player = temp[1]
                                        checker_for_first = checker_for_first + 1
                                    team_one_lineup.append(player)
                                substitution = [player.strip() for player in substitution if player.strip()]
                                for player in substitution:
                                    team_one_lineup.append(player)
                                number_of_subs = len(substitution)
                                for i in range(5-number_of_subs):
                                    team_one_lineup.append("-")
                                bench = [player.strip() for player in bench if player.strip()]
                                for player in bench:
                                    team_one_lineup.append(player)
                                
                        
                            if count == 1:
                                team_two_lineup_data = lineup.text.strip()
                                print(team_two_lineup_data)
                                data = re.split("Yellow Cards:", team_two_lineup_data)[0]
                                
                                # Remove parentheses and their contents
                                data = re.sub(r"\(.*?\)", "", data)
                                
                                # Split into starting lineup, substitution, and bench
                                parts = re.split("Substitution:|Bench:", data)
                                
                                starting_lineup = parts[0].split(",")[0:]  # Skip the "Ukraine U20:" part
                                substitution = parts[1].split(",") if len(parts) > 1 else []
                                bench = parts[2].split(",") if len(parts) > 2 else []
                                
                                # Strip whitespace and filter empty strings
                                starting_lineup = [player.strip() for player in starting_lineup if player.strip()]
                                checker_for_first = 0
                                for player in starting_lineup:
                                    if(checker_for_first == 0):
                                        temp = player.split(":")
                                        player = temp[1]
                                    checker_for_first = checker_for_first + 1
                                    team_two_lineup.append(player)
                                substitution = [player.strip() for player in substitution if player.strip()]
                                for player in substitution:
                                    team_two_lineup.append(player)
                                number_of_subs = len(substitution)
                                for i in range(5-number_of_subs):
                                    team_two_lineup.append("-")
                                bench = [player.strip() for player in bench if player.strip()]
                                for player in bench:
                                    team_two_lineup.append(player)
                            count = count + 1    
                    
                    number_of_goals = len(team_one_goals)
                    for i in range(11-number_of_goals):
                        team_one_goals.append("-")
                    number_of_goals = len(team_two_goals)
                    for i in range(11-number_of_goals):
                        team_two_goals.append("-")
                    number_of_players = len(team_one_lineup)
                    for i in range(32-number_of_players):
                        team_one_lineup.append("-")
                    number_of_players = len(team_two_lineup)
                    for i in range(32-number_of_players):
                        team_two_lineup.append("-")
                    team_one_lineup.append(competitionName)
                    team_one_lineup.append(match_date)
                    team_one_lineup.append(match_name)
                    team_two_lineup.append(competitionName)
                    team_two_lineup.append(match_date)
                    team_two_lineup.append(match_name)
                    team_one_goals.append(competitionName)
                    team_one_goals.append(match_date)
                    team_one_goals.append(match_name)
                    team_two_goals.append(competitionName)
                    team_two_goals.append(match_date)
                    team_two_goals.append(match_name)
                    
                    print("Team One Lineup", team_one_lineup)
                    print("Team Two Lineup", team_two_lineup)
                    print("Team One Goals", team_one_goals)
                    print("Team Two Goals",team_two_goals)
                    
                    if(len(team_one_goals) <= 14 and len(team_two_goals) <= 14):
                        df.loc[len(df)] = team_one_lineup
                        df.loc[len(df)] = team_two_lineup
                        df_two.loc[len(df_two)] = team_one_goals
                        df_two.loc[len(df_two)] = team_two_goals
        return df, df_two
                    
df, df_two = match_results_scrape()