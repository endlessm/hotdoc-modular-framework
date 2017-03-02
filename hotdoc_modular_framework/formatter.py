import os

from hotdoc.core import formatter, symbols


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
        })

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
