from bs4 import BeautifulSoup
from selenium import webdriver
import pandas as pd
import numpy as np

# Parse out section of HTML code that contains all bracket-related information
# Use selenium webdriver to access javascript elements not accessible through HTML alone
# Uses <div> attribute 'data-testid' to extract bracket section
# Inputs: url (string)
# Outputs: bracket_soup (soup)
def parseBracketFromURL(url):
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-extensions')
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1200")
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, features="lxml")
    driver.quit()
    full_bracket = soup.find("div", {"data-testid": "FourRegionBracket"})
    f = open("troubleshootHTML.txt", "w")
    f.write(full_bracket.prettify())
    f.close()
    return(full_bracket)

# Parse out games from Initial 4 regions in Bracket
# Inputs: bracket_soup (soup represeting entire bracket)
# Output: all_regions_soup (soup representing the 4 regions)
def parseFourRegionChunk(full_bracket):
    initial_regions = full_bracket.find_all("div", {"data-testid": "renderRegion"})
    data_regionName = []
    data_roundNumber = []
    data_team1Name = []
    data_team1Seed = []
    data_team1Score = []
    data_team2Name = []
    data_team2Seed = []
    data_team2Score = []
    data_gameStatus = []
    for region in initial_regions:
        region_name = region.find("div").text
        # Find If Round # in Region is Counting Up or Down
        temp_region = region.find("div", {"data-testid": "regionRound"}).parent
        if len(temp_region.div['class']) == 5:
            region_type = "LeftToRight"
        else:
            region_type = "RightToLeft"
        region_rounds = region.find_all("div", {"data-testid": "regionRound"})
        for count, round in enumerate(region_rounds): 
            if region_type == "LeftToRight":
                round_number = count + 1
            else:
                round_number = 4 - count
            region_games = round.select('div[class*=BracketMatchup]')
            for game in region_games:
                game_status = game.select_one('div[class*=BracketCell__Status]').text
                if game_status != '':
                    game_status = game_status.replace("/OT", "")
                else:
                    game_status = np.nan
                game_seeds = []
                game_names = []
                game_scores = []
                teams = game.find_all("div", {"class": "BracketCell__CompetitorItem mb2"})
                if len(teams) > 0:
                    for team in teams:
                        seed = team.select_one('div[class*=BracketCell__Rank]').text
                        if seed != " ":
                            game_seeds.append(seed)
                        else:
                            game_seeds.append(np.nan)
                        
                        name = team.select_one('div[class*=BracketCell__Name]').text
                        if name != " ":
                            game_names.append(name)
                        else:
                            game_names.append(np.nan)
                        
                        score = team.select_one('div[class*=BracketCell__Score]').text
                        if score != " ":
                            game_scores.append(score)
                        else:
                            game_scores.append(np.nan)

                # Check For Play-In Games or TBD Games
                while len(game_seeds) < 2:
                    game_seeds.append(np.nan)
                while len(game_names) < 2:
                    game_names.append(np.nan)
                while len(game_scores) < 2:
                    game_scores.append(np.nan)
                
                data_regionName.append(region_name)
                data_roundNumber.append(round_number)
                data_gameStatus.append(game_status)
                data_team1Seed.append(game_seeds[0])
                data_team1Name.append(game_names[0])
                data_team1Score.append(game_scores[0])
                data_team2Seed.append(game_seeds[1])
                data_team2Name.append(game_names[1])
                data_team2Score.append(game_scores[1]) 
    
    data = {"Region Name": data_regionName,
            "Round Number": data_roundNumber,
            "Team 1 Seed": data_team1Seed,
            "Team 1 Name": data_team1Name,
            "Team 1 Score": data_team1Score,
            "Team 2 Seed": data_team2Seed,
            "Team 2 Name": data_team2Name,
            "Team 2 Score": data_team2Score,
            "Game Status": data_gameStatus}

    df = pd.DataFrame(data)
    return(df)

# Parse out games from Final 4 in Bracket
# Inputs: bracket_soup (soup represeting entire bracket)
# Output: all_regions_soup (soup representing the 4 regions)
def parseFinalFourChunk(full_bracket_soup):
    final_four = full_bracket_soup.find_all("div", {"data-testid": "finalsmatchup"})
    data_regionName = []
    data_roundNumber = []
    data_team1Name = []
    data_team1Seed = []
    data_team1Score = []
    data_team2Name = []
    data_team2Seed = []
    data_team2Score = []
    data_gameStatus = []

    for game in final_four:
        data_regionName.append("Final Four")
        data_roundNumber.append("5")
        game_status = game.select_one('div[class*=BracketCell__Status]').text
        if game_status != '':
            game_status = game_status.replace("/OT", "")
        else:
            game_status = np.nan
        data_gameStatus.append(game_status)
        game_seeds = []
        game_names = []
        game_scores = []
        teams = game.find_all("div", {"class": "BracketCell__CompetitorItem mb2"})
        if len(teams) > 0:
            for team in teams:
                seed = team.select_one('div[class*=BracketCell__Rank]').text
                if seed != " ":
                    game_seeds.append(seed)
                else:
                    game_seeds.append(np.nan)
                
                name = team.select_one('div[class*=BracketCell__Name]').text
                if name != " ":
                    game_names.append(name)
                else:
                    game_names.append(np.nan)
                
                score = team.select_one('div[class*=BracketCell__Score]').text
                if score != " ":
                    game_scores.append(score)
                else:
                    game_scores.append(np.nan)
        
        # Check For Play-In Games or TBD Games
        while len(game_seeds) < 2:
            game_seeds.append(np.nan)
        while len(game_names) < 2:
            game_names.append(np.nan)
        while len(game_scores) < 2:
            game_scores.append(np.nan)
        
        data_team1Seed.append(game_seeds[0])
        data_team1Name.append(game_names[0])
        data_team1Score.append(game_scores[0])
        data_team2Seed.append(game_seeds[1])
        data_team2Name.append(game_names[1])
        data_team2Score.append(game_scores[1]) 

    data = {"Region Name": data_regionName,
            "Round Number": data_roundNumber,
            "Team 1 Seed": data_team1Seed,
            "Team 1 Name": data_team1Name,
            "Team 1 Score": data_team1Score,
            "Team 2 Seed": data_team2Seed,
            "Team 2 Name": data_team2Name,
            "Team 2 Score": data_team2Score,
            "Game Status": data_gameStatus}

    df = pd.DataFrame(data)
    return(df)

# Parse out games from Final 4 in Bracket
# Inputs: bracket_soup (soup represeting entire bracket)
# Output: all_regions_soup (soup representing the 4 regions)
def parseChampionship(full_bracket_soup):
    championship = full_bracket_soup.select_one('div[class*=BracketMatchup--championship]')
    # Discard first 2 layers of hexidecimal codes
    championship = championship.find("div")
    championship = championship.find("div")

    teamsInfo = championship.find_all("div", recursive=False)
    gameData = []
    game_status = np.nan
    if len(teamsInfo) > 0:
        for team in teamsInfo:
            team_data = team.find("div")
            if(team_data is not None):
                unassigned_data = team_data.find_all("span")
                for data_value in unassigned_data:
                    if (data_value.text != '') & (data_value.text != 'TBD'):
                        gameData.append(data_value.text)
            else:
                game_status = team.find("span").text
                if game_status != '':
                    game_status = game_status.replace("/OT", "")
                else:
                    game_status = np.nan

    # Check For Play-In Games or TBD Games
    while len(gameData) < 6:
        gameData.append(np.nan)
    
    team1Seed = gameData[2]
    if type(gameData[1]) != str:
        team1Name = np.nan
    else:
        team1Name = ''.join([i for i in gameData[1] if not i.isdigit()])
    team1Score = gameData[0]
    team2Seed = gameData[5]
    if type(gameData[4]) != str:
        team2Name = np.nan
    else:
        team2Name = ''.join([i for i in gameData[4] if not i.isdigit()])
    team2Score = gameData[3]

    data = {"Region Name": ["Championship"],
            "Round Number": ["6"],
            "Team 1 Seed": [team1Seed],
            "Team 1 Name": [team1Name],
            "Team 1 Score": [team1Score],
            "Team 2 Seed": [team2Seed],
            "Team 2 Name": [team2Name],
            "Team 2 Score": [team2Score],
            "Game Status": [game_status]}
    
    df = pd.DataFrame(data)
    return(df)


def compileBracketData(url):
    bracket_soup = parseBracketFromURL(url)
    regions_games_df = parseFourRegionChunk(bracket_soup)
    final_four_df = parseFinalFourChunk(bracket_soup)
    championship_df = parseChampionship(bracket_soup)
    
    temp_df = regions_games_df.append(final_four_df, ignore_index=True)
    final_df = temp_df.append(championship_df, ignore_index=True)

    final_df[["Round Number", "Team 1 Seed", "Team 1 Score", "Team 2 Seed", "Team 2 Score"]] = \
        final_df[["Round Number", "Team 1 Seed", "Team 1 Score", "Team 2 Seed", "Team 2 Score"]].apply(pd.to_numeric)

    return(final_df)

    
    
