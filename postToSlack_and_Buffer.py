from slackclient import SlackClient
import requests
import json
import subprocess
import os
import ConfigParser
import datetime

cwd = r'/home/ubuntu/Proj-15/tnrminutes'
version = 'PROD'

# Read the config to get slack and buffer tokens
Config = ConfigParser.ConfigParser()
Config.read(os.path.join(cwd, 'config.ini'))

slackToken = Config.get(version, 'slackToken')
slackUser = Config.get(version, 'slackUser')
bufferToken = Config.get(version, 'bufferToken')


def postBuffer(minuteDict, hourOffset):
	
	# Get the profile ID from buffer, based on our token
	r = requests.get('https://api.bufferapp.com/1/profiles.json?access_token={0}'.format(bufferToken))
	idVal = r.json()[0]['id']

	# Figure out what time for buffer to post, based on the hour offset
	currentTime = datetime.datetime.utcnow()
	offsetTimeDelta = datetime.timedelta(hours=hourOffset)
	postTime = currentTime + offsetTimeDelta

	# Build payload
	data = {'profile_ids[0]': [idVal],
			'text': minuteDict['minuteText'] + ' ' + minuteDict['minuteURL'],
			'scheduled_at':  postTime.isoformat()
			}

	srcText = minuteDict['minuteText']

	#GIF/image adds 24 chars
	#Link adds 24 chars as well
	# Post to slack that we've added this minute to buffer
        postSlack('Posted to buffer: ', srcText)

    # If there's an image associated, add it to the payload
	if minuteDict['imgURL']:
		data['media[picture]'] = minuteDict['imgURL']
		data['media[thumbnail]'] = minuteDict['imgURL']
	else:
		pass

	# Create URL for the buffer API
	tokenStr = 'https://api.bufferapp.com/1/updates/create.json?access_token={0}'.format(bufferToken)

	r = requests.post(tokenStr, data=data)

	return r.json()


def updateBufferPost(bufferID, newText):

	# Get the current status of the buffer post we want to edit
	r = requests.get('https://api.bufferapp.com/1/updates/{1}.json?access_token={0}'.format(bufferToken, bufferID))

	# Grab the time it's scheduled. We don't want to change this, but 
	# do have to resubmit it when we update the post
	timeScheduled  = r.json()[0]['due_at']

	# Update URL
	tokenStr = 'https://api.bufferapp.com/1/updates/{1}/update.json?access_token={0}'.format(bufferToken, bufferID)

	# Payload of updated text with time scheduled
	data = {
                'text': newText,
                'scheduled_at': timeScheduled
                }

	r = requests.post(tokenStr, data=data)

	return r.json()


def postSlack(slackMessage, minuteText):

	# Connect to slack and to the DM channel
	sc = SlackClient(slackToken)
	dmChannel = json.loads(sc.api_call("im.open", user=slackUser))['channel']['id']

    # Text formatting, per slack specifications
    # https://api.slack.com/docs/formatting

    # Encode in utf-8 and meet other slack requirements
	formatted = slackMessage + minuteText.encode('utf-8')
	text = formatted.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
	
	print text

	# Email me so I can keep track of what's been posted
	subprocess.call('mail -a "Content-type: text/html; charset=UTF-8" -s "{0}" charlie.hofmann@gmail.com < /dev/null'.format(text), shell=True)
   
    # Post minute text to slack
	sc.api_call("chat.postMessage", as_user="false", channel=dmChannel, text=text)
	sc.api_call("im.close", channel=dmChannel)
