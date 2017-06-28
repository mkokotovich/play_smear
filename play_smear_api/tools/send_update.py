import requests
from datetime import datetime
import os
import sys
sys.path.insert(0, "..")

from dbqueries.daily_status import DailyStatus

def load_mailgun_key():
    auth_key = None
    if "MAILGUN_KEY" in os.environ:
        auth_key = os.environ["MAILGUN_KEY"]
    if not auth_key:
        print "Could not find MAILGUN_KEY environmental variable, exiting"
        sys.exit(1)
    return auth_key


def send_status_message(key, num_games, status):
    return requests.post(
        "https://api.mailgun.net/v3/mg.playsmear.com/messages",
        auth=("api", key),
        data={"from": "Play Smear <admin@playsmear.com>",
              "to": ["mkokotovich@gmail.com"],
              "subject": "{} Games - Play Smear Daily Status for {}".format(num_games, datetime.now().strftime("%x")),
              "text": status,
              "html": "<html><pre>{}</pre><br><br><br><a href='www.playsmear.com'>Unsubscribe</a></html>".format(status)})

def main():

    # Load stats
    daily_status = DailyStatus()
    daily_status.load_stats_since_previous_date(1)
    stats = daily_status.print_game_stats()
    num_games = daily_status.get_num_games()

    auth_key = load_mailgun_key()

    ret = send_status_message(auth_key, num_games, stats)

    if ret.status_code != 200:
        print "Failed to send email"
    else:
        print ret.json()



if __name__ == '__main__':
    main()
