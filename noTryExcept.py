#!/usr/bin/python

from bs4 import BeautifulSoup
import urllib2
import sqlite3
import datetime
import time
import json
import subprocess
from slackclient import SlackClient


token = r'xoxp-2198482637-4145942825-16146661090-f56d96e2d5'
sc = SlackClient(token)

dbPath = r'/home/ubuntu/Proj-15/Slack/slack.db'
conn = sqlite3.connect(dbPath)
curs = conn.cursor()

    #CREATE TABLE minutes (id INTEGER PRIMARY KEY, title varchar(500), under40chars varchar(10), minutesdate real);

     #testing try/except block
#    raise ValueError('bad!')

url= 'https://newrepublic.com/minutes'
page = urllib2.urlopen(url)
soup = BeautifulSoup(page.read(), "lxml")

titleList = soup.find_all("h1", {"class": "minute-title"})

existingTitles = []

selectSQL = "SELECT title FROM minutes;"
curs.execute(selectSQL)

existingTitles = [unicode(x[0]) for x in curs.fetchall()]

    #print existingTitles

    for title in titleList:
        textVal = title.contents[0].text.strip()

        if textVal in existingTitles:
            pass
            #print 'Already in database'
        else:

            if len(textVal) > 140:
                under40 = 'No'
            else:
  	       under40 = 'Yes'

            insertSQL = "INSERT INTO minutes (title, under40chars, minutesdate) VALUES (?, ?, julianday(?))"
            curs.execute(insertSQL, (textVal, under40, datetime.date.today()))

#	    dmChannel = json.loads(sc.api_call("im.open", user="U0449TQQ9"))['channel']['id']
#  	    sc.api_call("chat.postMessage", as_user="false", channel=dmChannel, text=textVal)
#	    sc.api_call("im.close", channel=dmChannel)

	    subprocess.call('mail -s "update sent" charlie.hofmann@gmail.com < /dev/null'.format(textVal), shell=True)
	    print textVal

	    #important due to api rates
	    time.sleep(2)

    #Delete old minutes from the system
    curs.execute("DELETE FROM minutes WHERE julianday() - minutesdate > 3;")

    conn.commit()

    #Check that the script is running all the way through, and email me
    currentTime = datetime.datetime.now().time()

    if currentTime.hour == 1 and currentTime.minute == 1:
        subprocess.call('mail -s "minutes script works" charlie.hofmann@gmail.com < /dev/null', shell=True)
    else:
        pass

except:
    subprocess.call('mail -s "error in minutes script" charlie.hofmann@gmail.com < /dev/null', shell=True)
