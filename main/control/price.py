# coding: utf-8

from google.appengine.ext import ndb
import flask
import flask_wtf
import wtforms

import auth
import config
import model
import util

from main import app


###############################################################################
# List
###############################################################################
@app.route('/price/')
def price_list():
  price_dbs, price_cursor = model.Price.get_dbs()
  return flask.render_template(
    'price/price_list.html',
    html_class='price-list',
    title='Price List',
    price_dbs=price_dbs,
    next_url=util.generate_next_url(price_cursor),
    api_url=flask.url_for('api.price.list'),
  )


###############################################################################
# View
###############################################################################
@app.route('/price/<int:price_id>/')
def price_view(price_id):
  price_db = model.Price.get_by_id(price_id)
  if not price_db:
    flask.abort(404)

  return flask.render_template(
    'price/price_view.html',
    html_class='price-view',
    title='Price',
    price_db=price_db,
    api_url=flask.url_for('api.price', price_key=price_db.key.urlsafe() if price_db.key else ''),
  )


###############################################################################
# Admin List
###############################################################################
@app.route('/admin/price/')
@auth.admin_required
def admin_price_list():
  price_dbs, price_cursor = model.Price.get_dbs(
    order=util.param('order') or '-modified',
  )
  return flask.render_template(
    'price/admin_price_list.html',
    html_class='admin-price-list',
    title='Price List',
    price_dbs=price_dbs,
    next_url=util.generate_next_url(price_cursor),
    api_url=flask.url_for('api.admin.price.list'),
  )


###############################################################################
# Admin Update
###############################################################################
class PriceUpdateAdminForm(flask_wtf.FlaskForm):
  currency_from_key = wtforms.SelectField(
    model.Price.currency_from_key._verbose_name,
    [wtforms.validators.required()],
    choices=[],
  )
  currency_to_key = wtforms.SelectField(
    model.Price.currency_to_key._verbose_name,
    [wtforms.validators.required()],
    choices=[],
  )
  amount = wtforms.FloatField(
    model.Price.amount._verbose_name,
    [wtforms.validators.optional()],
  )


@app.route('/admin/price/create/', methods=['GET', 'POST'])
@app.route('/admin/price/<int:price_id>/update/', methods=['GET', 'POST'])
@auth.admin_required
def admin_price_update(price_id=0):
  if price_id:
    price_db = model.Price.get_by_id(price_id)
  else:
    price_db = model.Price()

  if not price_db:
    flask.abort(404)

  form = PriceUpdateAdminForm(obj=price_db)

  currency_dbs, currency_cursor = model.Currency.get_dbs(limit=-1)
  form.currency_from_key.choices = [(c.key.urlsafe(), c.name) for c in currency_dbs]
  form.currency_to_key.choices = [(c.key.urlsafe(), c.name) for c in currency_dbs]
  if flask.request.method == 'GET' and not form.errors:
    form.currency_from_key.data = price_db.currency_from_key.urlsafe() if price_db.currency_from_key else None
    form.currency_to_key.data = price_db.currency_to_key.urlsafe() if price_db.currency_to_key else None

  if form.validate_on_submit():
    form.currency_from_key.data = ndb.Key(urlsafe=form.currency_from_key.data) if form.currency_from_key.data else None
    form.currency_to_key.data = ndb.Key(urlsafe=form.currency_to_key.data) if form.currency_to_key.data else None
    form.populate_obj(price_db)
    price_db.put()
    return flask.redirect(flask.url_for('admin_price_list', order='-modified'))

  return flask.render_template(
    'price/admin_price_update.html',
    title='%s' % '%sPrice' % ('' if price_id else 'New '),
    html_class='admin-price-update',
    form=form,
    price_db=price_db,
    back_url_for='admin_price_list',
    api_url=flask.url_for('api.admin.price', price_key=price_db.key.urlsafe() if price_db.key else ''),
  )


###############################################################################
# Admin Delete
###############################################################################
@app.route('/admin/price/<int:price_id>/delete/', methods=['POST'])
@auth.admin_required
def admin_price_delete(price_id):
  price_db = model.Price.get_by_id(price_id)
  price_db.key.delete()
  flask.flash('Price deleted.', category='success')
  return flask.redirect(flask.url_for('admin_price_list'))
