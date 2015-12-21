from bs4 import BeautifulSoup
import urllib2
import sqlite3
import datetime
import time
import json
import subprocess
import sys
import os
from urlparse import urljoin
from slackclient import SlackClient
import ConfigParser

url = 'https://newrepublic.com/minutes/'
page = urllib2.urlopen(url)
soup = BeautifulSoup(page.read(), "lxml")

minuteList = soup.find_all("article")

existingIDs = []

for minute in minuteList:
	minuteIDStr= minute['id']
	minuteID = int(minuteIDStr.replace('minute-',''))

	minuteText = minute.h1.text
	minuteURL = urljoin(url, str(minuteID))

	#Grab second image-- first is face
	try:
		imgText = minute.find_all('img')[1]['src']
		img = imgText.replace(r'//','')
	except:
		img = None
		
	print minuteID, minuteText, minuteURL, img

