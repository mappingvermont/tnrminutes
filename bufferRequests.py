import requests
import json

bufferToken = 'FROM CONFIG.INI'
r = requests.get('https://api.bufferapp.com/1/profiles.json?access_token={0}'.format(token))

idVal = r.json()[0]['id']
print idVal

tokenStr = 'https://api.bufferapp.com/1/updates/create.json?access_token={0}'.format(token)

photoLink = r'https://images.newrepublic.com/7fcd69b8b53691d5bc919723b29341d7f2e4c5bd.jpeg?w=600&q=65&dpi=1&fm=pjpg&h=476'
minuteLink = r'https://newrepublic.com/minutes/126366/print-isnt-deadthanks-adult-coloring-books-youtube-stars'
minuteText = r'Print isnt dead thanks to adult coloring books and YouTube stars.'


data = {'profile_ids[0]': [idVal],
	'text': minuteText,
	'media[picture]': photoLink,
	'media[thumbnail]': photoLink
	}


r = requests.post(tokenStr, data=data)
print r.json()
