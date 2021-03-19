import pandas as pd
import htmlParser as parser

url_template = "http://www.espn.com/mens-college-basketball/tournament/bracket/_/id/{year}22/{year}-ncaa-tournament"

def assembleDF(tournament_year):
    url = url_template.format(year=tournament_year)
    games_df = pd.DataFrame(data=parser.compileGameData(url), columns=parser.assignDataHeaders())
    return(games_df)

x = assembleDF("2021")