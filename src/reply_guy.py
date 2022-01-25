REPLY_GUY_BOT_NAME = "reply-guy-bot"
REPLY_GUY_MESSAGES = ["*Gasp!* Me, a bot? Never nanora! 有りえないのら!", \
        "NanoraBot is bot? No! I'm adult sexy wonderful beautiful cute えーと、 adult sexy NanoraBot. てへぺろ!", \
        "No! No bot! NanoraBot is cutest beautiful genius sexy sexy adult wonderful great exellent perfect NanoraBot. えへへ!"]

def get_reply_guy_message():
    return REPLY_GUY_MESSAGES[random.randrange(0, len(REPLY_GUY_MESSAGES))]