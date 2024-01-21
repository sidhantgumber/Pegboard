import game
import pentago
import sys
import getopt
from ec_sg3824 import ec_sg3824
import agents


# ---------------------------------------------------------------------------
# Pentago
# This program is designed to play Pentago.  It will allow the user to play a game 
# against the machine, or allow the machine to play against itself for purposes of 
# learning to improve its play.  All 'learning'code has been removed from this program.
#
# Pentago is a 2-player game played on a 6x6 grid subdivided into four
# 3x3 subgrids.  The game begins with an empty grid.  On each turn, a player
# places a token in an empty slot on the grid, then rotates one of the
# subgrids either clockwise or counter-clockwise. Each player attempts to
# be the first to get 5 of their own tokens in a row, either horizontally,
# vertically, or diagonally.
# 
# 
# JL Popyack, ported to Python, May 2019, updated Nov 2021. v2 Nov 29, 2021
# Ehsan Khosroshahi, updated Nov 2023.
# ---------------------------------------------------------------------------

# --------------------------------------------------------------------------------
# Game Setup:
# The player types (human/computer) are received through command line argument; the 
# first is the player to go first, and the first player token is always white, and 
# the second is black. 
# Also, you can allow the game to begin with a particular initial state, again with 
# Player 1 to play first.
# --------------------------------------------------------------------------------

# --------------------------------------------------------------------------------
#  MAIN PROGRAM
# --------------------------------------------------------------------------------
if __name__ == "__main__":
    # --------------------------------------------------------------------------------
    #  To run program:
    #    python3 main.py <player1> <player2> <arguments>
    #  
    #  This will lead to a game with 2 players which each player is human or AI agent.
    #
    #  To begin the game at a particular initial state expressed as a 36-character
    #  string linsting the board elements in row-major order (Player 1 to play first):
    #   python3 main.py <player1> <player2> -b "w.b.bw.w.b.wb.w..wb....w...bw.bbb.ww"
    #  This is useful for mid-game testing.
    #
    #  A transcript of the game can be produced with -o option with name beginning 
    # "transcript_" and ending with a timestamp value.  The file contains player 
    # info, followed by lines containing each state as a 36-character string, 
    # followed by the move made.
    # --------------------------------------------------------------------------------

    
    output = False
    time_limit = 100 # default value
    depth_limit = 1 # default value
    board = pentago.PentagoBoard()
    if len(sys.argv) >= 2 :
        agent1 = sys.argv[1].capitalize()
        agent2 = sys.argv[2].capitalize()
    else:
        print("In the arguments, indicate two player types (e.g., human random etc.)") 
        sys.exit()
         
    try:
        opts, args = getopt.getopt(sys.argv[3:],"ob:t:d:",["output", "board=","time=","depth="])
    except getopt.GetoptError as err:
        # print help information and exit:
        print(err)  # will print something like "option -a not recognized"
        sys.exit(2)
        
    for opt, arg in opts:
        if opt in ("-b", "--board"):
            initialState = arg
            board = pentago.PentagoBoard(arg)
        elif opt in ("-t", "--time"):
            if arg.isdigit():
                time_limit = arg
            else:
                print("Time argument should be a digit!")
                sys.exit(2)
        elif opt in ("-d", "--depth"):
            if arg.isdigit():
                depth_limit = arg
            else:
                print("Depth argument should be a digit!")
                sys.exit(2)
        elif opt in ("-o", "--output"):
            output = True
        else:
            print("Unknown option, " + opt + " " + arg )

    try:
        print('agents.'+ agent1 + '("Player 1", "W", ' + str(depth_limit) + ', ' + str(time_limit) + ')')
        player1 = eval('agents.'+ agent1 + '("Player 1", "W", ' + str(depth_limit) + ', ' + str(time_limit) + ')')
        player2 = eval('agents.'+ agent2 + '("Player 2", "B", ' + str(depth_limit) + ', ' + str(time_limit) + ')')
    except:
        print("Unknown agent(s)! Some options are Human and Random.")
        print("Make sure the spelling is correct.")
        sys.exit(2)
        
    print( "\n-------------------\nWelcome to Pentago!\n-------------------" )
    print("\n" + str(player1) + "\n" + str(player2) + "\n")

    # -----------------------------------------------------------------------
    # Play game, alternating turns until a win encountered, board is full
    # with no winner, or human user types "exit".
    # -----------------------------------------------------------------------

    agent = ec_sg3824(player_number="1", token='w', time_limit=100)

    game = game.Game(board, player1, player2)
    game.play(output)