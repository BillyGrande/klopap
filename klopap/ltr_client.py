import hashlib
import base64
from base64 import b64encode
import time
import random
import requests
import yaml

from sawtooth_signing import create_context
from sawtooth_signing import CryptoFactory
from sawtooth_signing import ParseError
from sawtooth_signing.secp256k1 import Secp256k1PrivateKey

from sawtooth_sdk.protobuf.transaction_pb2 import TransactionHeader
from sawtooth_sdk.protobuf.transaction_pb2 import Transaction
from sawtooth_sdk.protobuf.batch_pb2 import BatchList
from sawtooth_sdk.protobuf.batch_pb2 import BatchHeader
from sawtooth_sdk.protobuf.batch_pb2 import Batch


def _sha512(data):
    return hashlib.sha512(data).hexdigest()

class LtrClient:

    def __init__(self):
        self._context = create_context('secp256k1')
        self._private_key = self._context.new_random_private_key()
        self.signer = CryptoFactory(self._context).new_signer(self._private_key)

    def create(self):
        #...

    def validate(self):
        #...


    def transaction(self):
        txn_header_bytes = TransactionHeader(

        )