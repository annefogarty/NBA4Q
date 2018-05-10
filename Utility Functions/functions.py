def proportion(table):
    ## takes in a table and returns counts of how many shots were assisted/not assisted
    table = table.where('SHOT_MADE', 1)
    table = table.with_column('ASSIST_PLAYER_ID', table.apply(lambda x: str(x), 'ASSIST_PLAYER_ID'))

    # Create Assist Table
    a = table.where('ASSIST_PLAYER_ID', predicates.are.not_equal_to('nan'))
    a_count = a.num_rows

    # Create Unassisted Table
    ua = table.where('ASSIST_PLAYER_ID', predicates.are.equal_to('nan'))
    ua_count = ua.num_rows
    
    try:
        p = ua_count /(a_count + ua_count)
    except ZeroDivisionError:
        p = 0 
    return p

def six_minute_interval(table):
    
    start_time = time.time() 

    # get a random game from all games.
    first_game_id = 21500001
    last_game_id = 21501230
    rand_game_id = 21500001 + random.randint(0, last_game_id - first_game_id + 1)
    
    game = table.where('GAME_ID', rand_game_id)
    
    # Random time between start and beginning of third
    # No overlap with last 6 mins
    max_time = 60 * 36
    time_start = random.randint(0, max_time)
    time_end = time_start + 60 * 6  # Add 360 seconds
    sampled_6min = game.where('TIME', predicates.are.above_or_equal_to(time_start)).\
        where('TIME', predicates.are.below_or_equal_to(time_end))
    
    return sampled_6min


def create_distributions(table):
    
    anyone1 = make_array()
    anyone2 = make_array()
    
    for i in np.arange(689):
        print('Iteration Count is: ' + str(i)) 
        
        start_time = time.time()
        six_minutes1 = six_minute_interval(table)
        print("i1 took ", time.time() - start_time, "to run")      
        
        start_time1 = time.time()
        six_minutes2 = six_minute_interval(table)
        print("i2 took ", time.time() - start_time1, "to run") 
        
        print('')
        # calculate the test statistic
        kappa1 = proportion(six_minutes1)
        kappa2 = proportion(six_minutes2)
        
        # append test statistic to array
        print('Test statistic ANY 6 1 is: ' + str(kappa1))
        print('Test statistic ANY 6 2 is: ' + str(kappa2))
        anyone1 = np.append(anyone1, kappa1)
        anyone2 = np.append(anyone2, kappa2)
          
        print(str(689 - i) + ' iterations left to go')
        print('')
        
        print('')
        print('NEW ITERATION')
        print('')  
        
            
    both = Table().with_columns('Any6 1', anyone1, 'Any6 2', anyone2)
    
    return both


# Writing the some 1230 tables to csvs...
game_array = all_games.group('GAME_ID').column('GAME_ID')
hello = Table().read_table('question2_table.csv')
length = len(game_array)
print(length)

def create_table_for_every_game():
    game_tables = make_array()
    count = 0
    for i in game_array:
        print('Iterations left: ', length - count)
        game_table = hello.where('GAME_ID', i)
        game_table.to_csv('q2_game_' + str(i) + '.csv')
        count += 1