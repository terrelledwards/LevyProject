#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 12 12:53:05 2024

@author: tedwards
"""

from PyPDF2 import PdfReader 
import re
import pandas as pd
import os
from datetime import datetime
import unicodedata
from collections import Counter

def find_doubles(arr, exclude_indices):
    # Create a set for faster lookup
    exclude_indices_set = set(exclude_indices)

    # Count occurrences of each number, excluding the specified indices
    counts = Counter(arr[index] for index in range(len(arr)) if index not in exclude_indices_set)

    # Find indices where the corresponding values appear an even number of times, excluding the specified indices
    even_occurrence_indices = [index for index in range(len(arr)) 
                               if arr[index] in counts and counts[arr[index]] % 2 == 0 
                               and index not in exclude_indices_set]

    return even_occurrence_indices

def find_non_matching_indices(names, event_indices):
    non_matching_indices = []
    for index in range(len(names)):
        if index not in event_indices:
            non_matching_indices.append(index)
    return non_matching_indices

def find_non_matching_indices_bench(names, event_indices, even_indices):
    non_matching_indices = []
    for index in range(len(names)):
        if index not in event_indices and index not in even_indices:
            non_matching_indices.append(index)
    return non_matching_indices

def find_matching_event_indices(starters, bench):
    return [i for i, event in enumerate(starters) if event in bench]

def check_for_colon(line, count):
    if ':' in line:
        count += 1
    return count

def multiple_events(string):
    return ',' in string

def event_check(string):
    # Regular expression to find ':' or '-'
    pattern = r'[:\-]'
    return not bool(re.search(pattern, string))

def extract_up_to_last_apostrophe(s):
    # Regular expression pattern
    pattern = r"^(.*?)'[^']*$"
    match = re.match(pattern, s)
    
    if match:
        return match.group(1) + "'"
    else:
        return ""

def extract_events(line):
    events = line.split(")")
    return events[1] if events else ""

def extract_numbers(time_str):
    # Split the string by commas to separate different time values
    time_values = time_str.split(',')
    # Process each time value to calculate its total minutes
    new_res = []
    for value in time_values:
        #print(value)
        value = value.strip()  # Remove leading and trailing spaces
        new_res.append(value)
    return new_res

"""
def extract_numbers(string):
    return [int(num) for num in re.findall(r'\d+', string)]
"""
def has_special_characters(string):
    # Regular expression to check for characters outside the standard ASCII range
    return bool(re.search(r'[^\x00-\x7F]', string))
"""
def refine_name(name):
    # Step 1: Remove double spaces
    name = re.sub(r'\s{2,}', ' ', name)

    # Step 2: Remove space to the left of a special character and space to the right if the next letter is lowercase
    # Pattern explanation: 
    # - (?<=\s) checks for a preceding space without including it in the match.
    # - ([a-zà-ž]) matches a lowercase special character.
    # - \s? checks for an optional following space.
    # - (?=[a-z]) checks if the next character is lowercase without including it in the match.
    name = re.sub(r'(?<=\s)([a-zà-ž])\s?(?=[a-z])|(?<=\s)([a-zà-ž])', r'\1\2', name)

    return name
"""
def refine_name(s):
    new_string = []
    i = 0
    length = len(s)

    while i < length:
        c = s[i]

        if c == ' ':
            # Look ahead for the next non-space character
            j = i + 1
            while j < length and s[j] == ' ':
                j += 1

            # If next non-space character is uppercase, keep one space
            if j < length and s[j].isupper():
                new_string.append(' ')

            # Skip all spaces (if next non-space character is lowercase or end of string)
            i = j - 1
        else:
            # Add the current non-space character
            new_string.append(c)

        i += 1

    return ''.join(new_string)

def extract_name_and_jersey_number(line):
    # Extracting leading jersey number
    jersey_number_match = re.match(r'^[\d\s]+', line)
    jersey_number = ''.join(jersey_number_match.group(0).split()) if jersey_number_match else ""
    # Removing jersey number and position code
    line_without_number_and_position = re.sub(r'^[\d\s]+[A-Z]{3}', '', line)
    # Extracting player name
    name_match = re.match(r'([^\(]+)', line_without_number_and_position)
    name = name_match.group(0).strip() if name_match else ""
    return jersey_number, name

def is_valid_player_line(line):
    return bool(re.search(r"\('\d{2}\)", line))

def team_split_string(s):
    pattern = r'([a-zA-Z &\'.*-]+?)\s*(\d+\s*-\s*\d+)\s*([a-zA-Z &\'.*-]+)'
    match = re.match(pattern, s)
    
    if match:
        matches = match.groups()
        return matches[0], matches[2]
    else:
        before_first_number = re.search(r'^(.*?)\d', s)
        before_first_number = before_first_number.group(1).strip() if before_first_number else ""
    
        # Extract words after the last number
        after_last_number = re.search(r'\d\s*([a-zA-Z]+)$', s)
        after_last_number = after_last_number.group(1).strip() if after_last_number else ""

        if(before_first_number != "" and after_last_number != ""): return before_first_number, after_last_number
        return "None", None, "None"

def extract_file_scores(filename):
    # Regular expression to match the score pattern
    #score_pattern = r',\s*(\d+)\s*-\s*(\d+)\s*-sheet'
    score_pattern = r',\s*(\d+)\s*-\s*(\d+)(\s*\(.*?\))?\s*-sheet'
    match = re.search(score_pattern, filename)

    if match:
        home_team_listed_score = int(match.group(1))
        away_team_listed_score = int(match.group(2))
        return home_team_listed_score, away_team_listed_score
    else:
        return "None", "None"
    
def remove_accents(input_str):
    # Normalize the string to decompose the characters with accents
    # into characters and combining marks
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    # Return the string with only the base characters
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])

def extract_date(file_path):
    match = re.search(r'/(\d{2}-\d{2}-\d{4}) ', file_path)
    return match.group(1) if match else None
def classify_date(date_str):
    # Convert the string to a datetime object
    date = datetime.strptime(date_str, "%d-%m-%Y")

    # Define the comparison dates
    
    #"""
    #Gold Cup Dates
    date_2015 = datetime.strptime("07-07-2015", "%d-%m-%Y")
    date_2017 = datetime.strptime("07-07-2017", "%d-%m-%Y")
    date_2019 = datetime.strptime("15-06-2019", "%d-%m-%Y")
    date_2021 = datetime.strptime("10-07-2021", "%d-%m-%Y")
    date_2023 = datetime.strptime("16-06-2023", "%d-%m-%Y")
    
    if date < date_2015:
        return "2013"
    elif date < date_2017:
        return "2015"
    elif date < date_2019:
        return "2017"
    elif date < date_2021:
        return "2019"
    elif date < date_2023:
        return "2021"
    else:
        return "2023"
    #"""
    
    """
    #WorldCup Dates
    date_2014 = datetime.strptime("12-06-2014", "%d-%m-%Y")
    date_2018 = datetime.strptime("14-06-2018", "%d-%m-%Y")
    date_2022 = datetime.strptime("20-11-2022", "%d-%m-%Y")
    
    if date < date_2014:
        return "2014"
    elif date < date_2018:
        return "2018"
    elif date < date_2022:
        return "2022"
    else:
        return "2026"
    """
    """
    #AFCON Dates
    date_2015 = datetime.strptime("09-02-2015", "%d-%m-%Y")
    date_2017 = datetime.strptime("06-02-2017", "%d-%m-%Y")
    date_2019 = datetime.strptime("19-07-2019", "%d-%m-%Y")
    date_2021 = datetime.strptime("06-02-2021", "%d-%m-%Y")
    # Compare and return the corresponding year
    if date < date_2015:
        return "2015"
    elif date < date_2017:
        return "2017"
    elif date < date_2019:
        return "2019"
    elif date < date_2021:
        return "2021"
    else:
        return "2023"
    """
def scrape_pdfs(files):
    df = pd.DataFrame(columns = ["TeamName", "Starter_1" , "Starter_2", "Starter_3", "Starter_4", "Starter_5", "Starter_6", "Starter_7", "Starter_8", "Starter_9", "Starter_10", "Starter_11", "Sub_1", "Sub_2", "Sub_3", "Sub_4", "Sub_5", "Unused_1","Unused_2","Unused_3","Unused_4","Unused_5","Unused_6","Unused_7","Unused_8","Unused_9","Unused_10","Unused_11", "Unused_12","Unused_13","Unused_14","Unused_15","Competition", "Date", "Match"])
    df_two = pd.DataFrame(columns = ["TeamName", "Goal_1", "Goal_2", "Goal_3", "Goal_4", "Goal_5", "Goal_6", "Goal_7", "Goal_8", "Goal_9", "Goal_10", "Competition", "Date", "Match", "Requires Check" ])
    df_three = pd.DataFrame(columns = ["Team 1", "Team 2", "Result", "Date", "Competition"])
    # creating a pdf reader object 
    for file in files:
        if(file != ".DS_Store"):
            full_path = folder_path+ "/" + file
            reader = PdfReader(full_path)
            page = reader.pages[0] 
            text = page.extract_text() 
            text_as_strings = text.split("\n")
            home_team_listed_score, away_team_listed_score = extract_file_scores(file)
            print(file)
            print("Home Team listed score: ", home_team_listed_score)
            print("Away Team listed score: ", away_team_listed_score)
            
            count = 0
            colon_count = 0
            team_one, team_two = "", ""
            competition_string = "Gold Cup,"
            #competition_string = "World Cup Intercontinental Playoffs,"
            match_date = extract_date(full_path)
            competition_year = classify_date(match_date)
            competitionName = competition_string + " " + competition_year
            match_name = ""
            finished_work = False
            prev_line = ""

            team_one_lineup = []
            team_one_subs = []
            team_one_bench = []
            team_one_goals = []
            team_two_lineup = []
            team_two_subs = []
            team_two_bench = []
            team_two_goals = []
            
            team_one_starter_events = []
            team_two_starter_events = []
            team_one_bench_events = []
            team_two_bench_events = []     
            team_one_starter_events_names = []
            team_two_starter_events_names = []
            team_one_bench_events_names = []
            team_two_bench_events_names = []
            team_one_bench_events_val = []
            team_two_bench_events_val = []
            
            match_report = []
            
            for s in text_as_strings:
                name, jersey_num = "", ""
                print(s)
                if count == 2:
                    unaccented_s = remove_accents(s)
                    team_one, team_two = team_split_string(unaccented_s)
                    team_one_lineup.append(team_one)
                    team_one_goals.append(team_one)
                    team_two_lineup.append(team_two)
                    team_two_goals.append(team_two)
                if count >= 4: #and not reached_end:
                    is_good_line = is_valid_player_line(s)
                    if(is_good_line):
                        print(s)
                        jersey_num, name = extract_name_and_jersey_number(s)
                        if has_special_characters(name): name = refine_name(name)
                        full_name = jersey_num + " " + name
                        
                        if(colon_count == 0):
                            team_one_lineup.append(full_name)
                            events = extract_events(s)
                            events_cleaned = extract_up_to_last_apostrophe(events)
                            if(events_cleaned != ""): 
                                #event_vals = extract_numbers(events)
                                event_vals = extract_numbers(events_cleaned)
                                print(event_vals)

                                for val in event_vals:
                                    if not val == "":
                                        print(val)

                                        if val in team_one_starter_events: val = str(val) + "-1"
                                        #print("Adding val to starter event. Val: ", val)
                                        team_one_starter_events.append(val)
                                        team_one_starter_events_names.append(full_name)
                        elif(colon_count == 1):
                            events = extract_events(s)
                            print(events)
                            events_cleaned = extract_up_to_last_apostrophe(events)
                            if(events_cleaned != ""): 
                            #if(event_check(events) and events != ""):
                                team_one_subs.append(full_name)
                                #Then they are a sub. Otherwise a bench player.
                                #event_vals = extract_numbers(events)
                                event_vals = extract_numbers(events_cleaned)
                                print(event_vals)

                                for val in event_vals:
                                    if not val == "":
                                        og_val = val
                                        print(val)

                                        if val in team_one_bench_events: val = str(val) + "-1"
                                        #print("Adding val to bench event. Val: ", val)
                                        team_one_bench_events.append(val)
                                        team_one_bench_events_names.append(full_name)
                                        team_one_bench_events_val.append(og_val)
                            else:
                                team_one_bench.append(full_name)
                        elif(colon_count == 2):
                            team_two_lineup.append(full_name)
                            events = extract_events(s)
                            events_cleaned = extract_up_to_last_apostrophe(events)
                            if(events_cleaned != ""): 
                            #if(event_check(events) and events != ""):
                                #event_vals = extract_numbers(events)
                                event_vals = extract_numbers(events_cleaned)
                                print(event_vals)

                                for val in event_vals:
                                    if not val == "":
                                        print(val)

                                        if val in team_two_starter_events: val = str(val) + "-1"
                                        team_two_starter_events_names.append(full_name)
                                        team_two_starter_events.append(val)
                        elif(colon_count == 3):
                            events = extract_events(s)
                            print(events)
                            events_cleaned = extract_up_to_last_apostrophe(events)
                            if(events_cleaned != ""): 
                            #if(event_check(events) and events != ""):
                                team_two_subs.append(full_name)
                                #event_vals = extract_numbers(events)
                                event_vals = extract_numbers(events_cleaned)
                                print(event_vals)

                                for val in event_vals:
                                    if not val == "":
                                        print(val)

                                        og_val = val
                                        if val in team_two_bench_events: val = str(val) + "-1"
                                        team_two_bench_events.append(val)
                                        team_two_bench_events_names.append(full_name)
                                        team_two_bench_events_val.append(og_val)
                            else:
                                team_two_bench.append(full_name)
                    else:
                        if(event_check(s) and multiple_events(s)):
                            #print(prev_line)
                            jersey_num, name = extract_name_and_jersey_number(prev_line)
                            if has_special_characters(name): name = refine_name(name)
                            full_name = jersey_num + " " + name
                            event_vals = extract_numbers(s)
                            yc_check = 0
                            print(event_vals)
                            for val in event_vals:
                                if yc_check > 0:
                                    print(val)
                                    if colon_count == 0 and not val == "":
                                        if val in team_one_starter_events: val = str(val) + "-1"
                                        team_one_starter_events.append(val)
                                        team_one_starter_events_names.append(full_name)
                                    elif colon_count == 1 and not val == "":
                                        og_val = val
                                        if val in team_one_bench_events: val = str(val) + "-1"
                                        team_one_bench_events.append(val)
                                        team_one_bench_events_names.append(full_name)
                                        team_one_bench_events_val.append(og_val)
                                    elif colon_count == 2 and not val == "":
                                        if val in team_two_starter_events: val = str(val) + "-1"
                                        team_two_starter_events_names.append(full_name)
                                        team_two_starter_events.append(val)
                                    elif colon_count == 3 and not val == "":
                                        og_val = val
                                        if val in team_two_bench_events: val = str(val) + "-1"
                                        team_two_bench_events.append(val)
                                        team_two_bench_events_names.append(full_name)
                                        team_two_bench_events_val.append(og_val)
                                yc_check = yc_check + 1
                if count > 5: colon_count = check_for_colon(s, colon_count)
                prev_line = s
                count = count + 1
            if not finished_work:
                # Finding non-matching indices
                # Finding indices of matching events
                print("reached end")
                team_one_starter_events_in_bench = find_matching_event_indices(team_one_starter_events, team_one_bench_events)
                team_two_starter_events_in_bench = find_matching_event_indices(team_two_starter_events, team_two_bench_events)
                team_one_bench_events_in_starter = find_matching_event_indices(team_one_bench_events, team_one_starter_events)
                team_two_bench_events_in_starter = find_matching_event_indices(team_two_bench_events, team_two_starter_events)
                """
                Here I think we need to only check for double events on the bench after getting rid of the matching events with the starters
                """
                team_one_bench_events_in_bench = find_doubles(team_one_bench_events_val, team_one_bench_events_in_starter)
                print(team_one_starter_events)
                print(team_one_bench_events)
                
                print(team_one_starter_events_in_bench)
                print(team_one_bench_events_in_starter)
                
                team_two_bench_events_in_bench = find_doubles(team_two_bench_events_val, team_two_bench_events_in_starter)
                print(team_two_starter_events)
                print(team_two_bench_events)
                
                print(team_two_starter_events_in_bench)
                print(team_two_bench_events_in_starter)
                
                #print(team_one_bench_events_in_bench)
                #print(team_two_bench_events_in_bench)
                
                non_matching_team_one_starters = find_non_matching_indices(team_one_starter_events_names, team_one_starter_events_in_bench)
                non_matching_team_two_starters = find_non_matching_indices(team_two_starter_events_names, team_two_starter_events_in_bench)
                non_matching_team_one_bench = find_non_matching_indices_bench(team_one_bench_events_names, team_one_bench_events_in_starter, team_one_bench_events_in_bench)
                non_matching_team_two_bench = find_non_matching_indices_bench(team_two_bench_events_names, team_two_bench_events_in_starter, team_two_bench_events_in_bench)
                
                for val in non_matching_team_one_starters:
                    team_one_goals.append(team_one_starter_events_names[val])
                for val in non_matching_team_one_bench:
                    team_one_goals.append(team_one_bench_events_names[val])
                num_goals_team_one = len(team_one_goals) -1
                print(num_goals_team_one)
                print(home_team_listed_score)
                number_of_goals = len(team_one_goals)
                for i in range(11-number_of_goals):
                    team_one_goals.append("-")
                
                
                for val in non_matching_team_two_starters:
                    team_two_goals.append(team_two_starter_events_names[val])
                for val in non_matching_team_two_bench:
                    team_two_goals.append(team_two_bench_events_names[val])
                num_goals_team_two = len(team_two_goals)-1
                print(num_goals_team_two)
                print(away_team_listed_score)
                number_of_goals = len(team_two_goals)
                for i in range(11-number_of_goals):
                    team_two_goals.append("-")
                
                
                
                
                
                print(team_one_goals)
                print(team_two_goals)
                number_of_subs = len(team_one_subs)
                for i in range(5-number_of_subs):
                    team_one_lineup.append("-")
                for player in team_two_subs:
                    team_two_lineup.append(player)
                number_of_subs = len(team_two_subs)
                for i in range(5-number_of_subs):
                    team_two_lineup.append("-")
                for player in team_one_bench:
                    team_one_lineup.append(player)
                for player in team_two_bench:
                    team_two_lineup.append(player)
                number_of_players = len(team_one_lineup) +3
                for i in range(35-number_of_players):
                    team_one_lineup.append("-")
                number_of_players = len(team_two_lineup) +3
                for i in range(35-number_of_players):
                    team_two_lineup.append("-")
                match_name = team_one + " vs " + team_two
                
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
                if num_goals_team_one == home_team_listed_score:
                    team_one_goals.append("No")
                else: team_one_goals.append("Yes")
                if num_goals_team_two == away_team_listed_score:
                    team_two_goals.append("No")
                else: team_two_goals.append("Yes")
                
                official_result_match = str(home_team_listed_score) + ":" + str(away_team_listed_score)
                match_report.append(team_one)
                match_report.append(team_two)
                match_report.append(official_result_match)
                match_report.append(match_date)
                match_report.append(competitionName)

                
                if(len(team_one_goals) == 15 and len(team_two_goals) == 15 and match_name != "Gabon vs Morocco" ):#and len(team_one_lineup) ==35 and len(team_two_lineup) ==35):
                    #print("Team One Lineup", team_one_lineup)
                    #print("Team Two Lineup", team_two_lineup)
                    #print("Team One Goals", team_one_goals)
                    #print("Team Two Goals",team_two_goals)
                    print(match_name)
                    df.loc[len(df)] = team_one_lineup
                    df.loc[len(df)] = team_two_lineup
                    df_two.loc[len(df_two)] = team_one_goals
                    df_two.loc[len(df_two)] = team_two_goals
                    df_three.loc[len(df_three)] = match_report
                finished_work = True
    return df, df_two, df_three

folder_path = '/Users/tedwards/Downloads/pdfs for match lineups/Gold Cup'
#folder_path = '/Users/tedwards/Downloads/pdfs for match lineups/WC Intercontinental Playoffs'
# List all files in the folder
files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]    
df, df_two, df_three = scrape_pdfs(files)
