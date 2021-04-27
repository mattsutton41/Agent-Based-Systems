# Bot World

## arena.py
Here you can run auctions with different bots and see the results. 

You can run an auction game like this:

	from auctioneer import Auctioneer
	my_auction = Auctioneer(<ADD ANY VARIABLES YOU WANT TO HERE>)
	winners = my_auction.run_auction()

run_auction returns a list of the winners, with the name of the winning bots, for example if a random_bot won, the returned variable would be ["random_bot"].

The arena file has some example functions that show how to run auctions with different bots and different variables. 

## auctioneer.py
DO NOT CHANGE THE CODE IN THE AUCTIONEER. THIS IS THE EXACT FILE WE WILL USE TO MARK YOUR BOT
IF YOU CHANGE SOMETHING IN THE AUCTIONEER FILE THEN YOUR BOT MIGHT NOT RUN PROPERLY WHEN WE MARK IT 

You DO NOT need to understand how the auctioneer works to complete this coursework and do well. 
But it always helps to understand software that you are using. 

The auctioneer runs the auctions.
Each auction consists of 200 rounds, with one painting auctioned each round.

### How to Use
There is some code at the bottom of auctioneer.py that runs an auction for you. You can run that by running auctioneer.py from terminal

	python3 auctioneer.py

### How It Works

#### Initialising the auction
The auctioneer is given the set of rules for the game and a "room", which is a list of the bots that will play. 
The auctioneer begins by initialising itself in the method self.__init__(), and initialising the bots with the method initialise_bots(). 

#### Running the auction
Once all the bots are accounted for and running, the auctioneer runs the method run_auction(). This includes a "game loop" that keeps going until one of the bots wins or the round limit is reached (usually 200 rounds).

Each round of the auction, the auctioneer performs the following process:
	- __start_round(). Prints a message to the screen, and sets all bids to zero. 
	- __collect_bids(). Asks each of the bots for their bid on the current round.
	- __pick_winner_of_the_round(). Chooses a winning bid and awards the painting.
	- __update_scores(). Updates the scores for each bot. 
	- __export_data(). Exports a log of the auction run to a csv file. 
	- __check_end_conditions(). Checks if the auction should keep going or finish

#### Winners
__get_winners() determines the winners of the auction. If more than one bot has the same top score then all bots with that score win. 
The winners are returned with the run_auction method call.