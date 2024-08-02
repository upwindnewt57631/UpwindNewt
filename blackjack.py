from os import system , name
from random import shuffle
from time import sleep

def full_deck():
    suits = ["Spades", "Diamonds", "Clubs", "Hearts"]
    cards = (["Ace"] + 
    [str(i) for i in range(2, 11)] # Generates 2 - 10 using a range and converts them to a string
    + ["Jack", "Queen", "King"])
    return [card + " of " + suit for card in cards for suit in suits]
    #Creates a deck by creating items for each card and then for each suit

def get_icon(card):
    #Returns the value of the card if the card isnt a High Value card else it returns the first letter of the card
    return card.split()[0] if card.split()[0] not in ["Ace","Jack", "Queen", "King"] else card.split()[0][0]

def add_commas(number):
    result = ""
    #reverses the order of the string of the number and for every 3rd letter after 0 a comma is added
    for i , letter in enumerate(reversed(str(number))):
        if i % 3 == 0 and i != 0:
            result+= ","
        result += letter
    #reveses the order back
    return "".join([i for i in reversed(result)])

def clear_console():
    #cls if for windows aka 'nt'
    system("cls" if name == 'nt' else "clear")
    
def balance_is_valid(cost):
    global balance
    #returns true if the cost is greater / equal to one and less/equal to the balance
    return 1 <= cost <= balance

def get_suit(card):
    #uses a dictionary to conert the suit of a card to an icon represening that suit
    suit = card.split()[-1]
    suits = {"Spades":"♠" , "Diamonds": "♦", "Clubs": "♣" , "Hearts": "♥" , "Unknown": "U"}
    return suits[suit]

def remove_commas(word):
    #takes a word and removes ","s by 
    return "".join([letter if letter != "," else "" for letter in word])

def make_bet(balance):
    while True:
        try: #used if an non int value is entered
            bet = int(remove_commas(input(f"Your current balance: ${add_commas(balance)}\n\nEnter your bet: ").strip()))
            clear_console()
            if balance_is_valid(bet):
                break
            else:
                print("Invalid bet. Please enter a valid amount.\n")
        except ValueError:
            clear_console()
            print("Invalid input. Please enter a valid number.\n")
    return bet

def new_turn():
    #just uses global values to make a new hand
    global player , cpu
    player.new_hand()
    cpu.new_hand()
    #used for the cpu to have 2 hands in deck
    for _ in range(2):
        cpu.draw()

class Hand:
    def __init__(self):
        self.hand = []
    
    def new_hand(self):
        self.hand = []
    
    def get_hand(self):
        return self.hand
        
    def show_hand(self):
        #creates dynamic ascii art of cards using print statments
        # end =" " so the cards are next to each other
        if self.get_hand():
            
            for card in self.get_hand():
                print("┌─────────┐ ", end=" ")
            print()  # Move to the next line
    
            for card in self.get_hand():
                value = get_icon(card)                
                print(f"│ {value.center(5)}   │ ", end=" ")
            print()  # Move to the next line
            
            for card in self.get_hand():
                print("│         │ ", end=" ")
            print()  # Move to the next line
            
            for card in self.get_hand():
                suit_icon = get_suit(card)
                print(f"│    {suit_icon}    │ ", end=" ")
            print()  # Move to the next line
            
            for card in self.get_hand():
                print("│         │ ", end=" ")
            print()  # Move to the next line
            
            for card in self.get_hand():
                value = get_icon(card)
                print(f"│   {value.center(5)} │ ", end=" ")
            print()  # Move to the next line
    
            for card in self.get_hand():
                print("└─────────┘ ", end=" ")
            print("\n")
    
    def show_hand_last_card_hidden(self):
        temp_hand = [card for card in self.get_hand()]
        temp_hand[-1] = "? of Unknown"
        
        for card in temp_hand:
            print("┌─────────┐ ", end=" ")
        print()  # Move to the next line

        for card in temp_hand:
            value = get_icon(card)        
            print(f"│ {value.center(5)}   │ ", end=" ")
        print()  # Move to the next line
        
        for card in temp_hand:
            print("│         │ ", end=" ")
        print()  # Move to the next line
        
        for card in temp_hand:
            suit_icon = get_suit(card)
            print(f"│    {suit_icon}    │ ", end=" ")
        print()  # Move to the next line
        
        for card in temp_hand:
            print("│         │ ", end=" ")
        print()  # Move to the next line
        
        for card in temp_hand:
            value = get_icon(card)
            print(f"│   {value.center(5)} │ ", end=" ")
        print()  # Move to the next line

        for card in temp_hand:
            print("└─────────┘ ", end=" ")
        print("\n")
    def draw(self):
        global deck
        card = deck[0]
        #takes the first item in the deck and adds it you the hand
        self.hand.append(card)
        deck.pop(0)
        #if the deck is empty, create a new deck with all the cards
        if not deck:
            print("\nShuffling Deck\n")
            deck = full_deck()
            shuffle(deck)
        return card

    def value(self):
        score = 0 # counts score
        ace = 0 # counts aces
        for card in self.hand:
            if card.split()[0] in ["Jack", "Queen", "King"]: # if the value of a card is royal, add 10 to the score
                score += 10
            elif card.split()[0] == "Ace":
                score += 11 # adds eleven, score might be greater then 21 here
                ace += 1
            else:
                score += int(card.split()[0]) # adds the value of the numeric cards
                
        while ace > 0 and score > 21: #used becaues aces can equal 11 or 1
            score -= 10
            ace -= 1
        return score if score <= 21 else -1 # -1 is used a a failure state
    
deck = full_deck()
shuffle(deck)

player = Hand()
cpu = Hand()

balance = 1000

running = True
sleep_factor = 1.5

while running:
    bet = make_bet(balance)
    new_turn()
    while True:
        print("The dealers hand looks like: ")
        cpu.show_hand_last_card_hidden()
        print(f"\nThe Deck looks like it contains {len(deck)} cards\n")
        choice = input("You can Hit, Stand, Double Down or Fold <H,S,D,F>: ").strip().lower()
        clear_console()
        if choice in ["stand" , "s"]:
            print(f"You have played a hand worth {player.value()}")
            break
        elif choice in ["hit","h"]:
            print(f"You drew a {player.draw()}\n")
            if player.value() == -1:
                print("You Busted")
                break
        elif choice in ["double down","d"]:
            if balance < 2 * bet:
                print("You don't have enough money to double down")
            else:
                bet *= 2
                print(f"You drew a {player.draw()}")
                if player.value() == -1:
                    print("You Busted")
                else:
                    print(f"You have played a hand worth {player.value()}")
                break
        elif choice in ["fold","f"]:
            if bet // 2 > 0:
                bet //= 2
                print(f"The bet has been halfed to {bet}\n\nYou lost because you folded")
                balance -= bet
                sleep(sleep_factor)
                clear_console()
                print(f"Current balance: ${add_commas(balance)}\n")
                new_turn()
                bet = make_bet(balance)
            else:
                print("Your bet would be 0 if you folded")
        else:
            print("Invalid input. Please enter either Hit or Stand.\n")
        print("The your hand looks like: ")
        player.show_hand()
    
    cpu.show_hand()
    sleep(sleep_factor)
        
    while cpu.value() < max((player.value(),12)) and cpu.value() != -1:
        # Dealer draws cards until their hand value is at least 12 or they bust (value == -1)
        clear_console()
        print(f"The dealer Drew a {cpu.draw()}\n")
        cpu.show_hand()
        sleep(sleep_factor)
    clear_console()
    
    # if cpu.value() == -1 and player.value() != -1:
        # bet *= 2
        # print(f"The Bet has doubled to {bet} because the CPU busted\n")
    
    if player.value() != cpu.value():
        print("The Winning Hand: \n")
        
        if player.value() > cpu.value():
            player.show_hand()
        elif player.value() < cpu.value():
            cpu.show_hand()
            
        sleep(sleep_factor)
    
    if (cpu.value() < player.value()):
        print(f"You won the bet worth ${add_commas(bet)}")
        balance += bet
    elif (cpu.value() > player.value()):
        print(f"The dealer wins the bet worth ${add_commas(bet)}")
        balance -= bet
    else:
        print("Tie Game")
    
    print(f"\nCurrent balance: ${add_commas(balance)}\n")
    if balance <= 0:
        break
    while choice not in ["y","n"]:
        choice = input("Play Agian? <Y/N>: ").strip().lower()
    if choice == "n":
        clear_console()
        break
    clear_console()
    
if balance <= 0:
    print("Game over. You're out of money.")
else:
    print(f"Thanks for playing! Final balance: ${add_commas(balance)}")
    
input("PRESS ENTER TO EXIT")