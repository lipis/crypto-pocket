# coding: utf-8

from __future__ import absolute_import

from flask_babel import lazy_gettext as _
from google.appengine.ext import ndb

from api import fields
import model
import util
import crypto


class Transaction(model.Base):
  user_key = ndb.KeyProperty(kind=model.User, required=True, verbose_name=_(u'User Key'))
  date = ndb.DateProperty(required=True, verbose_name=_(u'Date'))
  spent_amount = ndb.FloatProperty(default=0, verbose_name=_(u'Spent'))
  spent_currency_key = ndb.KeyProperty(kind=model.Currency, required=True, verbose_name=_(u'Spent Currency'))
  fee = ndb.FloatProperty(default=0, verbose_name=_(u'Fee'))
  acquired_amount = ndb.FloatProperty(default=0, verbose_name=_(u'Acquired'))
  acquired_currency_key = ndb.KeyProperty(kind=model.Currency, verbose_name=_(u'Acquired Currency'))
  notes = ndb.StringProperty(default='', verbose_name=_(u'Notes'))
  platform = ndb.StringProperty(default='', verbose_name=_(u'Platform'))

  @ndb.ComputedProperty
  def spent(self):
    return self.spent_amount

  @ndb.ComputedProperty
  def acquired(self):
    return self.acquired_amount

  @ndb.ComputedProperty
  def acquired_rate(self):
    if self.acquired_amount != 0:
      return self.spent_amount / self.acquired_amount
    return 0

  @ndb.ComputedProperty
  def current_rate(self):
    return crypto.get_exchange_rate_by_keys(self.acquired_currency_key, self.spent_currency_key)

  @ndb.ComputedProperty
  def profit_amount(self):
    return (self.current_rate - self.acquired_rate) * self.acquired_amount - self.fee

  @ndb.ComputedProperty
  def profit_percentage(self):
    if self.acquired_rate != 0:
      return (self.current_rate / self.acquired_rate - 1) * 100
    return 0

  @ndb.ComputedProperty
  def total(self):
    return self.profit_amount + self.spent_amount

  @classmethod
  def get_dbs(cls, order=None, **kwargs):
    return super(Transaction, cls).get_dbs(
      order=order or util.param('order') or '-profit_percentage',
      **kwargs
    )

  FIELDS = {
    'acquired_amount': fields.Float,
    'acquired_currency_key': fields.Key,
    'acquired_rate': fields.Float,
    'acquired': fields.Float,
    'current_rate': fields.Float,
    'date': fields.DateTime,
    'fee': fields.Float,
    'notes': fields.String,
    'platform': fields.String,
    'profit_amount': fields.Float,
    'profit_percentage': fields.Float,
    'spent_amount': fields.Float,
    'spent_currency_key': fields.Key,
    'spent': fields.Float,
    'total': fields.Float,
    'user_key': fields.Key,
  }

  FIELDS.update(model.Base.FIELDS)
