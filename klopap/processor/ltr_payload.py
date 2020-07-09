
from sawtooth_sdk.processor.exceptions import InvalidTransaction


class LtrPayload:
	"""docstring for Payload"""

	def __init__(self, payload):
		"""
		payload: <action>,<id>,<numbers>
			if action is play then omit the id and numbers
			if action is validate then id is necessary numbers I have not decide yet!
		Args:
			payload: string with format <action>,<id>,<numbers>
		"""
		try:
			action, ltr_id, numbers = payload.decode().split(",")
		except ValueError:
			raise InvalidTransaction("Invalid payload serialization")

		if not action:
			raise InvalidTransaction('Action is required')

		if action not in ("play", "validate"):
			raise InvalidTransaction('Invalid action: {}'.format(action))

		if action == "validate":
			try:
				ltr_id = ltr_id
			except ValueError:
				raise InvalidTransaction("id is invalid")

		self._action = action
		self._ltr_id = ltr_id
		self._numbers = numbers

	@staticmethod
	def from_bytes(payload):
		return LtrPayload(payload=payload)

	@property
	def action(self):
		return self._action

	@property
	def ltr_id(self):
		return self._ltr_id

	@property
	def numbers(self):
		return list(map(int, self._numbers.join(" ")))
