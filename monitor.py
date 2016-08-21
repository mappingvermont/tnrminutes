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

    # Check the Google Doc to make sure the app is live-- i.e. we should be posting to buffer and slack
    # https://docs.google.com/spreadsheets/d/1t0wCIi_ZV4mHFyGyQs3DqidCSUZD4pifj74IedKMVr0/edit#gid=0
    configDict = checkAppStatus()

    # Connect to the local datasbase where we store information about the minutes that have been written
    dbPath = os.path.join(cwd, 'slack.db')
    conn = sqlite3.connect(dbPath)
    curs = conn.cursor()

    # Grab a list of the current minutes
    url = 'https://newrepublic.com/minutes/'
    minuteList = getMinuteData(url)

    # Grab a list of the minutes we've already logged
    selectSQL = "SELECT minuteid, title FROM minutes;"
    curs.execute(selectSQL)

    # Build a minuteid: title dictionary of minutes we've logged
    existingMinutes = {x:unicode(y) for (x,y) in curs.fetchall()}

    # For every new minute, see if we've already recorded it
    # based on minute ID
    for minuteDict in minuteList:
        try:
            existingText = existingMinutes[minuteDict['minuteID']]

            # If we already have the minute recorded, but the title text has changed, 
            # call update function to buffer
            if minuteDict['minuteText'] != existingText:

                # Grab the bufferid of the offending minute
                curs.execute("SELECT bufferid FROM minutes WHERE minuteid = ?;", (minuteDict['minuteID'], ))
                updateBufferID = curs.fetchone()[0]

                # Update the text of the buffer post to to be the new minute headline and its old URL
                newText = minuteDict['minuteText'] + minuteDict['minuteURL']
                bufferDict = updateBufferPost(updateBufferID, newText)

                print "Updated existing post on buffer, success: {}".format(bufferDict['success'])

                # Save the updated title to the database
                curs.execute("UPDATE minutes SET title = ? WHERE minuteid = ?", (minuteDict['minuteText'], minuteDict['minuteID']))
                conn.commit()

            else:
             #If the minuteID and title match, no reason to update an existing post
                pass
            
        
        #If we this is a new minute (and new minuteID) that we don't have in the database
        except KeyError:

            #Check if the app is running before posting something to buffer
            if configDict['app_running'].lower() == 'true':

                # Hour offset is used to determine when buffer should schedule the tweet
                # If hour offset == 2, the buffer will post the tweet in 2 hours
                hourOffset = int(configDict['hour_offset'])

                # Post the tweet to buffer
                bufferDict = postBuffer(minuteDict, hourOffset)
                successText = bufferDict['success']

                if successText:
                    # print 'Added minuteid {} to buffer!'.format(minuteDict['minuteID'])

                    # Grab the ID that buffer generates in case we want to update the post later
                    bufferID = bufferDict['updates'][0]['id']
                    #important due to api rates
                    time.sleep(1)

                else:
                    #insert fake buffer ID
                    bufferID = '9999'
                    print bufferDict

            # If app isn't running, don't post it, but do want to add it to database
            else:
                print 'Found new post, but app turned off'
                bufferID = '9999'

            # Regardless of whether the buffer post was successful, or if the app is running,
            # add to database anyway
            # we don't want to keep trying and failing to post this to buffer
            insertSQL = """INSERT INTO minutes (minuteid, title, minuteurl, imgurl, under120chars, bufferid, minutesdate) 
                            VALUES (?, ?, ?, ?, ?, ?, julianday(?))"""

            curs.execute(insertSQL, (minuteDict['minuteID'], minuteDict['minuteText'], minuteDict['minuteURL'],
                                      minuteDict['imgURL'], minuteDict['under120chars'], bufferID, datetime.date.today()))

            conn.commit()


        # Delete old minutes (i.e. from 100 days ago) from the system
        curs.execute("DELETE FROM minutes WHERE julianday() - minutesdate > 100;")
        conn.commit()

        currentTime = datetime.datetime.now().time()

        # If it's 12:01 AM and email me so I know the script is running properly
        if currentTime.hour == 1 and currentTime.minute == 1:
            print 'minutes script works'
            subprocess.call('mail -s "minutes script works" charlie.hofmann@gmail.com < /dev/null', shell=True)
        else:
            pass


# If it fails at any point, email me the error
except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    print exc_type, exc_tb.tb_lineno
    subprocess.call('mail -s "error in minutes script {0}" charlie.hofmann@gmail.com < /dev/null'.format(exc_type), shell=True)
    print 'Error in minutes script'
