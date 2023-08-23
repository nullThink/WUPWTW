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
    print("Tweeted!")

def setRandTime(client, apiObj):
    hourInt = random.randint(0, 23)
    minuteInt = random.randint(0, 59)

    for job in scheduler.get_jobs():
        if(job.id == "worm_message"):
            scheduler.remove_job("worm_message")
    
    def sendTweet():
        sendWormTweet(client, apiObj, "Who up?")
    
    scheduler.add_job(sendTweet, trigger=CronTrigger(hour=str(hourInt), minute=str(minuteInt)),id="worm_message")
    print("Hours set to {0}:{1}".format(hourInt, minuteInt))

scheduler = BackgroundScheduler()

def runTwitter():
    print("Running Twitter!")
    client = tweepy.Client(twitterSecrets["bearerToken"],twitterSecrets["apiKey"], twitterSecrets["apiSecret"],twitterSecrets["accessToken"], twitterSecrets["accessSecret"])

    apiObj = api()

    def sendTweet():
        sendWormTweet(client, apiObj)
    
    def setTime():
        setRandTime(client, apiObj)

    scheduler.add_job(sendTweet, id="worm_message")
    scheduler.add_job(setTime, trigger=CronTrigger(hour="00"), id="set_time")
    scheduler.start()
    # Run program infinitely
    while(True):
        sleep(1)