from hotdoc.core import symbols


class Introspector:
    """
    This analyzes the JSON introspection info obtained from a module, and
    creates Hotdoc symbols based on it.
    """

    def __init__(self, extension):
        self.extension = extension

    def create_symbols(self, info, filename):
        """
        Create symbols for a JSON introspection info object.

        Args:
            info (dict): JSON introspection info obtained from the
                introspect utility
            filename (str): Filename containing the code that was introspected
        """
        self.extension.get_or_create_symbol(symbols.ClassSymbol,
            display_name=info['name'], filename=filename)
