import better_profanity
import random
import regex

# Constants
BOT_NAME = "NanoraBot"
TRIGGER_NANORA = "!nanora"
TRIGGER_GOOD_BOT = "good bot"
FAILED_MESSAGE = "Sorry! I am unable to nanora that for some reason!"
THANK_MESSAGES = ["Thank you nanora!", "uwu :3", "ありがちゅ！", "すっ、すき…\n\n\n\nバ、バカ！", "ぎゅ〜 <3"]

ZERO_WIDTH_SPACE = "\u200B" # Note: len(ZERO_WIDTH_SPACE) is 1.

ALPHANUM = "a-zA-Z0-9"
HIRAGANA = "\u3041-\u3096"
KATAKANA = "\u30A0-\u30FF"
KANJI = "\u3400-\u4DB5\u4E00-\u9FCB\uF900-\uFA6A"
KANJI_RADICALS = "\u2E80-\u2FD5"
HALF_WIDTH_KATAKANA_AND_PUNCTUATIONS = "\uFF5F-\uFF9F"
JAP_MISC_SYMBOLS = "\u31F0-\u31FF\u3220-\u3243\u3280-\u337F"
JAP_ALPHANUM_AND_PUNCTUATIONS = "\uFF01-\uFF5E"
WORDS = f"[{ALPHANUM}{HIRAGANA}{KATAKANA}{KANJI}{KANJI_RADICALS}]" # Working with regex has greatly reduced my lifespan.

EN_PUNCTUATION = ('.', '?', '!', '\]', '\n')
JP_PUNCTUATION = ('。', '？', '！', '」', '・', '”', '】', '』', '；', '、')
PUNCTUATION = EN_PUNCTUATION + JP_PUNCTUATION

LOWERCASE_NORABLE = "[a-z]a"
UPPERCASE_NORABLE = "[A-Z]A"
HIRAGANA_NORABLE = rf"[{HIRAGANA}]?[かさたなまやがざだばぱ]|ああ|です"
KATAKANA_NORABLE = rf"[{KATAKANA}]?[カサタナハマヤガザダバパ]|アア"

# Pattern looks incomprehensible, but it just matches links, and any punctuation at the end (plus parenthesis).
LINK_PATTERN = rf'https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]*\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)([{"".join(PUNCTUATION)})])*'
# Pattern matches any punctuation, with the exception of those in spoiler tags.
PUNCTUATION_PATTERN = rf'(?<!<|!>)([{"".join(PUNCTUATION)}]+)(?!>)'
# Pattern matches words that may be able to end with a "のら".
NANORA_PATTERN = rf'{WORDS}+(no|NO|{LOWERCASE_NORABLE}|{UPPERCASE_NORABLE}|の|ノ|{HIRAGANA_NORABLE}|{KATAKANA_NORABLE})\b'
# Pattern matches anywhere we want to insert a keyword.
INSERTION_PATTERN = rf'(?<!({LINK_PATTERN}))({PUNCTUATION_PATTERN}|{NANORA_PATTERN})'

def is_japanese(text):
    return regex.compile(f"[{HIRAGANA}{KATAKANA}{KANJI}{KANJI_RADICALS}{HALF_WIDTH_KATAKANA_AND_PUNCTUATIONS}{JAP_MISC_SYMBOLS}{JAP_ALPHANUM_AND_PUNCTUATIONS}]").search(text)

def is_hiragana(text):
    return regex.compile(f"[{HIRAGANA}]").search(text)

def is_katakana(text):
    return regex.compile(f"[{KATAKANA}]").search(text)

def get_thank_message():
    return THANK_MESSAGES[random.randrange(0, len(THANK_MESSAGES))]

def nanora(text, censor):
    text += '\n' # Just to make the matching work if the text doesn't already include a newline at the end.
    modified_text = text

    offset = 0 # Everytime we insert a keyword, the length of the text grows.
    last_insert_idx = -1 # Sometimes there is a punctuation immediately after a word we nanora-ed. In that case, do not nanora it again.
    for match in regex.finditer(rf"{INSERTION_PATTERN}", text):
        try:
            if regex.search(rf"{PUNCTUATION_PATTERN}", text[match.start()]): # If this is a punctuation, we want to add the keyword BEFORE the punctuation.
                last_word_char = regex.search(rf"{WORDS}", text[match.start()::-1])
                insert_idx = match.start() - last_word_char.start() + 1
            else: # If this is a word, we want to add the keyword AFTER the word.
                last_word_char = regex.search(rf"{WORDS}", text[match.end()-1::-1])
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
            if is_japanese(last_word_char.group()):
                if text[insert_idx-1] == "の":
                    keyword = "ーら"
                elif text[insert_idx-1] == "ノ":
                    keyword = "ーラ"
                elif regex.search(rf"({HIRAGANA_NORABLE})", text[insert_idx-2:insert_idx]):
                    keyword = "ーのら"
                elif regex.search(rf"({KATAKANA_NORABLE})", text[insert_idx-2:insert_idx]):
                    keyword = "ーノラ"
                else:
                    keyword = "ーナノラ" if is_katakana(text[insert_idx-1]) else "ーなのら"
            else:
                if text[insert_idx-2:insert_idx] == "no":
                    keyword = "-ra"
                elif text[insert_idx-2:insert_idx] == "NO":
                    keyword = "-RA"
                elif regex.search(rf"({LOWERCASE_NORABLE})", text[insert_idx-2:insert_idx]):
                    keyword = "-nora"
                elif regex.search(rf"({UPPERCASE_NORABLE})", text[insert_idx-2:insert_idx]):
                    keyword = "-NORA"
                else:
                    keyword = " NANORA" if text[insert_idx-1].isupper() else " nanora"
        except AttributeError: # The entire string does not contain any words.
            continue

        # Ignore triggers.
        if text[insert_idx-len(TRIGGER_NANORA):insert_idx] == TRIGGER_NANORA:
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
    if censor:
        modified_text = better_profanity.profanity.censor(modified_text, '\*')

    return modified_text