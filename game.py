import random

# CONSTANTS
MIN_PLAYERS = 4             # min player count
MAX_PLAYERS = 6             # max player count
MIN_ROUND_NUM = 4           # min number of rounds of matching
MAX_ROUND_NUM = 6           # max number of rounds of matching
MIN_MESSAGE_TIMER = 90      # min time to message, in sec
MAX_MESSAGE_TIMER = 120     # max time to message, in sec
ROLE_REVEAL_ROUND = 1       # turn that role is revealed for 1st place
ROLES_34 = ["slacker", "thief", "snitch", "flake", "leech"]    # role set, 3-4
ROLES_5 = ["slacker", "thief", "snitch", "flake", "leech"]     # role set, 5
ROLES_6 = ["slacker", "thief", "snitch", "god", "flake", "gossip", "leech", "team_player",      # role set, 6+
            "schadenfreuder", "hacker"]

ROLE_DICT = {"default":"DefaultPlayer",
            "slacker":"SlackerPlayer",
            "thief":"ThiefPlayer",
            "snitch":"SnitchPlayer",
            "god":"CSGodPlayer",
            "flake":"FlakePlayer",
            "gossip":"GossipPlayer",
            "leech":"LeechPlayer",
            "team_player":"TeamPlayer",
            "schadenfreuder":"SchadenfreuderPlayer",
            "hacker":"HackerPlayer",}

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
    players = []
    for p, r in zip(game_state.players, game_state.roles):
        players.append(globals()[ROLE_DICT[r]](p, r))

    for player in players:
        player.on_game_init()

    return players


def announce_init_roles(players, roles):
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
        SchadenfreuderPlayer.setEnemy(SchadenfreuderPlayer, enemy)
        print("Narrator, please let " + schadenfreuder_name + " know their enemy is " + enemy)


def announce_role(game_state):
    ''' Prompts narrator to publically announce a player's role, if necessary given the game state
        @param game_state   The game state
    ''' 
    if game_state.round >= ROLE_REVEAL_ROUND:
        current_ranking = [(p, fs) for fs , p in sorted(zip(game_state.public_scores, players))]
        current_ranking.reverse() # start from last place and move up
        print("Current ranking is " + str(current_ranking))

        idx = 0
        while current_ranking[idx][0] in game_state.public_roles:
            idx += 1
        leader_name = current_ranking[idx][0]
        leader_index = game_state.player_dict[leader_name]
        game_state.public_roles.add(leader_name)

        print(leader_name + " is the player with the most points who's still hidden, meaning it's time to reveal their role!")
        print(leader_name + "'s role is.... the " + game_state.roles[leader_index] + "!!!")


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
    successful_pairs = {}
    for k, v in matches.items():
        if matches[v] == k:
            successful_pairs[k] = v
            successful_pairs[v] = k
    
    return successful_pairs

def calculate_unsuccessful_num(matches, flake_name):
    ''' Exclusively used for The Flake role 
        @return number of players that tried but failed to match with The Flake
    '''
    unsuccessful = 0
    for k, v in matches.items():
        if v == flake_name and matches[flake_name] != k:
            unsuccessful += 1

    return unsuccessful




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
            if (ps.name in successful_match_dict):
                game_state.public_scores[i] += 1
            
            i += 1


        # Calculate bonus points for round
        for ps in player_states:
            if ps.name in successful_match_dict:
                if ps.role == "The Flake":
                    num_unsuccessful = calculate_unsuccessful_num(matches, ps.name)
                    ps.add_unsuccessful(num_unsuccessful)
                
                ps.calculate_round_bonuses(game_state, successful_match_dict[ps.name])
            else:
                if ps.role == "The Leech" or ps.role == "The Team Player":
                    ps.clear_prev_match()


        # Reveal role of current leader
        announce_role(game_state)

        game_state.round += 1


    # All rounds have finished, tally final scores
    for ps in player_states:
        ps.final_bonuses(game_state)

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
        self.public_roles = set() # set of publically revealed players
        self.public_scores = [0] * n # public scores of each player, in the same order as self.players
        self.player_dict = {val : i for i, val in enumerate(players)}   # maps {player name string : corresponding index in players, roles, and public_scores}
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
    def on_game_init(self):
        self.role = "Default"

    def final_bonuses(self, game_state):
        return 0

class SlackerPlayer(Player):
    ''' 
    Makes both SlackerPlayer and matched partner gain 0 points during a match. Adds 1 point per match
    to themselves at the end of the game.
    '''

    def on_game_init(self):
        self.role = "The Slacker"
        self.successful_pairings = 0

    def calculate_round_bonuses(self, game_state, match_name):
        my_index = game_state.player_dict[self.name]
        match_index = game_state.player_dict[match_name]
        game_state.public_scores[my_index] -= 1
        game_state.public_scores[match_index] -= 1

        self.successful_pairings += 1

    def final_bonuses(self, game_state):
        my_index = game_state.player_dict[self.name]
        game_state.public_scores[my_index] += self.successful_pairings
        return game_state.public_scores[my_index]

class ThiefPlayer(Player):
    ''' 
    Steals one point from their partner, except when the other player is a slacker or
    a snitch.
    '''

    def on_game_init(self):
        self.role = "The Thief"

    def calculate_round_bonuses(self, game_state, match_name):
        my_index = game_state.player_dict[self.name]
        match_index = game_state.player_dict[match_name]
        match_role = game_state.roles[match_index]    #set enemy score

        if (match_role != "slacker") and (match_role != 'thief'):
            game_state.public_scores[match_index] -= 1  #set enemy score
            game_state.public_scores[my_index] += 1   #set own score


    def final_bonuses(self, game_state):
        my_index = game_state.player_dict[self.name]
        return game_state.public_scores[my_index]

class SnitchPlayer(Player):
    ''' 
    Steals 2 points if paired with either the slacker or thief
    '''

    def on_game_init(self):
        self.role = "The Snitch"

    def calculate_round_bonuses(self, game_state, match_name):
        my_index = game_state.player_dict[self.name]
        match_index = game_state.player_dict[match_name]
        match_role = game_state.roles[match_index]    #set enemy score

        if (match_role == "slacker") or (match_role == 'thief'):
            game_state.public_scores[match_index] -= 2  #set enemy score
            game_state.public_scores[my_index] += 2   #set own score


    def final_bonuses(self, game_state):
        my_index = game_state.player_dict[self.name]
        return game_state.public_scores[my_index]

class CSGodPlayer(Player):
    ''' 
    Starts with 3 points
    '''

    def on_game_init(self):
        self.role = "The CS God"

    def final_bonuses(self, game_state):
        my_index = game_state.player_dict[self.name]
        game_state.public_scores[my_index] += 3
        return game_state.public_scores[my_index]

class FlakePlayer(Player):
    ''' 
    When successfully paired, gets one bonus point per player that
    unsuccessfully tried to pair with them or lose one point
    if no other players.
    '''

    def on_game_init(self):
        self.role = "The Flake"
        self.unsuccessful_pairings = 0

    def add_unsuccessful(self, x):
        self.unsuccessful_pairings += x

    def calculate_round_bonuses(self, game_state, match_name):
        my_index = game_state.player_dict[self.name]
        if self.unsuccessful_pairings == 0:
            game_state.public_scores[my_index] -= 1
        else:
            game_state.public_scores[my_index] += self.unsuccessful_pairings

        self.unsuccessful_pairings = 0

    def final_bonuses(self, game_state):
        my_index = game_state.player_dict[self.name]
        return game_state.public_scores[my_index]

class GossipPlayer(Player):
    ''' 
    Sees their project partner’s role when in a project team.
    (dm’ed after announcement of the matching period results,
    during the following period)
    '''

    def on_game_init(self):
        self.role = "The Gossip"

    def calculate_round_bonuses(self, game_state, match_name):
        match_index = game_state.player_dict[match_name]
        match_role = game_state.roles[match_index]
        print("Narrator, please let " + self.name + " know their partner this round is the " + match_role)

    def final_bonuses(self, game_state):
        my_index = game_state.player_dict[self.name]
        return game_state.public_scores[my_index]

class LeechPlayer(Player):
    ''' 
    Receives half of their project partner’s points (rounded down) when
    successfully paired with the same person 2 weeks in a row.
    '''

    def on_game_init(self):
        self.role = "The Leech"
        self.previous_match = None
        
    def clear_prev_match(self):
        self.previous_match = None

    def calculate_round_bonuses(self, game_state, match_name):
        my_index = game_state.player_dict[self.name]
        match_index = game_state.player_dict[match_name]

        if match_name == self.previous_match:
            match_half = int(game_state.public_scores[match_index] / 2)
            game_state.public_scores[my_index] += match_half   #set own score
        else:
            self.previous_match = match_name

    def final_bonuses(self, game_state):
        my_index = game_state.player_dict[self.name]
        return game_state.public_scores[my_index]

class TeamPlayer(Player):
    ''' 
    Gives one point to themselves and their project partner when
    successfully paired with the same person 2 weeks in a row.
    '''

    def on_game_init(self):
        self.role = "The Team Player"
        self.previous_match = None
        
    def clear_prev_match(self):
        self.previous_match = None

    def calculate_round_bonuses(self, game_state, match_name):
        my_index = game_state.player_dict[self.name]
        match_index = game_state.player_dict[match_name]

        if match_name == self.previous_match:
            game_state.public_scores[match_index] += 1   #set partner's score
            game_state.public_scores[my_index] += 1   #set own score
        else:
            self.previous_match = match_name

    def final_bonuses(self, game_state):
        my_index = game_state.player_dict[self.name]
        return game_state.public_scores[my_index]

class SchadenfreuderPlayer(Player):
    ''' 
    Receives a random enemy and receives one point if their enemy
    fails to find a project match.
    '''

    def on_game_init(self):
        self.role = "The Schadenfreuder"

    def setEnemy(self, schadenfreuder_name):
        self.enemy = schadenfreuder_name

    def calculate_round_bonuses(self, game_state, match_name):
        my_index = game_state.player_dict[self.name]
        if match_name == self.enemy:
            game_state.public_scores[my_index] += 1

    def final_bonuses(self, game_state):
        my_index = game_state.player_dict[self.name]
        return game_state.public_scores[my_index]

class HackerPlayer(Player):
    ''' 
    Swaps their points with their project partner’s points when in a project team.
    '''

    def on_game_init(self):
        self.role = "The Hacker"

    def calculate_round_bonuses(self, game_state, match_name):
        my_index = game_state.player_dict[self.name]
        match_index = game_state.player_dict[match_name]
        my_points_tmp = game_state.public_scores[my_index]

        game_state.public_scores[my_index] = game_state.public_scores[match_index]    #set own score
        game_state.public_scores[match_index] = my_points_tmp    #set enemy score


    def final_bonuses(self, game_state):
        my_index = game_state.player_dict[self.name]
        return game_state.public_scores[my_index]



if __name__ == '__main__':
    players = init_game()
    roles = generate_roles((len(players)))
    announce_init_roles(players, roles)
    game_state = State(len(players), players, roles)
    player_states = init_player_states(game_state)
    run_game(game_state, player_states)
