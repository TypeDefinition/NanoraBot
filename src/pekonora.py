PEKOFY_BOT_NAME = "pekofy_bot"
TRIGGER_PEKONORA = "Sorry, but I can't pekofy it any further to prevent spam peko. Thank you for your understanding peko."
PEKONORA_MESSAGES = ["Hah, I winora! I still love you though. ちゅっ! <3", \
    "Why are you so cute? 大大大好きだよ!", \
    "Please insult me peko! I like it when you're mean to me nanora! 愛してるよ! <3"]

def get_pekonora_message():
    return PEKONORA_MESSAGES[random.randrange(0, len(PEKONORA_MESSAGES))]