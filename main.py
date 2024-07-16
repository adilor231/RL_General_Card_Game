import model
import cardgame as CardGame
import agent as Agent
import Deck
import debug
import time
import numpy as np
import argparse

def sum_list(arr, n):
    temp = [0 for _ in range(len(arr))]
    for i in range(len(arr)):
        if i == 0:
            temp[i] = arr[i]
        else:
            temp[i] = arr[i] + temp[i-1]
    for i in range(len(temp)):
        temp[i] = temp[i]/n
    return temp

def train(game: CardGame.Game, n_rounds = 100):
    for i in range(n_rounds):
        #if i%1==0: print(i)
        game.start_game()
        winper0 = sum_list(game.wins[0], i+1)
        winper1 = sum_list(game.wins[1], i+1)
        draws = sum_list(game.draws, i+1)
        #if i > 0.99*n_rounds: debug.plot(winper0, winper1, draws)
    if game.players[1].policy==Agent.RANDOM: 
        if game.players[0].policy==Agent.Q: game.players[0].agent.model.save()
    else:
        if winper0[-1]>=winper1[-1]:
            if game.players[0].policy==Agent.Q: game.players[0].agent.model.save()
        else:
            if game.players[1].policy==Agent.Q: game.players[1].agent.model.save()   
    return (winper0[-1])

def test(training, n_rounds, n_superrounds):

    # Arguments

    N_PLAYERS = 2   # Only 2 players supported at the moment
    POLICIES = []
    for char in training:
        if char == "Q":
            POLICIES.append(Agent.Q)
        elif char == "q":
            POLICIES.append(Agent.Q_NOT_LEARN)
        elif char == "R":
            POLICIES.append(Agent.RANDOM)
        elif char == "I":
            POLICIES.append(Agent.INPUT)
        else:
            raise ValueError("Policy character not supported.")
    N_ROUNDS = n_rounds
    N_SUPERROUNDS = n_superrounds
    if Agent.INPUT in POLICIES:
        PRINT_FLAG = 1
        N_ROUNDS = 1
        N_SUPERROUNDS = 1
    else:
        PRINT_FLAG = 0

    # Deck construction

    DECK = Deck.ITALIAN_DECK
    TRUMP_SUIT = "Coins"
    LIST_PAIRS = Deck.create_briscola_order(TRUMP_SUIT)
    ORDER =  Deck.Order(DECK, LIST_PAIRS) #Deck.ORDER_TAROT
    POINTS = Deck.create_briscola_points() #Deck.POINTS_TAROT

    ###

    game = CardGame.Game(DECK, ORDER, POLICIES, POINTS, trump_suit=TRUMP_SUIT, print_flag=PRINT_FLAG)
    time_old = time.time()
    score_old = 0
    scores = []
    for i in range(N_SUPERROUNDS):
        score_new = train(game, n_rounds=N_ROUNDS)
        scores.append(score_new)
        game.total_reset()
        time_new = time.time()
        if not(PRINT_FLAG): print(i, ": ",time_new-time_old, "|", score_new-score_old, "|", score_new)
        time_old = time_new
        score_old = score_new
    if not(PRINT_FLAG) and (int(N_SUPERROUNDS/5)>0): debug.plot_moving(scores, lag=int(N_SUPERROUNDS/5))
    pass

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--training", type=str, help="Choose between: QQ (training Q-table vs Q-table), QR (training Q-table vs Random), qI (Q-table without training vs Input), qR (Q-table without training vs Random)", default = "QQ")
    parser.add_argument("--n_rounds", type=int, help="Number of rounds in a superround", default=100)
    parser.add_argument("--n_superrounds", type=int, help="Number of superrrounds. After each superround, if training, the Q-table gets saved.", default=100)

    args = parser.parse_args()

    test(
        training=args.training,
        n_rounds=args.n_rounds,
        n_superrounds=args.n_superrounds
    )

if __name__ == '__main__':
    main()