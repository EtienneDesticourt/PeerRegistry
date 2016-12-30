import time
import uuid
from collections import namedtuple


MAX_CHALLENGE_DELAY = 120

Challenge = namedtuple('Challenge', ['secret', 'issued'])


class IpManagerException(Exception):
    pass


class NoChallengeError(IpManagerException):
    pass


class IpManager(object):

    def __init__(self):
        self.ips = {}
        self.challenges = {}

    def get_ip(self, username):
        if username in self.ips:
            return self.ips[username]
        return None

    def create_challenge(self, username):
        secret = str(uuid.uuid4())
        secret = str(0)
        challenge = Challenge(secret, issued=time.time())
        self.challenges[username] = challenge
        return challenge

    def challenge_is_correct(self, username, answer):
        if username not in self.challenges:
            raise NoChallengeError("No challenge for this user.")
        challenge = self.challenges[username]
        elapsed = time.time() - challenge.issued
        if answer == challenge.secret and elapsed < MAX_CHALLENGE_DELAY:
            return True
        return False

    def has_challenge(self, username):
        if username in self.challenges:
            return True
        return False

    def update_ip(self, username, new_ip):
        self.ips[username] = new_ip
