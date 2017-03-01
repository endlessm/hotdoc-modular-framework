import os

from hotdoc.core import formatter


class HmfFormatter(formatter.Formatter):
    """
    This overrides the default Hotdoc formatter and its templates, in order to
    render modular framework documentation the way we want it rendered.
    """

    def __init__(self, link_resolver):
        module_path = os.path.dirname(__file__)
        searchpath = [os.path.join(module_path, 'templates')]

        super().__init__(link_resolver, searchpath)
