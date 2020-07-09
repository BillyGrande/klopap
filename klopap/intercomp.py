from sawtooth_signing import create_context
from sawtooth_signing import CryptoFactory
import cbor
from hashlib import sha512
from sawtooth_sdk.protobuf.transaction_pb2 import TransactionHeader
from sawtooth_sdk.protobuf.transaction_pb2 import Transaction
from sawtooth_sdk.protobuf.batch_pb2 import Batch
from sawtooth_sdk.protobuf.batch_pb2 import BatchHeader
import urllib.request
from urllib.error import HTTPError
import hashlib
from sawtooth_sdk.protobuf.batch_pb2 import BatchList


class User:

    def __init__(self):
        self.context = create_context('secp256k1')
        self.private_key = self.context.new_random_private_key()
        self.signer = CryptoFactory(self.context).new_signer(self.private_key)


class Payload:

    def __init__(self, verb, name, value):
        self.payload = {
            'Verb': verb,
            'Name': name,
            'Value': value
        }

    def bytes(self):
        return cbor.dumps(self.payload)

    def get_name(self):
        return self.payload['Name']

    def get_value(self):
        return self.payload['Value']

    def get_verb(self):
        return self.payload['Verb']


class Client:

    def __init__(self, user):
        self.user = user

    def create(self, name, value):
        payload = Payload('set', name, value)
        return self._transaction(payload)

    def increase(self, name, value):
        payload = Payload('inc', name, value)
        return self._transaction(payload)

    def decrease(self, name, value):
        payload = Payload('dec', name, value)
        return self._transaction(payload)

    def _transaction(self, payload):

        address = self._get_address(payload.get_name())

        print(address)
        print(self.user.signer.get_public_key().as_hex())
        txn_header_bytes = TransactionHeader(
            family_name='intkey',
            family_version='1.0',
            inputs=[address],
            outputs=[address],
            signer_public_key=self.user.signer.get_public_key().as_hex(),
            batcher_public_key=self.user.signer.get_public_key().as_hex(),
            dependencies=[],
            payload_sha512=sha512(payload.bytes()).hexdigest()
        ).SerializeToString()

        signature = self.user.signer.sign(txn_header_bytes)

        txn = Transaction(
            header=txn_header_bytes,
            header_signature=signature,
            payload=payload.bytes()
        )

        batch_list = self._batch(txn).SerializeToString()
        return self._submit(batch_list)

    def _batch(self, txn):

        txns = [txn]

        batch_header_bytes = BatchHeader(
            signer_public_key=self.user.signer.get_public_key().as_hex(),
            transaction_ids=[txn.header_signature for txn in txns],
        ).SerializeToString()

        signature = self.user.signer.sign(batch_header_bytes)

        batch = Batch(
            header=batch_header_bytes,
            header_signature=signature,
            transactions=txns
        )
        return BatchList(batches=[batch])

    def _submit(self, batch_list_bytes):

        try:
            request = urllib.request.Request(
                'http://sawtooth-rest-api-default-0:8008/batches',
                batch_list_bytes,
                method='POST',
                headers={'Content-Type': 'application/octet-stream'})
            response = urllib.request.urlopen(request)

        except HTTPError as e:
            response = e

    def _write(self, batch_list_bytes):
        output = open('intkey.batches', 'wb')
        output.write(batch_list_bytes)
        output.close()

    def _get_address(self, name):
        address = hashlib.sha512('intkey'.encode('utf-8')).hexdigest()[0:6] + hashlib.sha512(name.encode('utf-8')).hexdigest()[-64:]
        return address
