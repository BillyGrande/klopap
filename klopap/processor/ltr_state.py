import hashlib
import itertools
import random
import sys
from sawtooth_sdk.processor.exceptions import InternalError

LTR_NAMESPACE = hashlib.sha512('ltr'.encode("utf-8")).hexdigest()[0:6]


def _make_ltr_address(id):
    return LTR_NAMESPACE + \
           hashlib.sha512(id.encode('utf-8')).hexdigest()[:64]


class Lottery:
    id_iter = itertools.count()

    def __init__(self, numbers, player, ltr_id=None):
        if ltr_id is None:
            self.id = next(Lottery.id_iter)
        else:
            next(Lottery.id_iter)
            self.id = ltr_id

        self.numbers = numbers
        self.player = player

    @classmethod
    def new(cls, player):
        numbers = random.sample(range(51), 5)
        return Lottery(numbers, player)


class LtrState:
    TIMEOUT = 3

    def __init__(self, context):
        self._context = context
        self._address_cache = {}

    def delete_lottery(self, ltr_id):
        lotteries = self._load_lotteries(id=ltr_id)
        del lotteries[ltr_id]
        if lotteries:
            self._store_lottery(ltr_id, lotteries=lotteries)
        else:
            self._delete_lottery(ltr_id)

        def set_lottery(self, ltr_id, lottery):
            # later
            lotteries = self._load_lotteries(ltr_id=ltr_id)

            lotteries[ltr_id] = lottery

            self._store_lottery(ltr_id, lotteries=lotteries)

        def get_lotery(self, id):
            # later
            return self._load_lotteries(ltr_id=ltr_id).get(ltr_id)

        def _store_lottery(self, ltr_id, lotteries):
            address = _make_ltr_address(ltr_id)

            state_data = self._serialize(lotteries)

            self._address_cache[address] = state_data

            self._context.set_state(
                {address: state_data},
                timeout=self.TIMEOUT)

        def _delete_lottery(self, ltr_id):
            address = _make_ltr_address(ltr_id)

            self._context.delete_state(
                [address],
                timeout=self.TIMEOUT)

            self._address_cache[address] = None

        def _load_lotteries(self, ltr_id):
            address = _make_ltr_address(ltr_id)

            if address in self._address_cache:
                if self._address_cache[address]:
                    serialized_lotteries = self._address_cache[address]
                    lotteries = self._deserialize(serialized_lotteries)
                else:
                    lotteries = {}
            else:
                state_entries = self._context.get_state(
                    [address],
                    timeout=self.TIMEOUT)
                if state_entries:

                    self._address_cache[address] = state_entries[0].data

                    lotteries = self._deserialize(data=state_entries[0].data)

                else:
                    self._address_cache[address] = None
                    lotteries = {}

            return lotteries

        def _deserialize(self, data):
            lotteries = {}
            try:
                for lottery in data.decode().split("|"):
                    ltr_id, nums, player = lottery.split(",")

                    lotteries[ltr_id] = Lottery(list(map(int, nums.split('-'))), player, ltr_id)
            except ValueError:
                raise InternalError("Failed to deserialize game data")

            return lotteries

        def _serialize(self, lotteries):
            lottery_strs = []
            for ltr_id, l in lotteries.items():
                lottery_str = ",".join(
                    [ltr_id, ' '.join(l.numbers), l.player])
                lottery_strs.append(lottery_str)

            return "|".join(sorted(lottery_strs)).encode()
