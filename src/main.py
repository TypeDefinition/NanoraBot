import jsonpickle
import logging
import praw
import regex
import sys
import time
import traceback
import nanora
import pathlib
import os

from nanora import BOT_NAME
from nanora import TRIGGER_LUNA_POST, TRIGGER_LUNA_POST_JP, TRIGGER_NANORA, TRIGGER_GOOD_BOT, TRIGGER_CUTE_BOT, TRIGGER_NTF
from nanora import get_luna_submission_message, get_thank_message, get_spam_message, get_ntf_message
from nanora import nanora

from pekonora import PEKOFY_BOT_NAME
from pekonora import TRIGGER_PEKONORA
from pekonora import get_pekonora_message

# Constants
BOOT_DURATION = 5
WAIT_DURATION = 5
SPAM_LIMIT = 10
PARENT_DIR = str(pathlib.Path(os.path.abspath(__file__)).parents[1])
SAVE_FILE = PARENT_DIR + "/replied_posts.json"
LOG_FILE =  PARENT_DIR + "/output.log"

UNCENSORED_SUBREDDIT_LIST = ( \
    "OKBuddyHololive", \
    "GoodAnimemes", \
    "Hololewd")

CENSORED_SUBREDDIT_LIST = ( \
    "u_" + BOT_NAME, \
    "PrivateBotTest", \
    "Hololive", \
    "Himemori_Luna", \
    "VtuberV8", \
    "HololiveYuri", \
    "Singapore", \
    "NUS")

# Logging
# logging.basicConfig(filename=LOG_FILE, filemode='a', format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s', datefmt='%H:%M:%S', level=logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
for logger_name in ("praw", "prawcore"):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)

# Nanora Bot
def load_file():
    try:
        file = open(SAVE_FILE, "r")
        json_str = file.read()
        file.close()
        return jsonpickle.decode(json_str)
    except:
        return set()

def save_file(replied_posts):
    file = open(SAVE_FILE, "w+")
    file.write(jsonpickle.encode(replied_posts))
    file.close()

def is_deleted_post(post):
    if not post.author:
        logger.info(f"Deleted post: https://www.reddit.com{post.permalink}")
        return True
    return False

def is_replied_post(post, replied_posts):
    if post.id in replied_posts:
        logger.info(f"Already replied: https://www.reddit.com{post.permalink}")
        return True
    return False

def has_trigger(text, trigger):
    return regex.compile(rf"{trigger}", flags=regex.IGNORECASE).search(text)

def has_trigger_word(text, trigger):
    return regex.compile(rf"\b{trigger}\b", flags=regex.IGNORECASE).search(text)

def is_top_level(comment):
    return comment.parent_id == comment.link_id

def is_author(post, author):
    return post is not None and post.author is not None and post.author.name == author

def reply_count(comment, author, limit):
    count = 0
    while comment is not None:
        if is_author(comment, author):
            count = count + 1
        if is_top_level(comment):
            break
        if count > limit:
            break
        comment = comment.parent()
    return count

def main(release):
    if release:
        logger.info("Running in release mode.\nApplication starting in " + str(BOOT_DURATION) + " seconds.\n")
        time.sleep(BOOT_DURATION)
        replied_posts = load_file() # Load IDs of posts we've already modified.
    else:
        logger.info("Running in debug mode.\n")
        replied_posts = set() # Pretend we haven't replied to any posts.

    run = True
    empty_streams = True
    while run:
        try:
            # If both streams are empty, then there is a chance the stream has broken due to Reddit server's going down.
            # In that case, reinitialise the streams.
            if empty_streams:
                reddit = praw.Reddit(BOT_NAME)
                subreddits = reddit.subreddit("+".join(UNCENSORED_SUBREDDIT_LIST + CENSORED_SUBREDDIT_LIST))
                submission_stream = subreddits.stream.submissions(pause_after=-1)
                comment_stream = subreddits.stream.comments(pause_after=-1)
            empty_streams = True

            # Parse submissions.
            logger.info("Streaming submissions.")
            for submission in submission_stream:
                if submission is None:
                    break
                empty_streams = False

                # Do not reply to our own submissions.
                if is_author(submission, BOT_NAME):
                    continue
                # Do not reply to deleted or already replied submissions.
                if is_deleted_post(submission) or is_replied_post(submission, replied_posts):
                    continue

                # Reply to !nanora.
                if has_trigger_word(submission.title, TRIGGER_LUNA_POST):
                    reply = get_luna_submission_message()
                elif has_trigger_word(submission.title, TRIGGER_LUNA_POST_JP):
                    reply = get_luna_submission_message()
                else:
                    continue

                # Reply to submission.
                if release:
                    submission.reply(reply)
                    replied_posts.add(submission.id)
                    save_file(replied_posts)

                # Log reply.
                logger.info(f"Replied to: https://www.reddit.com{submission.permalink}")
                logger.info(reply)

            # Parse comments. The first time this starts, it returns 100 historical comments. After that, it only listens for new comments.
            logger.info("Streaming comments.")
            for comment in comment_stream:
                if comment is None:
                    break
                empty_streams = False

                # Do not reply to our own comments.
                if is_author(comment, BOT_NAME):
                    continue
                # Do not reply to deleted or already replied comments.
                if is_deleted_post(comment) or is_replied_post(comment, replied_posts) or is_deleted_post(comment.parent()):
                    continue

                # Reply to !nanora.
                if has_trigger(comment.body, TRIGGER_NANORA):
                    # Modify parent text.
                    if is_top_level(comment):
                        reply = (comment.submission.title + '\n\n' + comment.submission.selftext if comment.submission.selftext else comment.submission.title)
                    else:
                        reply = comment.parent().body
                    reply = nanora(reply, comment.subreddit.name in CENSORED_SUBREDDIT_LIST)
                # Reply to !ntf.
                elif has_trigger(comment.body, TRIGGER_NTF):
                    reply = get_ntf_message()
                # Reply to Good Bot
                elif has_trigger(comment.body, TRIGGER_GOOD_BOT) and is_author(comment.parent(), BOT_NAME):
                    reply = get_thank_message()
                # Reply to Cute Bot
                elif has_trigger(comment.body, TRIGGER_CUTE_BOT) and is_author(comment.parent(), BOT_NAME):
                    reply = get_thank_message()
                # Reply to u/pekofy_bot giving up replying to u/NanoraBot due to possible spam.
                elif has_trigger(comment.body, TRIGGER_PEKONORA) and is_author(comment, PEKOFY_BOT_NAME) and is_author(comment.parent(), BOT_NAME):
                    reply = get_pekonora_message()
                else:
                    continue

                # Possible spam, do not reply.
                if reply_count(comment, BOT_NAME, SPAM_LIMIT) > SPAM_LIMIT:
                    logger.info("Possible spam detected. Ignoring comment: https://www.reddit.com{comment.permalink}")
                    continue
                # Notify that this reply thread is closed due to possible spam.
                elif reply_count(comment, BOT_NAME, SPAM_LIMIT) == SPAM_LIMIT:
                    reply = get_spam_message()
                # Reply to comment.
                if release:
                    comment.reply(reply)
                    replied_posts.add(comment.id)
                    save_file(replied_posts)

                # Log reply.
                logger.info(f"Replied to: https://www.reddit.com{comment.permalink}")
                logger.info(reply)
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt. Terminating...")
            run = False
        except praw.exceptions.RedditAPIException:
            logger.error(f"RedditAPIException: {traceback.format_exc()}")
        except praw.exceptions.PRAWException:
            logger.error(f"PRAWException: {traceback.format_exc()}")
        except Exception:
            logger.error(f"Unhandled exception: {traceback.format_exc()}")
        finally:
            if release and run:
                logger.info(f"Program sleeping for " + str(WAIT_DURATION) + " seconds.")
                time.sleep(WAIT_DURATION)

if __name__ == "__main__":
    main(eval(sys.argv[1]))
