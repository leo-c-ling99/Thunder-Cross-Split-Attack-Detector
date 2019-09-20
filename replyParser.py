import praw
import time
import queue
import re
import config
import logging

# Sets up logging
logging.basicConfig(filename='bot.log', level=logging.DEBUG, 
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger=logging.getLogger(__name__)

# Create reddit instance
reddit = praw.Reddit(client_id=config.clientId,
                     client_secret=config.clientSecret,
                     user_agent='reply parser by /u/tcsaBot',
                     username=config.username,
                     password=config.password)

# Keep a queue of 100 comment id, since comments returns 100 by default,
# each comment should only be processed once
seen_comments_id = queue.Queue(maxsize=200)
reply_string = """Hey Gamers, Kakyoin bot here. This is likely a Thunder Cross Split Attack- [here](https://www.reddit.com/r/TooWeakTooWeak/comments/cmz99v/hinjaku_hinjaku/) is the actual link.
***
^Beep ^Boop, ^I ^am ^a ^bot"""
link_pattern =  r'https://www.reddit.com/r/youfellforitfool/comments/cjlngm/you_fell_for_it_fool'
subredditStr = 'all'

replyWaitTime = 60 * 5
replyDict = {}

def search(linkPattern, subredditStr):
	try:
		comments = reddit.subreddit(subredditStr).comments()
	except Exception as err:
		logger.error(err)

	# Grab all the Recent Comments in every subreddit. This will return 100 of the newest comments on Reddit
	for results in comments:
		global seen_comments_id # Import global comment queues

		comment_id = results.id  # Get the Comment ID

		# Check if we already replied to this comment, break if so
        # Otherwise, add to seen comments queue
		if comment_id in seen_comments_id.queue:
			break
		
		# If queue is full remove oldest element
		if seen_comments_id.full():
			seen_comments_id.get()
		
		# Add new comment to seen comments queue
		seen_comments_id.put(comment_id)

		# Checks the subreddit, filters are ignored by the comments method
		if results.subreddit.display_name == 'YouFellForItFool':
			break

		body = results.body  # Grab the Comment
		# Convert the comment to lowercase so we can search it no matter how it was written
		body = body.lower()
            
		# Checks if comment contains link
		match = re.search(linkPattern, body)
		# Checks if comment contains a direct link to the subreddit, if so ignore
		legitLink = re.search(r'\[r\/[yY]ou[fF]ell[fF]or[iI]t[fF]ool\]', body)
		
		if match and legitLink is None:
			replyDict.update({results.id: time.time()})


while True:
	search(link_pattern, subredditStr)
	# Using a copy to allow for deletion of items during iteration
	for commentId, starttime in replyDict.copy().items():
		if time.time() - starttime >= replyWaitTime:
			try:
				reddit.comment(id=commentId).reply(reply_string)
				replyDict.pop(commentId)
			except Exception as err:
				logger.error(err)
				break