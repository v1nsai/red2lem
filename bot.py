import praw
import requests
import os
import time
import logging
from pythorhead import Lemmy
from imgurpython import ImgurClient
from threading import Lock

# Configure logging
logging.basicConfig(level=logging.INFO)

# Detect Docker
if os.environ.get("container", False):
    logging.info("Running as a container...")


# Function to get Reddit API client
def get_reddit():
    try:
        reddit_instance = praw.Reddit(
            client_id=os.environ["reddit_client_id"],
            client_secret=os.environ["reddit_client_secret"],
            user_agent=os.environ["reddit_user_agent"],
        )
        # Verify that you're authenticated
        reddit_instance.user.me()
        return reddit_instance
    except Exception as e:
        logging.error(f"Error connecting to Reddit: {e}")
        return None


# Function to get Lemmy API client
def get_lemmy():
    try:
        lemmy = Lemmy(os.environ["lemmy_url"])
        lemmy.log_in(os.environ["lemmy_username"], os.environ["lemmy_password"])
        return lemmy
    except Exception as e:
        logging.error(f"Error connecting to Lemmy: {e}")
        return None


# Function to upload media to Imgur
def upload_to_imgur(media_url):
    imgur_client_id = os.environ.get("imgur_client_id")
    imgur_client_secret = os.environ.get("imgur_client_secret")
    MAX_RETRIES = 5
    retry_count = 0

    if not imgur_client_id or not imgur_client_secret:
        logging.warning(
            "Imgur client ID or secret is missing, using original Reddit link."
        )
        return media_url

    while retry_count < MAX_RETRIES:
        try:
            client = ImgurClient(
                client_id=imgur_client_id, client_secret=imgur_client_secret
            )
            return client.upload_from_url(media_url, config=None, anon=True)["link"]
        except requests.exceptions.RequestException as e:
            if e.response.status_code == 429:
                retry_count += 1
                wait_time = 2**retry_count  # exponential backoff
                logging.warning(
                    f"Imgur rate limit hit, sleeping for {wait_time} seconds..."
                )
                time.sleep(wait_time)
            else:
                logging.error(
                    f"Failed to upload to Imgur: {e}, using original Reddit link."
                )
                return media_url

    logging.error("Max retries reached. Using original Reddit link.")
    return media_url


# Function to get a Reddit submission object from a submission ID
def get_submission_from_json(submission_id):
    url = f"https://www.reddit.com/comments/{submission_id}.json"
    try:
        response = requests.get(
            url, headers={"User-agent": os.environ["reddit_user_agent"]}
        )
        response.raise_for_status()
        json_data = response.json()
        submission_data = json_data[0]["data"]["children"][0]["data"]
        return praw.models.Submission(reddit=None, _data=submission_data)
    except Exception as e:
        logging.error(f"Error fetching Reddit submission: {e}")
        return None


# Main function to watch Reddit for new posts and post them to Lemmy
def main():
    lock = Lock()  # Lock for thread safety

    reddit = get_reddit()
    if reddit is None:
        return

    try:
        subreddit = reddit.subreddit(os.environ["subreddit_name"])
    except Exception as e:
        logging.error(f"Error while connecting to Reddit: {e}")
        return

    try:
        lemmy = get_lemmy()
        community_id = lemmy.discover_community(os.environ["community_name"])
    except Exception as e:
        logging.error(f"Error while connecting to Lemmy: {e}")
        return

    # Sleep time between checking new posts, default is 60 seconds
    sleep_time = int(os.environ.get("post_check_interval", 60))

    # Watch subreddit for new posts
    for submission in subreddit.stream.submissions():
        try:
            with lock:  # Ensure thread safety
                logging.info(f"New post found: {submission.title} ({submission.url})")

                author_name = submission.author.name if submission.author else "Unknown"

                # Don't copy automoderator posts
                copy_automoderator_posts = os.environ.get(
                    "copy_automoderator_posts", False
                )
                if author_name == "AutoModerator" and not copy_automoderator_posts:
                    logging.info("Not copying automoderator content")
                    continue

                # Check if media exists and if it contains 'reddit_video'
                if submission.media and "reddit_video" in submission.media:
                    media_url = submission.media["reddit_video"]["fallback_url"]
                    media_url = upload_to_imgur(media_url)
                    logging.info("Video found, uploading to imgur...")
                else:
                    media_url = submission.url

                # Construct the link to the original Reddit post
                original_post_link = f"**Original Post**: [link to OP](https://np.reddit.com{submission.permalink})"

                # Customize the title using an environment variable or keep the default
                title_template = os.environ.get(
                    "title_template",
                    "[X-Posted from Reddit - /u/{author_name}] - {submission_title}",
                )
                title = title_template.format(
                    author_name=author_name, submission_title=submission.title
                )

                body = f"{submission.selftext}\n\n\n{original_post_link}"

                logging.info("Uploading to lemmy...")
                try:
                    lemmy_post = lemmy.post.create(
                        community_id=community_id, name=title, url=media_url, body=body
                    )
                except Exception as e:
                    logging.error(f"Error while posting to Lemmy: {e}")
                    continue

                # Check if the Lemmy post was created successfully
                if lemmy_post:
                    logging.info("Lemmy post created successfully")
                    lemmy_post_url = lemmy_post["post_view"]["post"]["ap_id"]
                    logging.info(f"Post URL: {lemmy_post_url}")
                else:
                    logging.warning("Failed to create Lemmy post")
                # Sleep for the configured interval before checking for the next submission
                logging.info(
                    f"Sleeping for {sleep_time} seconds before checking for new posts..."
                )
                time.sleep(sleep_time)

        except praw.exceptions.PRAWException as e:
            logging.error(f"Error fetching or processing submission: {e}")
        except praw.exceptions.RateLimitExceeded as e:
            logging.warning(
                f"Rate limit exceeded. Sleeping for {e.sleep_time} seconds."
            )
            time.sleep(e.sleep_time)


if __name__ == "__main__":
    main()
