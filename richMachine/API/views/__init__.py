from apscheduler.schedulers.background import BackgroundScheduler

from .api_payday import exchange_rates, give_payday

scheduler = BackgroundScheduler()
# scheduler.add_job(exchange_rates, 'cron', hour='*/1')
# scheduler.add_job(give_payday, 'cron', minute='*/1')
scheduler.start()

