# coding: utf-8

import model


def get_exchange_rate_by_keys(currency_from_key, currency_to_key):
  if not (currency_from_key or currency_to_key):
    return 0
  if currency_from_key == currency_to_key:
    return 1

  invert = False
  price_dbs, price_cursor = model.Price.get_dbs(
    limit=1,
    currency_from_key=currency_from_key,
    currency_to_key=currency_to_key,
  )
  if not price_dbs:
    price_dbs, price_cursor = model.Price.get_dbs(
      limit=1,
      currency_from_key=currency_to_key,
      currency_to_key=currency_from_key,
    )
    invert = True

  if not price_dbs or price_dbs[0].amount == 0:
    return 0

  price_db = price_dbs[0]
  rate = price_db.amount_invert if invert else price_db.amount

  return rate


def get_exchange_rate(currency_from, currency_to):
  currency_from_db = model.Currency.get_by('code', currency_from.upper())
  currency_to_db = model.Currency.get_by('code', currency_to.upper())
  if not (currency_from_db and currency_to_db):
    return 0
  return get_exchange_rate_by_keys(currency_from_db.key, currency_to_db.key)
