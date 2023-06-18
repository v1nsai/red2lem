# Reddit to Lemmy Crosspost Bot
Some of the post popular content on reddit is crossposts from bots that follow Twitter, Facebook, TikTok etc.  This is a way to build some foundation for new communities to grow on.

Please be sure using a bot to post content isn't against your community or instance rules before you unleash it.  The default waits 10 seconds, otherwise it posts pretty quickly and is likely to get banned pretty quickly.

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
* Add support for anonymous scraping using JSON (you can do this by appending `.json` to pretty much any Reddit URL).  I like the handy streaming service that the Reddit API exposes but since basically all goodwill is gone between devs and Reddit I'm expecting to get shut down at some point.
