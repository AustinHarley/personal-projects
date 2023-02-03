import random
from classes import *
import pandas as pd
from tabulate import tabulate

# TODO: why is the winner declared if the non-bot user still has higher to play? it looks like the bots can't win against each other if non-bot passes (3+ player)

if __name__ == "__main__":
    doc = DeckOfCards()
    player_count_message = """how many players?     
    2: each player gets 17 cards, third is discarded along with top card
    3: each player gets 17 cards, top card is discarded to round out
    4: each player gets 13 cards (traditional)
    TODO: 4 player should give teams option\n"""
    player_count = input(player_count_message)
    is_valid_player_count = player_count.strip().isdigit()
    while not is_valid_player_count:
        player_count = input(player_count_message)

    doc.deal_hands(int(player_count))
    bot_players = {"first": False}
    for player_no in range(2, int(player_count) + 1):
        bot_players.update({doc.position_values_reverse[player_no]: True})

    # if doc.number_of_hands_with_bombs() > 1:
    winner_declared = False
    round_count = 0
    round_winner = ""
    while not winner_declared:
        round_is_active = True
        active_players = list(doc.hands.keys())
        round_rule_type = ""
        turn_count = 0
        previous_play = []
        if round_count == 0:
            active_player = doc.who_goes_first()
            print(f"{active_player} has the lowest card and will start the game\n")
        else:
            print(f"{round_winner} won the last round and will start this round")
            active_player = round_winner
        while round_is_active:
            if len(active_players) == 1:
                print(f"{active_player} has won this round after {turn_count} turns")
                round_is_active = False
                round_winner = active_player
                break
            elif active_player not in active_players:
                print(f"{active_player} has already passed")
            else:
                if not bot_players[active_player]:
                    print(f"{active_player}, this is your hand:")
                card_position_num = 1
                card_position_map = {}
                for k, v in doc.hands[active_player].items():
                    card_position_map.update({card_position_num: v})
                    card_position_num += 1
                card_position_map_reverse = {v: k for k, v in card_position_map.items()}
                if not bot_players[active_player]:
                    hand_df = pd.DataFrame(
                        {
                            "display": doc.hands[active_player].keys(),
                            "value": doc.hands[active_player].values(),
                        }
                    ).T
                    hand_df.columns = [i + 1 for i in hand_df.columns]
                    hand_df = hand_df.reset_index().rename(
                        columns={"index": "position"}
                    )
                    print(
                        tabulate(
                            hand_df,
                            headers="keys",
                            tablefmt="fancy_grid",
                            showindex=False,
                        )
                    )
                if turn_count > 0 and not bot_players[active_player]:
                    print(f"the previous play was {previous_play}")
                if bot_players[active_player]:
                    play_input = doc.guess_next_play(
                        previous_play, doc.hands[active_player].values()
                    )
                    if isinstance(play_input, tuple):
                        print(play_input)
                        play_input = ",".join(
                            [str(card_position_map_reverse[i]) for i in play_input]
                        )
                    elif play_input == "pass":
                        play_input = "pass"
                    else:
                        play_input = str(card_position_map_reverse[play_input])
                else:
                    play_input = input(
                        f"please type card or list of cards (comma sep) that you would like to play: "
                    )
                if str(play_input).lower() == "pass" and turn_count > 0:
                    # TODO: FIRST PLAYER CANNOT PASS
                    active_players.remove(active_player)
                else:
                    played_cards = [card.strip() for card in play_input.split(",")]
                    if all([str(card).isdigit() for card in played_cards]):
                        # check if all played cards are ints
                        played_cards = [
                            card_position_map[int(card)] for card in played_cards
                        ]
                        is_valid_hand = doc.is_valid_hand(
                            play=played_cards,
                            previous_play=previous_play,
                            hand=doc.hands[active_player].values(),
                            round_rule_type=round_rule_type,
                        )
                    else:
                        played_cards = []
                        is_valid_hand = {
                            "is_valid": False,
                            "errors": "input must be whole numbers (position)",
                        }
                    passed_mid_play = False
                    if not is_valid_hand["is_valid"]:
                        while not is_valid_hand["is_valid"]:
                            print(f"invalid play, {is_valid_hand['errors']}")
                            play_input = input(
                                f"please type card or list of cards (comma sep) that you would like to play: "
                            )
                            if str(play_input).lower() == "pass":
                                active_players.remove(active_player)
                                is_valid_hand["is_valid"] = True
                                passed_mid_play = True
                            else:
                                played_cards = [
                                    card.strip() for card in play_input.split(",")
                                ]
                                if all([str(card).isdigit() for card in played_cards]):
                                    # check if all played cards are ints
                                    played_cards = [
                                        card_position_map[int(card)]
                                        for card in played_cards
                                    ]
                                    is_valid_hand = doc.is_valid_hand(
                                        play=played_cards,
                                        previous_play=previous_play,
                                        hand=doc.hands[active_player].values(),
                                        round_rule_type=round_rule_type,
                                    )
                                else:
                                    played_cards = []
                                    is_valid_hand = {
                                        "is_valid": False,
                                        "errors": "input must be whole numbers (position)",
                                    }

                    if not passed_mid_play:
                        if bot_players[active_player]:
                            print(f"{active_player} played {played_cards}")
                        doc.hands[active_player] = {
                            k: v
                            for k, v in doc.hands[active_player].items()
                            if v not in played_cards
                        }
                        previous_play = played_cards
                        if not doc.hands[active_player]:
                            print(
                                f"{active_player} has emptied their hand and is the winner"
                            )
                            winner_declared = True
                            break
                    if turn_count == 0:
                        round_rule_type = doc.check_rule_type(played_cards)
                        print(
                            f"{active_player} has set the rule type for this round as {round_rule_type}\n"
                        )
            next_player_value = doc.position_values[active_player] + 1
            if next_player_value > int(player_count):
                next_player_value = 1
            print(
                f"the next player will be {doc.position_values_reverse[next_player_value]}\n"
            )
            active_player = doc.position_values_reverse[next_player_value]
            turn_count += 1
        round_count += 1
