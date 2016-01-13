#!/usr/bin/python
import sqlite3
import datetime
import time
import subprocess
import sys
import os
from scrapeMinutes import getMinuteData
from postToSlack_and_Buffer import *
from checkGoogleDoc import checkAppStatus

try:

    configDict = checkAppStatus()
    
    if configDict['app_running'].lower() == 'true':

        url = 'https://newrepublic.com/minutes/'
        #    print "Using version {}, we have slack token {}, user {} and buffer token {}".format(version, slackToken, slackUser, bufferToken)

        dbPath = os.path.join(cwd, 'slack.db')
        conn = sqlite3.connect(dbPath)
        curs = conn.cursor()

        minuteList = getMinuteData(url)

        selectSQL = "SELECT minuteid, title FROM minutes;"
        curs.execute(selectSQL)

        existingMinutes = {x:unicode(y) for (x,y) in curs.fetchall()}

        for minuteDict in minuteList:
            try:
                existingText = existingMinutes[minuteDict['minuteID']]

                #Need to check here for an updated title, then call update function to buffer
                if minuteDict['minuteText'] != existingText:

                    curs.execute("SELECT bufferid FROM minutes WHERE minuteid = ?;", (minuteDict['minuteID'], ))
                    updateBufferID = curs.fetchone()[0]

                    newText = minuteDict['minuteText']+minuteDict['minuteURL']
                    bufferDict = updateBufferPost(updateBufferID, newText)

                    print "Updated existing post on buffer, success: {}".format(bufferDict['success'])

                    curs.execute("UPDATE minutes SET title = ? WHERE minuteid = ?", (minuteDict['minuteText'], minuteDict['minuteID']))
                    conn.commit()

                else:
                 #If the minuteID and title match, no reason to update an existing post
                    pass
                
            
            #If we haven't already processed this minuteID
            except KeyError:

                bufferDict = postBuffer(minuteDict)
                successText = bufferDict['success']

                if successText:
                    #print 'Added minuteid {} to buffer!'.format(minuteDict['minuteID'])

                    bufferID = bufferDict['updates'][0]['id']
                    #important due to api rates
                    time.sleep(1)

                else:
                    #insert fake buffer ID
                    bufferID = '9999'
                    print bufferDict

                #Regardless of whether the buffer post was successful, add to database anyway
                #we don't want to keep trying and failing to post this to buffer
                insertSQL = """INSERT INTO minutes (minuteid, title, minuteurl, imgurl, under120chars, bufferid, minutesdate) 
                                VALUES (?, ?, ?, ?, ?, ?, julianday(?))"""

                curs.execute(insertSQL, (minuteDict['minuteID'], minuteDict['minuteText'], minuteDict['minuteURL'],
                                          minuteDict['imgURL'], minuteDict['under120chars'], bufferID, datetime.date.today()))

                conn.commit()


        #Delete old minutes from the system
        curs.execute("DELETE FROM minutes WHERE julianday() - minutesdate > 100;")
        conn.commit()

        #Check that the script is running all the way through, and email me
        currentTime = datetime.datetime.now().time()

        if currentTime.hour == 1 and currentTime.minute == 1:
            print 'minutes script works'
            subprocess.call('mail -s "minutes script works" charlie.hofmann@gmail.com < /dev/null', shell=True)
        else:
            pass

    else:
        pass
        #print 'app disabled by google doc'

except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    print exc_type, exc_tb.tb_lineno
    subprocess.call('mail -s "error in minutes script" charlie.hofmann@gmail.com < /dev/null', shell=True)
    print 'Error in minutes script'
