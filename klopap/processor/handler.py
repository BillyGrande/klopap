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
        #to complete
        header = transaction.header
        signer = header.signer_public_key

        ltr_payload = LotteryPayload.from_bytes(transaction.payload)
        ltr_state = LotteryState(context)

        if ltr_payload.action == "play":
            #...
            if ltr_state.get_lottery(ltr_payload) is not None:
                raise InvalidTransaction(
            'Invalid action: You have already play: {}'.format(
                ltr_payload.numbers))

        elif ltr_payload.action == "validate":
            #...
        else:
            raise InvalidTransaction('Unhandled action: {}'.format(ltr_payload.action))