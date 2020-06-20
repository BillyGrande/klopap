import hashlib
import base64
from base64 import b64encode
import time
import random
import requests
import yaml
import urllib


from klopap.processor.randomID import RandomId

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

    def __init__(self, base_url):
        self._base_url = base_url
        self._context = create_context('secp256k1')
        self._private_key = self._context.new_random_private_key()
        self._signer = CryptoFactory(self._context).new_signer(self._private_key)

    def create(self, ltr_id, wait=None, auth_user=None, auth_password=None):
        return self._send_ltr_txn(
            ltr_id,
            "create",
            wait=wait,
            auth_user=auth_user,
            auth_password=auth_password)

    def validate(self, ltr_id, wait=None, auth_user=None, auth_password=None):
        return self._send_ltr_txn(
            ltr_id,
            "delete",
            wait=wait,
            auth_user=auth_user,
            auth_password=auth_password)

    def _get_status(self, batch_id, wait, auth_user=None, auth_password=None):
        try:
            result = self._send_request(
                'batch_statuses?id={}&wait={}'.format(batch_id, wait),
                auth_user=auth_user,
                auth_password=auth_password)
            return yaml.safe_load(result)['data'][0]['status']
        except BaseException as err:
            raise Exception(err)

    def _get_prefix(self):
        return _sha512('ltr'.encode('utf-8'))[0:6]

    def _get_address(self, name):
        ltr_prefix = self._get_prefix()
        game_address = _sha512(name.encode('utf-8'))[0:64]
        return ltr_prefix + game_address

    def _send_request(self,
                      suffix,
                      data=None,
                      content_type=None,
                      name=None,
                      auth_user=None,
                      auth_password=None):
        if self._base_url.startswith("http://"):
            url = "{}/{}".format(self._base_url, suffix)
        else:
            url = "http://{}/{}".format(self._base_url, suffix)

        headers = {}
        if auth_user is not None:
            auth_string = "{}:{}".format(auth_user, auth_password)
            b64_string = b64encode(auth_string.encode()).decode()
            auth_header = 'Basic {}'.format(b64_string)
            headers['Authorization'] = auth_header

        if content_type is not None:
            headers['Content-Type'] = content_type

        try:
            if data is not None:
                result = requests.post(url, headers=headers, data=data)
            else:
                result = requests.get(url, headers=headers)

            if result.status_code == 404:
                raise Exception("No such game: {}".format(name))

            if not result.ok:
                raise Exception("Error {}: {}".format(
                    result.status_code, result.reason))

        except requests.ConnectionError as err:
            raise Exception(
                'Failed to connect to {}: {}'.format(url, str(err)))

        except BaseException as err:
            raise BaseException(err)

        return result.text

    def _send_ltr_txn(self,
                    ltr_id,
                    action,
                    numbers = None,
                    wait = None,
                    auth_user = None,
                    auth_password = None):
        # Serialization is just a delimited utf-8 encoded string
        self._player = self._signer.get_public_key().as_hex()
        payload = ",".join([str(self._player), action,' '.join(sorted(numbers))]).encode()

        # Construct the address
        address = self._get_address(ltr_id)

        header = TransactionHeader(
            signer_public_key=self._player,
            family_name="ltr",
            family_version="1.0",
            inputs=[address],
            outputs=[address],
            dependencies=[],
            payload_sha512=_sha512(payload),
            batcher_public_key=self._player,
            nonce=hex(random.randint(0, 2 ** 64))
        ).SerializeToString()

        signature = self._signer.sign(header)

        transaction = Transaction(
            header=header,
            payload=payload,
            header_signature=signature
        )

        batch_list = self._create_batch_list([transaction])
        batch_id = batch_list.batches[0].header_signature

        if wait and wait > 0:
            wait_time = 0
            start_time = time.time()
            response = self._send_request(
                "batches", batch_list.SerializeToString(),
                'application/octet-stream',
                auth_user=auth_user,
                auth_password=auth_password)
            while wait_time < wait:
                status = self._get_status(
                    batch_id,
                    wait - int(wait_time),
                    auth_user=auth_user,
                    auth_password=auth_password)
                wait_time = time.time() - start_time

                if status != 'PENDING':
                    return response

            return response

        return self._send_request(
            "batches", batch_list.SerializeToString(),
            'application/octet-stream',
            auth_user=auth_user,
            auth_password=auth_password)

    def _create_batch_list(self, transactions):
        transaction_signatures = [t.header_signature for t in transactions]

        header = BatchHeader(
            signer_public_key=self._signer.get_public_key().as_hex(),
            transaction_ids=transaction_signatures
        ).SerializeToString()

        signature = self._signer.sign(header)

        batch = Batch(
            header=header,
            transactions=transactions,
            header_signature=signature)
        return BatchList(batches=[batch])