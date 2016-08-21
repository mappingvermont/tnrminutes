import json
import gspread
from oauth2client.client import SignedJwtAssertionCredentials


def checkAppStatus():
    # URL: https://docs.google.com/spreadsheets/d/1t0wCIi_ZV4mHFyGyQs3DqidCSUZD4pifj74IedKMVr0/edit#gid=0
    jsonInput = r'/home/ubuntu/Proj-15/tnrminutes/gspread.json'

    json_key = json.load(open(jsonInput))
    scope = ['https://spreadsheets.google.com/feeds']

    credentials = SignedJwtAssertionCredentials(json_key['client_email'], json_key['private_key'].encode(), scope)

    gc = gspread.authorize(credentials)

    wks = gc.open("Slackbot").sheet1

    # Build a config dictionary of key: value pairs
    # Used to determine if the app is running or not
    valuesList = wks.get_all_values()
    valuesDict = {x:y for (x,y) in valuesList}

    return valuesDict
