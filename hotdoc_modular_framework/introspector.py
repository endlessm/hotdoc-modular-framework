from hotdoc.core import comment, symbols
from . import util

_WHITELIST_TYPES = ['Number', 'String', 'Boolean',
    'GtkAlign', 'GtkJustification', 'GtkOrientation', 'GtkStackTransitionType',
    'PangoEllipsizeMode', 'PangoWrapMode']
_BLACKLIST_ORIGINS = ['Gjs_Module', 'GtkActionable', 'GtkActivatable',
    'GtkButton', 'GtkContainer', 'GtkGrid', 'GtkWindow']
_WHITELIST_PROPERTIES = {
    'GtkEntry': ['max-length', 'max-width-chars', 'placeholder-text',
        'width-chars'],
    'GtkLabel': ['angle', 'ellipsize', 'justify', 'label', 'lines',
        'max-width-chars', 'selectable', 'single-line-mode', 'width-chars',
        'wrap', 'wrap-mode'],
    'GtkStack': ['transition-duration', 'transition-type'],
    'GtkWidget': ['expand', 'halign', 'hexpand', 'orientation', 'valign',
        'vexpand'],
}


class Introspector:
    """
    This analyzes the JSON introspection info obtained from a module, and
    creates Hotdoc symbols based on it.
    """

    def __init__(self, extension):
        self.extension = extension
        self.database = extension.app.database
        self._filename = None

    def create_symbols(self, info, filename):
        """
        Create symbols for a JSON introspection info object.

        Args:
            info (dict): JSON introspection info obtained from the
                introspect utility
            filename (str): Filename containing the code that was introspected
        """
        self._filename = filename

        name = info['name']

        self.extension.get_or_create_symbol(symbols.ClassSymbol,
            display_name=name, filename=self._filename)

        for p in info['properties']:
            self._process_property(p, name)

        # Done with this file
        self._filename = None

    def _process_property(self, info, module_name):
        """Create symbols for property introspection info."""

        name = info['name']
        origin = info['origin']
        type_name = info['type']

        # Skip over any code-only properties: we only want properties that make
        # sense to use from the YAML
        if not info['writable']:
            return
        if type_name not in _WHITELIST_TYPES:
            return
        if origin in _BLACKLIST_ORIGINS:
            return
        if (origin in _WHITELIST_PROPERTIES and
            name not in _WHITELIST_PROPERTIES[origin]):
            return

        type_symbol = symbols.QualifiedSymbol(type_tokens=type_name)
        unique_name = '{}:{}'.format(module_name, name)

        self.extension.get_or_create_symbol(symbols.PropertySymbol,
            unique_name=unique_name,
            display_name=name, filename=self._filename, prop_type=type_symbol)

        doc = comment.Comment(name=unique_name, filename=self._filename,
            description=info['long_desc'])
        doc.title = util.create_text_subcomment(doc, name)
        doc.short_description = util.create_text_subcomment(doc,
            info['short_desc'])

        self.database.add_comment(doc)
