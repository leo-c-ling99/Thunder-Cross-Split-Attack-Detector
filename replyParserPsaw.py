import praw
from psaw import PushshiftAPI
import config
import queue
import asyncio
import random
import re
import logging
import time

# Custom Bot settings for replies and filtering
queryStr = '(https://www.reddit.com/r/YouFellForItFool/comments/cjlngm'
# Reply base, needs to be closed
replyStrBase = """Hey Gamers, Kakyoin bot here. This link seems to be incorrectly formatted- [here](https://www.reddit.com/r/TooWeakTooWeak/comments/cmz99v/hinjaku_hinjaku/) is the fixed link.
***
^(Beep Boop, I am a bot"""
# Subs to skip reply process
ignoredSubs = ('youfellforitfool', 'pics', 'minecraft', 'askreddit')
replyWaitTime = 5 * 60

async def reply(commentId, replyStr):
    await asyncio.sleep(replyWaitTime, loop=mainLoop)
    for ii in range(3):
        try:
            reddit.comment(id=commentId).reply(replyStr)
            return
        except Exception as err:
            await asyncio.sleep(random.randrange(5,20))
            logger.error(err)
 
def parseComment(comment):
	# Checks the subreddit, some subreddits are ignored
    # Also avoid replies in user profiles, since that can be used for testing
    # Makes sure properly tagged links (to TCSA) are avoided
    if (comment.subreddit.display_name.lower() in ignoredSubs or
        re.search(r'u_\S+', comment.subreddit.display_name) is not None or
        '[r/youfellforitfool]' in comment.body.lower() or
        '[deleted]' == comment.body.lower()): 
        return
    
    logger.info(comment.id)
    
    # Search comment to see if there is a linked subreddit
    subLink = re.match(r'\[(r/\S+)\]\(https:', comment.body)
    
    replyStr = replyStrBase
    # if sublink exists append to end of reply string
    if subLink:
        replyStr += f' | {subLink.groups()[0]}'
    
    replyStr += ')'
    
    mainLoop.create_task(reply(comment.id, replyStr))


def search():
    global seenComments  # Import global comment queues
    try:
        # API generator for comment containing link
        # looks only in the most recent hour
        gen=api.search_comments(q=queryStr, 
                                limit = maxResps,
                                after= int(time.time())-3600)
        
        for comment in gen:
            if comment.id in seenComments.queue:
                continue  # Skips if already seen

			# If queue is full remove oldest element
            if seenComments.full():
                seenComments.get()

            # Add new comment to seen comments queue
            seenComments.put(comment.id, timeout=3)

            parseComment(comment)
        

    except Exception as err:
        logger.error(err)


async def main(sleepTime):
    # Discard the first 5 messages on startup to avoid overlap
    #   Adds to queue without processing
    
    # API generator for comment containing link
    gen=api.search_comments(q=queryStr, 
                                limit = maxResps,
                                after= int(time.time())-3600)
    
    for comment in gen:
        seenComments.put(comment.id, timeout=30)

    # Infintely Parses comments
    try:
        while True:
            search()
            await asyncio.sleep(sleepTime)
    except Exception as err:
        logger.error(err)
        mainLoop.stop()


if __name__ == "__main__":
    # Sets up logging
    logging.basicConfig(filename='bot.log', level=logging.INFO,
                        format='%(asctime)s %(levelname)s %(name)s %(message)s')
    logger=logging.getLogger(__name__)

    # Using pushshift to fetch Ids, and using Praw to comment
    reddit=praw.Reddit(client_id=config.clientId,
                         client_secret=config.clientSecret,
                         user_agent='reply parser by /u/tcsaBot',
                         username=config.username,
                         password=config.password)
    api=PushshiftAPI(reddit)

    maxResps=5  # Limits comments to parse from pushshift
    
    # Queue to store messages from generator
    # pushishift seems to return slightly different results everytime
    seenComments=queue.Queue(maxsize=maxResps * 2)
    mainLoop = asyncio.get_event_loop()
    mainLoop.run_until_complete(main(15))