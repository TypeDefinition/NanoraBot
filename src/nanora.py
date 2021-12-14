import regex
import better_profanity

# Constants
BOT_NAME = "NanoraBot"
TRIGGER = "!nanora"
FAILED_MESSAGE = "Sorry! I am unable to nanora that for some reason!"

ZERO_WIDTH_SPACE = "\u200B" # Note: len(ZERO_WIDTH_SPACE) is 1.
ALPHANUM = "a-zA-Z0-9"
HIRAGANA = "\u3041-\u3096"
KATAKANA = "\u30A0-\u30FF"
KANJI = "\u2E80-\u2FD5"
HALF_WIDTH_KATAKANA_AND_PUNCTUATIONS = "\uFF5F-\uFF9F"
JAP_MISC_SYMBOLS = "\u31F0-\u31FF\u3220-\u3243\u3280-\u337F"
JAP_ALPHANUM_AND_PUNCTUATIONS = "\uFF01-\uFF5E"
WORDS = f"[{ALPHANUM}{HIRAGANA}{KATAKANA}{KANJI}]" # Working with regex has greatly reduced my lifespan.

SUBREDDIT_LIST = ("u_" + BOT_NAME, BOT_NAME, "Hololive", "Hololewd", "OKBuddyHololive", "GoodAnimemes")

def is_japanese(text):
    return regex.compile(f"[{HIRAGANA}{KATAKANA}{KANJI}{HALF_WIDTH_KATAKANA_AND_PUNCTUATIONS}{JAP_MISC_SYMBOLS}{JAP_ALPHANUM_AND_PUNCTUATIONS}]").search(text)

def is_hiragana(text):
    return regex.compile(f"[{HIRAGANA}]").search(text)

def is_katakana(text):
    return regex.compile(f"[{KATAKANA}]").search(text)

def nanora(text):
    text += '\n' # Just to make the matching work if the text doesn't already include a newline at the end.
    modified_text = text

    en_punctuation_list = ['.', '?', '!', '\]', '\n']
    jp_punctuation_list = ['。', '？', '！', '」', '・', '”', '】', '』', '；']
    punctuation_list = en_punctuation_list + jp_punctuation_list

    # Pattern looks incomprehensible, but it just matches links, and any punctuation at the end (plus parenthesis).
    link_pattern = rf'https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]*\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)([{"".join(punctuation_list)})])*'
    # Pattern matches any punctuation, with the exception of those in spoiler tags.
    punctuation_pattern = rf'(?<!<|!>)([{"".join(punctuation_list)}]+)(?!>)'
    # Pattern matches any words that ends with "na", "no", "な" or "の", excluding these by themselves.
    nano_pattern = rf'{WORDS}+(na|no|NA|NO|な|の|ナ|ノ)\b'
    # Pattern matches any english or japanese words.
    word_pattern = rf"{WORDS}"
    # Pattern matches anywhere we want to insert a keyword.
    insertion_pattern = rf'(?<!({link_pattern}))({punctuation_pattern}|{nano_pattern})'

    offset = 0 # Everytime we insert a keyword, the length of the text grows.
    last_insert_idx = -1 # Sometimes there is a punctuation immediately after a word we nanora-ed. In that case, do not nanora it again.
    for match in regex.finditer(rf"{insertion_pattern}", text):
        try:
            if regex.search(rf"{punctuation_pattern}", text[match.start()]): # If this is a punctuation, we want to add the keyword BEFORE the punctuation.
                last_alphanum = regex.search(rf"{WORDS}", text[match.start()::-1])
                insert_idx = match.start() - last_alphanum.start() + 1
            else: # If this is a word, we want to add the keyword AFTER the word.
                last_alphanum = regex.search(rf"{WORDS}", text[match.end()-1::-1])
                insert_idx = match.end()

            if insert_idx == last_insert_idx:
                continue
            last_insert_idx = insert_idx

            # Ignore Princess Himemori Luna's name.
            if text[insert_idx-len("Luna"):insert_idx].title() == "Luna":
                continue
            if text[insert_idx-len("ルーナ"):insert_idx] == "ルーナ":
                continue

            # Decide the keyword based on the previous word.
            if is_japanese(last_alphanum.group()):
                if text[insert_idx-len("の"):insert_idx] == "の":
                    keyword = "ら"
                elif text[insert_idx-len("な"):insert_idx] == "な":
                    keyword = "のら"
                elif text[insert_idx-len("ノ"):insert_idx] == "ノ":
                    keyword = "ラ"
                elif text[insert_idx-len("ナ"):insert_idx] == "ナ":
                    keyword = "ノラ"
                elif is_katakana(last_alphanum.group()):
                    keyword = "ナノラ"
                else:
                    keyword = "なのら"
            else:
                if text[insert_idx-len("no"):insert_idx] == "no":
                    keyword = "ra"
                elif text[insert_idx-len("na"):insert_idx] == "na":
                    keyword = "nora"
                elif text[insert_idx-len("NO"):insert_idx] == "NO":
                    keyword = "RA"
                elif text[insert_idx-len("NA"):insert_idx] == "NA":
                    keyword = "NORA"
                elif text[insert_idx-1:insert_idx].isupper():
                    keyword = " NANORA"
                else:
                    keyword = " nanora"
        except AttributeError: # The entire string is just non-alphanumeric.
            continue

        # Ignore triggers.
        if text[insert_idx-len(TRIGGER):insert_idx] == TRIGGER:
            continue

        # Ignore zero width spaces.
        if text[insert_idx-len(ZERO_WIDTH_SPACE):insert_idx] == ZERO_WIDTH_SPACE:
            continue

        # Insert keyword.
        modified_text = modified_text[:insert_idx+offset]+keyword+modified_text[insert_idx+offset:]
        offset += len(keyword)

    # Check if text was successfully modified.
    if modified_text == text:
        return FAILED_MESSAGE

    # Add zero-width whitespace to disable mentioning usernames.
    modified_text = modified_text[:-1].replace('u/',f'u{ZERO_WIDTH_SPACE}/')
    # Censor profanity.
    modified_text = better_profanity.profanity.censor(modified_text, '\*')

    return modified_text