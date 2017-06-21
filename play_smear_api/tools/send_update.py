import yagmail
import sys
sys.path.insert(0, "..")

from dbqueries.daily_status import DailyStatus

yag = yagmail.SMTP('mkokotovich@gmail.com')

daily_status = DailyStatus()
daily_status.load_stats_since_previous_date(1)
stats = daily_status.print_game_stats()

yag.send('to@someone.com', 'subject', stats)

