# coding: utf-8

import flask

import config
import model
import task

from main import app


###############################################################################
# Cron Stuff
###############################################################################
@app.route('/admin/cron/price/')
def admin_cron_price():
  if config.PRODUCTION and 'X-Appengine-Cron' not in flask.request.headers:
    flask.abort(403)

  price_dbs, price_cursor = model.Price.get_dbs(limit=-1)
  for price_db in price_dbs:
    task.update_price_task(price_db)

  return 'OK'
