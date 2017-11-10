import re


def remove_parenthesis(text):
    return re.sub(r"\(.+\)$", "", text)

def remove_ellipsis(text):
    return re.sub(r"\.+$", "", text)


def remove_redundant_chars(text):
    text = text.strip()
    text = remove_parenthesis(text)
    text = text.strip()
    text = remove_ellipsis(text)
    text = text.strip()
    return text