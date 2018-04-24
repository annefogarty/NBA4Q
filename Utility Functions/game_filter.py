import matplotlib.pyplot as plt
import numpy as np
from datascience import Table, make_array, predicates
plt.style.use('fivethirtyeight')
# %matplotlib inline

# pbp = Table().read_table('2015-16_pbp.csv')
# print(pbp.column(1))

def time_string_to_number(time_string):
	index = len(time_string)-3
	minute = int(time_string[:index:])
	seconds = int(time_string[index::].replace(':', '')) / 60
	return minute + seconds

def game_filter(csv_file):
	# Takes in a csv filepath of one of the EightThirtyFour data sets
	# and filters the data to games with a 10 or less point lead in 
	# the last 6 minutes of the game.
	pbp = Table().read_table(csv_file)
	unique_games = pbp.group('GAME_ID').column(0)
	print(unique_games)
	last_quarter = pbp.where('PERIOD', predicates.are.equal_to(4))
	transformed_minutes = last_quarter.apply(time_string_to_number, 'PCTIMESTRING')
	last_quarter_and_minutes = last_quarter.with_column('TIME', transformed_minutes)
	between_six_and_seven = last_quarter_and_minutes.where('TIME', predicates.are.below_or_equal_to(6.5))
	close_games = make_array()
	for game in unique_games:
		game_scores_only = between_six_and_seven.where('GAME_ID', 
			predicates.are.equal_to(game)).select('TIME', 'SCORE').where('SCORE', predicates.are.not_equal_to('nan'))
		score = game_scores_only.row(0).item(1)
		t1, t2 = score.split('-')
		if abs(int(t1) - int(t2)) <= 10:
			close_games = np.append(close_games, game)
	return close_games
print(game_filter('DUPLICATE.csv'))
# print(time_string_to_number('12:30'))
	




