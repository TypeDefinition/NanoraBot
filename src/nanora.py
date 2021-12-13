import regex
import better_profanity

# Constants
BOT_NAME = "NanoraBot"
TRIGGER = "!nanora"
FAILED_MESSAGE = "Sorry! I am unable to nanora that for some reason!"
SUBREDDIT_LIST = ("u_" + BOT_NAME, BOT_NAME, "Hololive", "Hololewd", "OKBuddyHololive")
# SUBREDDIT_LIST = ("u_" + BOT_NAME, BOT_NAME)

ZERO_WIDTH_WHITESPACE = str("​") # Note: len(ZERO_WIDTH_WHITESPACE) is 1.

def is_japanese(text):
    return regex.compile("[\u3000-\u303f\u3040-\u309f\u30a0-\u30ff\uff00-\uff9f\u4e00-\u9faf\u3400-\u4dbf]").search(text)

def nanora(text):
    text += '\n' # Just to make the matching work if the text doesn't already include a newline at the end.
    modified_text = text

    en_punctuation_list = ['.', '?', '!', '\]', '\n']
    jp_punctuation_list = ['。', '？', '！', '」', '・', '”', '】', '』', '；']
    punctuation_list = en_punctuation_list + jp_punctuation_list

    en_keyword = " nanora"
    jp_keyword = "なのら"

    # Pattern looks incomprehensible, but it just matches links, and any punctuation at the end (plus parenthesis).
    link_pattern = rf'https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]*\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)([{"".join(punctuation_list)})])*'
    # Pattern matches any punctuation, with the exception of those in spoiler tags.
    incomp_pattern = rf'(?<!<|!>)([{"".join(punctuation_list)}]+)(?!>)'
    # Pattern matches any punctuation not in a link.
    punctuation_pattern = regex.compile(rf'(?<!({link_pattern})){incomp_pattern}')

    offset = 0 # Everytime we insert a keyword, the length of the text grows.
    for match in punctuation_pattern.finditer(text):
        # Reverse the text, and search from the match.start() to the beginning.
        # Find the nearest alphanumeric (excluding underscores) behind match.start().
        last_alphanum = regex.search(r'[^\W_]', text[match.start()::-1])
        try:
            # Since last_alphanum was found using the reversed text, last_alphanum.start() gives
            # us how many characters before match_idx the last alphanumeric appears.
            # Therefore we need to do match_idx - last_alphanum.start() + 1.
            insert_idx = match.start() - last_alphanum.start() + 1

            if is_japanese(last_alphanum.group()):
                keyword = jp_keyword
            elif last_alphanum.group().isupper():
                keyword = en_keyword.upper()
            else:
                keyword = en_keyword.lower()
        except AttributeError: # The entire string is just non-alphanumeric.
            continue

        # Ignore triggers.
        if text[insert_idx - len(TRIGGER):insert_idx] == TRIGGER:
            continue

        # Ignore non-breaking spaces.
        if text[insert_idx - len('&#x200B'):insert_idx] == '&#x200B':
            continue

        # Insert keyword.
        modified_text = modified_text[:insert_idx + offset] + keyword + modified_text[insert_idx + offset:]
        offset += len(keyword)

    # Check if text was successfully modified.
    if modified_text == text:
        return FAILED_MESSAGE

    # Add zero-width whitespace to disable mentioning usernames.
    modified_text = modified_text[:-1].replace('u/',f'u{ZERO_WIDTH_WHITESPACE}/')
    # Censor profanity.
    modified_text = better_profanity.profanity.censor(modified_text, '\*')

    return modified_text