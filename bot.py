import praw
import requests
import os
import time
from pythorhead import Lemmy
from imgurpython import ImgurClient

# Detect Docker
if os.environ.get("container", False):
    print("Running as a container...")


# Function to get Reddit API client
def get_reddit():
    return praw.Reddit(
        client_id=os.environ["reddit_client_id"],
        client_secret=os.environ["reddit_client_secret"],
        user_agent=os.environ["reddit_user_agent"],
    )


# Function to get Lemmy API client
def get_lemmy():
    lemmy = Lemmy(os.environ["lemmy_url"])
    lemmy.log_in(os.environ["lemmy_username"], os.environ["lemmy_password"])
    return lemmy


# Function to upload media to Imgur
def upload_to_imgur(media_url):
    imgur_client_id = os.environ.get("imgur_client_id")
    imgur_client_secret = os.environ.get("imgur_client_secret")
    client = ImgurClient(client_id=imgur_client_id, client_secret=imgur_client_secret)
    return client.upload_from_url(media_url, config=None, anon=True)["link"]


# Function to get a Reddit submission object from a submission ID
def get_submission_from_json(submission_id):
    url = f"https://www.reddit.com/comments/{submission_id}.json"
    response = requests.get(
        url, headers={"User-agent": os.environ["reddit_user_agent"]}
    )
    json_data = response.json()
    submission_data = json_data[0]["data"]["children"][0]["data"]
    return praw.models.Submission(reddit=None, _data=submission_data)


# Main function to watch Reddit for new posts and post them to Lemmy
def main():
    # Get the subreddit object
    reddit = get_reddit()
    subreddit = reddit.subreddit(os.environ["subreddit_name"])

    # Get the lemmy object
    lemmy = get_lemmy()
    community_id = lemmy.discover_community(os.environ["community_name"])

    # Sleep time between checking new posts, default is 60 seconds
    sleep_time = int(os.environ.get("post_check_interval", 60))

    # Watch subreddit for new posts
    for submission in subreddit.stream.submissions():
        time.sleep(sleep_time)
        print(f"New post found: {submission.title} ({submission.url})")

        try:
            author_name = submission.author.name
        except Exception:
            print(
                f"Failed to get submission from API for {submission.id}, falling back to JSON..."
            )
            submission = get_submission_from_json(submission.id)
            author_name = submission.author.name

        # Don't copy automoderator posts
        copy_automoderator_posts = os.environ.get("copy_automoderator_posts", False)
        if author_name == "AutoModerator" and not copy_automoderator_posts:
            print("Not copying automoderator content")
            continue

        # Check if media exists and if it contains 'reddit_video'
        if submission.media is not None and "reddit_video" in submission.media:
            media_url = submission.media["reddit_video"]["fallback_url"]
            imgur_client_id = os.environ.get("imgur_client_id")
            if imgur_client_id:
                media_url = upload_to_imgur(media_url)
                print("Video found, uploading to imgur...")
        else:
            media_url = submission.url

        # Construct the link to the original Reddit post
        original_post_link = (
            f"**Original Post**: [link to OP](https://np.reddit.com{submission.permalink})"
        )

        # Create title and body for Lemmy post
        title = f"[X-Posted from Reddit - /u/{author_name}] - {submission.title}"
        body = f"{submission.selftext}\n\n{original_post_link}"

        print("Uploading to lemmy...")
        lemmy_post = lemmy.post.create(
            community_id=community_id, name=title, url=media_url, body=body
        )

        # Check if the Lemmy post was created successfully
        if lemmy_post:
            print("Lemmy post created successfully")
            # Get and print the actual URL of the created post
            lemmy_post_url = lemmy_post["post_view"]["post"]["ap_id"]
            print(f"Post URL: {lemmy_post_url}")
        else:
            print("Failed to create Lemmy post")

        # Sleep for the configured interval before checking for new posts
        time.sleep(sleep_time)


if __name__ == "__main__":
    main()
