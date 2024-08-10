RRR giveaway alerter

Alerts you when new giveaways are announced

Update `config.json` with your discord webhook url

Add to your crontab for 10am every morning `0 10 \* \* \* /usr/bin/python3 /your/path/rrr_giveaway_alerter/rrr_giveaways.py >> /your/path/rrr_giveaway_alerter/cron.log 2>&1`
