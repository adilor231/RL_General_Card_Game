import Deck
import agent as Agent
from typing import List
import random
import time
from enum import Enum
from collections import namedtuple
import numpy as np
from debug import DebugItem
from pynput import keyboard
import termios
import sys
import tty

N_CARDS_HAND = 3

WINNING_REWARD = 100
LOSING_REWARD = -100



def calc_points(cards: List[Deck.Card], point_structure):
    temp = 0
    for card in cards:
        temp += point_structure[card]
    return temp

class Hand:

    def __init__(self, cards, order = []):
        self.cards = cards
        self.length = len(self.cards)
        self.order = order
        self.order_hand()

    def __str__(self):
        temp = "[ "        
        for idx, card in enumerate(self.cards):
            if idx == len(self.cards)-1:
                temp = temp + str(card) + " "
            else:
                temp = temp + str(card) + " , "
        temp = temp + "]"
        return temp
    
    def order_hand(self):
        if self.order == []:
            return DebugItem("<NO ORDER>", time=time.time())
        temp = []
        for card in self.order:
            if card in self.cards:
                temp.append(card)
        if len(temp) == self.length:
            self.cards = temp
            return DebugItem("<SUCCESSFULLY ORDERED>", time=time.time())
        for card in self.cards:
            if card not in temp:
                temp.append(card)
        return DebugItem("<WARNING: PARTIALLY ORDERED>", time=time.time())
    
    def refresh(self):
        self.order_hand()
        self.length = len(self.cards)
        
        

class Player:

    def __init__(self, deck: Deck.Deck, policy, point_structure, name, n_players, load_flag = 1, print_flag = 0):
        self.deck = deck
        self.policy = policy
        self.name = name
        self.point_structure = point_structure
        self.load_flag = load_flag
        self.print_flag = print_flag
        if (self.policy == Agent.Q) or (self.policy == Agent.Q_NOT_LEARN):
            self.agent = Agent.Agent(self.deck, N_CARDS_HAND, n_players, point_structure=point_structure)
            if self.load_flag: self.agent.model.load()
        self.total_points = 0
        
        self.list_total_points = []
        self.total_wins = 0

        self.order = None
        self.pressed_key = ''

        self.reset()

    def __str__(self):
        return self.name
    
    def total_reset(self):
        self.reset()
        self.total_points = 0
        self.list_total_points = []
        self.total_wins = 0
        if self.load_flag and ((self.policy==Agent.Q) or (self.policy == Agent.Q_NOT_LEARN)): self.agent.model.load()

    def put_order(self, order:Deck.Order):
        self.order = order

    def reset(self):        
        self.hand = Hand([], order=self.deck.initial_deck_order)
        self.hand.order_hand()
        self.pot = []
        self.pot_points = 0        

    def refresh(self):
        self.hand.refresh()
        self.pot_points = self.calc_pot_points()

    def add_card_to_hand(self, card):
        self.refresh()
        if self.hand.length >= N_CARDS_HAND:
            raise "Can't add cards to hand, too many already."
        self.hand.cards.append(card)
        self.refresh()

    def calc_pot_points(self):
        return calc_points(self.pot, self.point_structure)

    def add_to_pot(self, cards):        
        for card in cards:
            self.pot.append(card)
        self.pot_points = self.calc_pot_points()

    def final_appends(self):
        self.total_points += self.pot_points
        self.list_total_points.append(self.total_points)

    def choose_action(self, state):
        # action will be to choose among the cards, hence an index between 0 and N_CARDS_HAND-1;
        # if there are less cards in hand, the index will be between 0 and hand.length-1. <--- Problem: we always choose 0 this way
        self.refresh()
        if (self.policy == Agent.Q) or (self.policy == Agent.Q_NOT_LEARN):
            # if policy = Q, we need a translator state -> input vector of floats
            # need to use the agent
            prediction = self.agent.model_prediction(state)
            if (random.random() < self.agent.epsilon) or (prediction>=self.hand.length):
                return random.choice(range(self.hand.length))
            else:                
                return prediction
        elif self.policy == Agent.RANDOM:            
            return random.choice(range(self.hand.length))
        elif self.policy == Agent.INPUT:
            table_card = state[0]
            if table_card == []:
                print("[  ]")
            else:
                print("[",table_card[0],"]")
            print(self.hand)
            choice = -1
            while (choice not in range(self.hand.length)):
                print("<-: Left | ^: Centre | ->: Right")
                #fd = sys.stdin.fileno()
                #old_settings = disable_echo(fd)
                listener = keyboard.Listener(on_press=on_press)
                listener.start()
                listener.join()
                self.pressed_key = pressed_key
                if self.pressed_key == "LEFT":
                    choice = 0
                elif self.pressed_key == "UP":
                    choice = 1
                elif self.pressed_key == "RIGHT":
                    choice = 2
                else:
                    raise "Other value for pressed key"
                #restore_echo(fd, old_settings)
            return choice
        raise "Policy unknown"   
    
        
    def play_turn(self, state):
        if not(self.hand.cards == state[1]):
            raise "Hand different from player's hand in state"
        action = self.choose_action(state)
        if self.print_flag: print(self.name, ": ", self.hand.cards[action]) 
        return action                       # action is the index of the card in hand to play

def disable_echo(fd):
    if hasattr(termios, 'tcgetattr'):
        old_settings = termios.tcgetattr(fd)
        new_settings = termios.tcgetattr(fd)
        new_settings[3] = new_settings[3] & ~termios.ECHO
        termios.tcsetattr(fd, termios.TCSADRAIN, new_settings)
        return old_settings
    return None

def restore_echo(fd, old_settings):
    if old_settings and hasattr(termios, 'tcsetattr'):
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

def on_press(key):
        global pressed_key        
        pressed_key = ""        
        try:
            if key == keyboard.Key.left:
                pressed_key = "LEFT"
                return False           
            elif key == keyboard.Key.up:
                pressed_key = "UP"
                return False                    
            elif key == keyboard.Key.right:
                pressed_key = "RIGHT"
                return False                         
        finally:            
            pass
            

class Game:

    def __init__(self, deck: Deck.Deck, order: Deck.Order, policies = [Agent.Q, Agent.Q], point_structure = {}, print_flag = 0, trump_suit = "Major Arcana"):
        self.deck = deck
        self.print_flag = print_flag

        if trump_suit in deck.deck_suits:
            self.trump_suit = trump_suit
        else:
            raise "Trump suit not in deck suits."

        if order.deck == self.deck:            
            self.order = order
        else:
            raise "Order not matching deck."
        
        if point_structure == {}:       # need to check every card of the deck has a point value, and if not put it to 0
            raise "Missing point structure."
        self.point_structure = self.adjust_point_structure(point_structure)

        self.n_players = len(policies)       
        self.players = [Player(self.deck, policies[i], self.point_structure, f"P{i}", self.n_players, print_flag=self.print_flag) for i in range(self.n_players)]
        self.wins = [ [] for _ in self.players]
        self.draws = []
        self.turn_order = [i for i in range(self.n_players)]
        random.shuffle(self.turn_order)
        self.table_cards = [] # cards that will be played and put on the table
        

        self.modified_orders = {}
        for suit in self.deck.deck_suits:
            if not(suit == self.trump_suit):
                self.modified_orders[suit] = self.order.get_modified_order(self.trump_suit, suit) 

        self.turn = 0
        self.reset()

    def total_reset(self):
        self.reset()
        for player in self.players:
            player.total_reset()
        self.wins = [ [] for _ in self.players]
        self.draws = []

    def reset(self):
        self.turn = 0
        self.turn_order = [i for i in range(self.n_players)]
        random.shuffle(self.turn_order)
        self.deck.reset() 
        for player in self.players:
            player.reset()

    def refresh_players_orders(self, order):
        for player in self.players:
            player.put_order(order)

    def play_game(self):
        flag = 0
        idx = 0
        while (not flag):
            idx+=1
            if self.print_flag: print(f"Turn: {idx}")
            flag = self.play_step()
        if self.print_flag: print("Game over.")                

    def adjust_point_structure(self, point_structure):
        temp = point_structure
        for card in self.deck.deck:
            if card not in point_structure:
                temp[card] = 0
        return temp

    def is_game_over_player(self, idx):
        self.players[idx].hand.refresh()
        if (self.deck.n_deck == 0) and (self.players[idx].hand.length == 0):
            return 1
        return 0        

    def start_game(self):
        if N_CARDS_HAND >= self.deck.n_deck / self.n_players:
            raise "Not enough cards to play."        
        for idx in self.turn_order:
            cards = []
            for _ in range(N_CARDS_HAND):
                cards.append(self.deck.draw())
            first_hand = Hand(cards, self.deck.initial_deck_order)
            first_hand.order_hand()
            self.players[idx].hand = first_hand
        self.play_game()


    def get_state(self, idx):
        # in state: cards on table (none if first to play), player hand, player's obtained cards (-> points), opponenents' obtained cards (-> points)
        state = []
        table_cards = [card for card in self.table_cards]
        state.append(table_cards)
        self.players[idx].hand.order_hand()
        state.append(self.players[idx].hand.cards)
        state.append(self.players[idx].pot)
        for jdx in self.turn_order:
            if not(jdx == idx):
                state.append(self.players[jdx].pot)
        # also add the capture order
        if state[0] == []:
            state.append(self.order)
        else:
            suit = state[0][0].suit
            order = self.get_order(suit)
            state.append(order)
        return state    # states need a translator to be used in NNs

    def get_order(self, hand_suit):
        if hand_suit == self.trump_suit:    # if the hand suit is the trump suit, there's nothing to change
            return self.order
        return self.modified_orders[hand_suit]   # if the hand suit is not trump, we return a modified version of the order decided in the Order class
                                                 # usually, it will be an order for which the other suits are below the lowest hand suited card
        
    def resolve_cards(self, cards: List[Deck.Card]):
        hand_suit = cards[0].suit              # the first suit played has priority if no trump has been played
        order = self.get_order(hand_suit)      # get the order depending on the hand suit
        self.refresh_players_orders(order)
        card_pairs = [order.get_card_pair(card.value, card.suit) for card in cards]
        winning_pair = order.compare_list_pairs(card_pairs)
        winning_pair = self.order.get_card_pair(winning_pair.card.value, winning_pair.card.suit)       # we want the card in the original order, not the copy in the modified one
        idx = 0
        while (1):
            if cards[idx] == winning_pair.card: return idx
            idx += 1
            if idx > len(cards):
                raise "Cannot find winning card among the card list."


    def play_step(self):
        if not(self.table_cards == []):
            raise "Cards still on table."       
        self.turn += 1
        if (self.turn > 1) and (self.deck.n_deck > 0):                  # if there are cards in the deck, each player draws one card
            for idx in self.turn_order:
                drawn_card = self.deck.draw()
                self.players[idx].add_card_to_hand(drawn_card)
        old_states = {}
        final_moves = {}     
        for idx in self.turn_order:
            state = self.get_state(idx)                                 # get the state to decide the action
            old_states[idx] = state                                    
            idx_player_action = self.players[idx].play_turn(state)      # decide the action
            final_moves[idx] = idx_player_action
            self.table_cards.append(self.players[idx].hand.cards[idx_player_action]) # play the card on the table            
            self.players[idx].hand.cards.pop(idx_player_action)         # remove the card from player's hand
        capture_order = self.get_order(self.table_cards[0].suit)
        outcome = self.turn_order[self.resolve_cards(self.table_cards)]                  # returns the index of the winning card
        points = calc_points(self.table_cards, self.point_structure)     
        self.players[outcome].add_to_pot(self.table_cards) 
        new_states = {}       
        for idx in self.turn_order:
            new_states[idx] = self.get_state(idx)
            reward = -points
            if idx == outcome: reward = points
            done = self.is_game_over_player(idx)            
            if self.players[idx].policy == Agent.Q: self.players[idx].agent.train_short_memory(old_states[idx], final_moves[idx], reward, new_states[idx], done)
            if self.players[idx].policy == Agent.Q: self.players[idx].agent.remember(old_states[idx], final_moves[idx], reward, new_states[idx], done)
        self.turn_order = [(outcome + i) % self.n_players for i in range(self.n_players)]   # the player winning the hand starts the next one
        self.table_cards = []
        if done:
            self.game_over_handle(old_states, final_moves, new_states)     # if the last player is done, it means they are all done, hence the game is over.
            return 1
        return 0
        
    def game_over_handle(self, old_states, final_moves, new_states):
        points_list = [(self.players[idx].calc_pot_points(),idx) for idx in self.turn_order]
        winning_points, _ = max(points_list)
        winning_idx = []
        for points_pair in points_list:
            points, idx = points_pair
            if points == winning_points:
                winning_idx.append(idx)
        n_winners = len(winning_idx)
        if n_winners>1:
            self.draws.append(1)
        else:
            self.draws.append(0)        
        for idx in self.turn_order:
            if idx in winning_idx:
                if self.print_flag: print("Winner: ", self.players[idx])
                if n_winners==1: self.players[idx].total_wins += 1
                if n_winners==1: self.wins[idx].append(1)
                self.players[idx].final_appends()
                # here we train only if we have 3 cards to check
                if (self.players[idx].policy == Agent.Q): self.players[idx].agent.train_short_memory(old_states[idx], final_moves[idx], WINNING_REWARD/n_winners, new_states[idx], 1)
                if (self.players[idx].policy == Agent.Q): self.players[idx].agent.remember(old_states[idx], final_moves[idx], WINNING_REWARD/n_winners, new_states[idx], 1)
            else:
                self.wins[idx].append(0)
                self.players[idx].final_appends()
                if (self.players[idx].policy == Agent.Q): self.players[idx].agent.train_short_memory(old_states[idx], final_moves[idx], LOSING_REWARD, new_states[idx], 1)
                if (self.players[idx].policy == Agent.Q): self.players[idx].agent.remember(old_states[idx], final_moves[idx], LOSING_REWARD, new_states[idx], 1)  
        for idx in self.turn_order:
            if self.players[idx].policy == Agent.Q: self.players[idx].agent.train_long_memory()
        self.reset()
        

        





