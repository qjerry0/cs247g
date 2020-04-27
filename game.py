import random

# CONSTANTS
MIN_PLAYERS = 3             # min player count
MAX_PLAYERS = 8             # max player count
MIN_ROUND_NUM = 4           # min number of rounds of matching
MAX_ROUND_NUM = 6           # max number of rounds of matching
MIN_MESSAGE_TIMER = 90      # min time to message, in sec
MAX_MESSAGE_TIMER = 120     # max time to message, in sec
ROLES_34 = ["team_player", "schadenfreuder", "slacker", "thief", "snitch", "flake", "leech"]    # role set, 3-4
ROLES_5 = ["slacker", "thief", "snitch", "god", "leech", "team_player", "schadenfreuder"],      # role set, 5
ROLES_6 = ["slacker", "thief", "snitch", "god", "flake", "gossip", "leech", "team_player",      # role set, 6+
            "schadenfreuder", "hacker"]

def initGame():
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

def generateRoles(n):
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

def initPlayerStates(game_state):
    ''' Prompts narrator to publically announce a player's role, if necessary given the game state
        @param game_state   The game state
        @return list        A list of Player objects
    ''' 
    #TODO: once real players are created, change this to use them
    players = []
    for p, r in zip(game_state.players, game_state.roles):
        players.append(DefaultPlayer(p, r))
    return players

def announceRoles(players, roles):
    ''' Prompts narrator to tell players their role assignments
        @param players      The players' names
        @param roles        The players' roles, in the same order
    ''' 
    for p, r in zip(players, roles):
        print("Narrator, please let %s know that they are: %s" %(p, r))

def announceMatches(players, matches):
    ''' Prompts narrator to tell players their preferences in the reveal phase
        @param players      The players' names
        @param roles        The players' matches, in the same order
    ''' 
    # TODO: implement this, figure out some fun/interesting way to announce
    pass

def announceRole(game_state):
    ''' Prompts narrator to publically announce a player's role, if necessary given the game state
        @param game_state   The game state
    ''' 
    # TODO: implement this
    pass

def inputMatches(players):
    ''' Prompts narrator to input the matches of each player after the matching phase
        @param players  The players in the game
        @return list    The intended matches of the players, in the same order
    '''
    matches = []
    for p in players:
        while True:
            match = input("Please input the student %s picked: " % p)
            if match not in players:
                print("You've made a typo, please input one of the players")
            else:
                break
        matches.append(match)
    return matches

def runGame(game_state, player_states):
    ''' Core loop of the game, this runs throughout the game.
        @param game_state       The initial state of the game, with players and role assignments
        @param player_states    The initial states of each player
    ''' 
    while game_state.round < game_state.max_rounds:
        
        # Matching/messaging phase
        print("Narrator, please say: ")
        round_print = game_state.round + 1
        print(  "It is the start of week %d! Students, you have %d seconds to find a project \
                partner by messaging them!" % (round_print, game_state.round_times[game_state.round]))
        # TODO: implement delay/prompts for narrator during the matching phase, e.g. 30 sec warning (please message me your matches!)
        matches = inputMatches(game_state.players)
        
        # Matching announce phase
        announceMatches(players, matches)
        for ps in player_states:
            ps.onMatchesRevealed(game_state)
        
        # Role reveal phase
        announceRole(game_state)
        for ps in player_states:
            ps.onRoleRevealed(game_state)

        game_state.round += 1

    # All rounds have finished, tally final scores
    final_scores = []
    for ps in player_states:
        final_scores.append(ps.onGameCompletion(game_state))

    rankings = [(p, fs) for fs , p in sorted(zip(final_scores, players))]
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

    def onGameInit(self, game_state):
        ''' This will be called upon initialization of the game. Implement for each player.
        @param game_state   The current game state
        '''
        raise NotImplementedError

    def onMatchesRevealed(self, game_state):
        ''' This will be called upon narrator revealing matches for the round. Implement for each player.
        @param game_state   The current game state
        '''
        pass

    def onRoleRevealed(self, game_state):
        ''' This will be called upon narrator revealing the role for the round. Implement for each player.
        @param game_state   The current game state
        '''
        pass

    def onGameCompletion(self, game_state):
        ''' This will be called upon the completion of the final round. Implement for each player.
        @param game_state   The current game state
        '''
        raise NotImplementedError


class DefaultPlayer(Player):
    ''' 
    A default player with no special role or ability. Always scores 0 at the end of the game.
    '''
    def onGameInit(self, player_info):
        pass

    def onGameCompletion(self, game_state):
        return 0

if __name__ == '__main__':
    players = initGame()
    roles = generateRoles((len(players)))
    announceRoles(players, roles)
    game_state = State(len(players), players, roles)
    player_states = initPlayerStates(game_state)
    runGame(game_state, player_states)