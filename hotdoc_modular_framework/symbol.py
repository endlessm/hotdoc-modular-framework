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
    is_optional = sql.Column(sql.Boolean)
    allowed_modules = sql.Column(sql.PickleType)

    def __init__(self, **kwargs):
        self.is_multi = kwargs.pop('multi', False)
        self.is_array = kwargs.pop('array', False)
        self.is_optional = kwargs.pop('is_optional', False)
        self.allowed_modules = kwargs.pop('allowed_modules', [])
        super().__init__(**kwargs)


class ReferenceSymbol(symbols.Symbol):
    """Modules can have references to other modules. Unlike slots, which create
    the modules on demand, a reference points to a module that exists elsewhere
    in the module tree."""

    # Sqlalchemy magic
    __tablename__ = 'references'
    id_ = sql.Column(sql.Integer, sql.ForeignKey('symbols.id_'),
        primary_key=True)
    __mapper_args__ = {
        'polymorphic_identity': 'references'
    }
