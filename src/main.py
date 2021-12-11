import praw
import logging
import regex
import jsonpickle

# Constants
SAVE_FILENAME = "./modified_posts.json"
TRIGGER = "!nanora"
BOT_NAME = "NanoraBot"
REDDIT = praw.Reddit(BOT_NAME)

SUBREDDIT_LIST = ("u_" + BOT_NAME, "testingground4bots") # For debugging purposes.
# SUBREDDIT_LIST = ("u_" + BOT_NAME, "hololive", "Hololewd", "okbuddyhololive") # For actual usage.
SUBREDDITS = REDDIT.subreddit("+".join(SUBREDDIT_LIST))

# Logging
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
for logger_name in ("praw", "prawcore"):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)

# Nanora Bot
def load_file():
    try:
        file = open(SAVE_FILENAME, "r")
        json_str = file.read()
        file.close()
        return jsonpickle.decode(json_str)
    except:
        return set()

def save_file(modified_posts):
    file = open(SAVE_FILENAME, "w+")
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
    return regex.compile(rf"{TRIGGER}", flags=regex.IGNORECASE).search(text) is not None

def is_top_level(comment):
    return comment.parent_id == comment.link_id

def main(debug=True):
    # Load_file IDs of posts we've already modified.
    modified_posts = load_file()

    # Scan each comment in the subreddits.
    for comment in SUBREDDITS.stream.comments():
        # Do not reply to our own comments.
        if comment.author.name == BOT_NAME:
            continue
        if not is_valid_post(comment, modified_posts):
            continue
        if not has_trigger(comment.body):
            continue
        if not is_valid_post(comment.parent(), modified_posts):
            continue

        # Modify parent and reply.
        if is_top_level(comment):
            print(comment.parent().selftext)
        else:
            print(comment.parent().body)

        # Save to replied comments.
        logger.info(f"Replied to: https://www.reddit.com{comment.permalink}")
        modified_posts.add(comment.parent().id)
        save_file(modified_posts)


if __name__ == "__main__":
    main(debug=True)