from deck import Card, Deck, Order, OrderPair, get_card_pair

# French Cards Deck
FRENCH_SUIT_GROUPS = {"Spades":"Black","Clubs":"Black","Diamonds":"Red","Hearts":"Red"}
FRENCH_DECK = Deck(suits_groups=FRENCH_SUIT_GROUPS)

JOLLIES = [Card("Jolly", "Black"), Card("Jolly", "Red")]
JOLLIES_SUIT_GROUPS = FRENCH_SUIT_GROUPS
JOLLIES_SUIT_GROUPS.update({"Black":"Black","Red":"Red"})
FRENCH_DECK_JOLLIES = Deck(additional_list=JOLLIES, suits_groups=JOLLIES_SUIT_GROUPS)

# Italian Cards Deck
ITALIAN_VALUES = ['A', '2', '3', '4', '5', '6', '7', "J", "Q", "K"]
ITALIAN_VALUES_IT = ['Asso', '2', '3', '4', '5', '6', '7', "Fante", "Cavallo", "Re"]

ITALIAN_SUITS = ["Coins", "Cups", "Swords", "Wands"]
ITALIAN_SUITS_IT = ["Denari", "Coppe", "Spade", "Bastoni"]

ITALIAN_DECK = Deck(ITALIAN_VALUES, ITALIAN_SUITS)
ITALIAN_DECK_IT = Deck(ITALIAN_VALUES_IT, ITALIAN_SUITS_IT)

# Tarot Cards Deck

NAMES_MAJOR_ARCANA_ENG = [  "Fool",
                            "Magician",
                            "High Priestess",
                            "Empress",
                            "Emperor",
                            "Hierophant",
                            "Lovers",
                            "Chariot",
                            "Justice",
                            "Hermit",
                            "Wheel of Fortune",
                            "Strength",
                            "Hanged Man",
                            "Death",
                            "Temperance",
                            "Devil",
                            "Tower",
                            "Star",
                            "Moon",
                            "Sun",
                            "Judgement",
                            "World" ]

# Tarot Deck
ROMAN_NUMERALS = [
    '0', 'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X',
    'XI', 'XII', 'XIII', 'XIV', 'XV', 'XVI', 'XVII', 'XVIII', 'XIX', 'XX', 'XXI'
]
MAJOR_ARCANA = [Card(ROMAN_NUMERALS[i], "Major Arcana", name=NAMES_MAJOR_ARCANA_ENG[i]) for i in range(len(NAMES_MAJOR_ARCANA_ENG))]
TAROT_VALUES = ['Ace', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten', "Jack", "Knight", "Queen", "King"]

TAROT_SUIT_GROUPS = {"Major Arcana":"Major Arcana", "Coins":"Minor Arcana", "Cups":"Minor Arcana", "Swords":"Minor Arcana", "Wands":"Minor Arcana"}
TAROT_DECK = Deck(values_list=TAROT_VALUES, suits_list=ITALIAN_SUITS, additional_list=MAJOR_ARCANA, suits_groups=TAROT_SUIT_GROUPS)
TAROT_DECK.change_print_style(1)

#########################            

def create_tarot_order():
    deck = TAROT_DECK
    list_pairs = []
    # Order Major Arcana
    list_pairs.append(OrderPair(deck.deck[20]))
    list_pairs.append(OrderPair(deck.deck[21], list_pairs[-1]))
    idx = 19
    while (idx>=0):
        list_pairs.append(OrderPair(deck.deck[idx], list_pairs[-1]))
        idx-=1
    # Order Aces pointing to the Fool
    aces = []
    for idx in [22, 23, 24, 25]:
        aces.append(OrderPair(deck.deck[idx], list_pairs[21]))
    for ace in aces:
        list_pairs.append(ace)
    # Order Kings pointing to Aces
    kings = []
    for idx in [74, 75, 76, 77]:
        kings.append(OrderPair(deck.deck[idx], aces[idx-74]))
    for king in kings:
        list_pairs.append(king)
    # Order other cards
    idx = 73
    jdx = 0
    temp_list = []
    while (idx>=26):   
        while (jdx<=3):
            pairs_jdx = -1-jdx
            if idx < 70:
                pairs_jdx = -4+jdx
            temp_list.append(OrderPair(deck.deck[idx-jdx], list_pairs[pairs_jdx]))
            jdx+=1
        for temp in temp_list:
            list_pairs.append(temp)
        idx -= 4
        jdx = 0
        temp_list = []
    return list_pairs

TAROT_LIST_PAIRS = create_tarot_order()
ORDER_TAROT = Order(TAROT_DECK, TAROT_LIST_PAIRS)

def roman_numeral_translator(roman_num):
    if roman_num not in ROMAN_NUMERALS:
        raise "Not a Roman numeral less or equal than 21."
    return ROMAN_NUMERALS.index(roman_num)

def create_tarot_points():
    deck = TAROT_DECK
    points = {}
    for card in deck.deck:
        if card.suit == "Major Arcana":
            points[card] = int(roman_numeral_translator(card.value)/2)
            if card.value == "XXI": points[card]+=1
        else:
            if card.value == "Ace":
                points[card] = 11
            elif card.value == "Three":
                points[card] = 10
            elif card.value == "King":
                points[card] = 5
            elif card.value == "Queen":
                points[card] = 4
            elif card.value == "Knight":
                points[card] = 3
            elif card.value == "Jack":
                points[card] = 2
            else:
                points[card] = 0
    return points

POINTS_TAROT = create_tarot_points()

# Briscola order and points

def create_briscola_order(briscola):
    deck = ITALIAN_DECK
    list_pairs = []
    suits = deck.deck_suits
    if briscola not in suits:
        raise "Briscola not in suits"
    non_trump_suits = []
    for suit in suits:
        if not(suit == briscola):
            non_trump_suits.append(suit)
    values = deck.deck_values
    # Briscola cards
    suit = briscola
    # Ace
    card = deck.get_card_deck("A", suit)
    list_pairs.append(OrderPair(card))
    # Three
    card = deck.get_card_deck("3", suit)
    ace_pair = get_card_pair("A", suit, list_pairs)
    list_pairs.append(OrderPair(card, ace_pair))
    # Other cards
    three_pair = get_card_pair("3", suit, list_pairs)
    king = deck.get_card_deck("K", suit)
    king_pair = OrderPair(king, three_pair)
    list_pairs.append(king_pair)
    queen = deck.get_card_deck("Q", suit)
    queen_pair = OrderPair(queen, king_pair)
    list_pairs.append(queen_pair)
    jack = deck.get_card_deck("J", suit)
    jack_pair = OrderPair(jack, queen_pair)
    list_pairs.append(jack_pair)

    other_cards = []
    other_pairs = []
    value = 7
    other_cards.append(deck.get_card_deck(str(value), suit))
    other_pairs.append(OrderPair(other_cards[-1], jack_pair))
    list_pairs.append(other_pairs[-1])
    value -= 1
    while (value >= 2):
        if not(value == 3):
            other_cards.append(deck.get_card_deck(str(value), suit))
            other_pairs.append(OrderPair(other_cards[-1], other_pairs[-1]))
            list_pairs.append(other_pairs[-1])
        value -= 1

    suits = non_trump_suits
    two_trump_pair = get_card_pair("2", briscola, list_pairs)

    # Order Aces
    for suit in suits:
        card = deck.get_card_deck("A", suit)
        list_pairs.append(OrderPair(card, two_trump_pair))
    # Order Threes
    for suit in suits:
        card = deck.get_card_deck("3", suit)
        ace_pair = get_card_pair("A", suit, list_pairs)
        list_pairs.append(OrderPair(card, ace_pair))
    # Order other cards
    for suit in suits:
        three_pair = get_card_pair("3", suit, list_pairs)
        king = deck.get_card_deck("K", suit)
        king_pair = OrderPair(king, three_pair)
        list_pairs.append(king_pair)
        queen = deck.get_card_deck("Q", suit)
        queen_pair = OrderPair(queen, king_pair)
        list_pairs.append(queen_pair)
        jack = deck.get_card_deck("J", suit)
        jack_pair = OrderPair(jack, queen_pair)
        list_pairs.append(jack_pair)

        other_cards = []
        other_pairs = []
        value = 7
        other_cards.append(deck.get_card_deck(str(value), suit))
        other_pairs.append(OrderPair(other_cards[-1], jack_pair))
        list_pairs.append(other_pairs[-1])
        value -= 1
        while (value >= 2):
            if not(value == 3):
                other_cards.append(deck.get_card_deck(str(value), suit))
                other_pairs.append(OrderPair(other_cards[-1], other_pairs[-1]))
                list_pairs.append(other_pairs[-1])
            value -= 1
    return list_pairs


def create_briscola_points():
    deck = ITALIAN_DECK
    points = {}
    for card in deck.deck:
        if card.value == "A":
            points[card] = 11
        elif card.value == "3":
            points[card] = 10
        elif card.value == "K":
            points[card] = 5
        elif card.value == "Q":
            points[card] = 3
        elif card.value == "J":
            points[card] = 2
        else:
            points[card] = 0
    return points

POINTS_BRISCOLA = create_briscola_points()






