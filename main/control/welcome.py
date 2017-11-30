# coding: utf-8

import flask
from google.appengine.ext import ndb

import auth
import config
import model

from main import app


###############################################################################
# Welcome
###############################################################################
@app.route('/')
def welcome():
  if auth.is_logged_in():
    currency_dbs, currency_cursor = model.Currency.get_dbs(limit=-1, order='is_crypto,name')
    transaction_dbs, transaction_cursor = model.Transaction.get_dbs(user_key=auth.current_user_key(), limit=-1)

    total_profit = 0
    total_net_worth = 0

    currency_codes = []
    for transaction_db in transaction_dbs:
      total_profit += transaction_db.profit_amount_user
      total_net_worth += transaction_db.net_worth_user
      currency_codes.append(transaction_db.acquired_currency_code)

    currency_codes = list(set(currency_codes))
    price_dbs = []
    user_currency_code = auth.current_user_db().currency_key.get().code if auth.current_user_db().currency_key else 'USD'
    for currency_code in currency_codes:
      if currency_code != user_currency_code:
        price_db = model.Price.get_by('code_unique', ':'.join(tuple(sorted([currency_code, user_currency_code]))))
        if price_db:
          price_dbs.append(price_db)

    return flask.render_template(
      'welcome.html',
      html_class='welcome',
      transaction_dbs=transaction_dbs,
      total_profit=total_profit,
      total_net_worth=total_net_worth,
      currency_dbs=currency_dbs,
      price_dbs=price_dbs,
      api_url=flask.url_for('api.transaction.list'),
    )
  return flask.render_template(
    'welcome.html',
    html_class='welcome',
  )


@app.route('/exchange/<code>/')
@app.route('/exchange/')
def exchange(code=None):
  price_qry = None
  code = code.upper() if code else code
  if code:
    code = code.upper()
    price_qry = model.Price.query(ndb.OR(model.Price.currency_from_code == code, model.Price.currency_to_code == code))
  price_dbs, price_cursor = model.Price.get_dbs(query=price_qry, limit=-1)
  currency_dbs, currency_cursor = model.Currency.get_dbs(limit=-1, order='is_crypto,name')
  return flask.render_template(
    'exchange.html',
    html_class='exchange',
    title='Exchange rates %s' % (' (%s)' % (code) if code else ''),
    price_dbs=price_dbs,
    currency_dbs=currency_dbs,
    code=code,
    canonical_url=flask.url_for('exchange', code=code if code else None),
    api_url=flask.url_for('api.price.list'),
  )


###############################################################################
# Sitemap stuff
###############################################################################
@app.route('/sitemap.xml')
def sitemap():
  response = flask.make_response(flask.render_template(
    'sitemap.xml',
    lastmod=config.CURRENT_VERSION_DATE.strftime('%Y-%m-%d'),
  ))
  response.headers['Content-Type'] = 'application/xml'
  return response


###############################################################################
# Warmup request
###############################################################################
@app.route('/_ah/warmup')
def warmup():
  # TODO: put your warmup code here
  return 'success'
