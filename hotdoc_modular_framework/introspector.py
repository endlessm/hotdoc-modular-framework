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


def _merge_comments(target, source, prefer_source=True):
    """Utility function to merge two Comment instances together."""

    props = ['title', 'params', 'topics', 'filename', 'line_offset',
        'col_offset', 'initial_col_offset', 'annotations', 'description',
        'short_description', 'extension_attrs', 'tags', 'raw_comment']
    for prop in props:
        # Overwrite target if property not present
        if not hasattr(target, prop) and hasattr(source, prop):
            setattr(target, prop, getattr(source, prop))
            continue

        # Overwrite target if property is default value (0, empty string)
        if not hasattr(source, prop):
            continue
        target_prop = getattr(target, prop)
        source_prop = getattr(source, prop)
        if not target_prop and source_prop:
            setattr(target, prop, source_prop)
            continue

        if prefer_source and source_prop:
            setattr(target, prop, source_prop)

    # Do the same thing for props whose default value is -1
    for prop in ['lineno', 'endlineno']:
        if not hasattr(target, prop) and hasattr(source, prop):
            setattr(target, prop, getattr(source, prop))
            continue

        if not hasattr(source, prop):
            continue
        target_prop = getattr(target, prop)
        source_prop = getattr(source, prop)
        if target_prop == -1 and source_prop != -1:
            setattr(target, prop, source_prop)
            continue

        if prefer_source and source_prop != -1:
            setattr(target, prop, source_prop)


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
            display_name=name, filename=self._filename, prop_type=type_symbol,
            extra={
                'default': info['default'],
            })

        doc = comment.Comment(name=unique_name, filename=self._filename,
            description=info['long_desc'])
        doc.title = util.create_text_subcomment(doc, name)
        doc.short_description = util.create_text_subcomment(doc,
            info['short_desc'])

        existing_comment = self.database.get_comment(unique_name)
        if existing_comment:
            _merge_comments(doc, existing_comment)

        self.database.add_comment(doc)
