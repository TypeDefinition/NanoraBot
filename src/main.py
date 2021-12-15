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

from nanora import nanora
from nanora import TRIGGER
from nanora import BOT_NAME

# Constants
BOOT_TIME = 5
WAIT_TIME = 10
PARENT_DIR = str(pathlib.Path(os.path.abspath(__file__)).parents[1])
SAVE_FILE = PARENT_DIR + "/modified_posts.json"
LOG_FILE =  PARENT_DIR + "/output.log"
DISCLAMER = "\n\n__Disclaimer: I am still in testing phase. Please forgive any mistakes nanora!__\n\n__Note: I currently cannot post in r/Hololive due to low karma.__\n"
SUBREDDIT_LIST = ("u_" + BOT_NAME, BOT_NAME, \
    "Hololive", \
    "Hololewd", \
    "OKBuddyHololive", \
    "Himemori_Luna", \
    "NinomaeInanis", \
    "AmeliaWatson", \
    "GawrGura", \
    "CalliopeMori", \
    "TakanashiKiara_HoloEN", \
    "TakaMori", \
    "GoodAnimemes", \
    "VirtualYoutubers", \
    "VtuberV8", \
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

def has_trigger(text):
    return regex.compile(rf"{TRIGGER}", flags=regex.IGNORECASE).search(text)

def is_top_level(comment):
    return comment.parent_id == comment.link_id

# Forgive me. This is my first time working with Python and web APIs.
def main(release):
    logger.info("Running in release mode.\n" if release else "Running in debug mode.\n")
    time.sleep(BOOT_TIME)

    reddit = praw.Reddit(BOT_NAME)
    subreddits = reddit.subreddit("+".join(SUBREDDIT_LIST))

    # Load_file IDs of posts we've already modified.
    modified_posts = load_file() if release else set()

    # Scan each comment in the subreddits.
    while True:
        try:
            for comment in subreddits.stream.comments():
                # Do not reply to our own comments.
                if comment.author.name == BOT_NAME:
                    continue
                if not is_valid_post(comment, modified_posts):
                    continue
                if not has_trigger(comment.body):
                    continue
                if not is_valid_post(comment.parent(), modified_posts):
                    continue

                # Modify parent text.
                if is_top_level(comment):
                    modified_text = nanora(comment.submission.title + '\n\n' + comment.submission.selftext if comment.submission.selftext else comment.submission.title)
                else:
                    modified_text = nanora(comment.parent().body)
                modified_text += DISCLAMER

                # Reply to comment.
                if release:
                    comment.reply(modified_text)
                    modified_posts.add(comment.parent().id)
                    save_file(modified_posts)

                # Log reply.
                logger.info(f"Replied to: https://www.reddit.com{comment.permalink}")
                print(modified_text)
        except KeyboardInterrupt:
            print("Keyboard interrupt. Terminating...")
            break
        except praw.exceptions.RedditAPIException:
            logger.error(f"RedditAPIException: {traceback.format_exc()}")
        except praw.exceptions.PRAWException:
            logger.error(f"PRAWException: {traceback.format_exc()}")
        except Exception:
            logger.error(f"Unhandled exception: {traceback.format_exc()}")
        finally:
            logger.info(f"Program sleeping.")
            time.sleep(WAIT_TIME)

if __name__ == "__main__":
    if sys.argv[1].lower() == "true":
        main(True)
    else:
        main(False)
