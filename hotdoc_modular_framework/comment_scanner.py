import collections
import os.path
import re

from hotdoc.core import comment, exceptions
from hotdoc.utils import loggable
from . import util

_FIND_COMMENT = re.compile(r'/\*\*(.+?)\*/', re.DOTALL)

_MatchedComment = collections.namedtuple('_MatchedComment',
    ['body', 'start', 'end'])


class _CommentScannerException(exceptions.HotdocSourceException):
    """Warnings with which the comment scanner diagnoses stuff that should be
    corrected in the source."""
    pass

loggable.Logger.register_warning_code('missing-class-comment',
    _CommentScannerException, 'modular-framework')
loggable.Logger.register_warning_code('redundant-namespace',
    _CommentScannerException, 'modular-framework')


def _process_line(line):
    """Remove leading asterisks from doc comment."""
    line = line.strip()
    if line.startswith('* '):
        return line[2:]
    if line == '*':
        return ''
    return line


def _get_comment_bodies(source):
    """Iterator, gets verbatim text of all raw comments in source."""
    for match in _FIND_COMMENT.finditer(source):
        lines = match.group(1).splitlines()
        lines = map(_process_line, lines)

        yield _MatchedComment('\n'.join(lines).strip(), *match.span(1))


def _demodulize(ident):
    """Can't use str.capitalize() for this, because there may be capital
    letters elsewhere in the string."""
    return str.upper(ident[0]) + ident[1:]


def _consume_blanks(lines):
    """Drop all blank lines from the beginning of an array of lines, and return
    True if there are still any lines left to process."""
    while lines and len(lines[0]) == 0:
        lines.pop(0)
    return bool(lines)


class Scanner(loggable.Logger):
    """
    Takes care of extracting all the documentation comments from a source file.
    """

    def _figure_line_number(self, pos):
        """Return the line number corresponding to a file position."""
        return next(ix for ix, val in enumerate(self._linenos) if pos < val)

    def _annotate_from_naturaldocs_comment(self, com):
        """Try to put everything specific to the Naturaldocs comment format
        inside this method."""
        lines = com.raw_comment.splitlines()
        header_match = re.match(r'(\w+): (.*)', com.raw_comment)
        if header_match is not None:
            lines.pop(0)

            symbol_type, symbol_name = header_match.group(1, 2)
            if symbol_type == 'Class':
                namespace = _demodulize(os.path.basename(
                    os.path.dirname(com.filename)))
                com.name = '{}.{}'.format(namespace, symbol_name)

                if symbol_name.startswith(namespace + '.'):
                    self.warn('redundant-namespace',
                        message=('Redundant namespace {} in class comment'
                            .format(namespace)),
                        filename=com.filename, lineno=com.lineno)

                com.title = util.create_text_subcomment(com, com.name)
                self._current_class = com.name
            else:
                if self._current_class is None:
                    self.warn('missing-class-comment',
                        message='Missing class comment', filename=com.filename,
                        lineno=com.lineno)

                    namespace = _demodulize(os.path.basename(os.path.dirname(
                        com.filename)))
                    classname = _demodulize(os.path.basename(com.filename[:-3]))
                    self._current_class = '{}.{}'.format(namespace, classname)

                com.name = '{}:{}'.format(self._current_class, symbol_name)
                com.title = util.create_text_subcomment(com, symbol_name)

            if not _consume_blanks(lines):
                return

        # One-line description, followed by blank line, followed by more text,
        # means we should treat the one line as a short description
        if len(lines) > 2 and len(lines[1]) == 0:
            com.short_description = util.create_text_subcomment(com,
                lines.pop(0))
            if not _consume_blanks(lines):
                return

        com.description = '\n'.join(lines)

    def scan(self, filename):
        """
        Iterator, yielding `hotdoc.core.comment.Comment` instances based on
        all documentation comments (surrounded by /** */) in a source file.

        Args:
            filename (str): Filename to scan
        """
        source = ''
        self._linenos = [0]

        with open(filename, 'r', encoding='utf-8') as f:
            line = f.readline()
            while line:
                self._linenos.append(f.tell())
                source += line
                line = f.readline()

        self._current_class = None

        for matched in _get_comment_bodies(source):
            start_line = self._figure_line_number(matched.start)
            end_line = self._figure_line_number(matched.end)

            com = comment.Comment(raw_comment=matched.body, filename=filename,
                lineno=start_line, endlineno=end_line)

            self._annotate_from_naturaldocs_comment(com)

            yield com
