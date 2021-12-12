import regex
from regex.regex import search
import better_profanity

from better_profanity import profanity

# Constants
BOT_NAME = "NanoraBot"
TRIGGER = "!nanora"
FAILED_MESSAGE = "Sorry! I am unable to nanora that for some reason!"
DEBUG_SUBREDDIT_LIST = ("u_" + BOT_NAME, BOT_NAME)
RELEASE_SUBREDDIT_LIST = ("u_" + BOT_NAME, BOT_NAME, "hololive", "Hololewd", "okbuddyhololive")

ZERO_WIDTH_WHITESPACE = str("​") # Note: len(ZERO_WIDTH_WHITESPACE) is 1.

def is_japanese(text):
    return regex.compile("[\u3000-\u303f\u3040-\u309f\u30a0-\u30ff\uff00-\uff9f\u4e00-\u9faf\u3400-\u4dbf}]").search(text)

def nanora(text):
    # Just to make the matching work if the text doesn't already include a newline at the end.
    modified_text = text + '\n'

    en_punctuation_list = ['.', '?', '!', '\]', '\n']
    jp_punctuation_list = ['。', '？', '！', '」', '・', '”', '】', '』', '；']
    punctuation_list = en_punctuation_list + jp_punctuation_list

    en_keyword = " nora"
    jp_keyword = "ーのら"

    # Pattern looks incomprehensible, but it just matches links, and any punctuation at the end (plus parenthesis).
    link_pattern = rf'https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]*\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)([{"".join(punctuation_list)})])*'
    # Pattern matches any punctuation, with the exception of those in spoiler tags.
    incomp_pattern = rf'(?<!<|!>)([{"".join(punctuation_list)}]+)(?!>)'
    # Pattern matches any punctuation not in a link.
    punctuation_pattern = regex.compile(rf'(?<!({link_pattern})){incomp_pattern}')

    offset = 0
    for match in punctuation_pattern.finditer(modified_text):
        i = match.start() + offset # match point
        last_word = regex.search(r'[^\W_]', modified_text[i::-1]) # Find the nearest alphanumeric behind match point.
        try:
            j = i - last_word.start() + 1 # Index to insert keyword.
            if is_japanese(last_word.group()):
                keyword = jp_keyword
            elif last_word.group().isupper():
                keyword = en_keyword.upper()
            else:
                keyword = en_keyword.lower()
        except AttributeError: # The entire string is just non-alphanumeric.
            continue

        # Exceptions
        # General case for when there's already a nanora and it's newly added.
        already_keyword = (modified_text[j - len(keyword):j] == keyword)
        if_newly_added = (text[j - offset - len(keyword):j - offset] == keyword)
        # Ignore triggers.
        is_trigger = (modified_text[j - len(TRIGGER):j] == TRIGGER)
        # NBSP-specific exception.
        nbsp = modified_text[j - len('&#x200B'):j] == '&#x200B'
        if (already_keyword and not if_newly_added) or nbsp or is_trigger:
            continue

        modified_text = modified_text[:j] + keyword + modified_text[j:]
        offset += len(keyword)

    # Check if text was successfully modified.
    if modified_text == text:
        return FAILED_MESSAGE

    # Add zero-width whitespace to disable mentioning usernames.
    modified_text = modified_text[:-1].replace('u/',f'u{ZERO_WIDTH_WHITESPACE}/')

    # Censor profanity.
    modified_text = profanity.censor(modified_text, '\*')

    return modified_text