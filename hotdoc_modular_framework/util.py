from hotdoc.core import comment


def create_text_subcomment(com, text):
    """
    Create a new Comment instance for use as another Comment instance's title
    or short_description field.

    Args:
        com (hotdoc.core.Comment): the original Comment instance
        text (str): the text of the subcomment
    """
    return comment.Comment(raw_comment=text, filename=com.filename,
        lineno=com.lineno, endlineno=com.endlineno, description=text)
