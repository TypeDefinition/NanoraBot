import better_profanity
import random
import regex

# Constants
BOT_NAME = "NanoraBot"

TRIGGER_LUNA_POST = "luna"
TRIGGER_LUNA_POST_JP = "ルーナ"
TRIGGER_NANORA = "!nanora"
TRIGGER_GOOD_BOT = "good bot"
TRIGGER_CUTE_BOT = "cute bot"
TRIGGER_NTF = "!ntf"
TRIGGER_QUOTE = "!qnanora"

LUNA_SUBMISSION_MESSAGES = ["Luna is adult sexy wonderful beautiful cute sexy adult nanora!", \
    "Luna is cutest beautiful genius sexy professor adult wonderful great excellent perfect nanora. えへへ!", \
    "ルーナが一番可愛いのら! CIJ! CIJ!", \
    "なのら…　なのら…　なのらがやがて来た！"]
FAILED_MESSAGE = "Sorry! I am unable to nanora that for some reason!"
THANK_MESSAGES = ["Thank you nanora!", "uwu :3", "ありがちゅ！", "すっ、好きのら…", "ぎゅ〜 <3", "えへへ！嬉しいのら！"]
SPAM_MESSAGE = "Sorry! I cannot continue to reply to this thread due to possible spam nanora."
NTF_MESSAGE = "何 the fuck did you just fucking 言います about 私, you 小さい bitch ですか? \
    私'll have あなた know that 私 graduated top of my class in 日本語3, and 私've been involved in 色々な日本語 tutoring sessions, and 私 have over 300 perfect test scores. \
    私 am trained in 漢字, and 私 is the top letter writer in all of southern California. あなた are nothing to 私 but another weabo. \
    私 will 殺す あなた the fuck out with vocabulary the likes of which has never been 見ました before on this continent. \
    Mark 私の fucking words. あなた thinks あなた can get away with 話します-ing that クソ to 私 over the インターネット? 思う again, fucker. \
    As we 話します, 私 am contacting 私の secret ネット of オタクs across the USA, and あなたの IP is being traced right now so you better 準備します for the 雨, 蛆虫. \
    The 雨 that 殺す the pathetic 小さい thing あなた calls あなたの life. You're fucking 死にました'd, 赤ちゃん."

ZERO_WIDTH_SPACE = "\u200B" # Note: len(ZERO_WIDTH_SPACE) is 1.
NBSP = "&nbsp;"

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
# Pattern matches new lines.
NEW_LINE_PATTERN = rf'[\n]'

def is_japanese(text):
    return regex.compile(f"[{HIRAGANA}{KATAKANA}{KANJI}{KANJI_RADICALS}{HALF_WIDTH_KATAKANA_AND_PUNCTUATIONS}{JAP_MISC_SYMBOLS}{JAP_ALPHANUM_AND_PUNCTUATIONS}]").search(text)

def is_hiragana(text):
    return regex.compile(f"[{HIRAGANA}]").search(text)

def is_katakana(text):
    return regex.compile(f"[{KATAKANA}]").search(text)

def get_luna_submission_message():
    return LUNA_SUBMISSION_MESSAGES[random.randrange(0, len(LUNA_SUBMISSION_MESSAGES))]

def get_thank_message():
    return THANK_MESSAGES[random.randrange(0, len(THANK_MESSAGES))]

def get_spam_message():
    return SPAM_MESSAGE

def get_ntf_message():
    return NTF_MESSAGE

def get_nanora_message(text, censor):
    text += '\n' # Just to make the matching work if the text doesn't already include a newline at the end.
    nanora_text = text

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
                    keyword = "ら"
                elif text[insert_idx-1] == "ノ":
                    keyword = "ラ"
                elif regex.search(rf"({HIRAGANA_NORABLE})", text[insert_idx-2:insert_idx]):
                    keyword = "のら"
                elif regex.search(rf"({KATAKANA_NORABLE})", text[insert_idx-2:insert_idx]):
                    keyword = "ノラ"
                else:
                    keyword = " ナノラ" if is_katakana(text[insert_idx-1]) else " なのら"
            else:
                if text[insert_idx-2:insert_idx] == "no":
                    keyword = "ra"
                elif text[insert_idx-2:insert_idx] == "NO":
                    keyword = "RA"
                elif regex.search(rf"({LOWERCASE_NORABLE})", text[insert_idx-2:insert_idx]):
                    keyword = "nora"
                elif regex.search(rf"({UPPERCASE_NORABLE})", text[insert_idx-2:insert_idx]):
                    keyword = "NORA"
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
        nanora_text = nanora_text[:insert_idx+offset]+keyword+nanora_text[insert_idx+offset:]
        offset += len(keyword)

    # Check if text was successfully modified.
    if nanora_text == text:
        return FAILED_MESSAGE
    # Add zero-width whitespace to disable mentioning usernames.
    nanora_text = nanora_text[:-1].replace('u/',f'u{ZERO_WIDTH_SPACE}/')
    # Censor profanity.
    if censor:
        nanora_text = better_profanity.profanity.censor(nanora_text, '\*')

    # Return successfully modified text.
    return nanora_text

def get_quote_message(author, text, censor):
    keyword = ">"
    nanora_text = "\n"+get_nanora_message(text, censor)
    quote_text = nanora_text

    # Wrap the nanora_text in quotes. The Reddit character for a quote is '>'. It needs to added after every new line.
    offset = 0 # Everytime we insert a >, the length of the text grows.
    for match in regex.finditer(rf"{NEW_LINE_PATTERN}", nanora_text):
        try:
            insert_idx = match.end()
            quote_text = quote_text[:insert_idx+offset]+keyword+quote_text[insert_idx+offset:]
            offset += len(keyword)
        except AttributeError:
            continue

    # Check if text was successfully modified.
    if quote_text == nanora_text:
        return FAILED_MESSAGE

    # Append post author's username.
    quote_text = "By u/"+author+" nanora:\n"+quote_text

    # Return successfully modified text.
    return quote_text