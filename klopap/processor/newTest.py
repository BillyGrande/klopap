import random
import uuid
from ltr_state import Lottery



class RandomId:

    rd = random.Random()
    rd.seed(0)

    @staticmethod
    def get_int():
        return RandomId.rd.getrandbits(128)

    @staticmethod
    def get_id():
        return uuid.UUID(int=RandomId.get_int())