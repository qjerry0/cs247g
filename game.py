import random

# CONSTANTS
MIN_PLAYERS = 3             # min player count
MAX_PLAYERS = 8             # max player count
MIN_ROUND_NUM = 4           # min number of rounds of matching
MAX_ROUND_NUM = 6           # max number of rounds of matching
MIN_MESSAGE_TIMER = 90      # min time to message, in sec
MAX_MESSAGE_TIMER = 120     # max time to message, in sec
ROLE_REVEAL_ROUND = 2       # turn that role is revealed for 1st place
ROLES_34 = ["team_player", "schadenfreuder", "slacker", "thief", "snitch", "flake", "leech"]    # role set, 3-4
ROLES_5 = ["slacker", "thief", "snitch", "god", "leech", "team_player", "schadenfreuder"],      # role set, 5
ROLES_6 = ["slacker", "thief", "snitch", "god", "flake", "gossip", "leech", "team_player",      # role set, 6+
            "schadenfreuder", "hacker"]

ROLE_DICT = {"default":DefaultPlayer,
            "slacker":SlackerPlayer,
            "thief":ThiefPlayer,
            "snitch":SnitchPlayer,
            "god":CSGodPlayer,
            "flake":FlakePlayer,
            "gossip":GossipPlayer,
            "leech":LeechPlayer,
            "team_player":TeamPlayer,
            "schadenfreuder":SchadenfreuderPlayer,
            "hacker":HackerPlayer,}

def init_game():
    ''' Initializes a game
        @return list    A list containing the names of the players, as strings.
    '''
    input_players = input("Welcome to Group Project Hell! How many players are playing? \n")
    while True:
        try:
            n = int(input_players)
            if n < MIN_PLAYERS or n > MAX_PLAYERS:
                input_players = input("Sorry, this game doesn't support that many players, please try again: \n")
            else:
                break
        except:
            input_players = input("That wasn't an integer, please try again: \n")

    
    players = []
    for i in range(1, n+1):
        while True:
            input_player_name = input("Please type the name for player %d:\n" % i)
            if input_player_name in players:
                print("You can't repeat player names, unfortunately. ")
            else:
                players.append(input_player_name)
                break
    return players

def generate_roles(n):
    ''' Generates a list of roles for the players
        @param n        The number of players in the game
        @return list    The roles, as strings, of the players
    '''
    if n == 3 or n == 4:
        return random.sample(ROLES_34, n)
    elif n == 5:
        return random.sample(ROLES_5, n)
    else:
        return random.sample(ROLES_6, n)

def init_player_states(game_state):
    ''' Prompts narrator to publically announce a player's role, if necessary given the game state
        @param game_state   The game state
        @return list        A list of Player objects
    ''' 
    # TODO: once real players are created, change this to use them
    players = []
    for p, r in zip(game_state.players, game_state.roles):
        print("$$$player$$$$")
        players.append(ROLE_DICT[r](p, r)) 

    print("$$$players$$$$")
    print(players)
    return players

def announce_roles(players, roles):
    ''' Prompts narrator to tell players their role assignments
        @param players      The players' names
        @param roles        The players' roles, in the same order
    ''' 
    schadenfreuder_name = None

    for p, r in zip(players, roles):
        print("Narrator, please let %s know that they are: %s" %(p, r))

        if r == "schadenfreuder":
            schadenfreuder_name = p

    if (schadenfreuder_name):
        enemy = random.choice(list(set(players) - set(schadenfreuder_name)))
        SchadenfreuderPlayer.setEnemy(schadenfreuder_name)
        print("Narrator, please let " + schadenfreuder_name + " know their enemy is " + enemy)



def announce_role(game_state):
    ''' Prompts narrator to publically announce a player's role, if necessary given the game state
        @param game_state   The game state
    ''' 
    
    pass

def input_matches(players):
    ''' Prompts narrator to input the matches of each player after the matching phase
        @param players  The players in the game
        @return list    The intended matches of the players, in the same order
    '''
    matches = {}    # Dict - {Player name (str) : Player name they chose to pair w/ (str)}
    for p in players:
        while True:
            match = input("Please input the student %s picked: " % p)
            if match == p:
                print("Players cannot pair with themselves, please try again.")
            elif match not in players:
                print("You've made a typo, please input one of the players.")
            else:
                matches[p] = match
                break
    return matches


def successful_pairings(matches):
    ''' @return dict of successful matches only '''
    reverse_matches = {v: k for k, v in matches.items()}    #dict with reverse key/values from matches
    successful_pairs = {k: matches[k] for k in matches if k in reverse_matches and matches[k] == reverse_matches[k]}    #finds matching k/v pairs
    return successful_pairs


def run_game(game_state, player_states):
    ''' Core loop of the game, this runs throughout the game.
        @param game_state       The initial state of the game, with players and role assignments
        @param player_states    The initial states of each player
    ''' 
    while game_state.round < game_state.max_rounds:
        
        # Matching/messaging phase
        print("Narrator, please say: ")
        round_print = game_state.round + 1
        print("It is the start of week %d! Students, you have %d seconds to find a project \
                partner by messaging them!" % (round_print, game_state.round_times[game_state.round]))
        # TODO: implement delay/prompts for narrator during the matching phase, e.g. 30 sec warning (please message me your matches!)
        
        # Calculate and announce matches
        matches = input_matches(game_state.players)
        successful_match_dict = successful_pairings(matches)
        print("These were the successfull pairings for the round: " + str(successful_match_dict))

        # Add 1 point for every match in round
        i = 0
        for ps in player_states:
            if (ps in successful_match_dict):
                game_state.public_scores[i] += 1
            
            i += 1

        # Calculate bonus points for round
        for ps in player_states:
            if player in successful_match_dict:
                ps.calculate_round_bonuses(game_state, successful_match_dict[ps])


        # Reveal role of current leader
        if game_state.round == ROLE_REVEAL_ROUND:
            current_ranking = [(p, fs) for fs , p in sorted(zip(game_state.public_scores, players))]
            current_ranking.reverse() # start from last place and move up
            leader_name = current_ranking[0]    # TODO: make sure this is right
            leader_index = game_state.player_dict[leader_name]

            print(leader_name + " is currently in the lead, meaning it's time to reveal their role!")
            print(leader_name + "'s role is.... " + game_state.roles[leader_index])

        game_state.round += 1


    # All rounds have finished, tally final scores
    for ps in player_states:
        final_bonuses(game_state))

    rankings = [(p, fs) for fs , p in sorted(zip(game_state.public_scores, players))]
    rankings.reverse() # start from last place and move up 

    print("Narrator, please say: ")
    print("And that was the last week! Let's see who ended up on top!")
    for p, fs in rankings:
        print("%s finished the class with a score of %d!" % (p, fs))

class State(object):
    ''' A class that stores the current public and global state of the game.
    '''

    def __init__(self, n, players, roles):
        self.n = n  # number of players in the game
        self.round = 0 # current round count
        self.max_rounds = min(MIN_ROUND_NUM, max(n, MAX_ROUND_NUM)) # number of rounds in the game
        self.players = players # list player names as strings
        self.roles = roles # list of player roles as strings, in the same order as self.players
        self.public_roles = ["hidden"] * n # list of publically revealed roles as strings, same order as self.players
        self.public_scores = [0] * n # public scores of each player, in the same order as self.players
        self.player_dict = {}    # maps {player name string : corresponding index in players, roles, and public_scores}
        self.round_times = [] # time in seconds for each round, with length = n
        self.current_round_matches = None   # matches for the current round of play. self.current_round_matches[i] indicates
                                            # the match for the i'th player
        for i in range(self.max_rounds):
            if i < 2:
                self.round_times.append(MIN_MESSAGE_TIMER)
            else:
                self.round_times.append(MAX_MESSAGE_TIMER)

class Player(object):
    ''' 
    A player in our game, each will be uniquely identified by its name. To make a new role,
    extend and implement this class.
    '''
    
    def __init__(self, name, role):
        self.name = name
        self.role = role
        self.index = None

    def on_game_init(self, game_state):
        ''' This will be called upon initialization of the game. Implement for each player.
        @param game_state   The current game state
        '''
        pass

    def calculate_round_bonuses(self, game_state, match_name):
        '''
        Called at the end of each round after normal points are added.
        Changes score based on each unique role
        Implement in each class.

        @param successful_match     name of person they matched with
        '''
        pass


    def final_bonuses(self, game_state):
        ''' This will be called upon the completion of the final round. Implement for each player.
        @param game_state   The current game state
        @return The final score the player has, both normal and bonus points combined
        '''

        pass

class DefaultPlayer(Player):
    ''' 
    A default player with no special role or ability. Always scores 0 at the end of the game.
    '''
    def on_game_init(self, player_info):
        self.role = "Default"
        self.index = game_state.player_dict[self.name]

    def final_bonuses(self, game_state):
        return 0

class SlackerPlayer(Player):
    ''' 
    Makes both SlackerPlayer and matched partner gain 0 points during a match. Adds 1 point per match
    to themselves at the end of the game.
    '''
    successful_pairings = None

    def on_game_init(self, player_info):
        self.role = "The Slacker"
        self.index = game_state.player_dict[self.name]
        self.successful_pairings = 0

    def calculate_round_bonuses(self, game_state, match_name):
        match_index = game_state.player_dict[match_name]
        game_state.public_scores[self.index] -= 1
        game_state.public_scores[match_index] -= 1

        self.successful_pairings += 1

    def final_bonuses(self, game_state):
        game_state.public_scores[self.index] += self.successful_pairings
        return game_state.public_scores[self.index]

class ThiefPlayer(Player):
    ''' 
    Steals one point from their partner, except when the other player is a slacker or
    a snitch.
    '''

    def on_game_init(self, player_info):
        self.role = "The Thief"
        self.index = game_state.player_dict[self.name]

    def calculate_round_bonuses(self, game_state, match_name):
        match_index = game_state.player_dict[match_name]
        match_role = game_state.roles[match_name]    #set enemy score

        if (match_role != "slacker") and (match_role != 'thief'):
            game_state.public_scores[match_index] -= 1  #set enemy score
            game_state.public_scores[self.index] += 1   #set own score


    def final_bonuses(self, game_state):
        return game_state.public_scores[self.index]

class SnitchPlayer(Player):
    ''' 
    Steals 2 points if paired with either the slacker or thief
    '''

    def on_game_init(self, player_info):
        self.role = "The Snitch"

    def calculate_round_bonuses(self, game_state, match_name):
        match_index = game_state.player_dict[match_name]
        match_role = game_state.roles[match_name]    #set enemy score

        if (match_role == "slacker") or (match_role == 'thief'):
            game_state.public_scores[match_index] -= 2  #set enemy score
            game_state.public_scores[self.index] += 2   #set own score


    def final_bonuses(self, game_state):
        return game_state.public_scores[self.index]

class CSGodPlayer(Player):
    ''' 
    Starts with 3 points
    '''

    def on_game_init(self, player_info):
        self.role = "The CS God"
        self.index = game_state.player_dict[self.name]
        self.score = 3

    def final_bonuses(self, game_state):
        return game_state.public_scores[self.index]

class FlakePlayer(Player):
    ''' 
    When successfully paired, gets one bonus point per player that
    unsuccessfully tried to pair with them or lose one point
    if no other players.
    '''
    #TODO logic for unsuccessful pairings
    unsuccessful_pairings = None

    def on_game_init(self, player_info):
        self.role = "The Flake"
        self.index = game_state.player_dict[self.name]
        self.unsuccessful_pairings = 0

    def add_point(self, game_state):
        pass

    def final_bonuses(self, game_state):
        game_state.public_scores[index] += unsuccessful_pairings
        return game_state.public_scores[self.index]

class GossipPlayer(Player):
    ''' 
    Sees their project partner’s role when in a project team.
    (dm’ed after announcement of the matching period results,
    during the following period)
    '''

    def on_game_init(self, player_info):
        self.role = "The Gossip"
        self.index = game_state.player_dict[self.name]

    def calculate_round_bonuses(self, game_state, match_name, index):
        match_index = game_state.player_dict[match_name]
        match_role = game_state.roles[match_name]
        print("Narrator, please let " + self.name + " know their partner this round is the " + match_role)

    def final_bonuses(self, game_state):
        return game_state.public_scores[self.index]

class LeechPlayer(Player):
    ''' 
    Receives half of their project partner’s points (rounded down) when
    successfully paired with the same person 2 weeks in a row.
    '''
    # TODO: implement calculate_round_bonuses for this class

    def on_game_init(self, player_info):
        self.role = "The Leech"
        self.index = game_state.player_dict[self.name]

    def add_point(self, game_state):
        pass

    def final_bonuses(self, game_state):
        return game_state.public_scores[self.index]

class TeamPlayer(Player):
    ''' 
    Gives one point to themselves and their project partner when
    successfully paired with the same person 2 weeks in a row.
    '''
    # TODO: implement calculate_round_bonuses for this class

    def on_game_init(self, player_info):
        self.role = "The Team Player"
        self.index = game_state.player_dict[self.name]

    def add_point(self, game_state):
        pass

    def final_bonuses(self, game_state):
        return game_state.public_scores[self.index]

class SchadenfreuderPlayer(Player):
    ''' 
    Receives a random enemy and receives one point if their enemy
    fails to find a project match.
    '''
    enemy = None

    def on_game_init(self, player_info):
        self.role = "The Schadenfreuder"
        self.index = game_state.player_dict[self.name]

    def setEnemy(schadenfreuder_name):
        self.enemy = schadenfreuder_name

    def calculate_round_bonuses(self, game_state, match_name):
        if matchname == self.enemy:
            game_state.public_scores[self.index] += 1

    def final_bonuses(self, game_state):
        return game_state.public_scores[self.index]

class HackerPlayer(Player):
    ''' 
    Swaps their points with their project partner’s points when in a project team.
    '''

    def on_game_init(self, player_info):
        self.role = "The Hacker"
        self.index = game_state.player_dict[self.name]

    def calculate_round_bonuses(self, game_state, match_name):
        match_index = game_state.player_dict[match_name]
        my_points_tmp = game_state.public_scores[self.index]

        game_state.public_scores[self.index] = game_state.public_scores[match_index]    #set own score
        game_state.public_scores[match_index] = my_point_tmp    #set enemy score


    def final_bonuses(self, game_state):
        return game_state.public_scores[self.index]



if __name__ == '__main__':
    players = init_game()
    roles = generate_roles((len(players)))
    player_dict = {val : i for i, val in enumerate(a)}
    announce_roles(players, roles)
    game_state = State(len(players), players, roles)
    player_states = init_player_states(game_state)
    run_game(game_state, player_states)