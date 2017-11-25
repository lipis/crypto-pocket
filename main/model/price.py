# coding: utf-8

from __future__ import absolute_import

from flask_babel import lazy_gettext as _
from google.appengine.ext import ndb

from api import fields
import model
import util


class Price(model.Base):
  currency_from_key = ndb.KeyProperty(kind=model.Currency, required=True, verbose_name=_(u'Currency From'))
  currency_to_key = ndb.KeyProperty(kind=model.Currency, required=True, verbose_name=_(u'Currency Key'))
  amount = ndb.FloatProperty(default=0, verbose_name=_(u'Amount'))

  @ndb.ComputedProperty
  def amount_currency(self):
    return '%.4f %s' % (self.amount, self.currency_to_key.get().code)

  @ndb.ComputedProperty
  def amount_invert(self):
    return 1.0 / self.amount

  FIELDS = {
    'currency_from_key': fields.Key,
    'currency_to_key': fields.Key,
    'amount': fields.Float,
  }

  FIELDS.update(model.Base.FIELDS)
