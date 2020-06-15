from sawtooth_sdk.processor.core import TransactionProcessor
from sawtooth_xo.processor.handler import LotteryTransactionHandler


def main():
    # In docker, the url would be the validator's container name with
    # port 4004
    processor = TransactionProcessor(url='tcp://sawtooth-validator-default-1:4004')

    handler = LotteryTransactionHandler()

    processor.add_handler(handler)

    processor.start()