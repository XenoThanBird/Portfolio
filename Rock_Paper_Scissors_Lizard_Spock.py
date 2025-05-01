#Rock, Paper, Scissors, Lizard, Spock
print("Let's play rock, paper, scissors, lizard, Spock")

import random

print('Here are the rules to rock, paper, scissors, lizard, Spock:\n' + \
      "Scissors cuts Paper -> Scissors Wins \n" + \
      "Paper covers Rock -> Paper Wins \n" + \
      "Rock crushes Lizard -> Rock Wins \n" + \
      "Lizard poisons Spock -> Lizard Wins \n" + \
      "Spock smashes Scissors -> Spock Wins \n" + \
      "Scissors decapitates Lizard -> Scissors Wins \n" + \
      "Lizard eats Paper -> Lizard Wins \n" + \
      "Paper disproves Spock -> Paper Wins \n" + \
      "Spock vaporizes Rock -> Spock Wins \n" + \
      "And as it always has, Rock crushes Scissors -> Rock Wins \n")

while True:
    print("Enter your choice \n 1 - Rock \n 2 - Paper \n 3 - Scissors \n 4 - Lizard \n 5 - Spock \n")
    choice = int(input('Enter your choice: '))

    while choice > 5 or choice < 1:
        choice = int(input('Enter a valid choice please: '))

    if choice == 1:
        choice_name = 'Rock'
    elif choice == 2:
        choice_name = 'Paper'
    elif choice == 3:
        choice_name = 'Scissors'
    elif choice == 4:
        choice_name = 'Lizard'
    else:
        choice_name = 'Spock'

    print('Player chose:', choice_name)

    print("Computer's turn....")
    comp_choice = random.randint(1, 5)
    if comp_choice == 1:
        comp_choice_name = 'Rock'
    elif comp_choice == 2:
        comp_choice_name = 'Paper'
    elif comp_choice == 3:
        comp_choice_name = 'Scissors'
    elif comp_choice == 4:
        comp_choice_name = 'Lizard'
    else:
        comp_choice_name = 'Spock'

    print("The computer chose:", comp_choice_name)
    print(choice_name, "versus", comp_choice_name)

    if choice == comp_choice:
        result = "It's a draw!"
    elif (choice == 1 and comp_choice in [3, 4]) or (choice == 2 and comp_choice in [1, 5]) or \
         (choice == 3 and comp_choice in [2, 4]) or (choice == 4 and comp_choice in [2, 5]) or \
         (choice == 5 and comp_choice in [1, 3]):
        result = "Player Wins!"
    else:
        result = "Computer Wins!"

    if result == "It's a draw!":
        print("<===It's a tie!===>")
    elif result == "Player Wins!":
        print("<===Player Wins!===>")
    else:
        print("<===Computer Wins!===>")

    print("Do you want to play again?(Y/N)")
    answer = input().lower()
    if answer == 'n':
        break

print("Thank you for playing!")
