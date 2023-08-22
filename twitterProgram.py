import tweepy
from botSecrets import twitterSecrets
from time import sleep

# For implementing scheduler.
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

import random

def api():
    auth = tweepy.OAuth1UserHandler(twitterSecrets["apiKey"], twitterSecrets["apiSecret"],twitterSecrets["accessToken"], twitterSecrets["accessSecret"])
    return tweepy.API(auth)

def sendWormTweet(client, api, message=""):
    wormImage = api.media_upload("IMG_3297.JPG")
    client.create_tweet(text=message, media_ids=[wormImage.media_id])

def setRandTime(client, apiObj):
    hourInt = random.randint(0, 23)
    minuteInt = random.randint(0, 59)

    scheduler.remove_job("worm_message")
    scheduler.add_job(sendWormTweet(client, apiObj), trigger=CronTrigger(hour=hourInt, minute=minuteInt),id="worm_message")

    print(hourInt)
    print(minuteInt)

scheduler = BackgroundScheduler()

def runTwitter():
    scheduler.start()

    print("Running Twitter!")
    client = tweepy.Client(twitterSecrets["bearerToken"],twitterSecrets["apiKey"], twitterSecrets["apiSecret"],twitterSecrets["accessToken"], twitterSecrets["accessSecret"])

    apiObj = api()

    def sendTweet():
        sendWormTweet(client, apiObj)
    
    def setTime():
        setRandTime(client, apiObj)

    scheduler.add_job(sendTweet, id="worm_message")

    scheduler.add_job(setTime, trigger=CronTrigger(hour="00"), id="setTime")

    # Run program infinitely
    while(True):
        sleep(1)