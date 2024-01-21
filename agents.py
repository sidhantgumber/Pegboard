from abc import abstractmethod
import random
import copy
import pentago
import time
# ---------------------------------------------------------------------------
# JL Popyack, ported to Python, May 2019, updated Nov 2021. v2 Nov 29, 2021
# Ehsan Khosroshahi, updated Nov 2023.
# Sidhant Gumber, updated Nov 2023.
# ---------------------------------------------------------------------------

#-----------------------------------------------------------------------
# Names for common abbreviations
#-----------------------------------------------------------------------
descr = {
  "b": "Black",
  "w": "White",
}

#--------------------------------------------------------------------------------
# Contains elements for abstract class players defining an agent that can play the 
# game. Each agents is an extention of this class.
# A human agent has been implemented for you as an example that gets the player's  
# move typed in at the console by the player, where either it is accepted as a  
# valid move, or the player is asked again to enter a valid move.
#--------------------------------------------------------------------------------




class Player:
    WINNING_SCORE = 1000000
    # Set the losing score to a low value beyond the normal heuristic range
    LOSING_SCORE = -1000000
    def __init__ (self,player_number,token, depth_limit, time_limit):
        self.INFINITY = 10000
        self.player_number = player_number
        self.depth_limit = depth_limit
        self.time_limit = time_limit
        
        if token.lower() in ["b","w"]:
            self.token = token.lower()

    def __str__ (self):
        return self.player_number + " is a " + self.__class__.__name__.lower() +  " agent and plays " + descr[self.token].lower() + " tokens."
    
    def player_type(self):
        return self.__class__.__name__
    
    def win(self,board):
    # Check for winner beginning with each element.
    # It is possible that both players have multiple "wins"	
        numWins = 0
        for i in range(board.BOARD_SIZE):
            for j in range(board.BOARD_SIZE):
                if board.board[i][j] == self.token:
                    # win in row starting with board[i][j]
                    if j<=1:
                        count = 5
                        k = j
                        fiveInRow = True
                        while count>0 and fiveInRow:
                            fiveInRow = ( board.board[i][k]==self.token )
                            k = k + 1
                            count = count - 1
                        if fiveInRow:
                            numWins = numWins + 1
                    # win in col starting with board[i][j]
                    if i<=1:
                        count = 5
                        k = i
                        fiveInRow = True
                        while count>0 and fiveInRow:
                            fiveInRow = ( board.board[k][j]==self.token )
                            k = k + 1
                            count = count - 1
                        if fiveInRow:
                            numWins = numWins + 1
                    # win in main diag starting with board[i][j]
                    if i<=1 and j<=1:
                        count = 5
                        m = i
                        n = j
                        fiveInRow = True
                        while count>0 and fiveInRow:
                            fiveInRow = ( board.board[m][n]==self.token )
                            m = m + 1
                            n = n + 1
                            count = count - 1
                        if fiveInRow:
                            numWins = numWins + 1
                    # win in off diag starting with board[i][j]
                    if i<=1 and j>=4 :
                        count = 5
                        m = i
                        n = j
                        fiveInRow = True
                        while count>0 and fiveInRow:
                            fiveInRow = ( board.board[m][n]==self.token )
                            m = m + 1
                            n = n - 1
                            count = count - 1
                        if fiveInRow:
                            numWins = numWins + 1

        return (numWins>0)

    def explain_move(self,move, board):
        gameBlock = int(move[0])  # 1,2,3,4
        position = int(move[2])   # 1,2,3,4,5,6,7,8,9
        rotBlock = int(move[4])   # 1,2,3,4
        direction = move[5]       # L,R

        G = board.GRID_SIZE
        i = (position-1)//G + G*((gameBlock-1)//2) ;
        j = ((position-1)%G) + G*((gameBlock-1)%2) ;

        print("Placing " + self.token + " in cell [" + str(i) + "][" + str(j) +  \
              "], and rotating Block " + str(rotBlock) +  \
              (" Left" if direction=="L" else " Right."))

    def sg3824_h(self, board, token):

        score = 0  # Initialize the score

        # Advanced line scoring
        score += self.advanced_line_scoring(board, token)

        # Twist potential
        score += self.evaluate_twist_potential(board, token)

        # Mobility
        score += self.evaluate_mobility(board, token)

        return score

    def advanced_line_scoring(self, board, token):
        score = 0
        # Check each row, column, and diagonal for scoring patterns
        for i in range(board.BOARD_SIZE):
            score += self.score_line(board.board[i], token)  # Check row
            score += self.score_line([board.board[j][i] for j in range(board.BOARD_SIZE)], token)  # Check column

        # Score diagonals
        for diag in board.get_diagonals():
            score += self.score_line(diag, token)

        return score

    def score_line(self, line, token):
        score = 0
        # Define scoring for different patterns
        patterns = {
            '5': 10000,  # Five in a row
            '4': 1000,  # Four in a row
            '3': 100,  # Three in a row
            '2': 10,  # Two in a row
            '1': 1,  # Single token
        }
        consecutive_count = 0
        for element in line:
            if element == token:
                consecutive_count += 1
            elif element != '.':
                # If there's a blocking token, reset the count
                consecutive_count = 0
            # Get the pattern score and reset count
            score += patterns.get(str(consecutive_count), 0)
            if element != token:
                consecutive_count = 0

        return score

    def evaluate_twist_potential(self, board, token):
        score = 0
        for game_block in range(1, 5):
            # Simulate a left twist
            left_twist = board.rotate_left(game_block)
            score = max(score, self.advanced_line_scoring(left_twist, token))

            # Simulate a right twist
            right_twist = board.rotate_right(game_block)
            score = max(score, self.advanced_line_scoring(right_twist, token))

        return score

    def evaluate_mobility(self, board, token):
        score = 0
        moves = board.get_moves()
        for move in moves:
            # Simulate the move
            new_board = board.apply_move(move, token)
            # Check the line scoring after move
            score += self.advanced_line_scoring(new_board, token)

        return score



    @abstractmethod
    def get_move(self, state):
        raise NotImplementedError



class Human(Player):

    def __init__(self,player_number,token, depth_limit, time_limit):
        super().__init__(player_number,token, depth_limit, time_limit)
    
    def get_move(self, board):
        moveList = board.get_moves()
        move = None
        
        ValidMove = False
        while(not ValidMove):
            hMove = input(self.player_number +': Input your move (block/position block-to-rotate direction): ')

            for move in moveList:
                if move == hMove:
                    ValidMove = True
                    break

            if(not ValidMove):
                print('Invalid move.  ')

        return hMove


class Random(Player):
    def __init__(self,player_number,token, depth_limit, time_limit):
        super().__init__(player_number,token, depth_limit, time_limit)

    def get_move(self, board):
        # Get the list of all legal moves from the current board state
        moveList = board.get_moves()

        # Select a move at random from the moveList
        selected_move = random.choice(moveList)

        return selected_move
class Minimax(Player):
    def __init__(self,player_number,token, depth_limit, time_limit):
        super().__init__(player_number,token, depth_limit, time_limit)

    def minimax(self, board, depth, maximizing_player):
        # print(f"Minimax called at depth {depth} for {'maximizing' if maximizing_player else 'minimizing'} player")

        if depth == 0 or self.win(board):  # If we are at the depth limit or a terminal state is detected
            return self.sg3824_h(board, self.token), None

        if maximizing_player:  # Maximizing player (AI)
            max_eval = float('-inf')
            best_move = None
            for move in board.get_moves():
                new_board = board.apply_move(move, self.token)  # Apply the move
                eval, _ = self.minimax(new_board, depth - 1, False)  # Recurse for the minimizing player
                if eval > max_eval:  # If the move is better than the current best, update max_eval and best_move
                    max_eval = eval
                    best_move = move
            return max_eval, best_move
        else:  # Minimizing player (opponent)
            min_eval = float('inf')
            best_move = None
            opponent_token = 'b' if self.token == 'w' else 'w'
            for move in board.get_moves():
                new_board = board.apply_move(move, opponent_token)  # Apply the move for the opponent
                if self.win(new_board):  # Directly check for opponent win
                    return float('-inf'), None  # Worst case for maximizer
                eval, _ = self.minimax(new_board, depth - 1, True)  # Recurse for the maximizing player
                if eval < min_eval:  # If the move is worse for the maximizing player, update min_eval and best_move
                    min_eval = eval
                    best_move = move
            return min_eval, best_move

    def get_move(self, board):
        start_time = time.time()
        _, best_move = self.minimax(board, self.depth_limit, True)  # Start the minimax algorithm
        end_time = time.time()
        print(f"Minimax Search Time: {end_time - start_time} seconds")
        return best_move

class Alphabeta(Player):
    def __init__(self,player_number,token, depth_limit, time_limit):
        super().__init__(player_number,token, depth_limit, time_limit)

    def alphabeta(self, board, depth, alpha, beta, maximizing_player):
        if depth == 0 or self.win(board):
            return self.sg3824_h(board, self.token), None

        if maximizing_player:
            max_eval = float('-inf')
            best_move = None
            for move in board.get_moves():
                new_board = board.apply_move(move, self.token)
                eval, _ = self.alphabeta(new_board, depth - 1, alpha, beta, False)
                if eval > max_eval:
                    max_eval = eval
                    best_move = move
                alpha = max(alpha, eval)
                if alpha >= self.WINNING_SCORE:  # Early termination for a winning move
                    return alpha, best_move
                if beta <= alpha:
                    break
            return max_eval, best_move
        else:
            min_eval = float('inf')
            best_move = None
            opponent_token = 'b' if self.token == 'w' else 'w'
            for move in board.get_moves():
                new_board = board.apply_move(move, opponent_token)
                eval, _ = self.alphabeta(new_board, depth - 1, alpha, beta, True)
                if eval < min_eval:
                    min_eval = eval
                    best_move = move
                beta = min(beta, eval)
                if beta <= self.LOSING_SCORE:  # Early termination for a losing move
                    return beta, best_move
                if beta <= alpha:
                    break
            return min_eval, best_move

    def get_move(self, board):
        # Determine the number of empty cells to estimate the game phase
        start_time = time.time()
        empty_cells = sum(row.count('.') for row in board.board)

        # Adjust the depth dynamically based on the number of empty cells
        if empty_cells > (board.BOARD_SIZE ** 2) // 2:
            # Early game, more empty cells, shallower search
            current_depth = min(self.depth_limit, 1)
        elif empty_cells > board.BOARD_SIZE:
            # Midgame, moderate number of empty cells, medium search depth
            current_depth = self.depth_limit // 2

            # USE THIS LIMIT IF SEARCH STARTS TAKING A LOT OF TIME AGAINST HUMAN AGENTS
            #current_depth = min(self.depth_limit, 1)
        else:
            # Endgame, fewer empty cells, deeper search
            current_depth = self.depth_limit

        # Proceed with the Alpha-beta search with the adjusted depth
        _, best_move = self.alphabeta(board, current_depth, float('-inf'), float('inf'), True)
        end_time = time.time()
        print(f"Alpha-Beta Search Time: {end_time - start_time} seconds")

        return best_move

class Minimax_mcts(Player):

    def __init__(self, player_number, token, depth_limit, time_limit, num_playouts=100):
        super().__init__(player_number, token, depth_limit, time_limit)
        self.num_playouts = num_playouts
      # self.alphabeta_agent = Alphabeta(player_number, token, depth_limit, time_limit)
        self.minimax_agent = Minimax(player_number, token, depth_limit, time_limit)

    def minimax_for_mcts(self, board, top_n=8):
        moves = board.get_moves()
        best_moves = []

        # Evaluate each possible move using the heuristic
        for move in moves:
            new_board = board.apply_move(move, self.token)
            score = self.sg3824_h(new_board, self.token)
            best_moves.append((score, move))

        # Sort the moves by the heuristic score and select the top 'n' moves
        best_moves.sort(reverse=True)
        best_moves = best_moves[:top_n]

        # For the top 'n' moves, look one step ahead with Alpha-beta search for the opponent's response
        final_moves = []
        for score, move in best_moves:
            new_board = board.apply_move(move, self.token)
            # Perform Alpha-beta/Minimax search with a depth of 1, which is effectively the opponent's next move
            # NOTE: For testing purposes I tried MCTS with both alpha beta and minimax but for the final submission I have left only MCTS with minimax implementation as was given in the question
            # opponent_score, _ = self.alphabeta_agent.alphabeta(new_board, 1, float('-inf'), float('inf'), False)
            opponent_score, _ = self.minimax_agent.minimax(new_board, 1, False)

            final_moves.append((opponent_score, move))

        # Sort the moves based on the opponent's score (we negate it because we want the lowest score for the opponent)
        final_moves.sort(key=lambda x: -x[0])

        # Return the top 'n' moves for the MCTS playouts
        return [move for _, move in final_moves[:top_n]]
    def playout(self, board, token):
        # Play a random game starting with the given board and token
        current_token = token
        while True:
            moves = board.get_moves()
            if not moves or board.is_full():  # No moves left or the board is full
                break
            move = random.choice(moves)
            board = board.apply_move(move, current_token)
            if self.win(board):
                return current_token
            current_token = 'b' if current_token == 'w' else 'w'  # Switch player
        return None  # No winner

    def mcts(self, board):
        # Perform the Monte Carlo Tree Search from the current board state
        start_time = time.time()
        best_moves = self.minimax_for_mcts(board)  # Get the best moves from minimax
        best_move = None
        best_score = float('-inf')
        for move in best_moves:
            wins = 0
            for _ in range(self.num_playouts):
                new_board = board.apply_move(move, self.token)
                winner = self.playout(new_board, self.token)
                if winner == self.token:
                    wins += 1
            if wins > best_score:
                best_score = wins
                best_move = move
        end_time = time.time()
        print("Search time: ", (end_time-start_time), "seconds")
        return best_move

    def get_move(self, board):

        return self.mcts(board)


# CODE FOR UNIT TESTING:


# class MockBoard:
#     BOARD_SIZE = 6
#
#     board = [
#
#         ['.', '.', '.', 'w', 'w', 'w'],
#
#         ['.', '.', '.', '.', '.', '.'],
#
#         ['.', '.', 'b', 'b', 'b', 'b'],
#
#         ['.', '.', '.', '.', '.', '.'],
#
#         ['w', 'w', '.', '.', '.', '.'],
#
#         ['.', '.', '.', '.', '.', '.'],
#
#     ]
#
#     def get_diagonals(self):
#         # Simulate getting all diagonals (not fully implemented)
#
#         return [
#
#             [self.board[i][i] for i in range(self.BOARD_SIZE)],  # Main diagonal
#
#             [self.board[i][self.BOARD_SIZE - i - 1] for i in range(self.BOARD_SIZE)]  # Anti-diagonal
#
#         ]


# pb = pentago.PentagoBoard(board =
#
#         ['.', '.', 'w', 'w', 'w', 'w',
#
#         '.', '.', '.', '.', '.', '.',
#
#         '.', '.', 'b', 'b', 'b', 'b',
#
#         '.', '.', '.', '.', '.', '.',
#
#         'w', 'w', '.', '.', '.', '.',
#
#         '.', '.', '.', '.', '.', '.'],
#
#     )

# Test the heuristic function with the mock board

# ... MockBoard and Player class definitions ...

# Create a player instance with dummy values for the constructor arguments
# player = Player(player_number="1", token='w', depth_limit=3, time_limit=30)
#
#
# print(str(pb))
#
# heuristic_w = player.sg3824_h(pb, 'w')
#
# heuristic_b = player.sg3824_h(pb, 'b')
#
# print(heuristic_w, heuristic_b)

    