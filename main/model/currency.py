# coding: utf-8

from __future__ import absolute_import

from flask_babel import lazy_gettext as _
from google.appengine.ext import ndb

from api import fields
import model
import util


class Currency(model.Base):
  name = ndb.StringProperty(required=True, verbose_name=_(u'Name'))
  code = ndb.StringProperty(required=True, verbose_name=_(u'Code'))
  is_crypto = ndb.BooleanProperty(default=True, verbose_name=_(u'Is Crypto'))

  @classmethod
  def get_dbs(cls, order=None, **kwargs):
    return super(Currency, cls).get_dbs(
      order=order or util.param('order') or 'is_crypt,name',
      **kwargs
    )

  def get_transaction_dbs(self, **kwargs):
    return model.Transaction.get_dbs(spent_currency_key=self.key, **kwargs)

  def get_price_dbs(self, **kwargs):
    return model.Price.get_dbs(currency_from_key=self.key, **kwargs)

  def _pre_put_hook(self):
    self.code = self.code.upper()

  @classmethod
  def _pre_delete_hook(cls, key):
    currency_db = key.get()
    transaction_keys = currency_db.get_transaction_dbs(keys_only=True, limit=-1)[0]
    price_keys = currency_db.get_price_dbs(keys_only=True, limit=-1)[0]
    ndb.delete_multi(transaction_keys + price_keys)

  FIELDS = {
    'name': fields.String,
    'code': fields.String,
    'is_crypto': fields.Boolean,
  }

  FIELDS.update(model.Base.FIELDS)
