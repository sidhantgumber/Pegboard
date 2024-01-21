import copy
import time
# ---------------------------------------------------------------------------
# JL Popyack, ported to Python, May 2019, updated Nov 2021. v2 Nov 29, 2021
# Ehsan Khosroshahi, updated Nov 2023.
# Sidhant Gumber, updated Nov 2023.
# ---------------------------------------------------------------------------
descr = {
  "b": "Black",
  "w": "White",
}

class Game:

    def __init__(self, initial_board, player1, player2):
        self.initial_board =initial_board
        self.players = [player1, player2]

    def play(self, output=False):
        pb = self.initial_board
        game_over = False
        currentPlayer = 0
        print(pb)
        if (output):
            timestamp = time.time()
            f = open("transcript_"+ str(timestamp) + ".txt","w")
            f.write("\n" + str(self.players[0]) + "\n" + str(self.players[1]) + "\n")

        numEmpty = pb.empty_cells
        while( not game_over ):
            move = self.players[currentPlayer].get_move(pb)
            if move == "exit":
                break
            print( self.players[currentPlayer].player_number + "'s move (" + self.players[currentPlayer].player_type().lower() + " agent): " + move)
            if (output):
                f.write(pb.to_string() + "\t" + move + "\n")
            # f.write(pb.toString() + "\t" + move + "\n")
            new_board = copy.deepcopy(pb)
            new_board = new_board.apply_move(move,self.players[currentPlayer].token)
            self.players[currentPlayer].explain_move(move, pb) 
            print(new_board)
            numEmpty = numEmpty - 1
            
            win0 = self.players[0].win(new_board)
            win1 = self.players[1].win(new_board)
            game_over = win0 or win1 or numEmpty==0
            
            currentPlayer = 1 - currentPlayer
            pb = copy.deepcopy(new_board)
        if not game_over:  # Human player requested "exit"
            print("Exiting game.")
        elif (win0 and win1):
            print("Game ends in a tie (multiple winners).")
        elif win0:
            print(self.players[0].player_number + " (" + self.players \
            [0].player_type().lower() + " agent) playing " + descr \
            [self.players[0].token].lower() + " wins!!")
        elif win1:
            print(self.players[1].player_number + " (" + self.players \
            [1].player_type().lower() + " agent) playing " + descr \
            [self.players[1].token].lower() + " wins!!")
        elif numEmpty==0:
            print("Game ends in a tie (no winner).")
        if (output):
            f.write(pb.to_string() + "\t\n")
            f.close()


