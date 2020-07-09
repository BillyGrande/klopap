
from sawtooth_sdk.processor.handler import TransactionHandler
from sawtooth_sdk.processor.exceptions import InvalidTransaction
from sawtooth_sdk.processor.exceptions import InternalError

from ltr_payload import LtrPayload
from ltr_state import Lottery
from ltr_state import LtrState
from ltr_state import LTR_NAMESPACE


class LtrTransactionHandler(TransactionHandler):
    def __init__(self, namespace_prefix):
        self._namespace_prefix = namespace_prefix

    @property
    def family_name(self):
        return 'ltr'

    @property
    def family_versions(self):
        return ['1.0']

    @property
    def namespaces(self):
        return [self._namespace_prefix]

    def apply(self, transaction, context):
        # to complete
        header = transaction.header
        signer = header.signer_public_key

        ltr_payload = LtrPayload.from_bytes(transaction.payload)
        ltr_state = LtrState(context)

        if ltr_payload.action == "play":
            # ...
            if ltr_state.get_lottery(ltr_payload.ltr_id) is not None:
                raise InvalidTransaction(
                    'Invalid action: You have already play: {}'.format(
                        ltr_payload.numbers))

            lottery = Lottery().new(ltr_payload.ltr_id, signer)
            ltr_state.set_lottery(lottery.id, lottery)
            _display("Player {} created a lottery.".format(signer[:6]))

        elif ltr_payload.action == "validate":
            lottery = ltr_state.get_game(ltr_payload.ltr_id)

            if lottery is None:
                raise InvalidTransaction(
                    'Invalid: Lottery not found'
                )
            result = lottery.validate()
            _display(result)

        else:
            raise InvalidTransaction('Unhandled action: {}'.format(ltr_payload.action))


def _display(msg):
    n = msg.count("\n")

    if n > 0:
        msg = msg.split("\n")
        length = max(len(line) for line in msg)
    else:
        length = len(msg)
        msg = [msg]