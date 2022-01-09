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

from nanora import TRIGGER_NANORA
from nanora import TRIGGER_GOOD_BOT
from nanora import BOT_NAME
from nanora import nanora
from nanora import get_thank_message

# Constants
BOOT_TIME = 5
WAIT_TIME = 10
PARENT_DIR = str(pathlib.Path(os.path.abspath(__file__)).parents[1])
SAVE_FILE = PARENT_DIR + "/modified_posts.json"
LOG_FILE =  PARENT_DIR + "/output.log"

UNCENSORED_SUBREDDIT_LIST = ( \
    "OKBuddyHololive", \
    "GoodAnimemes", \
    "Hololewd")

CENSORED_SUBREDDIT_LIST = ( \
    "u_" + BOT_NAME, \
    BOT_NAME, \
    "Hololive", \
    "Himemori_Luna", \
    "NinomaeInanis", \
    "AmeliaWatson", \
    "GawrGura", \
    "CalliopeMori", \
    "TakanashiKiara_HoloEN", \
    "TakaMori", \
    "VirtualYoutubers", \
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

def save_file(modified_posts):
    file = open(SAVE_FILE, "w+")
    file.write(jsonpickle.encode(modified_posts))
    file.close()

# Checks if a submission or comment is valid.
def is_valid_post(post, modified_posts):
    if not post.author:
        logger.info(f"Deleted post: https://www.reddit.com{post.permalink}")
        return False
    if post.id in modified_posts:
        logger.info(f"Already replied: https://www.reddit.com{post.permalink}")
        return False
    return True

def has_trigger(text, trigger):
    return regex.compile(rf"{trigger}", flags=regex.IGNORECASE).search(text)

def is_top_level(comment):
    return comment.parent_id == comment.link_id

def main(release):
    if release:
        logger.info("Running in release mode.\nApplication starting in " + str(BOOT_TIME) + " seconds.\n")
        time.sleep(BOOT_TIME)
        modified_posts = load_file() # Load IDs of posts we've already modified.
    else:
        logger.info("Running in debug mode.\n")
        modified_posts = set() # Pretend we haven't replied to any posts.

    reddit = praw.Reddit(BOT_NAME)
    subreddits = reddit.subreddit("+".join(UNCENSORED_SUBREDDIT_LIST + CENSORED_SUBREDDIT_LIST))

    # Scan each comment in the subreddits.
    while True:
        try:
            # The first time this starts, it returns 100 historical comments. After that, it only listens for new comments.
            for comment in subreddits.stream.comments():
                # Do not reply to our own comments.
                if comment.author.name == BOT_NAME:
                    continue
                if not is_valid_post(comment, modified_posts):
                    continue
                if not is_valid_post(comment.parent(), modified_posts):
                    continue
                
                # Reply to !nanora.
                if has_trigger(comment.body, TRIGGER_NANORA):
                    # Modify parent text.
                    if is_top_level(comment):
                        reply = (comment.submission.title + '\n\n' + comment.submission.selftext if comment.submission.selftext else comment.submission.title)
                    else:
                        reply = comment.parent().body
                    reply = nanora(reply, comment.subreddit.name in CENSORED_SUBREDDIT_LIST)
                # Reply to Good Bot!
                elif has_trigger(comment.body, TRIGGER_GOOD_BOT) and comment.parent().author.name == BOT_NAME:
                    reply = get_thank_message()
                else:
                    continue

                # Reply to comment.
                if release:
                    comment.reply(reply)
                    modified_posts.add(comment.parent().id)
                    save_file(modified_posts)

                # Log reply.
                logger.info(f"Replied to: https://www.reddit.com{comment.permalink}")
                logger.info(reply)
                
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt. Terminating...")
            break
        except praw.exceptions.RedditAPIException:
            logger.error(f"RedditAPIException: {traceback.format_exc()}")
        except praw.exceptions.PRAWException:
            logger.error(f"PRAWException: {traceback.format_exc()}")
        except Exception:
            logger.error(f"Unhandled exception: {traceback.format_exc()}")
        finally:
            if release:
                logger.info(f"Program sleeping.")
                time.sleep(WAIT_TIME)

if __name__ == "__main__":
    main(eval(sys.argv[1]))
