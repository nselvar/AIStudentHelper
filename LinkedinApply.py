from linkedinapply.linkedineasyapply import LinkedinEasyApply
from linkedinapply.main import validate_yaml, init_browser


class LinkedinApply:
    def __init__(self):
        parameters = validate_yaml()
        browser = init_browser()

        bot = LinkedinEasyApply(parameters, browser)
        bot.login()
        bot.security_check()
        bot.start_applying()