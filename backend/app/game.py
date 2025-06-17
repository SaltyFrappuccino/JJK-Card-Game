import random
from typing import Dict, List, Callable, Any

from .models import Game, Lobby, Player, Card, GameState, Effect, PlayerStatus, CardType, Rarity, Character
from .content import common_cards, characters
from .exceptions import GameException


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

    def select_character(self, lobby_id: str, player_id: str, character_name: str) -> Lobby:
        lobby = self.get_lobby(lobby_id)
        if not lobby: raise GameException("Лобби не найдено.")
        
        player = self._find_player_in_lobby(lobby, player_id)
        if not player: raise GameException("Игрок не найден.")

        if any(p.character and p.character.name == character_name for p in lobby.players):
            raise GameException("Этот персонаж уже выбран.")

        character = next((c for c in characters if c.name == character_name), None)
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

    def play_card(self, game_id: str, player_id: str, card_name: str, target_id: str = None, targets_ids: list = None) -> Game:
        game = self.get_game(game_id)
        if not game: raise GameException("Игра не найдена.")
        if game.players[game.current_turn_player_index].id != player_id: raise GameException("Сейчас не ваш ход.")

        player = self._find_player(game, player_id)
        if not player: raise GameException("Игрок не найден.")

        card_to_play = next((card for card in player.hand if card.name == card_name), None)
        if not card_to_play: raise GameException("Карта не найдена в руке.")

        is_free_udar = card_to_play.name == "Удар" and any(e.name == "Бесплатный Удар" for e in player.effects)
        
        player.chant_active_for_turn = False
        chant_effect = next((e for e in player.effects if e.name == "Песнопение (Чант)"), None)
        if chant_effect and card_to_play.type == CardType.TECHNIQUE:
            player.chant_active_for_turn = True

        card_cost = card_to_play.cost
        # Apply Gojo's discount
        if player.character and player.character.name == "Сатору Годзё":
            card_cost = int(card_cost * player.cost_modifier)
        
        # Apply Yuta's domain discount
        if card_to_play.is_copied and any(e.name == "Истинная и Взаимная Любовь" for e in player.effects):
            card_cost = -(-card_cost // 4) # Ceiling division

        if not game.is_training:
            if not is_free_udar and player.energy < card_cost:
                raise GameException("Недостаточно Проклятой Энергии.")

        # --- Conditional Cards ---
        if card_to_play.name == "Мнимая техника: \"Фиолетовый\"":
            if not player.used_blue or not player.used_red:
                raise GameException("Нужно сначала использовать 'Синий' и 'Красный'.")
        
        if card_to_play.name == "Искажённое Тело Изорённых Убийств":
            if player.ignore_block_attacks_count < 5:
                raise GameException(f"Нужно атаковать картами, игнорирующими блок, ещё {5 - player.ignore_block_attacks_count} раз.")

        # --- Domain Expansion Effects ---
        if any(e.name == "Информационная перегрузка" for e in player.effects):
            if card_to_play.type == CardType.TECHNIQUE or card_to_play.rarity in [Rarity.EPIC, Rarity.LEGENDARY]:
                raise GameException("Вы не можете использовать эту карту из-за 'Информационной перегрузки'.")

        if not is_free_udar:
            player.energy -= card_cost
        else:
            effect = next((e for e in player.effects if e.name == "Бесплатный Удар"), None)
            if effect: player.effects.remove(effect)

        player.hand.remove(card_to_play)
        player.discard_pile.append(card_to_play)
        
        if player.chant_active_for_turn:
            if chant_effect: player.effects.remove(chant_effect)

        if targets_ids:
            target_names = [self._find_player(game, tid).nickname for tid in targets_ids if self._find_player(game, tid)]
            game.game_log.append(f"{player.nickname} играет {card_name} на {', '.join(target_names)}")
        elif target_id:
            target = self._find_player(game, target_id)
            game.game_log.append(f"{player.nickname} играет {card_name} на {target.nickname}")
        else:
            game.game_log.append(f"{player.nickname} играет {card_name}")
        
        effect_function = self._get_effect_function(card_name)
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

        # Skip turns for dummies
        if game.is_training:
            while "dummy" in game.players[next_turn_index].id:
                if next_turn_index == game.current_turn_player_index:
                    # This should not happen, but as a safeguard
                    break
                next_turn_index = (next_turn_index + 1) % len(game.players)

        # Check if a full round has passed
        if next_turn_index <= game.current_turn_player_index:
             self._start_new_round(game)
        
        game.current_turn_player_index = next_turn_index
        new_current_player = game.players[game.current_turn_player_index]
        self._process_start_of_turn_effects(game, new_current_player)

        return game

    def discard_cards(self, game_id: str, player_id: str, card_names: List[str]) -> Game:
        game = self.get_game(game_id)
        player = self._find_player(game, player_id)
        
        if player.last_discard_round == game.round_number:
            raise GameException("Вы уже сбрасывали карты в этом раунде.")
        if len(card_names) > 2:
            raise GameException("Можно сбросить не более 2 карт.")

        discarded_count = 0
        for name in card_names:
            card = next((c for c in player.hand if c.name == name), None)
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
                if p.character and p.character.name == "Сатору Годзё":
                    p.cost_modifier = max(0.10, p.cost_modifier - 0.05)

                if game.is_training and "dummy" in p.id:
                    p.hp = p.max_hp
                    continue
                
                p.block = 0
                max_hand = 5
                if p.character and p.character.name == "Сатору Годзё": max_hand = 6
                if any(e.name == "Искажение души" for e in p.effects): max_hand -= 1
                if any(e.name == "Истинная и Взаимная Любовь" for e in p.effects): max_hand = 8
                
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
            drawn_cards.extend(draw_pool[:remaining_to_draw])
            draw_pool = draw_pool[remaining_to_draw:]
            
        player.hand.extend(drawn_cards)
        player.deck = draw_pool # The rest of the cards form the new deck

    def _create_game_from_lobby(self, lobby: Lobby) -> Game:
        game_id = f"game_{len(self.games) + 1}"
        players = lobby.players
        
        if lobby.is_training:
            player = players[0]
            player.energy = 99999
            player.deck = []
            all_cards = [card.copy(deep=True) for card in player.character.unique_cards]
            all_cards.extend([card.copy(deep=True) for card in common_cards])
            player.hand = all_cards
            
            for i in range(7):
                dummy_id = f"dummy_{i+1}"
                dummy = Player(id=f"dummy_{i+1}", nickname=f"Манекен {i+1}", hp=10000, max_hp=10000, energy=0, block=0, status=PlayerStatus.ALIVE)
                players.append(dummy)
        else:
            for player in players:
                if player.character:
                    player.energy = int(player.character.max_energy * 0.20)
                else:
                    player.energy = 0
                self._build_deck_for_player(player)
                self._draw_cards(player, 6 if player.character and player.character.name == "Сатору Годзё" else 5)
        
        # In training, the real player should always be first.
        if lobby.is_training:
            real_player_index = next((i for i, p in enumerate(players) if "dummy" not in p.id), -1)
            if real_player_index != -1:
                real_player = players.pop(real_player_index)
                players.insert(0, real_player)
        else:
            random.shuffle(players)

        game = Game(
            game_id=game_id,
            players=players,
            current_turn_player_index=0,
            game_state=GameState.IN_GAME,
            game_log=[f"Игра {game_id} началась!"],
            is_training=lobby.is_training,
        )
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
        if any(e.name == "Злобное Святилище" for e in player.effects):
            opponents = [p for p in game.players if p.id != player.id and p.status == PlayerStatus.ALIVE]
            for op in opponents: self._deal_damage(game, player, op, 1500, ignores_block=True)
        
        if player.character and player.character.name == "Юта Оккоцу":
            opponents = [p for p in game.players if p.id != player.id and p.status == PlayerStatus.ALIVE]
            if opponents:
                # Check for "Проявление: Рика" effect
                rika_manifested = any(e.name == "Проявление: Рика" for e in player.effects)
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
        
        if any(e.name == "Искажённое Тело Изорённых Убийств" for e in player.effects):
            player.block += 500

    def _process_start_of_turn_effects(self, game: Game, player: Player):
        effects_to_remove = []

        # Process Mahito's Domain effect first
        if any(e.name == "Искажение души" for e in player.effects):
            player.block = 0 # Annihilate block
            if len(player.hand) >= 1:
                cards_to_discard = random.sample(player.hand, k=1)
                for card in cards_to_discard:
                    player.hand.remove(card)
                    player.discard_pile.append(card)
                game.game_log.append(f"{player.nickname} теряет 1 карту из-за Искажения души.")

        for effect in player.effects:
            effect.duration -= 1
            if effect.duration <= 0:
                effects_to_remove.append(effect)
            
            if effect.name == "Горение": self._deal_damage(game, player, player, effect.value)
            if effect.name == "Гроб Стальной Горы": self._deal_damage(game, player, player, 800)
            if effect.name == "Кулак Дивергента": self._deal_damage(game, self._find_player(game, effect.source_player_id), player, 200)

        for effect in effects_to_remove:
            player.effects.remove(effect)
            if effect.name == "Последний Бой": self._defeat_player(game, player)

    def _process_end_of_turn_effects(self, game: Game, player: Player):
        pass # Placeholder for now

    def _deal_damage(self, game: Game, source_player: Player, target: Player, damage: int, ignores_block: bool = False, card: Card = None, card_type: CardType = None):
        if target.status == PlayerStatus.DEFEATED: return

        # Gojo's Neutral Infinity
        neutral_infinity = next((e for e in target.effects if e.name == "Техника Бесконечности: Нейтраль"), None)
        if neutral_infinity and neutral_infinity.source_player_id == target.id and neutral_infinity.target_id == source_player.id:
             game.game_log.append(f"Атака {source_player.nickname} на {target.nickname} отменена Бесконечностью!")
             return

        # Yuta Passive (Copy)
        if target.character and target.character.name == "Юта Оккоцу" and card_type == CardType.TECHNIQUE and source_player.id != target.id:
            copied_card = card.copy(deep=True)
            copied_card.cost = -(-copied_card.cost * 1.25 // 1) # Ceiling
            copied_card.is_copied = True
            target.discard_pile.append(copied_card)
            game.game_log.append(f"Рика скопировала {card.name} для {target.nickname}!")

        # Sukuna Passive (Energy)
        if target.character and target.character.name == "Рёмен Сукуна" and \
           source_player.max_hp and source_player.hp and target.max_hp and target.hp and \
           (source_player.hp / source_player.max_hp) > (target.hp / target.max_hp):
             restore_amount = int(target.character.max_energy * 0.05)
             target.energy = min(target.character.max_energy, target.energy + restore_amount)
             game.game_log.append(f"Жажда Развлечений дарует {target.nickname} {restore_amount} ПЭ!")
        
        # Jogo Passive (Burn)
        if source_player.character and source_player.character.name == "Дзёго" and card_type == CardType.TECHNIQUE:
            self._apply_effect(game, source_player, target, "Горение", 2, value=100)

        actual_damage = damage
        if source_player.chant_active_for_turn:
            actual_damage = int(actual_damage * 1.5)

        if any(e.name == "Чувства Опадающего Цветка" for e in target.effects):
            actual_damage = int(actual_damage * 0.67) # Reduce damage by 33%

        # Mahito's "True Body" damage reduction
        if any(e.name == "Искажённое Тело Изорённых Убийств" for e in target.effects) and card and card.name == "Удар":
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

        if target.hp <= 0 and not any(e.name == "Последний Бой" for e in target.effects):
            self._defeat_player(game, target)

    def _defeat_player(self, game: Game, player: Player):
        player.status = PlayerStatus.DEFEATED
        player.hp = 0
        game.game_log.append(f"{player.nickname} был побежден!")

    def _check_for_defeated_players(self, game: Game):
        for p in game.players:
            if p.hp <= 0 and p.status == PlayerStatus.ALIVE and not any(e.name == "Последний Бой" for e in p.effects):
                self._defeat_player(game, p)

    def _check_game_over(self, game: Game):
        alive_players = [p for p in game.players if p.status == PlayerStatus.ALIVE]
        if len(alive_players) <= 1:
            game.game_state = GameState.FINISHED
            winner = alive_players[0] if alive_players else None
            game.game_log.append("Игра окончена." + (f" Победитель: {winner.nickname}!" if winner else ""))

    # --- Card Effect Functions ---
    def _apply_effect(self, game: Game, source: Player, target: Player, name: str, duration: int, value: Any = None):
        target.effects.append(Effect(name=name, duration=duration, value=value, source_player_id=source.id))
        game.game_log.append(f"{target.nickname} получает эффект '{name}' на {duration} раунда.")

    def _effect_udar(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        target = self._find_player(game, target_id)
        if not target: return game
        
        damage = 300
        if player.character and player.character.name == "Юдзи Итадори": 
            damage += 150
            player.energy = min(player.character.max_energy, player.energy + 1000)
        if any(e.name == "Искажённое Тело Изорённых Убийств" for e in player.effects): damage *= 3
        
        final_damage = damage
        if target.character and target.character.name == "Махито": final_damage = 0
        if any(e.name == "Искажённое Тело Изорённых Убийств" for e in target.effects): final_damage = int(damage * 0.5)

        self._deal_damage(game, player, target, final_damage)
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
        self._apply_effect(game, player, player, "Песнопение (Чант)", 1)
        return game
    
    def _effect_prostaia_territoriia(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        self._apply_effect(game, player, player, "Простая Территория", 2)
        return game

    def _effect_chuvstva_opadaiushchego_tsvetka(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        self._apply_effect(game, player, player, "Чувства Опадающего Цветка", 3)
        return game

    def _effect_obratnaia_proklaiataia_tekhnika(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        player.hp = min(player.character.max_hp, player.hp + 1200)
        return game

    def _effect_chernaia_vspyshka(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        target = self._find_player(game, target_id)
        if not target: return game
        
        guaranteed = any(e.name == "Глубокая Концентрация" for e in player.effects)
        chance = 2 if player.character.name == "Юдзи Итадори" else 1
        
        if guaranteed or random.randint(1, 6) <= chance:
            self._deal_damage(game, player, target, 3500)
            player.successful_black_flash = True
            if guaranteed:
                effect = next(e for e in player.effects if e.name == "Глубокая Концентрация")
                player.effects.remove(effect)
        else:
            self._deal_damage(game, player, target, 300)
        return game

    def _effect_usilennyi_udar(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        target = self._find_player(game, target_id)
        if not target: return game
        self._deal_damage(game, player, target, 300, ignores_block=True)
        return game

    def _effect_neitral(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        target = self._find_player(game, target_id)
        if not target: return game
        self._apply_effect(game, player, player, "Техника Бесконечности: Нейтраль", 1, target_id=target.id)
        return game

    def _effect_sinii(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        opponents = [p for p in game.players if p.id != player.id and p.status == PlayerStatus.ALIVE]
        targets = random.sample(opponents, k=min(len(opponents), 2))
        for t in targets: self._deal_damage(game, player, t, 1000)
        player.used_blue = True
        return game

    def _effect_krasnyi(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        target = self._find_player(game, target_id)
        if not target: return game
        self._deal_damage(game, player, target, 1200)
        right_player = self._get_right_player(game, self._get_player_index(game, target.id))
        if right_player: self._deal_damage(game, player, right_player, 600)
        player.used_red = True
        return game

    def _effect_fioletovyi(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        target = self._find_player(game, target_id)
        if not target: return game
        self._deal_damage(game, player, target, 4000, ignores_block=True)
        return game
    
    def _effect_fioletovyi_yadernyi(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        opponents = [p for p in game.players if p.id != player.id and p.status == PlayerStatus.ALIVE]
        for op in opponents: self._deal_damage(game, player, op, 3000, ignores_block=True)
        return game

    def _effect_neobiatnaia_bezdna(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        self._apply_domain_to_opponents(game, player, "Информационная перегрузка", 3)
        return game

    def _effect_razrez(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        target = self._find_player(game, target_id)
        if not target: return game
        self._deal_damage(game, player, target, 600)
        left_player = self._get_left_player(game, self._get_player_index(game, target.id))
        if left_player: self._deal_damage(game, player, left_player, 300)
        return game
        
    def _effect_rasshcheplenie(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        target = self._find_player(game, target_id)
        if not target: return game
        self._deal_damage(game, player, target, 1600)
        return game

    def _effect_rasshcheplenie_pautina(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        target = self._find_player(game, target_id)
        if not target: return game
        self._deal_damage(game, player, target, 1000)
        left = self._get_left_player(game, self._get_player_index(game, target.id))
        right = self._get_right_player(game, self._get_player_index(game, target.id))
        if left: self._deal_damage(game, player, left, 500)
        if right: self._deal_damage(game, player, right, 500)
        return game

    def _effect_kamino(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        # Synergy with Domain
        if any(e.name == "Злобное Святилище" for e in player.effects):
            opponents = [p for p in game.players if p.id != player.id and p.status == PlayerStatus.ALIVE]
            for op in opponents: self._deal_damage(game, player, op, 1200)
            return game

        target = self._find_player(game, target_id)
        if not target: return game
        initial_hp = target.hp
        self._deal_damage(game, player, target, 1800)
        if target.hp <= 0 and initial_hp > 0:
            player.energy = min(player.character.max_energy, player.energy + 10000)
        return game

    def _effect_zlobnoe_sviatilishche(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        self._apply_effect(game, player, player, "Злобное Святилище", 3)
        return game

    def _effect_kasanie_dushi(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        target = self._find_player(game, target_id)
        if not target: return game
        self._deal_damage(game, player, target, 250, ignores_block=True)
        return game

    def _effect_iskazhenie_dushi(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        target = self._find_player(game, target_id)
        if not target or len(target.hand) < 2: return game
        cards_to_discard = random.sample(target.hand, k=2)
        for card in cards_to_discard:
            target.hand.remove(card)
            target.discard_pile.append(card)
        return game
    
    def _effect_ottalkivanie_tela(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        target = self._find_player(game, target_id)
        if not target: return game
        damage = 1400
        if target.block > 0: damage = int(damage * 1.5)
        self._deal_damage(game, player, target, damage)
        return game

    def _effect_istinnoe_telo(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        self._apply_effect(game, player, player, "Искажённое Тело Изорённых Убийств", 999)
        return game

    def _effect_samovoploshchenie_sovershenstva(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        self._apply_domain_to_opponents(game, player, "Искажение души", 3)
        return game
    
    def _effect_kulak_divergenta(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        target = self._find_player(game, target_id)
        if not target: return game
        self._deal_damage(game, player, target, 400)
        self._apply_effect(game, player, target, "Кулак Дивергента", 1)
        return game
    
    def _effect_zakhod_s_razvorota(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        for _ in range(2):
            udar_card = next((c for c in player.deck if c.name == "Удар"), None)
            if udar_card:
                player.deck.remove(udar_card)
                player.hand.append(udar_card)
                self._apply_effect(game, player, player, "Бесплатный Удар", 1)
        return game

    def _effect_glubokaia_kontsentratsiia(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        self._apply_effect(game, player, player, "Глубокая Концентрация", 2)
        return game

    def _effect_nesgibaemaia_volia(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        self._apply_effect(game, player, player, "Последний Бой", 5)
        return game
    
    def _effect_sikigami_ugolki(self, game: Game, player: Player, target_id: str, targets_ids: list[str]):
        target = self._find_player(game, target_id)
        if not target: return game
        
        left = self._get_left_player(game, self._get_player_index(game, target.id))
        right = self._get_right_player(game, self._get_player_index(game, target.id))
        
        self._deal_damage(game, player, target, 300)
        if left: self._deal_damage(game, player, left, 300)
        if right: self._deal_damage(game, player, right, 300)

        return game

    def _effect_izverzhenie_vulkana(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        opponents = [p for p in game.players if p.id != player.id and p.status == PlayerStatus.ALIVE]
        for op in opponents: self._deal_damage(game, player, op, 500)
        return game

    def _effect_maksimum_meteor(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        target = self._find_player(game, target_id)
        if not target: return game
        self._deal_damage(game, player, target, 2000)
        left = self._get_left_player(game, self._get_player_index(game, target.id))
        right = self._get_right_player(game, self._get_player_index(game, target.id))
        if left: self._deal_damage(game, player, left, 500)
        if right: self._deal_damage(game, player, right, 500)
        return game

    def _effect_grob_stalnoi_gory(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        self._apply_domain_to_opponents(game, player, "Гроб Стальной Горы", 3)
        return game

    def _effect_klinok_usilennyi_energiei(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        target = self._find_player(game, target_id)
        if not target: return game
        self._deal_damage(game, player, target, 500)
        return game

    def _effect_polnoe_proiavlenie_rika(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        self._apply_effect(game, player, player, "Проявление: Рика", 3)
        return game

    def _effect_istinnaia_i_vzaimnaia_liubov(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        self._apply_effect(game, player, player, "Истинная и Взаимная Любовь", 3)
        return game
    
    def _apply_domain_to_opponents(self, game: Game, source: Player, effect_name: str, duration: int):
         # Cancel previous domain
        for p in game.players:
            p.effects = [e for e in p.effects if e.name not in ["Необъятная Бездна", "Злобное Святилище", "Самовоплощение Совершенства", "Гроб Стальной Горы", "Истинная и Взаимная Любовь"]]
        
        opponents = [p for p in game.players if p.id != source.id]
        for op in opponents:
            self._apply_effect(game, source, op, effect_name, duration)
    
    def _get_effect_function(self, card_name: str) -> callable:
        effect_map = {
            "Удар": self._effect_udar, "Защита": self._effect_zashchita, "Концентрация": self._effect_kontsentratsiia,
            "Песнопение (Чант)": self._effect_pesnopenie, "Простая Территория": self._effect_prostaia_territoriia,
            "Чувства Опадающего Цветка": self._effect_chuvstva_opadaiushchego_tsvetka,
            "Обратная Проклятая Техника": self._effect_obratnaia_proklaiataia_tekhnika, "Чёрная Вспышка": self._effect_chernaia_vspyshka,
            "Усиленный Удар": self._effect_usilennyi_udar, "Техника Бесконечности: Нейтраль": self._effect_neitral,
            "Проклятая техника: \"Синий\"": self._effect_sinii, "Обратная проклятая техника: \"Красный\"": self._effect_krasnyi,
            "Мнимая техника: \"Фиолетовый\"": self._effect_fioletovyi,
            "Расширение Территории: Необъятная Бездна": self._effect_neobiatnaia_bezdna,
            "Разрез": self._effect_razrez, "Расщепление": self._effect_rasshcheplenie, "Расщепление: Паутина": self._effect_rasshcheplenie_pautina,
            "Камино (Пламенная стрела)": self._effect_kamino, "Расширение Территории: Злобное Святилище": self._effect_zlobnoe_sviatilishche,
            "Касание Души": self._effect_kasanie_dushi, "Искажение Души": self._effect_iskazhenie_dushi,
            "Отталкивание Тела": self._effect_ottalkivanie_tela, "Искажённое Тело Изорённых Убийств": self._effect_istinnoe_telo,
            "Расширение Территории: Самовоплощение Совершенства": self._effect_samovoploshchenie_sovershenstva,
            "Кулак Дивергента": self._effect_kulak_divergenta, "Заход с разворота": self._effect_zakhod_s_razvorota,
            "Глубокая Концентрация": self._effect_glubokaia_kontsentratsiia, "Несгибаемая Воля": self._effect_nesgibaemaia_volia,
            "Сикигами: Угольки": self._effect_sikigami_ugolki, "Извержение Вулкана": self._effect_izverzhenie_vulkana,
            "Максимум: Метеор": self._effect_maksimum_meteor, "Расширение Территории: Гроб Стальной Горы": self._effect_grob_stalnoi_gory,
            "Клинок, Усиленный Энергией": self._effect_klinok_usilennyi_energiei,
            "Проявление: Рика": self._effect_polnoe_proiavlenie_rika,
            "Расширение Территории: Истинная и Взаимная Любовь": self._effect_istinnaia_i_vzaimnaia_liubov,
        }
        return effect_map.get(card_name)

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

game_manager = GameManager()
