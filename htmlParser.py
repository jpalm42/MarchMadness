import bs4
import requests
import re

# Parse regional HTML sections out a specified table from block of HTML
# Uses <div> attribute 'class' to extract a section of HTML
# Inputs: url (string), div_class_name (string)
# Outputs: sections (list of [<div class> as a beautiful soup object])
def parseRegionsFromHTML(url):

    html = requests.get(url) # retrieve html code from url
    if(html.status_code != 200): # status code = 200 for valid URLs
        print('URL incorrect') # if status code is not 200, end method
        return
    
    soup = bs4.BeautifulSoup(html.content, 'lxml') # create beautifulsoup object
    
    # Parse out all of the <div_class=...> tags in HTML, and specifically look for ones corresponding to keys in provided dictionary
    # Then use BeautiFulSoup's find_parent function to pull the parent div where this div_class appears and assign it as a value to relevant key
    
    all_regions = soup.find_all("div", {"class": "region"})

    # separate regions_block into a list of region sections
    # using "<div class='region'>" as delimiter
    
    return(all_regions)


""" # Function to create/assign column headers for regional games
# Inputs: None
# Outputs: column_headers (list of strings)
def assignHeadersToRegionDiv():



    return(column_headers) """


# Function to parse out rows of data in the provided table
# Inputs: None
# Outputs: data (list of lists)
def parseDataFromHTML(url):
    
    # import list of HTML soups for all 4 regions
    all_regions = parseRegionsFromHTML(url)
    
    # create blank 'list of lists' to hold game data
    data = []
    
    # loop through each region of HTML soup
    for region in all_regions:
        
        # region name can be found within <div> tags as:
        #   <div class="regtitle">WEST</div>
        region_name = region.find("div", {"class" : "regtitle"}).getText()
        
        # region game information can be found within <dl> tags
        region_games = region.findAll("dl")

        # loop through each game in region
        for game in region_games:
            
            game_data = []

            # game_number and round_number can be found within <dl> tags as
            #   <dl id="match2" class="match round1">
            game_number = "n/a"
            if(game.get("id") is not None): game_number = game.get("id")
            round_number = "n/a"
            if(game.get("class") is not None): round_number = game.get("class")[1]
            
            # team_names can be found within <a> tags as
            #   <a href=(url link) title="Oklahoma">
            # add 'n/a' if both teams haven't been announced yet
            team_names = [team_link["title"] for team_link in game.findAll("a")]
            while(len(team_names) < 2): team_names.append("n/a")
            
            # seeding_info can be found as text between <dt> tags as
            #   <dt>1 ILL</br>16 DREX</dt>
            # ignore the team abbreviations and just parse out the seeds
            # use get_text() --> 'separator' to add a space, 'strip' to remove leading/trailing spaces
            # use .split() --> convert space delimited string to list --> ['8', 'OU', '9', 'MIZ']
            seeding_info = game.find("dt").get_text(separator=" ", strip=True).split()
            
            # add 'n/a' if both teams haven't been announced yet
            while(len(seeding_info) < 4): seeding_info.append("n/a")
            # delete abbreviations from seedin_info
            del seeding_info[3], seeding_info[1]
            
            # make new ordered list to hold matchup information
            # [seed1, name1, seed2, name2]
            matchup_info = []
            matchup_info.extend((seeding_info[0], team_names[0], seeding_info[1], team_names[1]))

            date_time_soup = game.find("dd")
            if(date_time_soup) is not None:
                date_time = date_time_soup.get_text(separator=" ", strip=True).split()
            else: date_time = ["n/a", "n/a"]

            game_data = [region_name, round_number, game_number] + matchup_info + date_time
        
            data.append(game_data)
    
    return(data)



bracket_url = "http://www.espn.com/mens-college-basketball/tournament/bracket"

print(parseDataFromHTML(bracket_url))