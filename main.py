from twilioProgram import *
from discordProgram import *
from twitterProgram import *

TWITTER = 1
DISCORD = 2
TWILIO = 3

programState = DISCORD

if programState == TWITTER:
    runTwitter()
elif programState == DISCORD:
    runDiscord()
elif programState == TWILIO:
    runTwilio()
else:
    print("Program state setting does not exist.")