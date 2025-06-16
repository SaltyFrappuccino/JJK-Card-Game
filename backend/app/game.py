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
        
        if not is_free_udar and player.energy < card_to_play.cost: 
            raise GameException("Недостаточно Проклятой Энергии.")

        # --- Conditional Cards ---
        if card_to_play.name in ["Мнимая техника: 'Фиолетовый'", "Мнимый Фиолетовый: Ядерный"]:
            if not player.used_blue or not player.used_red:
                raise GameException("Нужно сначала использовать 'Синий' и 'Красный'.")
        
        if card_to_play.name == "Истинное Тело Изощрённых Убийств":
            if not player.successful_black_flash:
                raise GameException("Нужно сначала успешно применить 'Чёрную Вспышку'.")

        # --- Domain Expansion Effects ---
        if any(e.name == "Информационная перегрузка" for e in player.effects):
            if card_to_play.type == CardType.TECHNIQUE or card_to_play.rarity in [Rarity.EPIC, Rarity.LEGENDARY]:
                raise GameException("Вы не можете использовать эту карту из-за 'Информационной перегрузки'.")

        if not is_free_udar:
            player.energy -= card_to_play.cost
        else:
            effect = next((e for e in player.effects if e.name == "Бесплатный Удар"), None)
            if effect: player.effects.remove(effect)

        player.hand.remove(card_to_play)
        player.discard_pile.append(card_to_play)

        chant_effect = next((e for e in player.effects if e.name == "Песнопение (Чант)"), None)
        if chant_effect and card_to_play.type != CardType.TECHNIQUE:
            pass # Chant is not consumed
        elif chant_effect:
             player.effects.remove(chant_effect)

        game.game_log.append(f"{player.nickname} играет {card_name}" + (f" на {self._find_player(game, target_id).nickname}" if target_id else ""))
        
        effect_function = self._get_effect_function(card_name)
        if effect_function:
            game = effect_function(game, player, target_id, targets_ids)

        self._check_for_defeated_players(game)
        if game.game_state != GameState.FINISHED:
            self._check_game_over(game)

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
        
        if next_turn_index == 0:
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
                p.block = 0
                max_hand = 5
                if p.character.name == "Сатору Годзё": max_hand = 6
                if any(e.name == "Искажение души" for e in p.effects): max_hand -= 1
                if any(e.name == "Истинная и Взаимная Любовь" for e in p.effects): max_hand = 8
                
                self._draw_cards(p, max_hand)
                p.energy = min(p.character.max_energy, p.energy + int(p.character.max_energy * 0.20))
        
        # Determine turn order for the new round
        start_index = game.current_turn_player_index
        game.current_turn_player_index = (start_index + 1) % len(game.players)


    def _draw_cards(self, player: Player, max_hand_size: int):
        while len(player.hand) < max_hand_size:
            if not player.deck:
                if not player.discard_pile: break
                player.deck = player.discard_pile
                player.discard_pile = []
                random.shuffle(player.deck)
            player.hand.append(player.deck.pop())

    def _create_game_from_lobby(self, lobby: Lobby) -> Game:
        game_id = f"game_{len(self.games) + 1}"
        players = lobby.players
        for player in players:
            player.energy = 0
            self._build_deck_for_player(player)
            self._draw_cards(player, 6 if player.character.name == "Сатору Годзё" else 5)
        
        random.shuffle(players)
        
        game = Game(
            game_id=game_id,
            players=players,
            current_turn_player_index=0,
            game_state=GameState.IN_GAME,
            game_log=[f"Игра {game_id} началась!"]
        )
        return game

    def _build_deck_for_player(self, player: Player):
        deck = []
        # Add common cards
        deck.extend([card.copy(deep=True) for card in common_cards] * 2) # Example: 2 of each common
        # Add unique character cards
        deck.extend([card.copy(deep=True) for card in player.character.unique_cards])
        random.shuffle(deck)
        player.deck = deck

    def _process_passives(self, game: Game, player: Player):
        if any(e.name == "Злобное Святилище" for e in player.effects):
            opponents = [p for p in game.players if p.id != player.id and p.status == PlayerStatus.ALIVE]
            for op in opponents: self._deal_damage(game, player, op, 1000, ignores_block=True)
        
        if player.character.name == "Юта Оккоцу":
            opponents = [p for p in game.players if p.id != player.id and p.status == PlayerStatus.ALIVE]
            if opponents:
                target = random.choice(opponents)
                damage = 1000 if any(e.name == "Полное Проявление: Рика" for e in player.effects) else 250
                self._deal_damage(game, player, target, damage)
        
        if any(e.name == "Истинное Тело Изощрённых Убийств" for e in player.effects):
            player.block += 500

    def _process_start_of_turn_effects(self, game: Game, player: Player):
        effects_to_remove = []
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

        # Yuta Passive (Copy)
        if target.character.name == "Юта Оккоцу" and card_type == CardType.TECHNIQUE and source_player.id != target.id:
            copied_card = card.copy(deep=True)
            copied_card.cost = int(copied_card.cost * 1.25)
            target.discard_pile.append(copied_card)
            game.game_log.append(f"Рика скопировала {card.name} для {target.nickname}!")

        # Sukuna Passive (Energy)
        if target.character.name == "Рёмен Сукуна" and (source_player.hp / source_player.character.max_hp) > (target.hp / target.character.max_hp):
             target.energy = min(target.character.max_energy, target.energy + 3000)
             game.game_log.append(f"Жажда Развлечений дарует {target.nickname} 3000 ПЭ!")

        actual_damage = damage
        if not ignores_block:
            blocked_damage = min(target.block, actual_damage)
            target.block -= blocked_damage
            actual_damage -= blocked_damage
        
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
        if player.character.name == "Юдзи Итадори": damage += 150
        if any(e.name == "Истинное Тело Изощрённых Убийств" for e in player.effects): damage *= 3
        
        final_damage = damage
        if target.character.name == "Махито": final_damage = 0
        if any(e.name == "Истинное Тело Изощрённых Убийств" for e in target.effects): final_damage = int(damage * 0.5)

        self._deal_damage(game, player, target, final_damage)
        return game

    def _effect_zashchita(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        player.block += 300
        return game

    def _effect_kontsentratsiia(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        player.energy = min(player.character.max_energy, player.energy + 8000)
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

    def _effect_usilennyi_sinim_udar(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        target = self._find_player(game, target_id)
        if not target: return game
        self._deal_damage(game, player, target, 300, ignores_block=True)
        return game

    def _effect_neitral(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        self._apply_effect(game, player, player, "Техника Бесконечности: Нейтраль", 1)
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
        self._apply_effect(game, player, player, "Истинное Тело Изощрённых Убийств", 999)
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
    
    def _effect_sikigami_ugolki(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        targets = [self._find_player(game, tid) for tid in targets_ids]
        for t in targets:
            if t: self._deal_damage(game, player, t, 300)
        return game

    def _effect_izverzhenie_vulkana(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        opponents = [p for p in game.players if p.id != player.id and p.status == PlayerStatus.ALIVE]
        for op in opponents: self._deal_damage(game, player, op, 600)
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
        self._apply_effect(game, player, player, "Полное Проявление: Рика", 3)
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
            "Усиленный Синим Удар": self._effect_usilennyi_sinim_udar, "Техника Бесконечности: Нейтраль": self._effect_neitral,
            "Проклятая техника: 'Синий'": self._effect_sinii, "Обратная проклятая техника: 'Красный'": self._effect_krasnyi,
            "Мнимая техника: 'Фиолетовый'": self._effect_fioletovyi, "Мнимый Фиолетовый: Ядерный": self._effect_fioletovyi_yadernyi,
            "Расширение Территории: Необъятная Бездна": self._effect_neobiatnaia_bezdna,
            "Разрез": self._effect_razrez, "Расщепление": self._effect_rasshcheplenie, "Расщепление: Паутина": self._effect_rasshcheplenie_pautina,
            "Камино (Пламенная стрела)": self._effect_kamino, "Расширение Территории: Злобное Святилище": self._effect_zlobnoe_sviatilishche,
            "Касание Души": self._effect_kasanie_dushi, "Искажение Души": self._effect_iskazhenie_dushi,
            "Отталкивание Тела": self._effect_ottalkivanie_tela, "Истинное Тело Изощрённых Убийств": self._effect_istinnoe_telo,
            "Расширение Территории: Самовоплощение Совершенства": self._effect_samovoploshchenie_sovershenstva,
            "Кулак Дивергента": self._effect_kulak_divergenta, "Заход с разворота": self._effect_zakhod_s_razvorota,
            "Глубокая Концентрация": self._effect_glubokaia_kontsentratsiia, "Несгибаемая Воля": self._effect_nesgibaemaia_volia,
            "Сикигами: Угольки": self._effect_sikigami_ugolki, "Извержение Вулкана": self._effect_izverzhenie_vulkana,
            "Максимум: Метеор": self._effect_maksimum_meteor, "Расширение Территории: Гроб Стальной Горы": self._effect_grob_stalnoi_gory,
            "Клинок, Усиленный Энергией": self._effect_klinok_usilennyi_energiei,
            "Полное Проявление: Рика": self._effect_polnoe_proiavlenie_rika,
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

game_manager = GameManager()
