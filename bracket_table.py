import htmlParser as parser

import pandas as pd
import numpy as np
import gspread
from gspread_dataframe import set_with_dataframe



url_template = "https://www.espn.com/mens-college-basketball/bracket/_/season/{year}"

def assembleDF(tournament_year):
    url = url_template.format(year=tournament_year)
    games_df = pd.DataFrame(data=parser.compileBracketData(url))
    games_df.sort_values(by=['Round Number', 'Region Name', 'Team 1 Seed'], inplace=True, ignore_index = True)
    games_df.to_excel("troubleshootDataFrame.xlsx")
    final_df = addCustomColumns(games_df)
    final_df.to_excel("Results.xlsx")
    uploadToGoogle(final_df)
    return(final_df)

def addWinnerColumn(df):
    conditions = [df['Team 1 Score'] > df['Team 2 Score'], df['Team 1 Score'] < df['Team 2 Score']]
    choices = [df['Team 1 Name'], df['Team 2 Name']]
    df['Winner'] = np.select(conditions, choices, default = np.nan)
    return(df)

def addLoserColumn(df):
    conditions = [df['Team 1 Score'] > df['Team 2 Score'], df['Team 1 Score'] < df['Team 2 Score']]
    choices = [df['Team 2 Name'], df['Team 1 Name']]
    df['Loser'] = np.select(conditions, choices, default = np.nan)
    return(df)

def addFavoriteUnderdogColumn(df):
    conditions = [
        (df['Team 1 Score'] > df['Team 2 Score']) & (df['Team 1 Seed'] > df['Team 2 Seed']), \
        (df['Team 1 Score'] > df['Team 2 Score']) & (df['Team 2 Seed'] > df['Team 1 Seed']), \
        (df['Team 2 Score'] > df['Team 1 Score']) & (df['Team 1 Seed'] > df['Team 2 Seed']), \
        (df['Team 2 Score'] > df['Team 1 Score']) & (df['Team 2 Seed'] > df['Team 1 Seed'])]
    choices = [
        'Underdog',\
        'Favorite',\
        'Favorite',\
        'Underdog'
    ]
    df['Fav/Dog'] = np.select(conditions, choices, default = np.nan)
    return(df)

def addPointMargin(df):
    conditions = [df['Team 1 Score'] > df['Team 2 Score'], df['Team 1 Score'] < df['Team 2 Score']]
    choices = [df['Team 1 Score'] - df['Team 2 Score'], df['Team 2 Score'] - df['Team 1 Score']]
    df['Point Margin'] = np.select(conditions, choices, default = np.nan)
    return(df)

def addSeedMargin(df):
    conditions = [df['Team 1 Seed'] > df['Team 2 Seed'], df['Team 1 Seed'] < df['Team 2 Seed']]
    choices = [df['Team 1 Seed'] - df['Team 2 Seed'], df['Team 2 Seed'] - df['Team 1 Seed']]
    df['Seed Margin'] = np.select(conditions, choices, default = np.nan)
    return(df)   

def addCustomColumns(df):
    df1 = addWinnerColumn(df)
    df2 = addLoserColumn(df1)
    df3 = addFavoriteUnderdogColumn(df2)
    df4 = addPointMargin(df3)
    df5 = addSeedMargin(df4)
    final_df = df5
    return(final_df)

def uploadToGoogle(df):
    gc = gspread.oauth(
        credentials_filename='google_api/credentials.json',
        authorized_user_filename='google_api/authorized_user.json')

    spreadsheet_key = '1iSB014G0fgfgltuJM7kJwrdv8HvE9z2UOnHgKhgM3FU'
    google_spreadsheet = gc.open_by_key(spreadsheet_key)
    results_sheet = google_spreadsheet.worksheet('Results')
    
    results_sheet.clear()
    set_with_dataframe(worksheet=results_sheet, dataframe=df, include_index=False, include_column_header=True, resize=True)

