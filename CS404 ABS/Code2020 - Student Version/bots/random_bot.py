import random


class Bot(object):
	"""
	Bids a random amount of it's budget
	"""

	def __init__(self):
		self.name = "random_bot"

	def get_bid_game_type_value(self, current_round, bots, game_type, winner_pays, artists_and_values, round_limit,
		starting_budget, painting_order, target_collection, my_bot_details, current_painting, winner_ids):
		my_budget = my_bot_details["budget"]
		return random.randint(0, my_budget)

	def get_bid_game_type_collection(self, current_round, bots, game_type, winner_pays, artists_and_values, round_limit,
		starting_budget, painting_order, target_collection, my_bot_details, current_painting, winner_ids):
		my_budget = my_bot_details["budget"]
		return random.randint(0, my_budget)
	