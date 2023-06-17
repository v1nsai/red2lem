import praw
import requests
import re

from pythorhead import Lemmy
from . import credentials
from time import sleep

# Create a Reddit instance
def get_reddit():
    return praw.Reddit(
        client_id=credentials.reddit_client_id,
        client_secret=credentials.reddit_client_secret,
        user_agent='bot that alerts on new subreddit posts v1.0 by u/RedPillOrRedKoolAid_',
    )

def get_lemmy():
    lemmy = Lemmy(credentials.lemmy_url)
    lemmy.log_in(credentials.lemmy_username, credentials.lemmy_password)
    return lemmy

if __name__ == '__main__':

    # TODO if api fails use json

    # Get the subreddit object
    reddit = get_reddit()
    subreddit = reddit.subreddit('NoStupidQuestions')

    # Get the lemmy object
    lemmy = get_lemmy()
    community_id = lemmy.discover_community("testsubforbots@lemmy.world")
    
    # Watch subreddit for new posts
    for submission in subreddit.stream.submissions():
        print(f"New post found: {submission.title} ({submission.url})")

        if submission.is_video:
            print("Saving video...")
            title = submission.title
            media_url = submission.media['reddit_video']['fallback_url']
            media_type = media_url.split('.')[-1]
            media_type = re.sub(r'\?.*', '', media_type)
            media_content = requests.get(media_url).content
        elif submission.url.endswith(('.jpg', '.jpeg', '.png', '.gif')):
            print("Saving image...")
            title = submission.title            
            media_url = submission.url
            media_type = submission.url.split('.')[-1]
            media_content = requests.get(media_url).content
        elif submission.is_self:
            print("Saving text...")
            title = submission.title
            media_type = 'txt'
            media_content = submission.selftext
            media_url = ''
            lemmy.post.create( community_id=community_id, name=title, body=media_content )
            continue
        else:
            print("Saving link...")
            title = submission.title
            media_type = 'link'
            media_url = submission.url
            media_content = ''
        
        print("Uploading to lemmy...")
        lemmy.post.create( community_id=community_id, name=title, url=media_url, body=media_content )
        sleep(10) # flooding is bad and likely to get you banned