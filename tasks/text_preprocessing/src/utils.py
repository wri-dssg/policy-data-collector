import re


def remove_html_tags(text):
    """Remove html tags from a string"""
    return re.sub(re.compile('<.*?>'), '', text)


def replace_links(text):
    text = re.sub(r'http\S+', '[URL]', text)
    return re.sub(r'www\S+', '[URL]', text)


def remove_multiple_spaces(text):
    return re.sub('\s+', ' ', text)


def parse_emails(text):
    """
    Remove the periods from emails in text, except the last one
    """
    emails = [email if email[-1] != "." else email[:-1] for email in re.findall(r"\S*@\S*\s?", txt)]

    for email in emails:
        new_email = email.replace(".", "")
        text = text.replace(email, new_email)

    return text


def parse_acronyms(text):
    """
    Remove the periods from acronyms in the text (i.e "U.S." becomes "US")
    """

    acronyms = re.findall(r"\b(?:[a-zA-Z]\.){2,}", text)

    for acronym in acronyms:
        new_acronym = acronym.replace(".", "")
        text = text.replace(acronym, new_acronym)

    return text