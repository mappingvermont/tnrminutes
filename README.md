# tnrminutes

- Scrape http://newrepublic.com/minutes once per minute
- Compare this data to previous posts saved in a local SQLite database
- Identify new posts based on the unique minute ID
- If a new post was found, compose a tweet with the headline and image
- Post the tweet to Buffer, and send the user a Slack message of the tweet

App configuration is stored locally in config.ini, which reads as follows:
```
[PROD]
userName: Mikaela
slackToken: <your token here>
slacKUser: <your user ID here>
bufferToken: <your buffer token here>
```

Application state (on/off) can be toggled by the user using this doc:
https://docs.google.com/spreadsheets/d/1t0wCIi_ZV4mHFyGyQs3DqidCSUZD4pifj74IedKMVr0/edit#gid=0

Code executed once each minute using cron:

`python monitor.py`
