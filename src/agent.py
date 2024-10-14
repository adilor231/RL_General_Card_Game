import torch
import random
import time
import numpy as np
from collections import deque
from model import Linear_QNet, QTrainer
from itertools import chain
import deck
import copy

BATCH_SIZE = 10
MAX_MEMORY = 10_000_000
LONG_MEMORY_FLAG = 1

POT_FLAG = 0
ORDER_INPUT_FLAG = 1
ORDER_DRAWN_FLAG = 1

Q = 0
INPUT = 1
RANDOM = 2
Q_NOT_LEARN = 3

LR = 0.001
GAMMA = 0.95
EPSILON = 0



def translate_into_pair(point_structure, card, capture_order: deck.Order):
    points = point_structure[card]
    pair = capture_order.get_card_pair(card.value, card.suit)
    depth = capture_order.get_depth(pair)
    return [points, depth]

def translate_into_pair_drawn(point_structure, card, capture_order: deck.Order, drawn_cards):
    # same as translate into pair above, with also the number of cards still in the deck (or in others' hands)
    # of the same suit that can capture the given card
    points, depth = translate_into_pair(point_structure, card, capture_order)
    idx = 0
    card_pair = capture_order.get_card_pair(card.value, card.suit)
    while (1):
        if card_pair == card_pair.upper_pair(): break
        if not(card_pair.card.suit == card_pair.upper_pair().card.suit): break
        card_pair = card_pair.upper_pair()
        if not(card_pair.card in drawn_cards): idx += 1
    return [points, depth, idx]
        

def state_translator(point_structure, state, deck_order, capture_order = None):
    input = []
    state_copy = copy.copy(state)
    capture_order = state_copy.pop()
    for card_set in state_copy:
        temp = [0 for _ in range(len(deck_order))]
        for i, card in enumerate(deck_order):
            if card in card_set:
                temp[i] = 1 
        input.append(temp)
    if POT_FLAG:        
        flattened_input = list(chain(*input))  
    else:
        input_new = [input[0], input[1]]
        if ORDER_INPUT_FLAG:
            # new translation: each card gets identified with a pair:
            # - position in the capture queue (e.g. Ace of Briscola = 1, Three of Briscola = 2, Ace of Hand suit = 11)
            # - points awarded for the capture of that card
            if capture_order == None: raise "No capture order in ORDER_INPUT_FLAG mode"
            if not(isinstance(capture_order,deck.Order)): raise "Capture order of wrong type"         
            temp = []
            state_new = [state[0], state[1]]
            drawn_cards = state[2] + state[3] # sum as list merge
            if state[0] == []:
                if ORDER_DRAWN_FLAG:
                    temp.append([0,0,0])
                else:
                    temp.append([0,0])
            for card_set in state_new:
                for card in card_set:
                    if ORDER_DRAWN_FLAG:
                        translated = translate_into_pair_drawn(point_structure, card, capture_order, drawn_cards)
                    else:
                        translated = translate_into_pair(point_structure, card, capture_order)                    
                    temp.append(translated)
            while len(temp)<4:
                if ORDER_DRAWN_FLAG:
                    temp.append([0,0,0])
                else:
                    temp.append([0,0])
            flattened_input = list(chain(*temp))
        else:
            flattened_input = list(chain(*input_new))       
    return flattened_input

class Agent:
    def __init__(self, deck: deck.Deck, n_cards_hand = 3, n_players = 2, point_structure = None, long_memory_flag = LONG_MEMORY_FLAG, softmax_flag = 0, temperature = 100):
        self.deck = deck
        self.point_structure = point_structure
        DECK_LENGTH = len(self.deck.initial_deck_order)
        self.n_games = 0
        self.epsilon = EPSILON
        self.memory = deque(maxlen=MAX_MEMORY)
        self.long_memory_flag = long_memory_flag
        self.gamma = GAMMA

        self.softmax_flag = softmax_flag
        if self.softmax_flag: self.temperature = temperature
        # DECK_LENGTH : cards on table
        # DECK_LENGTH : cands in hand
        # DECK_LENGTH : cards in pot
        # (N_PLAYERS-1)*DECK_LENGTH : cards in opponents' pots
        if POT_FLAG:
            INPUT_SIZE = (DECK_LENGTH) + (DECK_LENGTH) + (DECK_LENGTH) + (n_players-1)*(DECK_LENGTH)   
        else:
            if ORDER_INPUT_FLAG:
                if ORDER_DRAWN_FLAG:
                    INPUT_SIZE = 3 + 3*3
                else:
                    INPUT_SIZE = 2 + 3*2
            else:
                INPUT_SIZE = (DECK_LENGTH) + (DECK_LENGTH) 
        OUTPUT_SIZE = n_cards_hand
        HIDDEN_SIZE = 30 #max(int(2*INPUT_SIZE/3),OUTPUT_SIZE)      
        HIDDEN2_SIZE = 30 #min(int(3*OUTPUT_SIZE/2),HIDDEN_SIZE)
        self.model = Linear_QNet(INPUT_SIZE, HIDDEN_SIZE, HIDDEN2_SIZE, OUTPUT_SIZE)      
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)

    def model_prediction(self, state, capture_order = None):
        ###
        # in state: cards on table (none if first to play), player hand, player's obtained cards (-> points), opponenents' obtained cards (-> points)
        ###
        n_cards_hand = len(state[1])
        t_state = state_translator(self.point_structure, state, self.deck.initial_deck_order)
        t_state = torch.tensor(t_state, dtype=torch.float)
        prediction = self.model(t_state)
        if self.softmax_flag:
            softmax = torch.nn.functional.softmax(prediction*self.temperature)
            move = np.random.choice(range(len(softmax)), p=softmax.detach().numpy())
            return move
        move = torch.argmax(prediction).item()
        while (move > n_cards_hand - 1):
            mask = torch.ones(prediction.size(), dtype=torch.bool)
            mask[move] = False
            prediction = prediction[mask]
            move = torch.argmax(prediction).item()
        return move

    def train_short_memory(self, state_old, final_move, reward, state_new, done):
        deck_order = self.deck.initial_deck_order 
        t_state_old = state_translator(self.point_structure, state_old, deck_order)
        t_state_new = state_translator(self.point_structure, state_new, deck_order)        
        self.trainer.train_step(t_state_old, final_move, reward, t_state_new, done)
    
    def train_long_memory(self):
        if self.long_memory_flag:
            if len(self.memory) > BATCH_SIZE:
                mini_sample = random.sample(self.memory, BATCH_SIZE)
            else:
                mini_sample = self.memory
            for state, action, reward, next_state, done in mini_sample:
                self.trainer.train_step(state, action, reward, next_state, done)

    def remember(self, state_old, final_move, reward, state_new, done):
        deck_order = self.deck.initial_deck_order 
        t_state_old = state_translator(self.point_structure, state_old, deck_order)
        t_state_new = state_translator(self.point_structure, state_new, deck_order)
        self.memory.append((t_state_old, final_move, reward, t_state_new, done))