# deck class and methods
import random
import copy
import collections
from typing import List

class Card:
    def __init__(self, value, suit, name = "", verses = ["Up", "Down"], print_style = 0):
        self.value = value
        self.suit = suit
        self.name = name
        self.verses = verses
        self.verse = self.verses[0]
        self.print_verse = 0
        self.print_style = print_style
    def __str__(self):
        temp = ""
        if self.print_style == 0:
            temp = f"[{self.value}, {self.suit}]"
        else:
            if self.suit == "Major Arcana":
                temp = f"({self.value}, {self.name})"
            else:
                temp = f"({self.value} of {self.suit})"
        if self.print_verse:
            temp = temp + f" | {self.verse}"
        return temp
    def shuffle_verse(self):
        self.verse = random.choice(self.verses)

class Deck:
    def __init__(self,
                 values_list = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', "J", "Q", "K"],
                 suits_list = ["Spades", "Clubs", "Diamonds", "Hearts"], 
                 additional_list = [],
                 suits_groups = {}):
        self.deck = []
        self.n_deck = 0
        self.initial_deck_order = []    # useful to determine a "fixed" order to give as binary input (won't be the actual game order for card capture)
        self.initialise_deck(values_list, suits_list, additional_list)
        self.drawn = []
        self.n_drawn = 0
        self.update_lists()
        self.check_groups(suits_groups)
        self.suits_groups = suits_groups

    def initialise_deck(self, values_list, suits_list, additional_list, start_shuffle = False):
        for card in additional_list:
            self.add_card(card)
        for value in values_list:
            for suit in suits_list:
                temp_card = Card(value, suit)
                self.add_card(temp_card)
        self.initial_deck_order = copy.copy(self.deck)
        if start_shuffle: self.shuffle()

    def get_card_deck(self, value, suit):
        for card in self.deck:
            if (card.value == value) and (card.suit == suit):
                return card
        raise f"Value: {value}, Suit: {suit}, card not found"

    def check_groups(self, groups):
        for suit in groups.keys():
            if not(suit in self.deck_suits) and not(suit in self.drawn_suits):
                raise "Suit in groups dictionary not in the list of suits"

    def update_lists(self):
        self.deck_suits = list(set([card.suit for card in self.deck]))
        self.deck_values = list(set([card.value for card in self.deck]))
        self.deck_names = list(set([card.name for card in self.deck]))
        ###
        self.drawn_suits = list(set([card.suit for card in self.drawn]))
        self.drawn_values = list(set([card.value for card in self.drawn]))
        self.drawn_names = list(set([card.name for card in self.drawn]))

    def get_subdecks(self):
        subdecks = []
        if self.suits_groups == {}: return subdecks
        inverse_groups = {}
        # Iterate through the dictionary
        for suit, group in self.suits_groups.items():
        # Check if the value category exists in inverse_group
            if group in inverse_groups:
        # If it exists, append the key to the corresponding list
                inverse_groups[group].append(suit)
            else:
        # If it doesn't exist, create a new list with the key
                inverse_groups[group] = [suit]
        for group in inverse_groups.keys():
            temp_subdeck = []
            for card in self.deck:
                if card.suit in inverse_groups[group]:
                    temp_subdeck.append(card)
            subdecks.append(temp_subdeck)
        return subdecks
    
    def card_subdeck(self, card):
        if card not in self.deck:
            raise "Card not in deck"
        subdecks = self.get_subdecks()
        for subdeck in subdecks:
            if card in subdeck:
                return self.suits_groups[card.suit]
        return "N/A"
        

    def add_card(self, card):
        self.deck.append(card)
        self.n_deck += 1

    def add_list_cards(self, list_cards):
        for card in list_cards:
            self.add_card(card)
    
    def shuffle(self):
        random.shuffle(self.deck)
        for card in self.deck:
            card.shuffle_verse()

    def draw(self):
        card = self.deck.pop()
        self.n_deck -= 1
        self.drawn.append(card)
        self.n_drawn += 1
        self.update_lists()
        return card
    
    def reset(self):
        for card in self.drawn:
            self.deck.append(card)
        self.n_deck = len(self.deck)
        self.drawn = []
        self.n_drawn = 0
        self.shuffle()

    def switch_print_verse(self):
        for card in self.deck:
            card.print_verse = not(card.print_verse)
        for card in self.drawn:
            card.print_verse = not(card.print_verse)

    def change_print_style(self, print_style):
        for card in self.deck:
            card.print_style = print_style
        for card in self.drawn:
            card.print_style = print_style

    def print_deck(self):
        for card in self.deck:
            print(card)

    def is_in_deck(self, card):
        return (card in self.deck)
    
    def is_in_drawn(self, card):
        return (card in self.drawn)
    
    def all_ok(self):
        flag = 1
        if not(self.n_deck == len(self.deck)):
            flag = 0
        if not(self.n_drawn == len(self.drawn)):
            flag = 0
        return flag

# Linked lists to order (substantially a tree)

class OrderPair:
    def __init__(self, card: Card, pair=None):
        self.card = card
        self.pointer = pair
    def upper_pair(self, n=1):
        # n: number of pairs to pass going up, if arrived at the top, stop
        i = 0
        temp = self
        while (i < n):
            i+=1
            if temp.pointer == None:
                break
            temp = temp.pointer
        return temp

def get_card_pair(value, suit, list_pairs):
        for pair in list_pairs:
            if (pair.card.value == value) and (pair.card.suit == suit):
                return pair
        raise f"Value: {value}, Suit: {suit}, card not found"


class Order:
    def __init__(self, deck: Deck, list_pairs: List[OrderPair]):
        self.deck = deck
        self.list_pairs = list_pairs

    def get_card_pair(self, value, suit):
        return get_card_pair(value, suit, self.list_pairs)
    
    def compare_pairs(self, pair1: OrderPair, pair2: OrderPair):
        pair1 = self.get_card_pair(pair1.card.value, pair1.card.suit)       # we might pass orderpairs that are effectively the same but stored in another part of the memory
        pair2 = self.get_card_pair(pair2.card.value, pair2.card.suit)       # this way, we use the pairs in the list of pairs
        pair1_copy = copy.copy(pair1)           # shallow copy of the pair (the pointer needs to be the same)
        while not(pair1_copy.upper_pair() == pair1_copy):
            if pair1_copy.card == pair2.card: return pair2
            pair1_copy = pair1_copy.upper_pair()
        if pair1_copy.card == pair2.card: return pair2
        pair2_copy = copy.copy(pair2)
        while not(pair2_copy.upper_pair() == pair2_copy):
            if pair2_copy.card == pair1.card: return pair1
            pair2_copy = pair2_copy.upper_pair()
        if pair2_copy.card == pair1.card: return pair1
        raise f"{pair1.card}, {pair2.card}: pairs not comparable"
    
    def compare_list_pairs(self, list_pairs: List[OrderPair]):
        temp = list_pairs
        while(len(temp)>1):
            temp.append(self.compare_pairs(temp.pop(),temp.pop()))
        temp_pair = temp[0]
        return temp_pair
    
    def get_depth(self, pair):
        if not(pair in self.list_pairs):
            raise "Pair not in list of pairs"
        top_pairs = self.get_top_pairs()
        temp = pair
        i = 0
        while not(temp in top_pairs):
            i+=1
            temp = temp.upper_pair()
        return i
    
    def get_depth_dict(self):
        depth_dict = {}
        for pair in self.list_pairs:
            depth_dict[pair] = self.get_depth(pair)
        return depth_dict

    def get_top_suited_pair(self, suit):
        for pair in self.list_pairs:
            if pair.card.suit == suit:
                starting_pair = pair
                break
        top_pair = starting_pair
        while (1):
            if not(top_pair.upper_pair().card.suit == suit) or (top_pair.upper_pair() == top_pair):
                break
            top_pair = top_pair.upper_pair()
        return top_pair
    
    def get_top_pairs(self):
        lowest_pairs = self.get_lowest_pairs()
        n = len(self.list_pairs)
        top_pairs = [low_pair.upper_pair(n) for low_pair in lowest_pairs]
        return list(set(top_pairs))

    def get_lower_pairs(self, orderpair: OrderPair):
        temp = []
        for pair in self.list_pairs:
            if pair.pointer == orderpair:
                temp.append(pair)
        return temp
    
    def get_lowest_pairs(self):
        # This will be suboptimal, can be optimised with a dynamic programming approach
        temp = []
        for pair in self.list_pairs:
            # start from only one pair            
            temp_old = [pair]
            while (1):
                temp_new = []
                for new_pair in temp_old:
                    lower_pairs = self.get_lower_pairs(new_pair)
                    # create a list of pairs given all the pairs that are lower than the one considered
                    for lower_pair in lower_pairs:
                        temp_new.append(lower_pair)
                # if temp_new is empty, there is no lower pair to find, hence temp_old contains all the lowest pairs starting from "pair"
                if temp_new == []:
                    for old_pair in temp_old:
                        temp.append(old_pair)
                    break
                # if temp_new is not empty, work recursively 
                temp_old = temp_new
        # there will be many duplicated of the same pair in temp; eliminate duplicates and return
        return list(set(temp))

    def get_modified_order(self, trump_suit, hand_suit):
        new_order = copy.deepcopy(self)         # create a deep copy of the order (all pairs are reconstructed) - the two orders are separated
        suits = new_order.deck.deck_suits
        if trump_suit not in suits:
            raise "Trump suit not in deck suits"
        if hand_suit not in suits:
            raise "Hand suit not in deck suits"
        lowest_pairs = new_order.get_lowest_pairs()
        lowest_pairs_suits = [low_pair.card.suit for low_pair in lowest_pairs]
        n_hand_suit = 0
        for suit in lowest_pairs_suits:
            if suit == hand_suit: n_hand_suit+=1
        #if (hand_suit==trump_suit) and not(hand_suit in lowest_pairs_suits): n_hand_suit+=1
        if not(n_hand_suit==1):
            raise "Either no hand suit or too many hand suits in lowest ranked card, can't attach"
        # detect the pair with hand suit and remove it from the lowest pairs
        idx = 0
        for low_pair in lowest_pairs:
            if low_pair.card.suit == hand_suit:
                lowest_hand_pair = low_pair
                lowest_pairs.pop(idx)           
            idx += 1
        # find the top pairs for each suit (apart from the hand suit)
        top_suited_pairs = []
        for low_pair in lowest_pairs:
            suit = low_pair.card.suit
            # sanity check in case a trump-suited card is in the top cards of non-hand suits (it should not happen)
            if not(suit == trump_suit): top_suited_pairs.append(new_order.get_top_suited_pair(suit))
        for top_pair in top_suited_pairs:
            # repoint each top non-hand-suited top card to the lowest hand-suited card
            top_pair.pointer = lowest_hand_pair
        return new_order
        

         
        
        
        


