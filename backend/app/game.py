import random
from typing import Dict, List, Callable, Any

from .models import Game, Lobby, Player, Card, GameState, Effect, PlayerStatus, CardType, Rarity, Character
from .content import common_cards, characters
from .exceptions import GameException

# Effect IDs
EFFECT_ID_SOUL_DISTORTION = "mahito_self_embodiment_of_perfection" # Махито РТ дебафф
EFFECT_ID_UNLIMITED_VOID = "gojo_unlimited_void" # Годзё РТ дебафф
EFFECT_ID_DIVERGENT_FIST_DOT = "itadori_divergent_fist_dot"
EFFECT_ID_BURN = "jogo_burn"
EFFECT_ID_FREE_STRIKE = "free_strike_effect"

class GameManager:
    def __init__(self):
        self.games: Dict[str, Game] = {}
        self.lobbies: Dict[str, Lobby] = {}

    def get_lobby(self, lobby_id: str) -> Lobby | None:
        return self.lobbies.get(lobby_id)

    def get_game(self, game_id: str) -> Game | None:
        return self.games.get(game_id)

    def create_lobby(self, host_id: str, nickname: str) -> Lobby:
        lobby_id = f"lobby_{len(self.lobbies) + 1}"
        lobby = Lobby(id=lobby_id, host_id=host_id, players=[Player(id=host_id, nickname=nickname)])
        self.lobbies[lobby_id] = lobby
        return lobby

    def join_lobby(self, lobby_id: str, player_id: str, nickname: str) -> Lobby:
        lobby = self.get_lobby(lobby_id)
        if not lobby:
            raise GameException("Лобби не найдено.")
        if len(lobby.players) >= 8:
            raise GameException("Лобби заполнено.")
        if any(p.id == player_id for p in lobby.players):
             raise GameException("Игрок уже в лобби.")
        
        lobby.players.append(Player(id=player_id, nickname=nickname))
        return lobby

    def select_character(self, lobby_id: str, player_id: str, character_id: str) -> Lobby:
        lobby = self.get_lobby(lobby_id)
        if not lobby: raise GameException("Лобби не найдено.")
        
        player = self._find_player_in_lobby(lobby, player_id)
        if not player: raise GameException("Игрок не найден.")

        if any(p.character and p.character.id == character_id for p in lobby.players):
            raise GameException("Этот персонаж уже выбран.")

        character = next((c for c in characters if c.id == character_id), None)
        if not character: raise GameException("Персонаж не найден.")

        player.character = character
        player.hp = character.max_hp
        player.energy = character.max_energy
        return lobby
    
    def start_game(self, lobby: Lobby) -> Game:
        game = self._create_game_from_lobby(lobby)
        self.games[game.game_id] = game
        # The lobby is deleted in the LobbyManager now
        return game

    def play_card(self, game_id: str, player_id: str, card_id: str, target_id: str = None, targets_ids: list = None) -> Game:
        game = self.get_game(game_id)
        if not game: raise GameException("Игра не найдена.")
        if game.players[game.current_turn_player_index].id != player_id: raise GameException("Сейчас не ваш ход.")

        player = self._find_player(game, player_id)
        if not player: raise GameException("Игрок не найден.")

        card_to_play = next((card for card in player.hand if card.id == card_id), None)
        if not card_to_play: raise GameException("Карта не найдена в руке.")

        is_free_udar = card_to_play.id == "common_strike" and any(e.name == EFFECT_ID_FREE_STRIKE for e in player.effects)
        
        player.chant_active_for_turn = False
        chant_effect = next((e for e in player.effects if e.name == "common_chant"), None)
        if chant_effect and card_to_play.type == CardType.TECHNIQUE:
            player.chant_active_for_turn = True

        card_cost = card_to_play.cost
        # Apply Gojo's discount
        if player.character and player.character.id == "gojo_satoru":
            card_cost = int(card_cost * player.cost_modifier)
        
        # Apply Yuta's domain discount
        if card_to_play.is_copied and any(e.name == "yuta_true_mutual_love" for e in player.effects):
            card_cost = -(-card_cost // 4) # Ceiling division

        # Manji Kick counter check on the one being attacked
        target = self._find_player(game, target_id)
        if target:
            manji_kick_counter = next((e for e in target.effects if e.name == "manji_kick_counter" and e.source_player_id == player.id), None)
            is_attacking_card = card_to_play.type in [CardType.TECHNIQUE, CardType.ACTION] and "Наносит" in card_to_play.description
            
            if manji_kick_counter and is_attacking_card and card_to_play.type != CardType.DOMAIN_EXPANSION:
                game.game_log.append(f"Атака {player.nickname} на {target.nickname} была отменена эффектом 'Манджи-Кик'!")
                target.effects.remove(manji_kick_counter)
                # We still need to discard the card and pay the cost
                player.energy -= card_cost
                player.hand.remove(card_to_play)
                player.discard_pile.append(card_to_play)
                return game

        if not game.is_training:
            if not is_free_udar and player.energy < card_cost:
                raise GameException("Недостаточно Проклятой Энергии.")

        # --- Card specific cost checks ---
        if card_to_play.id == "mahito_polymorphic_soul_isomer":
            if player.distorted_souls < 1: raise GameException("Недостаточно Искажённых Душ.")
            player.distorted_souls -= 1
        
        if card_to_play.id == "mahito_body_repel":
            if player.distorted_souls < 3: raise GameException("Недостаточно Искажённых Душ.")
            player.distorted_souls -= 3

        # --- Conditional Cards ---
        if card_to_play.id == "gojo_purple":
            if not ("gojo_blue_effect" in [e.name for e in player.effects]) or not ("gojo_red_effect" in [e.name for e in player.effects]):
                raise GameException("Нужно сначала использовать 'Синий' и 'Красный'.")
        
        if card_to_play.id == "mahito_true_form":
            if not player.successful_black_flash:
                raise GameException(f"Нужно сначала успешно использовать 'Чёрную Вспышку'.")
        
        if card_to_play.id == "gojo_remove_blindfold":
            if player.hp > player.character.max_hp * 0.33:
                raise GameException("Можно использовать только если ХП меньше или равно 33%.")

        # --- Domain Expansion Effects ---
        if any(e.name == EFFECT_ID_UNLIMITED_VOID for e in player.effects):
            if card_to_play.type == CardType.TECHNIQUE or card_to_play.rarity in [Rarity.EPIC, Rarity.LEGENDARY]:
                raise GameException("Вы не можете использовать эту карту из-за 'Информационной перегрузки'.")

        if not is_free_udar:
            player.energy -= card_cost
        else:
            effect = next((e for e in player.effects if e.name == EFFECT_ID_FREE_STRIKE), None)
            if effect: player.effects.remove(effect)

        player.hand.remove(card_to_play)
        player.discard_pile.append(card_to_play)
        
        if player.chant_active_for_turn:
            if chant_effect: player.effects.remove(chant_effect)

        if targets_ids:
            target_names = [self._find_player(game, tid).nickname for tid in targets_ids if self._find_player(game, tid)]
            game.game_log.append(f"{player.nickname} играет {card_to_play.name} на {', '.join(target_names)}")
        elif target_id:
            target = self._find_player(game, target_id)
            game.game_log.append(f"{player.nickname} играет {card_to_play.name} на {target.nickname}")
        else:
            game.game_log.append(f"{player.nickname} играет {card_to_play.name}")
        
        effect_function = self._get_effect_function(card_id)
        if effect_function:
            game = effect_function(game, player, target_id, targets_ids)

        self._check_for_defeated_players(game)
        if game.game_state != GameState.FINISHED:
            self._check_game_over(game)

        if game.is_training:
            player.hand.append(card_to_play.copy(deep=True))

        player.chant_active_for_turn = False
        return game

    def end_turn(self, game_id: str, player_id: str) -> Game:
        game = self.get_game(game_id)
        if not game or game.game_state == GameState.FINISHED: return game
        if game.players[game.current_turn_player_index].id != player_id: raise GameException("Сейчас не ваш ход.")

        player = self._find_player(game, player_id)
        self._process_passives(game, player)
        self._process_end_of_turn_effects(game, player)
        
        current_turn_index = game.current_turn_player_index
        next_turn_index = (current_turn_index + 1) % len(game.players)

        # Skip defeated players
        while game.players[next_turn_index].status == PlayerStatus.DEFEATED:
            if next_turn_index == current_turn_index:
                # All other players are defeated, end the game
                self._check_game_over(game)
                return game
            next_turn_index = (next_turn_index + 1) % len(game.players)

        # Skip turns for dummies
        if game.is_training:
            while "dummy" in game.players[next_turn_index].id:
                if next_turn_index == current_turn_index:
                    # This should not happen, but as a safeguard
                    break
                next_turn_index = (next_turn_index + 1) % len(game.players)

        # Check if a full round has passed
        if next_turn_index <= current_turn_index:
             self._start_new_round(game)
        
        game.current_turn_player_index = next_turn_index
        new_current_player = game.players[game.current_turn_player_index]
        self._process_start_of_turn_effects(game, new_current_player)

        return game

    def discard_cards(self, game_id: str, player_id: str, card_ids: List[str]) -> Game:
        game = self.get_game(game_id)
        player = self._find_player(game, player_id)
        
        if player.last_discard_round == game.round_number:
            raise GameException("Вы уже сбрасывали карты в этом раунде.")
        if len(card_ids) > 2:
            raise GameException("Можно сбросить не более 2 карт.")

        discarded_count = 0
        for cid in card_ids:
            card = next((c for c in player.hand if c.id == cid), None)
            if card:
                player.hand.remove(card)
                player.discard_pile.append(card)
                discarded_count += 1
        
        self._draw_cards(player, len(player.hand) + discarded_count)
        player.last_discard_round = game.round_number
        return game

    # --- Private Helper Methods ---

    def _start_new_round(self, game: Game):
        game.round_number += 1
        game.game_log.append(f"--- Начинается раунд {game.round_number} ---")
        
        for p in game.players:
            if p.status == PlayerStatus.ALIVE:
                # Gojo's cost reduction
                if p.character and p.character.id == "gojo_satoru" and not p.is_blindfolded:
                    p.cost_modifier = max(0.10, p.cost_modifier - 0.05)

                if game.is_training and "dummy" in p.id:
                    p.hp = p.max_hp
                    continue
                
                p.block = 0
                max_hand = 5
                if p.character and p.character.id == "gojo_satoru": max_hand = 6
                if any(e.name == EFFECT_ID_SOUL_DISTORTION for e in p.effects): max_hand -= 1
                if any(e.name == "yuta_true_mutual_love" for e in p.effects): max_hand = 8
                
                self._draw_cards(p, max_hand)
                if p.character:
                    p.energy = min(p.character.max_energy, p.energy + int(p.character.max_energy * 0.10))
        
        # Determine turn order for the new round
        start_index = game.current_turn_player_index
        game.current_turn_player_index = (start_index + 1) % len(game.players)

        # Ensure the real player always starts first in training
        if game.is_training:
            real_player_index = next((i for i, p in enumerate(game.players) if "dummy" not in p.id), 0)
            game.players.insert(0, game.players.pop(real_player_index))

    def _draw_cards(self, player: Player, max_hand_size: int):
        cards_to_draw_count = max_hand_size - len(player.hand)
        if cards_to_draw_count <= 0:
            return

        # Combine deck and discard for drawing
        draw_pool = player.deck + player.discard_pile
        player.deck = []
        player.discard_pile = []
        random.shuffle(draw_pool)

        drawn_cards = []
        
        # Check for guaranteed cards
        has_action = any(c.type == CardType.ACTION for c in player.hand)
        has_technique = any(c.type == CardType.TECHNIQUE for c in player.hand)

        # Find guaranteed action card
        if not has_action:
            for i, card in enumerate(draw_pool):
                if card.type == CardType.ACTION:
                    drawn_cards.append(draw_pool.pop(i))
                    break
        
        # Find guaranteed technique card
        if not has_technique:
            for i, card in enumerate(draw_pool):
                if card.type == CardType.TECHNIQUE:
                    drawn_cards.append(draw_pool.pop(i))
                    break
        
        # Draw the rest of the cards needed
        remaining_to_draw = cards_to_draw_count - len(drawn_cards)
        if remaining_to_draw > 0:
            # Technique anti-drought mechanism
            cards_to_be_drawn = draw_pool[:remaining_to_draw]
            rest_of_deck = draw_pool[remaining_to_draw:]

            if not any(c.type == CardType.TECHNIQUE for c in cards_to_be_drawn) and any(c.type == CardType.TECHNIQUE for c in rest_of_deck):
                first_tech_index = -1
                for i, card in enumerate(rest_of_deck):
                    if card.type == CardType.TECHNIQUE:
                        first_tech_index = i
                        break
                
                if first_tech_index != -1:
                    technique_to_move = rest_of_deck.pop(first_tech_index)
                    card_to_swap = cards_to_be_drawn.pop(-1) if cards_to_be_drawn else None
                    cards_to_be_drawn.append(technique_to_move)
                    if card_to_swap:
                        rest_of_deck.insert(0, card_to_swap)
            
            draw_pool = cards_to_be_drawn + rest_of_deck
            
            # Final draw
            drawn_cards.extend(draw_pool[:remaining_to_draw])
            draw_pool = draw_pool[remaining_to_draw:]
            
        player.hand.extend(drawn_cards)
        player.deck = draw_pool # The rest of the cards form the new deck

    def _create_game_from_lobby(self, lobby: Lobby) -> Game:
        game = Game(game_id=lobby.id.replace("lobby", "game"), players=lobby.players, is_training=lobby.is_training)

        if lobby.is_training:
            player = lobby.players[0]
            player.max_hp = player.character.max_hp
            player.hp = player.character.max_hp
            player.energy = player.character.max_energy
            all_cards = [card.copy(deep=True) for card in player.character.unique_cards]
            all_cards.extend([card.copy(deep=True) for card in common_cards])
            player.hand = all_cards
            
            for i in range(7):
                dummy_id = f"dummy_{i+1}"
                dummy = Player(id=dummy_id, nickname=f"Манекен {i+1}", hp=10000, max_hp=10000, energy=0, block=0, status=PlayerStatus.ALIVE)
                game.players.append(dummy)
        else:
            random.shuffle(lobby.players)
            for p in lobby.players:
                p.max_hp = p.character.max_hp
                p.energy = int(p.character.max_energy * 0.20)
                self._build_deck_for_player(p)
                max_hand = 5
                if p.character and p.character.id == "gojo_satoru":
                    max_hand = 6
                    self._apply_effect(game, p, p, "gojo_blindfold", 999)
                self._draw_cards(p, max_hand)
        
        game.game_log.append("--- Игра начинается! ---")
        return game

    def _build_deck_for_player(self, player: Player):
        deck = []
        # Add common cards with new rules
        for card in common_cards:
            if card.type == CardType.ANTI_DOMAIN_TECHNIQUE:
                deck.append(card.copy(deep=True)) # 1 copy
            else:
                deck.extend([card.copy(deep=True)] * 2) # 2 copies

        # Add unique character cards
        deck.extend([card.copy(deep=True) for card in player.character.unique_cards])
        random.shuffle(deck)
        player.deck = deck

    def _process_passives(self, game: Game, player: Player):
        # Sukuna's Malevolent Shrine
        shrine_effect = next((e for e in player.effects if e.name == "sukuna_malevolent_shrine"), None)
        if shrine_effect:
            # Check for Simple Domain
            if not any(e.name == "common_simple_domain" for e in player.effects):
                source_player = self._find_player(game, shrine_effect.source_player_id)
                if source_player:
                    self._deal_damage(game, source_player, player, 1500, ignores_block=True, is_effect_damage=True)
        
        if player.character and player.character.id == "yuta_okkotsu":
            opponents = [p for p in game.players if p.id != player.id and p.status == PlayerStatus.ALIVE]
            if opponents:
                # Check for "Проявление: Рика" effect
                rika_manifested = any(e.name == "yuta_rika_manifestation" for e in player.effects)
                if rika_manifested:
                    left_player = self._get_left_player(game, self._get_player_index(game, player.id))
                    right_player = self._get_right_player(game, self._get_player_index(game, player.id))
                    if left_player and left_player.id != player.id:
                        self._deal_damage(game, player, left_player, 1000)
                    if right_player and right_player.id != player.id:
                        self._deal_damage(game, player, right_player, 1000)
                else:
                    target = random.choice(opponents)
                    self._deal_damage(game, player, target, 250)
        
        if any(e.name == "mahito_true_form" for e in player.effects):
            player.block += 500

    def _process_start_of_turn_effects(self, game: Game, player: Player):
        # Mahito's passive Soul Touch card
        if player.character and player.character.id == "mahito":
            player.mahito_turn_counter += 1
            if player.mahito_turn_counter >= 2:
                soul_touch_card = next((c.copy(deep=True) for c in player.character.unique_cards if c.id == "mahito_soul_touch"), None)
                if soul_touch_card:
                    player.hand.append(soul_touch_card)
                    player.mahito_turn_counter = 0
                    game.game_log.append(f"{player.nickname} получает 'Касание Души' в руку благодаря своей пассивной способности.")

        # Mahito's Domain soul gain
        if player.character and player.character.id == "mahito":
            opponents_in_domain = sum(1 for p in game.players if any(e.name == EFFECT_ID_SOUL_DISTORTION and e.source_player_id == player.id for e in p.effects))
            if opponents_in_domain > 0:
                player.distorted_souls += opponents_in_domain
                game.game_log.append(f"{player.nickname} получает {opponents_in_domain} Искажённых Душ от своей территории.")
        
        effects_to_remove = []
        for effect in player.effects:
            effect.duration -= 1
            if effect.name == EFFECT_ID_BURN: self._deal_damage(game, player, player, effect.value, is_effect_damage=True)
            if effect.name == "jogo_coffin_of_the_iron_mountain": self._deal_damage(game, player, player, 800, is_effect_damage=True)
            if effect.name == EFFECT_ID_DIVERGENT_FIST_DOT: 
                source_player = self._find_player(game, effect.source_player_id)
                if source_player:
                    self._deal_damage(game, source_player, player, 200, is_effect_damage=True)

            if effect.name == "zone":
                recovery = int(player.character.max_energy * 0.05)
                player.energy = min(player.character.max_energy, player.energy + recovery)
                game.game_log.append(f"{player.nickname} восстанавливает {recovery} ПЭ от эффекта 'Зона'.")

            if effect.duration <= 0:
                effects_to_remove.append(effect)

        for effect in effects_to_remove:
            player.effects.remove(effect)
            if effect.name == "itadori_unwavering_will": self._defeat_player(game, player)

    def _process_end_of_turn_effects(self, game: Game, player: Player):
        pass # Placeholder for now

    def _deal_damage(self, game: Game, source_player: Player, target: Player, damage: int, ignores_block: bool = False, card: Card = None, card_type: CardType = None, is_effect_damage: bool = False):
        if target.status == PlayerStatus.DEFEATED:
            return

        final_damage = damage
        
        # Polymorphic Soul Isomer backlash
        isomer_effect = next((e for e in target.effects if e.name == "mahito_polymorphic_soul_isomer"), None)
        if isomer_effect and not ignores_block and final_damage > target.block:
            self._deal_damage(game, None, source_player, 500, ignores_block=True, is_effect_damage=True)
            game.game_log.append(f"{source_player.nickname} получает 500 ответного урона от 'Полиморфной Изомерной Души'!")
            target.effects.remove(isomer_effect)

        # Apply Zone effect bonus for the attacker
        if source_player and card_type == CardType.TECHNIQUE and any(e.name == "zone" for e in source_player.effects):
            final_damage = int(final_damage * 1.25)
            
        # Apply Yuta's passive
        if not is_effect_damage and target.character and target.character.id == "yuta_okkotsu" and card and card.type == CardType.TECHNIQUE:
            copied_card = card.copy(deep=True)
            copied_card.cost = int(copied_card.cost * 1.25)
            copied_card.is_copied = True
            target.discard_pile.append(copied_card)
            game.game_log.append(f"Юта Оккоцу скопировал {card.name}!")

        # Sukuna Passive (Energy)
        if target.character and target.character.id == "sukuna_ryomen" and \
           source_player and source_player.character and source_player.hp and target.character and target.hp and \
           (source_player.hp / source_player.max_hp) > (target.hp / target.max_hp):
             restore_amount = int(target.character.max_energy * 0.05)
             target.energy = min(target.character.max_energy, target.energy + restore_amount)
             game.game_log.append(f"Жажда Развлечений дарует {target.nickname} {restore_amount} ПЭ!")
        
        # Jogo Passive (Burn)
        if source_player and source_player.character and source_player.character.id == "jogo" and card_type == CardType.TECHNIQUE:
            existing_burn = next((e for e in target.effects if e.name == EFFECT_ID_BURN), None)
            if existing_burn:
                existing_burn.duration = 2
                game.game_log.append(f"Эффект 'Горение' на {target.nickname} обновлён.")
            else:
                self._apply_effect(game, source_player, target, EFFECT_ID_BURN, 2, value=100)

        actual_damage = final_damage
        if source_player.chant_active_for_turn:
            actual_damage = int(actual_damage * 1.5)

        if any(e.name == "common_falling_blossom_emotion" for e in target.effects):
            actual_damage = int(actual_damage * 0.67) # Reduce damage by 33%

        # Mahito's "True Body" damage reduction
        if any(e.name == "mahito_true_form" for e in target.effects) and card and card.id == "common_strike":
            actual_damage = int(actual_damage * 0.5)

        if not ignores_block:
            blocked_damage = min(target.block, actual_damage)
            target.block -= blocked_damage
            actual_damage -= blocked_damage
        else:
            # Mahito condition counter
            source_player.ignore_block_attacks_count += 1
        
        target.hp -= actual_damage
        game.game_log.append(f"{source_player.nickname} наносит {actual_damage} урона {target.nickname}.")

        if target.hp <= 0 and not any(e.name == "itadori_unwavering_will" for e in target.effects):
            self._defeat_player(game, target)

    def _defeat_player(self, game: Game, player: Player):
        player.status = PlayerStatus.DEFEATED
        player.hp = 0
        game.game_log.append(f"{player.nickname} был побежден!")

    def _check_for_defeated_players(self, game: Game):
        for p in game.players:
            if p.hp <= 0 and p.status == PlayerStatus.ALIVE and not any(e.name == "itadori_unwavering_will" for e in p.effects):
                self._defeat_player(game, p)

    def _check_game_over(self, game: Game):
        alive_players = [p for p in game.players if p.status == PlayerStatus.ALIVE]
        if len(alive_players) <= 1:
            game.game_state = GameState.FINISHED
            winner = alive_players[0] if alive_players else None
            game.game_log.append("Игра окончена." + (f" Победитель: {winner.nickname}!" if winner else ""))

    # --- Card Effect Functions ---
    def _apply_effect(self, game: Game, source: Player, target: Player, name: str, duration: int, value: Any = None, target_id: str = None):
        target.effects.append(Effect(name=name, duration=duration, value=value, source_player_id=source.id, target_id=target_id))
        effect_card = next((c for c in common_cards + source.character.unique_cards if c.id == name), None)
        effect_name_for_log = effect_card.name if effect_card else name
        game.game_log.append(f"{target.nickname} получает эффект '{effect_name_for_log}' на {duration} раунда.")

    def _effect_udar(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        target = self._find_player(game, target_id)
        if not target: return game
        
        damage = 300
        if player.character and player.character.id == "itadori_yuji": 
            damage += 150
            player.energy = min(player.character.max_energy, player.energy + 1000)
        if any(e.name == "mahito_true_form" for e in player.effects): damage *= 3
        
        final_damage = damage
        if target.character and target.character.id == "mahito": final_damage = 0
        if any(e.name == "mahito_true_form" for e in target.effects): final_damage = int(damage * 0.5)

        card = next(c for c in common_cards if c.id == 'common_strike')
        self._deal_damage(game, player, target, final_damage, card=card, card_type=card.type)
        return game

    def _effect_zashchita(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        player.block += 300
        return game

    def _effect_kontsentratsiia(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        if player.character:
            restore_percent = random.randint(5, 15) / 100
            restore_amount = int(player.character.max_energy * restore_percent)
            player.energy = min(player.character.max_energy, player.energy + restore_amount)
            game.game_log.append(f"{player.nickname} восстанавливает {restore_amount} ПЭ.")
        return game

    def _effect_pesnopenie(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        self._apply_effect(game, player, player, "common_chant", 1)
        return game
    
    def _effect_prostaia_territoriia(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        self._apply_effect(game, player, player, "common_simple_domain", 2)
        return game

    def _effect_chuvstva_opadaiushchego_tsvetka(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        self._apply_effect(game, player, player, "common_falling_blossom_emotion", 3)
        return game

    def _effect_obratnaia_proklaiataia_tekhnika(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        if player.character:
            heal_percent = random.randint(5, 15) / 100
            heal_amount = int(player.character.max_hp * heal_percent)
            player.hp = min(player.character.max_hp, player.hp + heal_amount)
            game.game_log.append(f"{player.nickname} восстанавливает {heal_amount} ХП.")
        return game

    def _effect_chernaia_vspyshka(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        target = self._find_player(game, target_id)
        if not target: return game

        is_itadori = player.character and player.character.id == "itadori_yuji"
        has_zone = any(e.name == "zone" for e in player.effects)
        
        chance = 1
        if is_itadori:
            chance = 3 if has_zone else 2
        elif has_zone:
            chance = 2

        roll = random.randint(1, 6)
        is_success = roll <= chance

        if any(e.name == "itadori_deep_concentration" for e in player.effects):
            is_success = True
            effect = next(e for e in player.effects if e.name == "itadori_deep_concentration")
            player.effects.remove(effect)
        
        card_being_played = next(c for c in common_cards if c.id == 'common_black_flash')

        if is_success:
            player.successful_black_flash = True
            self._deal_damage(game, player, target, 2500, card=card_being_played, card_type=CardType.TECHNIQUE)
            self._apply_effect(game, player, player, "zone", 4) # 3 of their turns + current
            game.game_log.append(f"{player.nickname} попадает Чёрной Вспышкой!")
        else:
            self._deal_damage(game, player, target, 100, card=card_being_played, card_type=CardType.TECHNIQUE)
            game.game_log.append(f"Чёрная Вспышка {player.nickname} не срабатывает...")
        return game

    def _effect_usilennyi_udar(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        target = self._find_player(game, target_id)
        if not target: return game
        self._deal_damage(game, player, target, 300, ignores_block=True, card_type=CardType.ACTION)
        return game

    def _effect_neitral(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        target = self._find_player(game, target_id)
        if not target: return game
        self._apply_effect(game, player, player, "gojo_infinity", 1, target_id=target.id)
        return game

    def _effect_sinii(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        if any(e.name == "gojo_blue_effect" for e in player.effects):
            game.game_log.append("Эффект 'Синий' уже активен.")
            # Still deal damage, just don't apply the effect again
            opponents = [p for p in game.players if p.id != player.id and p.status == PlayerStatus.ALIVE]
            targets = random.sample(opponents, min(len(opponents), 2))
            for target in targets:
                self._deal_damage(game, player, target, 1000, card_type=CardType.TECHNIQUE)
            return game

        opponents = [p for p in game.players if p.id != player.id and p.status == PlayerStatus.ALIVE]
        targets = random.sample(opponents, min(len(opponents), 2))
        for target in targets:
            self._deal_damage(game, player, target, 1000, card_type=CardType.TECHNIQUE)
        self._apply_effect(game, player, player, "gojo_blue_effect", 999)
        return game

    def _effect_krasnyi(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        target = self._find_player(game, target_id)
        if not target: return game

        if any(e.name == "gojo_red_effect" for e in player.effects):
            game.game_log.append("Эффект 'Красный' уже активен.")
            # Still deal damage
            self._deal_damage(game, player, target, 1200, card_type=CardType.TECHNIQUE)
            target_index = self._get_player_index(game, target_id)
            right_player = self._get_right_player(game, target_index)
            if right_player:
                self._deal_damage(game, player, right_player, 600, card_type=CardType.TECHNIQUE)
            return game
        
        self._deal_damage(game, player, target, 1200, card_type=CardType.TECHNIQUE)
        
        target_index = self._get_player_index(game, target_id)
        right_player = self._get_right_player(game, target_index)
        if right_player:
            self._deal_damage(game, player, right_player, 600, card_type=CardType.TECHNIQUE)
        self._apply_effect(game, player, player, "gojo_red_effect", 999)
        return game

    def _effect_fioletovyi(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        target = self._find_player(game, target_id)
        if not target: return game
        card = next(c for c in player.character.unique_cards if c.id == 'gojo_purple')
        self._deal_damage(game, player, target, 4000, ignores_block=True, card=card, card_type=card.type)
        
        # Remove the prerequisite effects
        blue_effect = next((e for e in player.effects if e.name == "gojo_blue_effect"), None)
        red_effect = next((e for e in player.effects if e.name == "gojo_red_effect"), None)
        if blue_effect:
            player.effects.remove(blue_effect)
            game.game_log.append("Эффект 'Синий' был поглощён.")
        if red_effect:
            player.effects.remove(red_effect)
            game.game_log.append("Эффект 'Красный' был поглощён.")
            
        return game
    
    def _effect_fioletovyi_yadernyi(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        opponents = [p for p in game.players if p.id != player.id and p.status == PlayerStatus.ALIVE]
        for op in opponents: self._deal_damage(game, player, op, 3000, ignores_block=True)
        return game

    def _effect_neobiatnaia_bezdna(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        self._apply_domain_to_opponents(game, player, EFFECT_ID_UNLIMITED_VOID, 3)
        return game

    def _effect_razrez(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        target = self._find_player(game, target_id)
        if not target: return game
        card = next(c for c in player.character.unique_cards if c.id == 'sukuna_cleave')
        self._deal_damage(game, player, target, 600, card=card, card_type=card.type)
        left_player = self._get_left_player(game, self._get_player_index(game, target.id))
        if left_player: self._deal_damage(game, player, left_player, 300, card=card, card_type=card.type)
        return game
        
    def _effect_rasshcheplenie(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        target = self._find_player(game, target_id)
        if not target: return game
        card = next(c for c in player.character.unique_cards if c.id == 'sukuna_dismantle')
        self._deal_damage(game, player, target, 1600, card=card, card_type=card.type)
        return game

    def _effect_rasshcheplenie_pautina(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        target = self._find_player(game, target_id)
        if not target: return game
        card = next(c for c in player.character.unique_cards if c.id == 'sukuna_spiderweb')
        self._deal_damage(game, player, target, 1000, card=card, card_type=card.type)
        left = self._get_left_player(game, self._get_player_index(game, target.id))
        right = self._get_right_player(game, self._get_player_index(game, target.id))
        if left: self._deal_damage(game, player, left, 500, card=card, card_type=card.type)
        if right: self._deal_damage(game, player, right, 500, card=card, card_type=card.type)
        return game

    def _effect_kamino(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        card = next(c for c in player.character.unique_cards if c.id == 'sukuna_kamino')
        # Synergy with Domain
        if any(e.name == "sukuna_malevolent_shrine" for e in player.effects):
            opponents = [p for p in game.players if p.id != player.id and p.status == PlayerStatus.ALIVE]
            for op in opponents: self._deal_damage(game, player, op, 1200, card=card, card_type=card.type)
            return game

        target = self._find_player(game, target_id)
        if not target: return game
        initial_hp = target.hp
        self._deal_damage(game, player, target, 1800, card=card, card_type=card.type)
        if target.hp <= 0 and initial_hp > 0:
            player.energy = min(player.character.max_energy, player.energy + 10000)
        return game

    def _effect_zlobnoe_sviatilishche(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        self._apply_domain_to_opponents(game, player, "sukuna_malevolent_shrine", 3)
        return game

    def _effect_kasanie_dushi(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        player_index = self._get_player_index(game, player.id)
        left_player = self._get_left_player(game, player_index)
        right_player = self._get_right_player(game, player_index)
        
        targets_hit = 0
        if left_player:
            self._deal_damage(game, player, left_player, 250, ignores_block=True, card_type=CardType.TECHNIQUE)
            targets_hit += 1
        if right_player and right_player != left_player:
            self._deal_damage(game, player, right_player, 250, ignores_block=True, card_type=CardType.TECHNIQUE)
            targets_hit += 1
        
        player.distorted_souls += targets_hit
        game.game_log.append(f"{player.nickname} получил {targets_hit} Искажённых Душ.")
        return game

    def _effect_iskazhenie_dushi(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        target = self._find_player(game, target_id)
        if not target or not target.hand: return game
        
        cards_to_discard = random.sample(target.hand, min(len(target.hand), 1))
        for card in cards_to_discard:
            target.hand.remove(card)
            target.discard_pile.append(card)
        
        game.game_log.append(f"{target.nickname} сбрасывает {len(cards_to_discard)} карту.")
        return game

    def _effect_ottalkivanie_tela(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        target = self._find_player(game, target_id)
        if not target: return game
        damage = 1400
        if target.block > 0: damage = int(damage * 1.5)
        card = next(c for c in player.character.unique_cards if c.id == 'mahito_body_repel')
        self._deal_damage(game, player, target, damage, card=card, card_type=card.type)
        return game

    def _effect_istinnoe_telo(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        self._apply_effect(game, player, player, "mahito_true_form", 999)
        return game

    def _effect_samovoploshchenie_sovershenstva(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        self._apply_domain_to_opponents(game, player, EFFECT_ID_SOUL_DISTORTION, 3)
        return game
    
    def _effect_kulak_divergenta(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        target = self._find_player(game, target_id)
        if not target: return game
        self._deal_damage(game, player, target, 400, card_type=CardType.TECHNIQUE)
        self._apply_effect(game, player, target, EFFECT_ID_DIVERGENT_FIST_DOT, 2, value=200)
        return game
    
    def _effect_zakhod_s_razvorota(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        for _ in range(2):
            udar_card = next((c for c in player.deck if c.id == "common_strike"), None)
            if udar_card:
                player.deck.remove(udar_card)
                player.hand.append(udar_card)
                self._apply_effect(game, player, player, EFFECT_ID_FREE_STRIKE, 1)
        return game

    def _effect_glubokaia_kontsentratsiia(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        self._apply_effect(game, player, player, "itadori_deep_concentration", 2)
        return game

    def _effect_nesgibaemaia_volia(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        self._apply_effect(game, player, player, "itadori_unwavering_will", 5)
        return game
    
    def _effect_sikigami_ugolki(self, game: Game, player: Player, target_id: str, targets_ids: list[str]):
        if not targets_ids:
            return game
        
        card = next((c for c in player.character.unique_cards if c.id == 'jogo_ember_insects'), None)
        if not card:
            return game

        for t_id in targets_ids:
            target = self._find_player(game, t_id)
            if target:
                self._deal_damage(game, player, target, 300, card=card, card_type=card.type)
        
        return game

    def _effect_izverzhenie_vulkana(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        opponents = [p for p in game.players if p.id != player.id and p.status == PlayerStatus.ALIVE]
        card = next(c for c in player.character.unique_cards if c.id == 'jogo_volcano_eruption')
        for op in opponents: self._deal_damage(game, player, op, 500, card=card, card_type=card.type)
        return game

    def _effect_maksimum_meteor(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        target = self._find_player(game, target_id)
        if not target: return game
        card = next(c for c in player.character.unique_cards if c.id == 'jogo_maximum_meteor')
        self._deal_damage(game, player, target, 2000, card=card, card_type=card.type)
        left = self._get_left_player(game, self._get_player_index(game, target.id))
        right = self._get_right_player(game, self._get_player_index(game, target.id))
        if left: self._deal_damage(game, player, left, 500, card=card, card_type=card.type)
        if right: self._deal_damage(game, player, right, 500, card=card, card_type=card.type)
        return game

    def _effect_grob_stalnoi_gory(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        self._apply_domain_to_opponents(game, player, "jogo_coffin_of_the_iron_mountain", 3)
        return game

    def _effect_klinok_usilennyi_energiei(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        target = self._find_player(game, target_id)
        if not target: return game
        card = next(c for c in player.character.unique_cards if c.id == 'yuta_energy_blade')
        self._deal_damage(game, player, target, 500, card=card, card_type=card.type)
        return game

    def _effect_polnoe_proiavlenie_rika(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        self._apply_effect(game, player, player, "yuta_rika_manifestation", 3)
        return game

    def _effect_istinnaia_i_vzaimnaia_liubov(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        self._apply_effect(game, player, player, "yuta_true_mutual_love", 3)
        return game
    
    def _apply_domain_to_opponents(self, game: Game, source: Player, effect_name: str, duration: int):
         # Cancel previous domain
        domain_effect_ids = [
            "gojo_unlimited_void", "sukuna_malevolent_shrine", 
            "mahito_self_embodiment_of_perfection", "jogo_coffin_of_the_iron_mountain", 
            "yuta_true_mutual_love"
        ]
        for p in game.players:
            p.effects = [e for e in p.effects if e.name not in domain_effect_ids]
        
        opponents = [p for p in game.players if p.id != source.id]
        for op in opponents:
            self._apply_effect(game, source, op, effect_name, duration)
    
    def _get_effect_function(self, card_id: str) -> callable:
        effect_map = {
            "common_strike": self._effect_udar, 
            "common_defense": self._effect_zashchita, 
            "common_concentration": self._effect_kontsentratsiia,
            "common_chant": self._effect_pesnopenie, 
            "common_simple_domain": self._effect_prostaia_territoriia,
            "common_falling_blossom_emotion": self._effect_chuvstva_opadaiushchego_tsvetka,
            "common_reverse_cursed_technique": self._effect_obratnaia_proklaiataia_tekhnika, 
            "common_black_flash": self._effect_chernaia_vspyshka,
            "gojo_strengthened_strike": self._effect_usilennyi_udar, 
            "gojo_infinity": self._effect_neitral,
            "gojo_blue": self._effect_sinii, 
            "gojo_red": self._effect_krasnyi,
            "gojo_purple": self._effect_fioletovyi,
            "gojo_unlimited_void": self._effect_neobiatnaia_bezdna,
            "sukuna_cleave": self._effect_razrez, 
            "sukuna_dismantle": self._effect_rasshcheplenie, 
            "sukuna_spiderweb": self._effect_rasshcheplenie_pautina,
            "sukuna_kamino": self._effect_kamino, 
            "sukuna_malevolent_shrine": self._effect_zlobnoe_sviatilishche,
            "mahito_soul_touch": self._effect_kasanie_dushi,
            "mahito_soul_distortion": self._effect_iskazhenie_dushi,
            "mahito_polymorphic_soul_isomer": self._effect_polymorphic_soul_isomer,
            "mahito_body_repel": self._effect_ottalkivanie_tela,
            "mahito_true_form": self._effect_istinnoe_telo,
            "mahito_self_embodiment_of_perfection": self._effect_samovoploshchenie_sovershenstva,
            "itadori_divergent_fist": self._effect_kulak_divergenta,
            "itadori_manji_kick": self._effect_manji_kick,
            "itadori_slaughter_demon": self._effect_zakhod_s_razvorota,
            "itadori_deep_concentration": self._effect_glubokaia_kontsentratsiia,
            "itadori_unwavering_will": self._effect_nesgibaemaia_volia,
            "jogo_ember_insects": self._effect_sikigami_ugolki,
            "jogo_volcano_eruption": self._effect_izverzhenie_vulkana,
            "jogo_maximum_meteor": self._effect_maksimum_meteor,
            "jogo_coffin_of_the_iron_mountain": self._effect_grob_stalnoi_gory,
            "yuta_energy_blade": self._effect_klinok_usilennyi_energiei,
            "yuta_rika_manifestation": self._effect_polnoe_proiavlenie_rika,
            "yuta_true_mutual_love": self._effect_istinnaia_i_vzaimnaia_liubov,
            "gojo_remove_blindfold": self._effect_snyat_povyazku,
            "manji_kick_counter": self._effect_manji_kick,
        }
        return effect_map.get(card_id)

    # --- Utility methods ---
    def _find_player_in_lobby(self, lobby: Lobby, player_id: str) -> Player | None:
        return next((p for p in lobby.players if p.id == player_id), None)
    
    def _find_player(self, game: Game, player_id: str) -> Player | None:
        return next((p for p in game.players if p.id == player_id), None)

    def _get_player_index(self, game: Game, player_id: str) -> int:
        return next((i for i, p in enumerate(game.players) if p.id == player_id), -1)

    def _get_left_player(self, game: Game, index: int) -> Player | None:
        alive_players = [p for p in game.players if p.status == PlayerStatus.ALIVE]
        if not alive_players: return None
        current_player_id = game.players[index].id
        try:
            alive_index = alive_players.index(next(p for p in alive_players if p.id == current_player_id))
            return alive_players[(alive_index - 1 + len(alive_players)) % len(alive_players)]
        except StopIteration:
            return None # Player not found in alive list

    def _get_right_player(self, game: Game, index: int) -> Player | None:
        alive_players = [p for p in game.players if p.status == PlayerStatus.ALIVE]
        if not alive_players: return None
        current_player_id = game.players[index].id
        try:
            alive_index = alive_players.index(next(p for p in alive_players if p.id == current_player_id))
            return alive_players[(alive_index + 1) % len(alive_players)]
        except StopIteration:
            return None

    def add_dummy(self, game_id: str) -> Game:
        game = self.get_game(game_id)
        if not game or not game.is_training:
            raise GameException("Нельзя добавить манекен в этой игре.")
        
        # Find the highest dummy number to avoid ID conflicts
        dummy_numbers = [int(p.id.split('_')[1]) for p in game.players if "dummy" in p.id]
        next_dummy_num = max(dummy_numbers) + 1 if dummy_numbers else 1
        
        dummy_id = f"dummy_{next_dummy_num}"
        dummy = Player(id=dummy_id, nickname=f"Манекен {next_dummy_num}", hp=10000, max_hp=10000, energy=0, block=0, status=PlayerStatus.ALIVE)
        game.players.append(dummy)
        game.game_log.append(f"Добавлен {dummy.nickname}")
        return game
    
    def remove_dummy(self, game_id: str, dummy_id: str) -> Game:
        game = self.get_game(game_id)
        if not game or not game.is_training:
            raise GameException("Нельзя удалить манекен из этой игры.")

        dummy_to_remove = self._find_player(game, dummy_id)
        if not dummy_to_remove or "dummy" not in dummy_to_remove.id:
            raise GameException("Манекен не найден.")
            
        game.players.remove(dummy_to_remove)
        game.game_log.append(f"Удален {dummy_to_remove.nickname}")
        return game

    def _effect_snyat_povyazku(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        player.is_blindfolded = False
        blindfold_effect = next((e for e in player.effects if e.name == "gojo_blindfold"), None)
        if blindfold_effect:
            player.effects.remove(blindfold_effect)
        game.game_log.append(f"{player.nickname} снимает повязку!")
        return game

    def _effect_manji_kick(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        target = self._find_player(game, target_id)
        if not target: return game
        self._deal_damage(game, player, target, 600, card_type=CardType.TECHNIQUE)
        self._apply_effect(game, player, target, "manji_kick_counter", 2) # Lasts for 1 round
        return game

    def _effect_polymorphic_soul_isomer(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        player.block += 500
        self._apply_effect(game, player, player, "mahito_polymorphic_soul_isomer", 2)
        game.game_log.append(f"{player.nickname} получает 500 блока от 'Полиморфной Изомерной Души'.")
        return game

game_manager = GameManager()
