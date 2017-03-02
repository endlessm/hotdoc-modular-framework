import os

from hotdoc.core import formatter, symbols
from . import symbol


class HmfFormatter(formatter.Formatter):
    """
    This overrides the default Hotdoc formatter and its templates, in order to
    render modular framework documentation the way we want it rendered.
    """

    def __init__(self, link_resolver):
        module_path = os.path.dirname(__file__)
        searchpath = [os.path.join(module_path, 'templates')]

        super().__init__(link_resolver, searchpath)

        # FIXME Private API: https://github.com/hotdoc/hotdoc/issues/96
        self._symbol_formatters.update({
            symbols.PropertySymbol: self._format_property_symbol,
            symbol.SlotSymbol: self._format_slot_symbol,
        })
        self._ordering.insert(self._ordering.index(symbols.PropertySymbol) + 1,
            symbol.SlotSymbol)

    def _format_property_symbol(self, prop):
        """Render modular framework property template."""

        # FIXME Private API: https://github.com/hotdoc/hotdoc/issues/96
        type_link = self._format_linked_symbol(prop.prop_type)
        template = self.engine.get_template('property.html')
        res = template.render({
            'symbol': prop,
            'property': prop,
            'property_name': prop.link.title,
            'property_type': type_link,
            'extra': {
                'Type': type_link,
                'Default value': str(prop.extra['default']),
            },
        })
        return res, False

    def _format_slot_symbol(self, slot):
        """Render modular framework slot template."""

        template = self.engine.get_template('slot.html')
        res = template.render({
            'symbol': slot,
            'slot': slot,
            'slot_name': slot.link.title,
        })
        return res, False
