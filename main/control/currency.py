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
@app.route('/currency/')
def currency_list():
  currency_dbs, currency_cursor = model.Currency.get_dbs()
  return flask.render_template(
    'currency/currency_list.html',
    html_class='currency-list',
    title='Currency List',
    currency_dbs=currency_dbs,
    next_url=util.generate_next_url(currency_cursor),
    api_url=flask.url_for('api.currency.list'),
  )


###############################################################################
# View
###############################################################################
@app.route('/currency/<int:currency_id>/')
def currency_view(currency_id):
  currency_db = model.Currency.get_by_id(currency_id)
  if not currency_db:
    flask.abort(404)

  return flask.render_template(
    'currency/currency_view.html',
    html_class='currency-view',
    title=currency_db.name,
    currency_db=currency_db,
    api_url=flask.url_for('api.currency', currency_key=currency_db.key.urlsafe() if currency_db.key else ''),
  )


###############################################################################
# Admin List
###############################################################################
@app.route('/admin/currency/')
@auth.admin_required
def admin_currency_list():
  currency_dbs, currency_cursor = model.Currency.get_dbs(
    order=util.param('order') or '-modified',
  )
  return flask.render_template(
    'currency/admin_currency_list.html',
    html_class='admin-currency-list',
    title='Currency List',
    currency_dbs=currency_dbs,
    next_url=util.generate_next_url(currency_cursor),
    api_url=flask.url_for('api.admin.currency.list'),
  )


###############################################################################
# Admin Update
###############################################################################
class CurrencyUpdateAdminForm(flask_wtf.FlaskForm):
  name = wtforms.StringField(
    model.Currency.name._verbose_name,
    [wtforms.validators.required(), wtforms.validators.length(max=500)],
    filters=[util.strip_filter],
  )
  code = wtforms.StringField(
    model.Currency.code._verbose_name,
    [wtforms.validators.required(), wtforms.validators.length(max=500)],
    filters=[util.strip_filter],
  )
  symbol = wtforms.StringField(
    model.Currency.symbol._verbose_name,
    [wtforms.validators.optional(), wtforms.validators.length(max=500)],
    filters=[util.strip_filter],
  )


@app.route('/admin/currency/create/', methods=['GET', 'POST'])
@app.route('/admin/currency/<int:currency_id>/update/', methods=['GET', 'POST'])
@auth.admin_required
def admin_currency_update(currency_id=0):
  if currency_id:
    currency_db = model.Currency.get_by_id(currency_id)
  else:
    currency_db = model.Currency()

  if not currency_db:
    flask.abort(404)

  form = CurrencyUpdateAdminForm(obj=currency_db)

  if form.validate_on_submit():
    form.populate_obj(currency_db)
    currency_db.put()
    return flask.redirect(flask.url_for('admin_currency_list', order='-modified'))

  return flask.render_template(
    'currency/admin_currency_update.html',
    title='%s' % currency_db.name if currency_id else 'New Currency',
    html_class='admin-currency-update',
    form=form,
    currency_db=currency_db,
    back_url_for='admin_currency_list',
    api_url=flask.url_for('api.admin.currency', currency_key=currency_db.key.urlsafe() if currency_db.key else ''),
  )


###############################################################################
# Admin Delete
###############################################################################
@app.route('/admin/currency/<int:currency_id>/delete/', methods=['POST'])
@auth.admin_required
def admin_currency_delete(currency_id):
  currency_db = model.Currency.get_by_id(currency_id)
  currency_db.key.delete()
  flask.flash('Currency deleted.', category='success')
  return flask.redirect(flask.url_for('admin_currency_list'))
