import json
import subprocess

from hotdoc.core import extension
from hotdoc.utils import loggable
from . import comment_scanner, formatter, introspector

_DESCRIPTION = '''
Output documentation for Endless's modular framework for offline apps.
Examines a module and outputs the documentation for using it from
app-description YAML.
'''


class HmfExtension(extension.Extension, loggable.Logger):
    extension_name = 'hotdoc_modular_framework'
    argument_prefix = 'mf'
    log_domain = 'modular-framework'

    def __init__(self, app, project):
        super().__init__(app, project)

        self.formatter = formatter.HmfFormatter(self)

    @staticmethod
    def add_arguments(parser):
        group = parser.add_argument_group('Modular framework', _DESCRIPTION)
        HmfExtension.add_index_argument(group)
        HmfExtension.add_sources_argument(group)

        HmfExtension.add_path_argument(group, 'introspect-utility',
            help_=('Path to the "introspect" utility from eos-knowledge-lib '
                '(if absent, look for it in PATH)'))

    def parse_config(self, config):
        """
        Overrides Extension.parse_config(), this is where we handle any custom
        command line arguments.
        """
        super().parse_config(config)

        if self.introspect_utility is None:
            self.introspect_utility = 'introspect'  # look up in PATH

    def setup(self):
        """
        Overrides Extension.setup(), this is where any updated source files are
        scanned.
        """
        super().setup()

        stale, unlisted = self.get_stale_files(self.sources)
        if not stale:
            self.info('Nothing to do', self.log_domain)
            return

        self.info('Refreshing {} files'.format(len(stale)), self.log_domain)

        ispect = introspector.Introspector(self)
        scanner = comment_scanner.Scanner()

        for f in stale:
            for comment in scanner.scan(f):
                self.app.database.add_comment(comment)

            data = subprocess.check_output([self.introspect_utility, '--file',
                f], universal_newlines=True)
            info = json.loads(data)
            ispect.create_symbols(info, f)


def get_extension_classes():
    return [HmfExtension]
