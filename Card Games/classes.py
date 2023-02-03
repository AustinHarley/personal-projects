import random
from collections import Counter
from itertools import chain, combinations


class DeckOfCards:
    def __init__(self):
        self.nums_with_rank = {
            "3": 1,
            "4": 2,
            "5": 3,
            "6": 4,
            "7": 5,
            "8": 6,
            "9": 7,
            "10": 8,
            "Jack": 9,
            "Queen": 10,
            "King": 11,
            "Ace": 12,
            "2": 13,
        }
        self.suits_with_rank = {"Clubs": 1, "Spades": 2, "Diamonds": 3, "Hearts": 4}
        self.deck = self.generate_deck()

    def generate_deck(self, num_decks=1):
        deck = []
        for dnum in range(num_decks):
            for n, nr in self.nums_with_rank.items():
                for s, sr in self.suits_with_rank.items():
                    deck.append(f"{n} {s}")
        random.shuffle(deck)
        return deck

    def get_card_value(self, card):
        card_split = card.split(" ")
        card_num_rank = self.nums_with_rank[card_split[0]]
        card_suit_rank = self.suits_with_rank[card_split[1]]
        return float(f"{card_num_rank}.{card_suit_rank}")

    def deal_hands(
        self, player_count=4, player_names=["first", "second", "third", "fourth"]
    ):
        # TODO: allow input for player names
        if player_count in [2, 3]:
            self.deck = self.deck[1:]  # drop one card to make the deck divisible by 3
            chunk_count = 3
        elif player_count == 4:
            chunk_count = 4
        hand_chunks = {
            0: {val: self.get_card_value(val) for val in self.deck[::chunk_count]},
            1: {val: self.get_card_value(val) for val in self.deck[1::chunk_count]},
            2: {val: self.get_card_value(val) for val in self.deck[2::chunk_count]},
            3: {val: self.get_card_value(val) for val in self.deck[3::chunk_count]},
        }

        hands = {}
        for idx, player in enumerate(player_names[:player_count]):
            hands.update(
                {
                    player: {
                        k: v
                        for k, v in sorted(
                            hand_chunks[idx].items(), key=lambda item: item[1]
                        )
                    }
                }
            )
        self.hands = hands
        self.position_values = dict(
            zip(player_names, [i + 1 for i in range(len(player_names))])
        )
        self.position_values_reverse = {v: k for k, v in self.position_values.items()}

    def who_goes_first(self):
        self.all_hands_cards = [
            item for sublist in self.hands.values() for item in sublist
        ]
        for player, hand in self.hands.items():
            if {
                k: v
                for k, v in hand.items()
                if v
                == min([self.get_card_value(card) for card in self.all_hands_cards])
            }:
                return player

    def is_valid_hand(self, play, previous_play, hand, round_rule_type):
        errors = []
        cards_intersect_check = set(play).issubset(
            hand
        )  # do the cards played exist in the players hand
        rule_type_check = self.check_rule_type(play)
        rule_type_match_check = (
            rule_type_check == round_rule_type
        )  # do the played cards follow the set rule
        if previous_play:
            previous_rule_type_check = self.check_rule_type(previous_play)
            if previous_rule_type_check.startswith(
                "bomb"
            ) and not rule_type_check.startswith("bomb"):
                # bombs can only be beat by bombs
                errors.append(f"previous play was a bomb")
            elif previous_rule_type_check.startswith(
                "bomb"
            ) and rule_type_check.startswith("bomb"):
                pass
            elif not previous_rule_type_check.startswith(
                "bomb"
            ) and rule_type_check.startswith("bomb"):
                pass
            else:
                # this doesn't matter if the above is true
                value_higher_check = max(play) > max(
                    previous_play
                )  # highest played card must exceed highest card in previous play
                if not value_higher_check:
                    errors.append(
                        f"highest value {max(play)} in play is not greater than previous play {max(previous_play)}"
                    )
        else:
            # no previous play means this is the round stater, has to utilize their 3 clubs
            if (
                min([self.get_card_value(card) for card in self.all_hands_cards])
                not in play
                and min([self.get_card_value(card) for card in self.all_hands_cards])
                in hand
            ):
                errors.append("the round starter must utilize their 3 of Clubs")
        if not cards_intersect_check:
            errors.append("some cards do not exist in your hand")
        if not rule_type_check.startswith("bomb"):
            # skip this if the played hand is a bomb
            if not rule_type_check:
                errors.append("play does not adhere to a valid rule type")
            if not rule_type_match_check and round_rule_type:
                errors.append(
                    f"play does not match the round rule type of {round_rule_type}"
                )

        if errors:
            return {"is_valid": False, "errors": ", ".join(errors)}
        else:
            return {"is_valid": True, "errors": None}

    def check_consecutive(self, l):
        return sorted(l) == list(range(min(l), max(l) + 1))

    def check_rule_type(self, cards):
        cards_numbers = [int(str(i).split(".")[0]) for i in cards]  # .values()
        cards_numbers_unique_counter = Counter(cards_numbers)
        found_triples = {
            k: v for k, v in cards_numbers_unique_counter.items() if v == 3
        }
        found_doubles = {
            k: v for k, v in cards_numbers_unique_counter.items() if v == 2
        }
        cards_suits = [int(str(i).split(".")[1]) for i in cards]  # .values()
        if len(cards) == 1:
            rule_type = "singles"
        elif len(set(cards_numbers)) == 1 and len(cards) == 2:
            rule_type = "doubles"
        elif len(set(cards_numbers)) == 1 and len(cards) == 3:
            rule_type = "triples"
        elif len(set(cards_numbers)) == 1 and len(cards) == 4:
            rule_type = "bomb (quads)"
        elif (len(set(cards_numbers)) == len(cards_numbers)) and len(
            cards_numbers
        ) >= 3:
            if self.check_consecutive(cards_numbers):
                rule_type = f"straight ({len(cards_numbers)})"
            else:
                rule_type = None
        elif len(set(cards_numbers)) == 2 and len(found_triples.keys()) == 2:
            if self.check_consecutive(set(cards_numbers)):
                rule_type = "bomb (triple straight)"
            else:
                rule_type = None
        elif len(set(cards_numbers)) == 3 and len(found_doubles.keys()) == 3:
            if self.check_consecutive(set(cards_numbers)):
                rule_type = "bomb (double straight)"
            else:
                rule_type = None
        else:
            rule_type = None
        return rule_type

    def number_of_hands_with_bombs(self):
        found_bomb_hands = []
        for pos, hand in self.hands.items():
            hand_values = list(hand.values())
            found_bomb_variants = []
            for i in range(0, 10000):
                # just try a bunch of times to find a variant that is a bomb
                random.shuffle(hand_values)
                rule_type = self.check_rule_type(hand_values[:6])
                if rule_type and rule_type.startswith("bomb"):
                    found_bomb_variants.append(hand_values[:6])
            if found_bomb_variants:
                found_bomb_hands.append(pos)
        print(found_bomb_hands)
        return len(found_bomb_hands)

    def get_all_combinations(self, stuff):
        def powerset(iterable):
            "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
            s = list(iterable)  # allows duplicate elements
            return chain.from_iterable(combinations(s, r) for r in range(len(s) + 1))

        combos = []
        for i, combo in enumerate(powerset(stuff), 1):
            combos.append(combo)
        return combos

    def guess_next_play(self, previous_play, hand):
        if previous_play:
            previous_play_max = max(previous_play)
            previous_play_rule = self.check_rule_type(previous_play)
            # TODO: this can be made much more efficient by eliminating the duplicate rule type checking
            if previous_play_rule == "singles":
                found_plays = [i for i in hand if i > previous_play_max]
                if found_plays:
                    play = found_plays[0]
                else:
                    play = "pass"
            else:
                cards_numbers = [int(str(i).split(".")[0]) for i in hand]  # .values()
                cards_numbers_unique_counter = Counter(cards_numbers)
                found_dupes = {
                    k: v for k, v in cards_numbers_unique_counter.items() if v >= 2
                }
                if found_dupes:
                    dupe_cards = [
                        i
                        for i in hand
                        if int(str(i).split(".")[0]) in found_dupes.keys()
                    ]  # narrow the results so that the combo finder is quicker
                    combos = self.get_all_combinations(dupe_cards)
                    all_types = [self.check_rule_type(combo) for combo in combos]
                    all_types_dict = dict(
                        zip(
                            [typ for typ in set(all_types) if typ != None],
                            [[] for i in range(len(set(all_types)))],
                        )
                    )
                    for rule_type in all_types_dict.keys():
                        all_types_dict.update(
                            {
                                rule_type: [
                                    i
                                    for i in combos
                                    if self.check_rule_type(i) == rule_type
                                ]
                            }
                        )
                    found_bombs = [i for i in all_types if i and i.startswith("bomb")]
                    if previous_play_rule in all_types_dict.keys():
                        found_plays = [
                            i
                            for i in all_types_dict[previous_play_rule]
                            if max(i) > previous_play_max
                        ]
                        if found_plays:
                            play = found_plays[0]
                        else:
                            play = "pass"
                    elif previous_play_rule.startswith("bomb"):
                        if found_bombs:
                            found_plays = [i for i in all_types_dict[found_bombs[0]]]
                            play = found_plays[0]
                        else:
                            play = "pass"
                    else:
                        play = "pass"
        else:
            play = min(hand)
        return play
