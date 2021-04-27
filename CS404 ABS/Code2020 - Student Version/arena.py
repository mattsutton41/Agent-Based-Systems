
# Import the auctioneer, to run your auctions
from auctioneer import Auctioneer

# Import some bots to play with
# We have given you some basic bots to start with in the bots folder
# You can also add your own bots to test against
from bots import flat_bot_10
from bots import random_bot
from bots import u1604990


def run_basic_auction():
	"""
	An example function that runs a basic auction with 3 bots
	"""
	# Setup a room of bots to play against each other, imported above from the bots folder
	room = [u1604990, random_bot, flat_bot_10]

	# Set the game type between "value" or "collection"
	game_type = "value"
	# Setup the auction
	my_auction = Auctioneer(room=room, game_type=game_type)
	# Play the auction
	my_auction.run_auction()


def run_lots_of_auctions():
	"""
	An example if you want to run alot of auctions at once
	"""
	# A large room with a few bots of the same type
	room = [random_bot, random_bot, random_bot, u1604990, flat_bot_10]
	# Set the game type between "value" or "collection"
	game_type = "collection"
	
	win_count = 0
	run_count = 10
	for i in range(run_count):
		# Setup the auction
		slowdown = 0 #makes it fast
		my_auction = Auctioneer(room=room, game_type=game_type, slowdown=0)
		# run_auction() returns a list of winners, sometimes there are more than one winner if there is a tie
		winners = my_auction.run_auction()
		# Check if the bot's name, "my_bot", was a winner 
		if "1604990" in winners:
			win_count +=1
	print("My bot won {} of {} games".format(win_count, run_count))	


if __name__=="__main__":
	run_lots_of_auctions()