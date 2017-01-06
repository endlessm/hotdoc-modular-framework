from hotdoc.core import extension

_DESCRIPTION = '''
Output documentation for Endless's modular framework for offline apps.
Examines a module and outputs the documentation for using it from
app-description YAML.
'''


class HmfExtension(extension.Extension):
    extension_name = 'hotdoc_modular_framework'

    def __init__(self, app, project):
        super().__init__(app, project)

    @staticmethod
    def add_arguments(parser):
        parser.add_argument_group('Modular framework', _DESCRIPTION)


def get_extension_classes():
    return [HmfExtension]
