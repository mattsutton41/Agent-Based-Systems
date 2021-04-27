####################################################################################################
# DO NOT CHANGE THE CODE IN THIS FILE. THIS IS THE EXACT FILE WE WILL USE TO MARK YOUR BOT
# IF YOU CHANGE SOMETHING IN THIS FILE THEN YOUR BOT MIGHT NOT RUN PROPERLY WHEN WE MARK IT 
####################################################################################################

import time
import random
import copy
import datetime
import csv

from bots import flat_bot_10
from bots import random_bot

from utilities import export_to_csv


class Auctioneer(object):
	"""
	Runs one full auction game
	"""

	##########################################
	## Setting up the auction
	##########################################
	
	# A lot of the game variables can be changed by passing in parameters when starting the auction
	# If nothing is passed in, the default values are used as below 
	def __init__(self, 
			game_type="value", # "collection" or "value"
			room=[flat_bot_10, random_bot], # List of bots to play in the game
			painting_order=None, # The order of paintings in the auction. None gives a random order
			target_collection=[4,2], # How many types of paintings needed in collection game. [4,2] means 4 of one and 2 of another
			slowdown=1, # Time to wait between rounds. Set to 0 for fast auctions
			output_csv_file="data/auctioneer_log.csv", # Result of every round is logged to csv
			verbose=True # Whether to print updates to terminal. 
			):

		# Game helper variables
		self.current_round = 0
		self.bots = []
		self.finished = False
		self.slowdown = slowdown
		self.verbose = verbose

		# Game variables
		self.round_limit = 200
		self.starting_budget = 1001
		self.artists_and_values = {
				"Da Vinci":12,
				"Rembrandt":8, 
				"Van Gogh":6, 
				"Picasso":4
			}
		self.target_collection = target_collection
		
		# Make sure there are at least two bots in the auction
		if len(room)>1:
			self.room = room
		else:
			raise TypeError("You need at least two bots in a room, this room only has one bot in it")
		
		# Reset the random seed
		random.seed()
		# Game specific variables
		self.painting_order = painting_order
		if self.painting_order == None:
			# Random painting order if none given
			artists = list(self.artists_and_values.keys())
			self.painting_order = [artists[random.randint(0,3)] for i in range(self.round_limit)]

		# Game type determines 1st or 2nd price auction
		self.game_type = game_type
		if self.game_type == "collection":
			# 1st price auction
			self.winner_pays = 1
		if self.game_type == "value":
			# 2nd price auction
			self.winner_pays = 2

		# Test for some argument type errors 
		if self.game_type not in ["collection", "value"]:
			raise ValueError("Please set game_type to either 'collection' or 'value'")
		if len(self.painting_order) != self.round_limit:
			raise TypeError("The length of 'painting_order' is {}, this should be the same as the round limit, {}".format(len (self.painting_order), self.round_limit))			
		if type(self.target_collection) != list:
			raise TypeError("The target collection should be a list of integers")
		if not (all(isinstance(x, int) for x in self.target_collection)):
			raise TypeError("The target collection should be a list of integers")
		if len(self.target_collection) == 0:
			raise TypeError("The target collection should be a list of integers")

		# Data export variables
		self.output_csv_file = output_csv_file
		self.error_log_csv_file = "data/error_log.csv"
		self.game_start_time = str(datetime.datetime.now())
		self.winner_ids = []
		self.amounts_paid = []

		# Start the bots
		self.__initialise_bots()

	def __initialise_bots(self):
		if self.verbose:
			print("Starting {} type game".format(self.game_type))
			if self.game_type == "collection":
				print("Target collection is {}".format(self.target_collection))

			print("Initialising bots . . .")
		count = 0
		for bot_module in self.room:
			if self.verbose:
				print("Initialising {}".format(bot_module))
			count += 1

			# Initialise the bot
			# Catch any errors here, add them to an error log and raise the error again so it stops the game
			try:
				bot_instance = bot_module.Bot()
			except Exception as e:
				print("Error caught ", str(e))
				self.__log_error(bot_name=bot_module, game_stage="initialisation", error_message=str(e))
				raise

			# The unique id is the bot's name and the bot's number in this auction. 
			# For student submissions, the bot's name should be their warwick student id number, which can be used for marking
			# For test bots, you can use a name to remind you which bot is which
			# Adding a number to the bot's name means that you can use the same bot class more than once in an auction 
			# Any errors are caught here, added to an error log and the error is raised again so that it stops the game
			# Errors will be raised here if the bot doesn't have a name variable
			try:
				bot_unique_id = "{}-{}".format(bot_instance.name, count)
			except Exception as e:
				print("Error caught ", str(e))
				self.__log_error(bot_name=bot_module, game_stage="initialisation - bot name", error_message=str(e))
				raise

			# Add bot details to a dictionary. Stores bot instance in memory
			# Also used to keep track of paintings won and budget
			new_bot = {
				"bot_instance":bot_instance,
				"bot_name":copy.deepcopy(bot_instance.name),
				"bot_unique_id":bot_unique_id,
				"paintings":{"Da Vinci":0,"Picasso":0,"Rembrandt":0,"Van Gogh":0},
				"budget":self.starting_budget,
				"current_bid":0,
				"score":0,
				}

			# Add the bot and its details to the bots array
			self.bots.append(new_bot)

		if self.verbose:
			print("All bots initialised")
			print("\nLET'S GO!\n")
		time.sleep(self.slowdown)

	##########################################
	## Running a single round of the auction
	##########################################

	def run_auction(self):
		while not self.finished:
			
			# Print an update to the terminal and reset bids
			self.__start_round()

			# Get bids from all of the bots playing
			self.__collect_bids()

			# Determine the winning bot of this auction round and award the painting
			self.__pick_winner_of_the_round() 
			
			# Update scores
			self.__update_scores()

			# Export data log
			self.__export_data()

			# Run end conditions check
			self.__check_end_conditions()

			# Slow things down a bit if you want to watch
			# if self.current_round%10==0:
			# 	print()
			# 	for bot in self.bots:
			# 		print("Bot: {} Score: {}, Money: {}".format(bot["bot_unique_id"],bot["score"], bot["budget"]))
			# 	time.sleep(self.slowdown)

		
		return self.__get_winners()

	def __start_round(self):
		"""
		Print out a statement about the auction
		Set all bots' bids to zero at the start of each round
		"""
		if self.verbose:
			print("\nRunning auction round {} of {}".format(self.current_round+1, self.round_limit))
		
		for bot in self.bots:
			bot["current_bid"] = 0

	def __collect_bids(self):
		"""
		Get bids from each of the bots, and check that the bids are valid
		This passes data to the bot so that the bot can build a strategy on that data
		Each bot receives a seperate deep copy of the data, so there is no chance that the bot
		can change the data held by other bots or the auction object.
		"""
		# Build a dictionary of the data we will pass to bots
		info_for_bots = {
			"current_round":self.current_round,
			"bots":self.bots,
			"game_type":self.game_type,
			"winner_pays":self.winner_pays,
			"artists_and_values":self.artists_and_values,
			"round_limit":self.round_limit,
			"starting_budget":self.starting_budget,
			"painting_order":self.painting_order,
			"target_collection":self.target_collection,
			"current_painting":self.painting_order[self.current_round],
			"winner_ids":self.winner_ids
		}
		# Make a deep copy of the data to pass to bots, so we are not just passing the bot shared references to data
		# Every bot gets data in completely seperate memory so there is no risk of changing data in other bots or the auction object
		info_for_bots_deep_copy = copy.deepcopy(info_for_bots)

		# Remove the bot instances from the dictionaries
		for bot in info_for_bots_deep_copy["bots"]:
			del bot["bot_instance"]
			del bot["current_bid"]

		for bot in self.bots:
			# Add this bot's details to the data to pass to the bot, but as a deep copy rather than the actual data  
			info_for_bots_deep_copy["my_bot_details"] = copy.deepcopy(bot)
			
			# If the bot raises an error - catch it, log it and either stop the game or carry on with the bot bidding zero
			try:
				# Match the bid type to the game type
				if self.game_type == "value":
					# Pass in all the information for the bot as kwargs
					bid = int(bot["bot_instance"].get_bid_game_type_value(**info_for_bots_deep_copy))
				elif self.game_type == "collection":
					bid = int(bot["bot_instance"].get_bid_game_type_collection(**info_for_bots_deep_copy))
			except Exception as e:
				print("Bidding error caught on {} - {}".format(bot["bot_unique_id"], e))
				# Log any errors that are raised in a csv file
				self.__log_error(bot_name=bot["bot_unique_id"], game_stage="bidding", error_message=str(e))
				
				# Either raise an exception to stop the game, or carry on but have the bot bid zero
				# Uncomment the raise line to have the bod bid zero and continue with the auction
				raise   		# Raise an error. Useful for testing and finding errors
				bid = 0   		# Bid zero and carry on if raise line is commented out

			# Check the bot can afford the bid, or else bid zero
			if bid <= bot["budget"]:
				bot["current_bid"] = bid
			else:
				bot["current_bid"] = 0

	def __pick_winner_of_the_round(self):
		"""
		Find the winner of the auction round based on the bids given
		"""
		# Sort the bots based on their current bid. If there is a tie, randomly break the tie
		self.bots.sort(key=lambda x: (x["current_bid"],random.random()), reverse=True)
		# Award the painting to the winning bot, the first in the sorted array of bots
		winner = self.bots[0]
		# Subtract bid value from the winning bot's budget
		bid_position_to_pay = min(self.winner_pays, len(self.bots))
		amount_paid = self.bots[bid_position_to_pay-1]["current_bid"]
		winner["budget"] -= amount_paid
		self.amounts_paid.append(amount_paid)

		# Add painting to winner's paintings
		current_painting = self.painting_order[self.current_round]
		winner["paintings"][current_painting] += 1
		self.winner_ids.append(winner["bot_unique_id"])

		if self.verbose:
			print("{} wins a {} and pays {}".format(winner["bot_unique_id"], current_painting, amount_paid))

	def __update_scores(self):
		"""
		Update each of the bot's scores.
		Based on the paintings won by each bot and the game rules
		"""
		if self.game_type == "value":
			self.__update_scores_value()
		elif self.game_type == "collection":
			self.__update_scores_collection()

	def __update_scores_value(self):
		"""
		Works out the score for each bot based on painting values
		"""
		for bot in self.bots:
			bot["score"] = 0
			# Add up score based on the paintings this bot has won and the artist values
			for artist in self.artists_and_values.keys():
				bot["score"] += bot["paintings"][artist] * self.artists_and_values[artist]

	def __update_scores_collection(self):
		"""
		Checks to see if any bots have a full collection.
		Score is 1 for full collection and 0 otherwise
		"""
		for bot in self.bots:
			bot["score"] = 0
			# Sort this bot's painting counts, and target counts, with highest value first 
			bot_painting_counts_sorted = sorted(bot["paintings"].values(), reverse=True)
			target_painting_counts_sorted = sorted(self.target_collection, reverse=True)

			# Subtract target painting counts from this bot's painting count
			paintings_needed = [target-bot_painting_counts_sorted[index] for index, target in enumerate(target_painting_counts_sorted)]
			# If all the paintings needed counts are 0 or less, then the collection is complete
			if max(paintings_needed)<1:
				bot["score"]=1
				self.finished = True

	def __export_data(self):
		"""
		Export the result of this round of the auction to a csv file
		"""
		export_data_list = [
			self.game_start_time,
			self.game_type,
			self.current_round + 1,
			self.winner_ids[self.current_round],
			self.painting_order[self.current_round],
			self.amounts_paid[self.current_round]
		]

		export_to_csv(self.output_csv_file, export_data_list)

	def __log_error(self, bot_name, game_stage, error_message):
		"""
		Log an error with a bot
		"""
		error_log_data_list = [
			self.game_start_time,
			self.game_type,
			self.current_round,
			bot_name,
			game_stage,
			error_message
		]

		export_to_csv(self.error_log_csv_file, error_log_data_list)


	def __check_end_conditions(self):
		"""
		Check if any of the game end conditions are met 
		"""
		self.current_round += 1
		# Condition 1 - round limit reached
		if self.current_round >= self.round_limit:
			self.finished = True


	##########################################
	## End of the auction
	##########################################

	def __get_winners(self):
		"""
		Declare the winners, based on who has the maximum score. 
		Returns a list of winners
		This is independent of the game type, 
		Points game - the score is based on artist values
		Collection game - the winner has score of 1 while losers have score of 0
		"""
		# Get the maximum (winning) score 
		winning_score = max(bot["score"] for bot in self.bots)
		if winning_score > 0:
			# Get all bots that have the winning score
			winners = [bot["bot_name"] for bot in self.bots if bot["score"] == winning_score]
			if self.verbose:
				print("Winner: {}".format(winners))
			# Return a list of the winners
			return winners
		else:
			if self.verbose:
				print("No-one won")
			return []


# This only runs if the auctioneer.py file is run itself (instead of being imported)
if __name__=="__main__":
	# An example of how to run an auction
	room = [random_bot, flat_bot_10]
	my_auction = Auctioneer(room=room, game_type="value")
	my_auction.run_auction()