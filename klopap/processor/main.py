from sawtooth_sdk.processor.core import TransactionProcessor
from klopap.processor.handler import LtrTransactionHandler


def main():
    # In docker, the url would be the validator's container name with
    # port 4004
    processor = TransactionProcessor(url='tcp://sawtooth-validator-default-1:4004')

    handler = LtrTransactionHandler()

    processor.add_handler(handler)

    processor.start()