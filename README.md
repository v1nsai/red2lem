# red2lem - a reddit to lemmy crossposter

## Description
This script automates the process of monitoring a specified subreddit and cross-posting new content to a specified Lemmy community. It enables a seamless bridge between Reddit and Lemmy, allowing for the continuous sharing of posts, images, videos, and links.

There was a lot of the same content being posted to both Digg and Reddit for a while as communities migrated. This bot helps close the "content gap" between old Reddit communities and new Lemmy ones.

Please be sure using a bot to post content isn't against your community or instance rules before you start letting it post. Might be best to start your own community. The default waits 10 seconds, otherwise it posts pretty quickly and is likely to get banned pretty quickly.


## Features

- **Monitors a Subreddit**: The script continuously watches a specified subreddit for new posts and actions them as they are detected.
- **Cross-Posts to Lemmy**: New Reddit posts are automatically cross-posted to a designated Lemmy community with proper attribution to the original author.
- **Handles Various Content Types**: Whether it's text, images, videos, or links, the script can process different types of content and post them appropriately on Lemmy.
- **Imgur Re-Upload Support**: Optionally, images and videos can be re-uploaded to Imgur, providing a fresh link for the Lemmy post. If no Imgur API client ID is provided, the original Reddit media URLs are used.
- **AutoModerator Handling**: You can choose whether to include or exclude posts by Reddit's AutoModerator, depending on your preferences.
- **Docker-Friendly**: Designed with Docker support in mind, the script can be easily containerized and run within a Docker environment.


## Installation and Usage Guide

### Prerequisites
- Python 3.x

### Installation (non Docker)
0. Clone the repo
   ```bash
   git clone https://github.com/v1nsai/red2lem.git
   ```

1. **Install Python (3.10 or newer):** Make sure you have a compatible version of Python installed on your system.

2. **Create a Virtual Environment:** Navigate to the directory where your script is located and run the following command to create a virtual environment:
   ```bash
   python3 -m venv red2lem
   ```

   Replace `red2lem` with the name you want for your virtual environment folder.

3. **Activate the Virtual Environment:**
   - **On macOS and Linux:**
     ```bash
     source red2lem/bin/activate
     ```

   - **On Windows:**
     ```bash
     .\red2lem\Scripts\activate
     ```

4. **Install Required Libraries:** With the virtual environment activated, you can install the required libraries.

   ```bash
   pip3 install -r requirements.txt
   ```

5. **Set Environment Variables:** You'll need to set the required environment variables for the script to work. You can export them in your shell or use a `.env` file.

6. **Run the Script:**
   ```bash
   python3 your_script.py
   ```

7. **Deactivate the Virtual Environment:** Once you're done, you can deactivate the virtual environment by simply running:

   ```bash
   deactivate
   ```

By using a virtual environment, you ensure that the dependencies for this project are kept separate from other Python projects on your system, minimizing potential conflicts and issues.


### Installation (Docker)
1. Clone the repository or download the script.
2. Build the Docker image using the provided Dockerfile:
```bash
docker build -t red2lem .
```

### Docker Compose Example
```yaml
version: "3.9"
services:
  red2lem:
    build: https://github.com/vp-en/red2lem.git
    container_name: red2lem
    environment:
      - reddit_client_id=YOUR_REDDIT_CLIENT_ID
      - reddit_client_secret=YOUR_REDDIT_CLIENT_SECRET
      - lemmy_url=YOUR_LEMMY_URL
      - lemmy_username=YOUR_LEMMY_USERNAME
      - lemmy_password=YOUR_LEMMY_PASSWORD
      - subreddit_name=NoStupidQuestions
      - community_name=bot_testing@lemm.ee
      - imgur_client_id=YOUR_OPTIONAL_IMGUR_CLIENT_ID
      - copy_automoderator_posts=YOUR_OPTIONAL_FLAG
    restart: unless-stopped
```

To start the container, use
```bash
docker-compose up -d
```

### Environment Variables (ENVs)

You need to set the following environment variables before running the script:

`reddit_client_id`: Your Reddit API client ID, used for authentication with the Reddit API.

`reddit_client_secret`: Your Reddit API client secret, used for authentication with the Reddit API.

`reddit_user_agent`: The user-agent string for Reddit API requests, which helps identify the client making the request. This is already set in the Dockerfile, and is not needed, unless you explicitly want to change it.

`lemmy_url`: The URL of the Lemmy instance where you want to post the content.

`lemmy_username`: Your username for the Lemmy instance, used to authenticate and post content.

`lemmy_password`: Your password for the Lemmy instance, used to authenticate and post content.

`subreddit_name`: The name of the subreddit you want to monitor for new posts, e.g. `NoStupidQuestions`.

`community_name`: The name of the Lemmy community where you want to cross-post the content, e.g. `bot_testing@lemm.ee`.

`copy_automoderator_posts`: (Optional) A boolean value (True/False) that determines whether posts by Reddit's AutoModerator should be copied to Lemmy. Defaults to False if not set.

`post_check_interval`: (Optional) The time interval, in seconds, that the bot should wait between checking for new posts on Reddit. Default is 60.

`imgur_client_id`: (Optional) Your Imgur API client ID, used to re-upload images and videos to Imgur. If not set, the original Reddit media URLs will be used.

`imgur_secret_id`: (Optional) Your Imgur API secret ID, used to re-upload images and videos to Imgur. If not set, the original Reddit media URLs will be used.

