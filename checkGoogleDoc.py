import json
import gspread
from oauth2client.client import SignedJwtAssertionCredentials

def checkAppStatus():
    jsonInput = r'/home/ubuntu/Proj-15/tnrminutes/gspread.json'

    json_key = json.load(open(jsonInput))
    scope = ['https://spreadsheets.google.com/feeds']

    credentials = SignedJwtAssertionCredentials(json_key['client_email'], json_key['private_key'].encode(), scope)

    gc = gspread.authorize(credentials)

    wks = gc.open("tnrminutes_config").sheet1

    valuesList = wks.get_all_values()
    valuesDict = {x:y for (x,y) in valuesList}

    return valuesDict
