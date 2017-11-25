# coding: utf-8

from __future__ import absolute_import

from google.appengine.ext import ndb
import flask
import flask_restful

from api import helpers
import auth
import model
import util

from main import api_v1


@api_v1.resource('/price/', endpoint='api.price.list')
class PriceListAPI(flask_restful.Resource):
  def get(self):
    price_dbs, price_cursor = model.Price.get_dbs()
    return helpers.make_response(price_dbs, model.Price.FIELDS, price_cursor)


@api_v1.resource('/price/<string:price_key>/', endpoint='api.price')
class PriceAPI(flask_restful.Resource):
  def get(self, price_key):
    price_db = ndb.Key(urlsafe=price_key).get()
    if not price_db:
      helpers.make_not_found_exception('Price %s not found' % price_key)
    return helpers.make_response(price_db, model.Price.FIELDS)


###############################################################################
# Admin
###############################################################################
@api_v1.resource('/admin/price/', endpoint='api.admin.price.list')
class AdminPriceListAPI(flask_restful.Resource):
  @auth.admin_required
  def get(self):
    price_keys = util.param('price_keys', list)
    if price_keys:
      price_db_keys = [ndb.Key(urlsafe=k) for k in price_keys]
      price_dbs = ndb.get_multi(price_db_keys)
      return helpers.make_response(price_dbs, model.price.FIELDS)

    price_dbs, price_cursor = model.Price.get_dbs()
    return helpers.make_response(price_dbs, model.Price.FIELDS, price_cursor)

  @auth.admin_required
  def delete(self):
    price_keys = util.param('price_keys', list)
    if not price_keys:
      helpers.make_not_found_exception('Price(s) %s not found' % price_keys)
    price_db_keys = [ndb.Key(urlsafe=k) for k in price_keys]
    ndb.delete_multi(price_db_keys)
    return flask.jsonify({
      'result': price_keys,
      'status': 'success',
    })


@api_v1.resource('/admin/price/<string:price_key>/', endpoint='api.admin.price')
class AdminPriceAPI(flask_restful.Resource):
  @auth.admin_required
  def get(self, price_key):
    price_db = ndb.Key(urlsafe=price_key).get()
    if not price_db:
      helpers.make_not_found_exception('Price %s not found' % price_key)
    return helpers.make_response(price_db, model.Price.FIELDS)

  @auth.admin_required
  def delete(self, price_key):
    price_db = ndb.Key(urlsafe=price_key).get()
    if not price_db:
      helpers.make_not_found_exception('Price %s not found' % price_key)
    price_db.key.delete()
    return helpers.make_response(price_db, model.Price.FIELDS)
