from bs4 import BeautifulSoup
import urllib2
from urlparse import urljoin
import os

def getMinuteData(minuteURL):
	page = urllib2.urlopen(minuteURL)
	soup = BeautifulSoup(page.read(), "lxml")

	minuteList = soup.find_all("article")

	returnList = []

	for minute in minuteList:
		minuteIDStr= minute['id']
		minuteID = int(minuteIDStr.replace('minute-',''))

		minuteText = minute.h1.text
		minuteURL = urljoin(minuteURL, str(minuteID))

		if len(minuteText) <= 120:
			under120chars = 'Yes'
		else:
			under120chars = 'No'

		imgList = minute.findAll('div', {'class':'minute-image'})

		if imgList:
			if len(imgList) == 1:
				imgText = minute.findAll('div', {'class':'minute-image'})[0].img['src']
				img = imgText.replace(r'//',r'https://')
			else:
				#More than one image-- not sure which one to select
				img = None
		else:
			img = None
			
		returnList.append({'minuteID': minuteID, 
						   'minuteText': minuteText, 
						   'under120chars': under120chars,
						   'minuteURL': minuteURL,
						   'imgURL': img})

	return returnList

