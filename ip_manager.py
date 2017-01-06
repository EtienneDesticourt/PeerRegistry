import time
import uuid
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from collections import namedtuple
import base64


def DEFAULT_PADDING():
    return padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None)

MAX_CHALLENGE_DELAY = 120

Challenge = namedtuple('Challenge', ['secret', 'encrypted', 'issued'])


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

    def create_challenge(self, username, public_key_data):
        key = load_pem_public_key(public_key_data.encode('utf8'), backend=default_backend())

        secret = str(uuid.uuid4())
        encrypted_secret = key.encrypt(secret.encode('utf8'), DEFAULT_PADDING())
        encrypted_secret_b64 = base64.b64encode(encrypted_secret).decode('utf8')

        challenge = Challenge(secret, encrypted_secret_b64, issued=time.time())
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
