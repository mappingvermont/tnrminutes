from slackclient import SlackClient
import requests
import json
import subprocess
import os
import ConfigParser

cwd = r'/home/ubuntu/Proj-15/tnrminutes'
#version = os.environ['TNRMINUTES_VERSION']
version = 'DEV'

Config = ConfigParser.ConfigParser()
Config.read(os.path.join(cwd, 'config.ini'))

slackToken = Config.get(version, 'slackToken')
slackUser = Config.get(version, 'slackUser')
bufferToken = Config.get(version, 'bufferToken')

def postBuffer(minuteDict):
	
	r = requests.get('https://api.bufferapp.com/1/profiles.json?access_token={0}'.format(bufferToken))

	idVal = r.json()[0]['id']

	tokenStr = 'https://api.bufferapp.com/1/updates/create.json?access_token={0}'.format(bufferToken)

	data = {'profile_ids[0]': [idVal],
			'text': minuteDict['minuteText'] + ' ' + minuteDict['minuteURL']}

	srcText = minuteDict['minuteText']

	#GIF/image adds 24 chars
	#Link adds 24 chars as well
	if len(srcText) > 140:
		postSlack('Did not add this to buffer; more than 140 chars: ', srcText)

		return {'success': False, 'message': 'Too many chars for buffer'}

	elif len(srcText) > 92:
		postSlack('Posted to buffer with only a link; too many chars for a photo: ', srcText)

		r = requests.post(tokenStr, data=data)
		return r.json()

	else:
		postSlack('Posted to buffer with link and photo (if present): ', srcText)

		if minuteDict['imgURL']:
			data['media[picture]'] = minuteDict['imgURL']
			data['media[thumbnail]'] = minuteDict['imgURL']
		else:
			pass

		r = requests.post(tokenStr, data=data)
		return r.json()

def updateBufferPost(bufferID, newText):
	r = requests.get('https://api.bufferapp.com/1/profiles.json?access_token={0}'.format(bufferToken))

	idVal = r.json()[0]['id']

	tokenStr = 'https://api.bufferapp.com/1/updates/{1}/update.json?access_token={0}'.format(bufferToken, bufferID)

	data = {'text': newText}

	r = requests.post(tokenStr, data=data)
	return r.json()

def postSlack(slackMessage, minuteText):
	sc = SlackClient(slackToken)

	dmChannel = json.loads(sc.api_call("im.open", user=slackUser))['channel']['id']

    #Text formatting, per slack specifications
    #https://api.slack.com/docs/formatting

	formatted = slackMessage + minuteText.encode('utf-8')
	text = formatted.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
	
	print text
	subprocess.call('mail -a "Content-type: text/html; charset=UTF-8" -s "{0}" charlie.hofmann@gmail.com < /dev/null'.format(text), shell=True)
    #print 'mail -a "Content-type: text/html; charset=UTF-8" -s "{0}" charlie.hofmann@gmail.com < /dev/null'.format(minuteDict['minuteText'])
   
	sc.api_call("chat.postMessage", as_user="false", channel=dmChannel, text=text)
	sc.api_call("im.close", channel=dmChannel)
