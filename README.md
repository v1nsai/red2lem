# Reddit to Lemmy Crosspost Bot
This is a very basic crossposting bot that follows a Reddit sub and posts media and links to a Lemmy community. 

I remember seeing a lot of the same content on both Digg and Reddit before I stopped going to Digg entirely. This bot helps close the "content gap" between old Reddit communities and new Lemmy ones. 

Please be sure using a bot to post content isn't against your community or instance rules before you start letting it post.  Might be best to start your own community. The default waits 10 seconds, otherwise it posts pretty quickly and is likely to get banned pretty quickly.

# Usage
* `git clone https://github.com/v1nsai/red2lem.git`
* `cd red2lem`
* `cp credentials.py.template credentials.py`
* Fill in reddit and lemmy credentials in `credentials.py`
* Fill in details in `vars.py`
* `python3 -m pip install -r requirements.txt`
* `python3 -m virtualenv --python=/path/to/python3.10 path/to/venv` # the pythorhead Lemmy API requires python3.10 for now
* `source path/to/venv/bin/activate`
* `python bot.py`

# TODO
* Add support for anonymous scraping using JSON (you can do this by appending `.json` to pretty much any Reddit URL).