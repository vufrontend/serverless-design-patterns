from .base import CuppingServiceBaseMixin
from ..db.mixins import Base

from sqlalchemy.orm import relationship, validates

from sqlalchemy import (
                Boolean,
                Column,
                ForeignKey,
                Integer,
                Numeric,
                String,
)

# class Session(Model):
#     name = StringType(max_length=127, required=True)
#     form_name = StringType(max_length=127, required=True)
#     account_id = IntType()
#     user_id = IntType()
#
#     cuppings = ListType(ModelType(Cupping))
#

class Session(CuppingServiceBaseMixin, Base):
    """A group of cuppings."""
    __tablename__ = 'sessions'

    name = Column(String(length=127))

    form_name = Column(String(length=127))

    account_id = Column(Integer, nullable=True)

    user_id = Column(Integer, nullable=True)

    cuppings = relationship('Cupping', order_by='Cupping.id', back_populates='session')

    def _validate_integer(self, key, value):
        try:
            return int(value)
        except ValueError:
            raise ValueError('%s field must be an integer value' % (key, ))

    def _validate_string(self, key, value):
        if not value.strip():
            raise ValueError('%s field must be non-empty string' % (key, ))
        return value

    @validates('name')
    def validate_name(self, key, value):
        return self._validate_string(key, value)

    @validates('form_name')
    def validate_form_name(self, key, value):
        return self._validate_string(key, value)

    @validates('account_id')
    def validate_account_id(self, key, value):
        if value:
            return self._validate_integer(key, value)

    @validates('user_id')
    def validate_user_id(self, key, value):
        if value:
            return self._validate_integer(key, value)

    @classmethod
    def from_model(cls, model):
        with dbtransaction():
            session = cls(
                    name=model.name,
                    form_name=model.form_name,
                    account_id=model.account_id,
                    user_id=model.user_id,
            )
            session.save()
            session.flush()

            cuppings = [
                    Cupping.from_model(c) \
                    for c in model.get('cuppings', ())
            ]

            return session