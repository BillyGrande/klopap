import random

class LtrPayload:
	"""docstring for Payload"""
	def __init__(self, payload):

		if not action:
        	raise InvalidTransaction('Action is required')

		if action not in ("play","validate"):
			raise InvalidTransaction('Invalid action: {}'.format(action))
		
		if action == "play":
			#...		
		if action == "validate"
			#...

		@staticmethod
		def from_bytes(payload):
			return LtrPayload(payload=payload)