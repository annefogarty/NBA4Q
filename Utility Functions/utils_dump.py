### ALL THESE FUNCTIONS WERE USED TO CONSTRUCT TABLES NOW SAVED AS CSVs, 
### AND ALL NBA_PY RELATED FUCNTIONS ARE NOW OUTDATED. WHAT IS HERE IS BUY AND LARGE NO LONGER NEEDED.


def calc_efg(FGM, THREEPTM, FGA):
    try:
        (FGM + (0.5 * THREEPTM)) / FGA
    except:
        return 0
    
    return (FGM + (0.5 * THREEPTM)) / FGA

def calc_ts(FTA, PTS, FGA):
    try:
        PTS / ((2 * FGA) + (0.88 * FTA))
    except:
        return 0
    
    return PTS / ((2 * FGA) + (0.88 * FTA))

# For nba_y
def convert_season_to_index(season):
    end = season[5:]
    int_year = int(end)
    return 18 - int_year

# Time string to number
def time_string_to_number(time_string):
    index = len(time_string)-3
    minute = int(time_string[:index:])
    seconds = int(time_string[index::].replace(':', '')) / 60
    return minute + seconds

# Gets first name
def first(string):
    name = string.split(' ')
    first = name[0]
    return first
 
# Gets last name   
def last(string):
    name = string.split(' ')
    if len(name) == 1:
        return 'nan'
    first = name[1]
    return first

def get_season_stats(first, last):
    first = first.replace('.', '')    
    
    print(first)
    print(last)
    
    try:
        player_id = py.player.get_player(first, last_name=last)
    except:
        return [0, 0]
          
    player_general_splits = py.player.PlayerGeneralSplits(player_id)

    player_yearoveryear_splits = py.player.PlayerYearOverYearSplits(player_id, '2015-16')
    


    q = ds.Table.from_df(player_yearoveryear_splits.by_year())
    

    q = q.where('GROUP_VALUE', '2015-16')
    
    if q.num_rows < 1:
        return [0, 0]

    FGA = q.column('FGA').item(0)
    FG3M = q.column('FG3M').item(0)
    FGM = q.column('FGM').item(0)

    EFG = calc_efg(FGM, FG3M, FGA)
    
    FTA = q.column('FTA').item(0)
    PTS = q.column('PTS').item(0)
    
    TS = calc_ts(FTA, PTS, FGA)
    
    print([TS, EFG])

    return [TS, EFG]

def game_filter(csv_file): 
    
    
    pbp = Table().read_table(csv_file)
        
    last_quarter = pbp.where('PERIOD', predicates.are.equal_to(4))
    transformed_minutes = last_quarter.apply(time_string_to_number, 'PCTIMESTRING')
    last_quarter_and_minutes = last_quarter.with_column('TIME', transformed_minutes)
    
    find_close_scores = last_quarter_and_minutes.where('TIME', predicates.are.between(6, 6.5))  

    close_games_ids = make_array()   
    last_id = 0
    
    for i in np.arange(find_close_scores.num_rows):      
        row = find_close_scores.row(i)    
        current_id = int(row[0])
        if current_id != last_id:
            diff = abs(int(row[7]) - int(row[8]))
            if diff <= 10:
                close_games_ids = np.append(current_id, close_games_ids)
        last_id = current_id
        
        
    close_games_table = Table().with_column('Close Games', close_games_ids)    
    time_less_than_six = last_quarter_and_minutes.where('TIME', predicates.are.below(6.6))
    time_less_than_six = time_less_than_six.join('GAME_ID', close_games_table, 'Close Games')
    
    return time_less_than_six

players = games.select('PLAYER1_ID', 'PLAYER1_NAME')
players = players.group('PLAYER1_ID', max).where('PLAYER1_NAME max', predicates.are.not_equal_to('nan')).relabel(1, 'PLAYER_NAME')

def first(string):
    name = string.split(' ')
    first = name[0]
    return first
    
def last(string):
    name = string.split(' ')
    if len(name) == 1:
        return 'nan'
    first = name[1]
    return first

def constuct_players(players):
    
    players = players.with_column('FIRST_NAME', players.apply(first, 'PLAYER_NAME'))
    players = players.with_column('LAST_NAME', players.apply(last, 'PLAYER_NAME'))


    game1 = games.take(np.arange(0, 69))
    names = game1.select('PLAYER1_NAME')


    players = players.join('PLAYER_NAME', names, 'PLAYER1_NAME').group('PLAYER1_ID', max)
    players.relabel(1, "PLAYER_NAME").relabel(2, "FIRST_NAME").relabel(3, "LAST_NAME")
    players
    statzz = Table(make_array('TS', 'EFG'))

    statzz.with_column('Player', players.column('PLAYER_NAME'))

    return players

# GET TS/ES
for i in np.arange(0, players.num_rows):
    print(i)
    row = players.row(i)
    statzz = statzz.with_row(get_season_stats(row[2], row[3]))
    
statzz = statzz.with_column('Player', players.column('PLAYER_NAME'))
stored = statzz
# stored.to_csv('Players.csv')
stored

players = players
players = players.join('PLAYER_NAME', statzz, 'Player').where('TS', predicates.are.not_equal_to(0))
players.to_csv('Players.csv')
players

# FIND WHO IS PLAYING THE MOST TIME
# WHAT KIND OF SHOT PLUS 3 POINT SHOTS

def construct_game_reference_table():
    count = 1
    season = Table(make_array('HOME_TEAM', 'AWAY_TEAM'))
    array = make_array()
    for t in games_list:
        index = t[0]
        row = games.take(index).select('HOME_TEAM', 'AWAY_TEAM')
        array = np.append(array, count)
        count += 1
        season = season.with_row(row)
    season = season.with_column('GAME NUMBER', array).with_column('INDICIES', games_list)
   

    return season 

def build_reference_table(table):     
    x = construct_game_reference_table()
    first_i = make_array()
    last_i = make_array()

    for elem in x.column(3):
        first = elem[0]
        last = elem[1]
        first_i = np.append(first_i, first)
        last_i = np.append(last_i, last)

    x = x.with_column('FIRST_INDEX', first_i)
    x = x.with_column('LAST_INDEX', last_i)
    x = x.drop(3)
    x.to_csv('gamereference.csv')