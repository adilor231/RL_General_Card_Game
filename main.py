import model
import cardgame as CardGame
import agent as Agent
import Deck
import debug
import time
import numpy as np

N_PLAYERS = 2
POLICIES = [Agent.Q_NOT_LEARN, Agent.RANDOM]
DECK = Deck.ITALIAN_DECK
TRUMP_SUIT = "Coins"
LIST_PAIRS = Deck.create_briscola_order(TRUMP_SUIT)
ORDER =  Deck.Order(DECK, LIST_PAIRS) #Deck.ORDER_TAROT
POINTS = Deck.create_briscola_points() #Deck.POINTS_TAROT

N_SUPERROUNDS = 50

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

if __name__ == '__main__':
    game = CardGame.Game(DECK, ORDER, POLICIES, POINTS, trump_suit=TRUMP_SUIT)
    time_old = time.time()
    score_old = 0
    scores = []
    for i in range(N_SUPERROUNDS):
        score_new = train(game)
        scores.append(score_new)
        game.total_reset()
        time_new = time.time()
        print(i, ": ",time_new-time_old, "|", score_new-score_old, "|", score_new)
        time_old = time_new
        score_old = score_new
    debug.plot_moving(scores, lag=10)
    pass