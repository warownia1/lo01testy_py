"""
Module providing a simplified markup to html conversion.
It may be used to format questions and answers in the test.

Conversions:
  **   : <strong>
  __   : <em>
  `    : <code>
    \n : <br /> (double whitespace and line feed)

all special characters preceded with \ are escaped
"""

import re


def get_html(text):
    """Convert markdown sumbols to html tags"""
    text = substitute_group_marks(text)
    text = substitute_newlines(text)
    text = unescape(text)
    return text


def substitute_group_marks(text):
    """Substitute text captured by marks into html syntax"""
    for (mark, tag) in [("\\*\\*", "strong"), ("__", "em"),
                        ("`", "code")]:
        text = re.sub(
            r"(?<!\\){0}(.*?[^\\]){0}".format(mark),
            r"<{0}>\1</{0}>".format(tag),
            text, flags=re.S
        )
    return text


def substitute_newlines(text):
    return re.sub(r"  \n", "<br />\n", text)


def unescape(text):
    return re.sub(r"\\([\\\*_`])", r"\1", text)
