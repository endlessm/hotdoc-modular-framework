import sqlalchemy as sql

from hotdoc.core import symbols


class SlotSymbol(symbols.Symbol):
    """Represents a slot - Like a property, but instead of having a value, it's
    a place where another module can fit in."""

    # Sqlalchemy magic
    __tablename__ = 'slots'
    id_ = sql.Column(sql.Integer, sql.ForeignKey('symbols.id_'),
        primary_key=True)
    __mapper_args__ = {
        'polymorphic_identity': 'slots'
    }

    is_multi = sql.Column(sql.Boolean)
    is_array = sql.Column(sql.Boolean)

    def __init__(self, **kwargs):
        self.is_multi = kwargs.pop('multi', False)
        self.is_array = kwargs.pop('array', False)
        super().__init__(**kwargs)
