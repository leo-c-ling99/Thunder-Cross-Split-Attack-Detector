import praw
import time
import queue
import re
import config

# Create reddit instance
reddit = praw.Reddit(client_id=config.clientId,
                     client_secret=config.clientSecret,
                     user_agent='reply parser by /u/tcsaBot',
                     username=config.username,
                     password=config.password)

# Keep a queue of 100 comment id, since comments returns 100 by default,
# each comment should only be processed once
seen_comments_id = queue.Queue(maxsize=200)
reply_string = """Hey Gamers, Kakyoin bot here. This is likely a Thunder Cross Split attack- [here](https://www.reddit.com/r/TooWeakTooWeak/comments/cmz99v/hinjaku_hinjaku/) is the actual link.
***
^Beep ^Boop, ^I ^am ^a ^bot"""
link_pattern =  r'https://www.reddit.com/r/youfellforitfool/comments/cjlngm/you_fell_for_it_fool'
subredditStr = 'all-YouFellForItFool'

def search(linkPattern, subredditStr):
	# Grab all the Recent Comments in every subreddit. This will return 100 of the newest comments on Reddit
	for results in reddit.subreddit(subredditStr).comments():
		global seen_comments_id # Import global comment queues

		body = results.body  # Grab the Comment
		# Convert the comment to lowercase so we can search it no matter how it was written
		body = body.lower()
		comment_id = results.id  # Get the Comment ID

		# Check if we already replied to this comment, break if so
        # Otherwise, add to seen comments queue
		if comment_id in seen_comments_id.queue:
			break
		
        # If queue is full remove oldest element
		if seen_comments_id.full():
			seen_comments_id.get()
            
		# Checks if comment contains link
		match = re.search(linkPattern, body)
		if match:
			print('Match Found')
			try:
				results.reply(reply_string)
			except:
				break

		seen_comments_id.put(comment_id)



while True:
	search(link_pattern, subredditStr)
