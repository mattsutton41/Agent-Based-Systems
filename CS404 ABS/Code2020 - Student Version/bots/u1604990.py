import numpy as np
import random
import math

class Bot(object):

	def __init__(self):
		self.name = "1604990"# Put your id number her. String or integer will both work

	def get_bid_game_type_collection(self, current_round, bots, game_type, winner_pays, artists_and_values, round_limit,
		starting_budget, painting_order, target_collection, my_bot_details, current_painting, winner_ids):
		

		# WRITE YOUR STRATEGY HERE FOR COLLECTION TYPE GAMES - FIRST TO COMPLETE A FULL COLLECTION
		##Check when possible to win
		my_budget = my_bot_details["budget"]
		target = sorted(target_collection, reverse = True)
		#Goal dictionary will store our objective
		goal = {"Da Vinci":0,"Picasso":0,"Rembrandt":0,"Van Gogh":0}
		#Takes a list of the remaining paintings, to check the earliest point at which our bot can win
		rem_painting = painting_order[current_round:]
		current_collection = my_bot_details["paintings"].copy()
		painters = current_collection.keys()
		goal_met = False
		i = current_round
		#Finds nearest winning position for greedy bidding. Assuming win of every painting, when do we meet target, and with what paintings.
		while(goal_met != True):
			current_collection[painting_order[i]] += 1
			target = sorted(target_collection, reverse = True)
			#For each painter, checks if current number of paintings meets the target
			for painter in painters:
				target = sorted(target, reverse = True)
				target_met = False
				j = 0
				while(target_met != True and j < len(target)):
					if(current_collection[painter] >= target[j]):
						goal[painter] = target[j]
						target[j] = 0
						target_met = True
					j+=1
			#If target can be met by round i, then this is our goal
			if sum(target) == 0: 
				goal_met = True
			else:
				i += 1
		#Calculates the number of paintings needed, and bids an equal portion of the remaining budget on each
		needed = 0
		for painter in painters:
			if(goal[painter]>0):
				needed += max(0, goal[painter] - my_bot_details["paintings"][painter])
		print(my_bot_details["paintings"])
		print(goal)
		#If the painting is needed for the goal collection we bid. If not, we bid a nominal amount.
		if(goal[current_painting]>my_bot_details["paintings"][current_painting]):
			my_util = math.ceil(my_budget/needed)
		else:
			my_util = 25

		return my_util

	def get_bid_game_type_value(self, current_round, bots, game_type, winner_pays, artists_and_values, round_limit,
		starting_budget, painting_order, target_collection, my_bot_details, current_painting, winner_ids):

		# WRITE YOUR STRATEGY HERE FOR VALUE GAMES - MOST VALUABLE PAINTINGS WON WINS
		# Collect info
		# myBudget, myScore, n, cpv
		myBudget = my_bot_details["budget"]
		myScore = my_bot_details["score"]
		n = len(bots)
		cpv = artists_and_values[current_painting]
		budgets = []
		scores  = []
		utils = []
		remval = 0
		myutil = 0
		#Takes necessary information; Remaining painting value, budget and score for each bot
		for artist in painting_order[current_round:]:
			remval += artists_and_values[artist]
		for bot in bots:
			if bot["bot_unique_id"]!=my_bot_details["bot_unique_id"]:
				budgets.append(bot["budget"]) 
				scores.append(bot["score"])	

		totval = 0


		#Plays a simple efficient strategy for the 2 player case
		if(n == 2):
			for artist in painting_order:
				totval += artists_and_values[artist]
			objval = (totval+1)/2
			avgval = myBudget/(objval-myScore)
			myutil = avgval*cpv
			if(myutil > myBudget):
				myutil = myBudget
		else:
			#Budget, ToWin, Scores, utils
			min_win_me = 0
			min_win_opp = []
			current_max = max(scores)
			current_max_op = max(current_max, myScore)
			pot_win = 0
			#Captures value needed to win
			min_win_me = (remval + current_max_op - myScore)/2
			#For every other bot, calculate the value they need to guarantee winning
			for bot in bots:
				if bot["bot_unique_id"]!=my_bot_details["bot_unique_id"]:
					pot_win = (remval+current_max_op-bot["score"])/2
					if pot_win <= remval:
						min_win_opp.append((remval+current_max_op-bot["score"])/2)
					else:
						#Forces the relevance of a player to be low if they can no longer win
						min_win_opp.append(1000)
			print(min_win_opp)
			#Calculates the expected bid of each player, based on their budget and what they need to win
			my_cpu = myBudget/min_win_me
			opp_cpu = []
			i = 0
			for bot in bots:
				if bot["bot_unique_id"]!=my_bot_details["bot_unique_id"]:
					opp_cpu.append(bot["budget"]/min_win_opp[i])
					i+=1
			my_bid = my_cpu*cpv
			opp_bids = []
			for i in range(len(opp_cpu)):
				opp_bids.append(opp_cpu[i]*cpv)
			#Aggression: High: Budget++, ToWin--, Utils++
			#Basic: Total/Opp
			tot_win = sum(min_win_opp) + min_win_me
			#Plays aggressively towards a player if their minimum win is low
			my_agg = tot_win / min_win_me
			opp_agg = []
			i = 0
			for bot in bots:
				if bot["bot_unique_id"]!=my_bot_details["bot_unique_id"]:		
					opp_agg.append(tot_win/min_win_opp[i])
					i += 1
			#Normalise aggression across bots
			tot_agg = sum(opp_agg) + my_agg
			norm_opp_agg = []
			norm_my_agg = my_agg / tot_agg
			i = 0
			for bot in bots:
				if bot["bot_unique_id"]!=my_bot_details["bot_unique_id"]:		
					norm_opp_agg.append(opp_agg[i]/tot_agg)
					i+=1

			#Calculates our bid as a combination of expected bids and aggression coefficients
			my_bid_agg = norm_my_agg * my_bid
			opp_bids_agg = []
			i = 0
			for bot in bots:
				if bot["bot_unique_id"]!=my_bot_details["bot_unique_id"]:
					opp_bids_agg.append(norm_opp_agg[i]*opp_bids[i])
					i += 1
			myutil = sum(opp_bids) + my_bid_agg
		
		print("My bid ", math.ceil(myutil))
		return math.ceil(myutil)
