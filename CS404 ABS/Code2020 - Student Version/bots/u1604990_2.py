import numpy as np
import random
import math

class Bot(object):

	def __init__(self):
		self.name = "1604990_2"# Put your id number her. String or integer will both work
        #akash = '1602498'
        #if(akash in bots_in_room):
         #   alpha = 1
            
		# Add your own variables here, if you want to. 

	def get_bid_game_type_collection(self, current_round, bots, game_type, winner_pays, artists_and_values, round_limit,
		starting_budget, painting_order, target_collection, my_bot_details, current_painting, winner_ids):
		"""Strategy for collection type games. 

		Parameters:
		current_round(int): 			The current round of the auction game
		bots(dict): 					A dictionary holding the details of all of the bots in the auction
										Includes what paintings the other bots have won and their remaining budgets
		game_type(str): 				Will be "collection" for collection type games
		winner_pays(int):				Rank of bid that winner plays. 1 is 1st price auction. 2 is 2nd price auction.
		artists_and_values(dict):		A dictionary of the artist names and the painting value to the score (for value games)
		round_limit(int):				Total number of rounds in the game - will always be 200
		starting_budget(int):			How much budget each bot started with - will always be 1001
		painting_order(list str):		A list of the full painting order
		target_collection(list int):	A list of the type of collection required to win, for collection games - will always be [4,2]
										[5] means that you need 5 of any one type of painting
										[4,2] means you need 4 of one type of painting and 2 of another
										[3,3,1] means you need 3 of one tpye of painting, 3 of another, and 1 of another
		my_bot_details(dict):			Your bot details. Same as in the bots dict, but just your bot. 
										Includes your current paintings, current score and current budget
		current_painting(str):			The artist of the current painting that is being bid on
		winner_ids(list str):			A list of the ids of the winners of each round so far 

		Returns:
		int:Your bid. Return your bid for this round. 
		"""

		# WRITE YOUR STRATEGY HERE FOR COLLECTION TYPE GAMES - FIRST TO COMPLETE A FULL COLLECTION

		my_budget = my_bot_details["budget"]
		return 20

	def get_bid_game_type_value(self, current_round, bots, game_type, winner_pays, artists_and_values, round_limit,
		starting_budget, painting_order, target_collection, my_bot_details, current_painting, winner_ids):
		"""Strategy for value type games. 

		Parameters:
		current_round(int): 			The current round of the auction game
		bots(dict): 					A dictionary holding the details of all of the bots in the auction
										Includes what paintings the other bots have won and their remaining budgets
		game_type(str): 				Will be either "collection" or "value", the two types of games we will play
		winner_pays(int):				rank of bid that winner plays. 1 is 1st price auction. 2 is 2nd price auction.
		artists_and_values(dict):		A dictionary of the artist names and the painting value to the score (for value games)
		round_limit(int):				Total number of rounds in the game
		starting_budget(int):			How much budget each bot started with
		painting_order(list str):		A list of the full painting order
		target_collection(list int):	A list of the type of collection required to win, for collection games
										[5] means that you need 5 of any one type of painting
										[4,2] means you need 4 of one type of painting and 2 of another
										[3,3,1] means you need 3 of one type of painting, 3 of another, and 1 of another
		my_bot_details(dict):			Your bot details. Same as in the bots dict, but just your bot. 
										Includes your current paintings, current score and current budget
		current_painting(str):			The artist of the current painting that is being bid on
		winner_ids(list str):			A list of the ids of the winners of each round so far 

		Returns:
		int:Your bid. Return your bid for this round. 
		"""
		# WRITE YOUR STRATEGY HERE FOR VALUE GAMES - MOST VALUABLE PAINTINGS WON WINS
		# Collect info
		# myBudget, myScore, n, cpv
		my_budget = my_bot_details["budget"]
		my_score = my_bot_details["score"]
		n = len(bots)
		cpv = artists_and_values[current_painting]

		#Simple 2 player strategy
		if(n == 2):
			tot_val = 0
			for artist in painting_order:
				tot_val += artists_and_values[artist]
			obj_val = (tot_val+1)/2			
			avg_val = my_budget/(obj_val-my_score)
			my_util = avg_val*cpv
			if(my_util > my_budget):
				my_util = my_budget

		else:
			#Testing
			
			#Loop for each bot
			#Takes current max score in game
			scores = []
			for bot in bots:
				scores.append(bot["score"])
			scoreboard = sorted(scores, reverse = True)
			current_max = max(bot["score"] for bot in bots)
			#Calculate remaining painting value
			rem_val = 0
			for artist in painting_order[current_round:]:
				rem_val += artists_and_values[artist]
			#Take my minimum win
			if (my_score==scoreboard[0]):
				current_max = scoreboard[1]
			else:
				current_max = scoreboard[0]
			min_win_me = max((rem_val+current_max-my_score)/2,0)
			min_win_op = []
			#Calculate my Cost per Unit
			if(min_win_me!=0):
				my_cpu = my_budget/min_win_me
			else:
				my_cpu = my_budget/rem_val
			op_cpu = []
			#Predict my bid
			my_bid = min(my_cpu*cpv,my_budget)
			op_bids = []
			#Calculate my aggression

			my_agg = min_win_me

			op_agg = []
			#loop for determining aggro of opposition
			i = 0
			for bot in bots:
				if bot["bot_unique_id"]!=my_bot_details["bot_unique_id"]:
					#Calculate this bots score to win
					if (bot["score"]==scoreboard[0]):
						current_max = scoreboard[1]
					else:
						current_max = scoreboard[0]
					pot_win = max((rem_val + current_max - bot["score"])/2,0)
					if pot_win <= rem_val:
						min_win_op.append(pot_win)
					else:
						min_win_op.append(10000000)
					#Calculate this bots Cost per Unit
					if(min_win_op[i]!=0):
						op_cpu.append(bot["budget"]/(min_win_op[i]))
					else:
						op_cpu.append(bot["budget"]/rem_val)
					#Calculate expected opposition bids
					op_bids.append(min(op_cpu[i]*cpv,bot["budget"]))
					#Calculate aggression values
					if(min_win_op[i]!=0):
						op_agg.append(rem_val/min_win_op[i])
					else:
						op_agg.append(0)
					i+=1

			#
			print("Opposition to win: ",min_win_op)
			print("opposition Expected bids:", op_bids)
			#Normalise aggression
			tot_agg = sum(op_agg) + my_agg
			if(tot_agg != 0):
				my_agg = my_agg/tot_agg
			else:
				my_agg = 0

			for i in range(len(op_agg)):
				if(tot_agg!=0):
					op_agg[i] = op_agg[i]/tot_agg
				else:
					op_agg[i] = 0

			#Sum bids
			my_agg = my_agg*my_bid
			for i in range(len(op_agg)):
				op_agg[i] = op_agg[i]*op_bids[i]
			my_util = sum(op_agg)+my_agg

			#prints
			print("My bid:", min(math.ceil(my_util), my_budget))
			print("Opp aggs:", op_agg)

			return min(math.ceil(my_util), my_budget)
