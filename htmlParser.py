import bs4
import requests

# Parse out section of HTML code that contains all bracket-related information
# Uses <div> attribute 'id' to extract bracket section
# Inputs: url (string)
# Outputs: bracket_soup (soup)
def parseBracketFromURL(url):
    html = requests.get(url) # retrieve html code from url
    if(html.status_code != 200): # status code = 200 for valid URLs
        print('URL incorrect') # if status code is not 200, end method
        return
    soup = bs4.BeautifulSoup(html.content, 'lxml') # create beautifulsoup object
    bracket_soup = soup.find('div', {'id': 'bracket'})
    return(bracket_soup)

# Parse out all of the <div class="region"> tags from bracket_soup HTML
# Use BeautiFulSoup's find_parent function to pull the soup for entire region
# Inputs: bracket_soup (soup represeting entire bracket)
# Output: all_regions_soup (soup representing the 4 regions)
def parseBracketRegions(bracket_soup):
    regions = bracket_soup.find_all("div", {"class": "region"})
    final_four = bracket_soup.find_all("div", {"id": "finalfour"})
    bracket_regions = regions.extend(final_four)
    return(bracket_regions)

# Function to parse out region name from soup of individual region
# region_ name can be found within <div> tags as:
#   <div class="regtitle">WEST</div>
# Inputs: soup of individual region
# Outputs: region_name (string)
def parseRegionName(region_soup):
    region_name = region_soup.find("div", {"class" : "regtitle"}).getText()
    return(region_name)

# Function to parse out block of soup that contains all of the games for that region
# region_ game information can be found within <dl> tags
# Inputs: soup of individual region (soup)
# Outputs: soup of all games in region (soup)
def parseGamesFromRegion(region_soup):
    games_soup = region_soup.findAll("dl")
    return(games_soup)


# Function to parse out round# and game# for game provided in soup
# game_number and round_number are attributes of <dl> tag representing a game
#   <dl id="match2" class="match round1">
# Inputs: game_soup (soup of individual game)
# Outputs: [round_number, game_number]
def parseRoundInfoFromGame(game_soup):
    game_number = "n/a"
    if(game_soup.get("id") is not None): game_number = game_soup.get("id")
    round_number = "n/a"
    if(game_soup.get("class") is not None): round_number = game_soup.get("class")[1]
    return([round_number, game_number])


# Function to parse out team names for game provided in soup
# team_names can be found within <a> tags as
#   <a href=(url link) title="Oklahoma">
# add 'n/a' if both teams haven't been announced yet
# Inputs:
# Outputs:
def parseTeamsFromGame(game_soup):
    team_names = [team_link["title"] for team_link in game_soup.findAll("a")]
    while(len(team_names) < 2): team_names.append("n/a")
    return(team_names)


# Function to parse out team seeds for game provided in soup
# seeding_info can be found as text between <dt> tags as
#   <dt>1 ILL</br>16 DREX</dt>
# add 'n/a' if both teams haven't been announced yet
# ignore the team abbreviations and just parse out the seeds
# use get_text() --> 'separator' to add a space, 'strip' to remove leading/trailing spaces
# use .split() --> convert space delimited string to list --> ['8', 'OU', '9', 'MIZ']
def parseSeedsFromGame(game_soup):
    seeding_info = game_soup.find("dt").get_text(separator=" ", strip=True).split()
    while(len(seeding_info) < 4): seeding_info.append("n/a")
    del seeding_info[3], seeding_info[1] # delete abbreviations
    return(seeding_info)


# Function to parse out date and time for game provided in soup
# date and time are found as text inside <dd> tag inside a game
#   <dd>3/20<br/>7:25</dd>
# Inputs: game_soup (soup of individual game)
# Outputs: [date, time]
def parseDateTimeFromGame(game_soup):
    date_time_soup = game_soup.find("dd")
    if(date_time_soup) is not None:
        date_time = date_time_soup.get_text(separator=" ", strip=True).split()
    else: date_time = ["n/a", "n/a"]
    return(date_time)

def parseScoreFromGame(game_soup):
    score

# Function to compile a list of games with all of their metadata
# To be used to assemble a pandas dataframe
# Inputs: url (string of url where bracket is located )
# Outputs data (list where each element is a game represented by its own list of metadata)
def compileGameData(url):
    data = []
    all_regions_soup = parseBracketRegions(parseBracketFromURL(url))
    for region_soup in all_regions_soup:
        region_name = parseRegionName(region_soup)
        games_soup = parseGamesFromRegion(region_soup)
        for game in games_soup:
            round_info = parseRoundInfoFromGame(game) # [round_num, game_num]
            team_names = parseTeamsFromGame(game) # [team1, team2]
            team_seeds = parseSeedsFromGame(game) # [seed1, seed2]
            date_time = parseDateTimeFromGame(game) # [date, time]
            data.append([region_name] + round_info + \
                [team_seeds[0], team_names[0], team_seeds[1], team_names[1]] + date_time)
    return(data)

# Function to assign naming and order of column headers associated with game data
# game_data = [Region, Round#, Game#, Seed, Team, Seed, Team, Date, Time]
# Inputs: none
# Outputs: headers (list of strings)
def assignDataHeaders():
    headers = ['Region', 'Round Number', 'Game Number', 'Seed1', \
        'Team1', 'Seed2', 'Team2', 'Date', 'Time']
    return(headers)