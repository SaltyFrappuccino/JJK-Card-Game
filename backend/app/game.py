import random
from typing import Dict, List, Callable, Any

from .models import Game, Lobby, Player, Card, GameState, Effect, PlayerStatus, CardType, Rarity
from .content import common_cards
from .exceptions import GameException

games: Dict[str, Game] = {}

class GameManager:
    def __init__(self):
        self.card_effects: Dict[str, Callable] = self._map_card_effects()

    def get_game(self, game_id: str) -> Game | None:
        return games.get(game_id)

    def create_game_from_lobby(self, lobby: Lobby) -> Game:
        if lobby.id in games:
            return games[lobby.id]

        players: List[Player] = []
        for p_template in lobby.players:
            if not p_template.character:
                raise GameException("Не все игроки выбрали персонажа.")
            
            player = p_template.copy(deep=True)
            player.hp = player.character.max_hp
            player.energy = 0
            
            deck = self._build_deck_for_player(player)
            random.shuffle(deck)
            player.deck = deck
            
            hand_size = 6 if player.character.name == "Сатору Годзё" else 5
            player.hand = self._draw_cards(player, hand_size)
            
            players.append(player)
            
        random.shuffle(players)
        
        game = Game(
            game_id=lobby.id,
            players=players,
            game_state=GameState.IN_GAME,
            game_log=[f"Игра началась! Порядок ходов: {', '.join([p.nickname for p in players])}"]
        )
        games[game.game_id] = game
        return game

    def _build_deck_for_player(self, player: Player) -> List[Card]:
        deck = [card.copy(deep=True) for card in common_cards]
        deck.extend([card.copy(deep=True) for card in player.character.unique_cards])
        
        if player.character.name == "Рёмен Сукуна":
            for card in deck:
                if card.name == "Простая Территория":
                    card.name = "Сплетение Абсолютной Пустоты"
        
        return deck

    def end_turn(self, game_id: str, player_id: str) -> Game:
        game = self.get_game(game_id)
        if not game:
            raise GameException("Игра не найдена.")
        
        current_player = game.players[game.current_turn_player_index]
        if current_player.id != player_id:
            raise GameException("Сейчас не ваш ход.")

        self._process_passives(game, current_player, "end_of_your_turn")
        self._process_effects(game, current_player, "end_of_your_turn")
        self._check_for_winner(game)
        if game.game_state == GameState.FINISHED:
            return game

        self._move_to_next_player(game)
        return game

    def play_card(self, game_id: str, player_id: str, card_name: str, target_id: str = None, targets_ids: List[str] = None) -> Game:
        game = self.get_game(game_id)
        if not game: raise GameException("Игра не найдена.")
        player = self._find_player(game, player_id)
        if not player or player.status == PlayerStatus.DEFEATED: raise GameException("Игрок не найден или побежден.")
        if game.players[game.current_turn_player_index].id != player_id: raise GameException("Сейчас не ваш ход.")
        
        card_to_play = next((card for card in player.hand if card.name == card_name), None)
        if not card_to_play: raise GameException("Карта не найдена в руке.")
        if player.energy < card_to_play.cost: raise GameException("Недостаточно Проклятой Энергии.")

        # Check for Gojo's Domain Expansion effect
        if any(e.name == "Информационная перегрузка" for e in player.effects):
            if card_to_play.type == CardType.TECHNIQUE or card_to_play.rarity in [Rarity.EPIC, Rarity.LEGENDARY]:
                raise GameException("Вы не можете использовать эту карту из-за эффекта 'Информационная перегрузка'.")

        player.energy -= card_to_play.cost
        player.hand.remove(card_to_play)
        player.discard_pile.append(card_to_play)

        effect_func = self.card_effects.get(card_name)
        if effect_func:
            game = effect_func(game, player, target_id, targets_ids)
        else:
            game.game_log.append(f"Неизвестный эффект для карты: {card_name}")

        self._check_for_winner(game)
        return game

    def discard_cards(self, game_id: str, player_id: str, card_names: List[str]) -> Game:
        game = self.get_game(game_id)
        if not game:
            raise GameException("Игра не найдена.")

        player = self._find_player(game, player_id)
        if not player or player.status == PlayerStatus.DEFEATED:
            raise GameException("Игрок не найден или побежден.")

        if game.players[game.current_turn_player_index].id != player_id:
            raise GameException("Сейчас не ваш ход.")

        if player.last_discard_round == game.round_number:
            raise GameException("Вы уже использовали сброс карт в этом раунде.")

        if not card_names or len(card_names) > 2:
            raise GameException("Можно сбросить от 1 до 2 карт.")

        actually_discarded = []
        for name in card_names:
            card = next((c for c in player.hand if c.name == name), None)
            if card:
                player.hand.remove(card)
                player.discard_pile.append(card)
                actually_discarded.append(card)

        if not actually_discarded:
            raise GameException("Выбранные карты не найдены в руке.")

        # добираем такое же количество карт
        new_cards = self._draw_cards(player, len(actually_discarded))
        player.hand.extend(new_cards)

        player.last_discard_round = game.round_number
        game.game_log.append(
            f"{player.nickname} сбросил {len(actually_discarded)} карт(ы) и добрал столько же." )

        return game

    def _get_player_index(self, game: Game, player_id: str) -> int:
        for i, p in enumerate(game.players):
            if p.id == player_id:
                return i
        return -1

    def _get_left_player(self, game: Game, player_index: int) -> Player:
        size = len(game.players)
        for i in range(1, size):
            left_player = game.players[(player_index - i + size) % size]
            if left_player.status == PlayerStatus.ALIVE:
                return left_player
        return None

    def _get_right_player(self, game: Game, player_index: int) -> Player:
        size = len(game.players)
        for i in range(1, size):
            right_player = game.players[(player_index + i) % size]
            if right_player.status == PlayerStatus.ALIVE:
                return right_player
        return None

    def _move_to_next_player(self, game: Game):
        current_idx = game.current_turn_player_index
        next_player_found = False
        for i in range(1, len(game.players) + 1):
            next_idx = (current_idx + i) % len(game.players)
            if game.players[next_idx].status == PlayerStatus.ALIVE:
                is_new_round = next_idx <= game.current_turn_player_index
                game.current_turn_player_index = next_idx
                next_player_found = True
                if is_new_round:
                    self._start_new_round(game)
                break
        
        if not next_player_found:
            self._check_for_winner(game)
            return

        new_current_player = game.players[game.current_turn_player_index]
        self._process_passives(game, new_current_player, "start_of_your_turn")
        self._process_effects(game, new_current_player, "start_of_your_turn")
        
    def _start_new_round(self, game: Game):
        game.round_number += 1
        game.game_log.append(f"--- Начало раунда {game.round_number} ---")
        for player in game.players:
            # Tick effects first
            player.effects = [effect for effect in player.effects if (effect.duration - 1) > 0]
            for effect in player.effects:
                effect.duration -= 1
                if effect.name == "Последний Бой" and effect.duration == 0:
                    self._defeat_player(game, player)

            if player.status == PlayerStatus.ALIVE:
                hand_size = 6 if player.character.name == "Сатору Годзё" else 5
                # Mahito's Domain Expansion effect
                if game.active_domain and game.active_domain.name == "Самовоплощение Совершенства" and player.id != game.active_domain.source_player_id:
                     hand_size = 4

                # Сохраняем карты, оставшиеся в руке, и добираем недостающие
                missing = max(hand_size - len(player.hand), 0)
                if missing > 0:
                    player.hand.extend(self._draw_cards(player, missing))
                player.energy = min(player.character.max_energy, player.energy + int(player.character.max_energy * 0.20))
                player.block = 0
                
    def _draw_cards(self, player: Player, num_cards: int) -> List[Card]:
        drawn_cards = []
        for _ in range(num_cards):
            if not player.deck:
                if not player.discard_pile: break
                player.deck = player.discard_pile
                player.discard_pile = []
                random.shuffle(player.deck)
            if player.deck:
                drawn_cards.append(player.deck.pop())
        return drawn_cards

    def _find_player(self, game: Game, player_id: str) -> Player | None:
        return next((p for p in game.players if p.id == player_id), None)
        
    def _deal_damage(self, game: Game, source_player:Player, target: Player, damage: int, ignores_block: bool = False, card_type: CardType = None):
        if target.status == PlayerStatus.DEFEATED: return

        # Sukuna's passive
        source_idx = self._get_player_index(game, source_player.id)
        target_idx = self._get_player_index(game, target.id)
        left_of_target = self._get_left_player(game, target_idx)
        right_of_target = self._get_right_player(game, target_idx)
        if (left_of_target and left_of_target.id == source_player.id and source_player.character.name == "Рёмен Сукуна") or \
           (right_of_target and right_of_target.id == source_player.id and source_player.character.name == "Рёмен Сукуна"):
            damage = int(damage * 0.85)

        actual_damage = damage

        # Neutralize hit-sure with Simple Domain
        is_hit_sure = game.active_domain and game.active_domain.source_player_id == source_player.id
        if is_hit_sure and any(e.name in ["Простая Территория", "Сплетение Абсолютной Пустоты"] for e in target.effects):
            game.game_log.append(f"{target.nickname} нейтрализует верное попадание!")
        else:
            if not ignores_block:
                # Mahito's Domain Expansion effect
                if game.active_domain and game.active_domain.name == "Самовоплощение Совершенства" and target.id != game.active_domain.source_player_id:
                    target.block = 0
                
                absorbed_by_block = min(target.block, actual_damage)
                target.block -= absorbed_by_block
                actual_damage -= absorbed_by_block
            
            target.hp -= actual_damage
            game.game_log.append(f"{target.nickname} получает {damage} урона.")

            # Jogo's passive
            if source_player.character.name == "Дзёго" and card_type == CardType.TECHNIQUE:
                self._apply_effect(game, source_player, target, "Горение", 2, 100)
            
            # Yuta's passive
            if target.character.name == "Юта Оккоцу" and card_type == CardType.TECHNIQUE:
                card_to_copy = next((c for c in source_player.character.unique_cards if c.type == card_type), None) # simplified
                if card_to_copy:
                    copied_card = card_to_copy.copy(deep=True)
                    copied_card.cost += 4000
                    target.discard_pile.append(copied_card)
                    game.game_log.append(f"Рика скопировала {copied_card.name} для {target.nickname}!")
        
        if target.hp <= 0:
            if any(e.name == "Последний Бой" for e in target.effects) and target.hp >= -3500:
                 pass
            else:
                self._defeat_player(game, target)

    def _defeat_player(self, game: Game, player: Player):
        player.hp = 0
        player.status = PlayerStatus.DEFEATED
        game.game_log.append(f"Игрок {player.nickname} побежден!")

    def _check_for_winner(self, game: Game):
        alive_players = [p for p in game.players if p.status == PlayerStatus.ALIVE]
        if len(alive_players) <= 1:
            game.game_state = GameState.FINISHED
            winner = alive_players[0] if alive_players else None
            win_message = f"👑 Игра окончена! Победитель: {winner.nickname}! 👑" if winner else "Игра окончена! Ничья."
            if game.game_log[-1] != win_message: game.game_log.append(win_message)
    
    def _apply_effect(self, game: Game, source: Player, target: Player, name: str, duration: int, value: int = None):
        # Prevent stacking certain unique effects
        if name in [e.name for e in target.effects]:
             # a rule could be to refresh duration, for now, just skip
            return
        
        effect = Effect(name=name, duration=duration, value=value, source_player_id=source.id)
        target.effects.append(effect)
        game.game_log.append(f"{target.nickname} получает эффект '{name}' на {duration} раунда.")

    def _process_passives(self, game: Game, player: Player, trigger: str):
        if trigger == "end_of_your_turn":
            if player.character.name == "Юта Оккоцу" and player.status == PlayerStatus.ALIVE:
                damage = 250
                if any(e.name == "Полное Проявление: Рика" for e in player.effects):
                    damage = 1000
                    opponents = [p for p in game.players if p.id != player.id and p.status == PlayerStatus.ALIVE]
                    for opponent in opponents:
                        self._deal_damage(game, player, opponent, damage, ignores_block=True)
                else:
                    opponents = [p for p in game.players if p.id != player.id and p.status == PlayerStatus.ALIVE]
                    if opponents:
                        random_opponent = random.choice(opponents)
                        self._deal_damage(game, player, random_opponent, damage, ignores_block=True)
    
    def _process_effects(self, game: Game, player: Player, trigger: str):
        effects_to_process = [e for e in player.effects]
        for effect in effects_to_process:
            if trigger == "start_of_your_turn":
                if effect.name == "Горение":
                    self._deal_damage(game, self._find_player(game, effect.source_player_id), player, effect.value, ignores_block=True)
                elif effect.name == "Полиморфный Душевный Изомер":
                    self._deal_damage(game, self._find_player(game, effect.source_player_id), player, effect.value, ignores_block=True)
                elif effect.name == "Гроб Стальной Горы":
                     self._deal_damage(game, self._find_player(game, effect.source_player_id), player, 800, ignores_block=False)
                elif effect.name == "Простая Территория" or effect.name == "Сплетение Абсолютной Пустоты":
                     player.block += 200
                     game.game_log.append(f"{player.nickname} получает 200 блока от 'Простой территории'.")

            elif trigger == "end_of_your_turn":
                if effect.name == "Злобное Святилище":
                    opponents = [p for p in game.players if p.id != player.id and p.status == PlayerStatus.ALIVE]
                    for opponent in opponents:
                        # Ignores block from "Защита" card, a bit tricky, let's just ignore all block for simplicity
                        self._deal_damage(game, player, opponent, 1000, ignores_block=True)
                if effect.name == "Кулак Дивергента":
                    target = self._find_player(game, effect.target_id) # Need to store target_id in effect
                    if target: self._deal_damage(game, player, target, 200, ignores_block=False)


    def _map_card_effects(self) -> Dict[str, Callable]:
        return {
            "Удар": self._effect_udar,
            "Защита": self._effect_zashchita,
            "Концентрация": self._effect_kontsentratsiia,
            "Чёрная Вспышка": self._effect_chernaia_vspyshka,
            "Обратная Проклятая Техника": self._effect_obratnaia_prokliataia_tekhnika,
            "Песнопение (Чант)": self._effect_pesnopenie,
            "Простая Территория": self._effect_prostaia_territoriia,
            "Сплетение Абсолютной Пустоты": self._effect_prostaia_territoriia, # Same effect
            "Чувства Опадающего Цветка": self._effect_chuvstva_opadaiushchego_tsvetka,
            
            # Gojo
            "Техника Бесконечности: Нейтраль": self._effect_tekhnika_beskonechnosti,
            "Проклятая техника: 'Синий'": self._effect_sinii,
            "Обратная проклятая техника: 'Красный'": self._effect_krasnyi,
            "Мнимая техника: 'Фиолетовый'": self._effect_fioletovyi,
            "Расширение Территории: Необъятная Бездна": self._effect_neobiatnaia_bezdna,

            # Sukuna
            "Разрез": self._effect_razrez,
            "Расщепление": self._effect_rasshcheplenie,
            "Камино (Пламенная стрела)": self._effect_kamino,
            "Расширение Территории: Злобное Святилище": self._effect_zlobnoe_sviatilishche,
            
            # Mahito
            "Касание Души": self._effect_kasanie_dushi,
            "Искажение Души": self._effect_iskazhenie_dushi,
            "Полиморфный Душевный Изомер": self._effect_polimorfnyi_dushevnyi_izomer,
            "Расширение Территории: Самовоплощение Совершенства": self._effect_samovoploshchenie_sovershenstva,

            # Yuji
            "Кулак Дивергента": self._effect_kulak_divergenta,
            "Заход с разворота": self._effect_zakhod_s_razvorota,
            "Глубокая Концентрация": self._effect_glubokaia_kontsentratsiia,
            "Несгибаемая Воля": self._effect_nesgibaemaia_volia,

            # Jogo
            "Сикигами: Угольки": self._effect_ugolki,
            "Извержение Вулкана": self._effect_izverzhenie_vulkana,
            "Максимум: Метеор": self._effect_maksimum_meteor,
            "Расширение Территории: Гроб Стальной Горы": self._effect_grob_stalnoi_gory,

            # Yuta
            "Клинок, Усиленный Энергией": self._effect_klinok_usilennyi_energiei,
            "Полное Проявление: Рика": self._effect_polnoe_proiavlenie_rika,
            "Расширение Территории: Истинная и Взаимная Любовь": self._effect_istinnaia_i_vzaimnaia_liubov,
        }

    # --- CARD EFFECT IMPLEMENTATIONS ---
    
    def _effect_udar(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        target = self._find_player(game, target_id)
        if not target: return game
        damage = 300
        if player.character.name == "Юдзи Итадори": damage += 150
        if target.character.name == "Махито":
            game.game_log.append(f"Удар не наносит урона {target.nickname} из-за 'Праздной Трансфигурации'!")
            return game
        self._deal_damage(game, player, target, damage, card_type=CardType.ACTION)
        return game

    def _effect_zashchita(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        player.block += 300
        game.game_log.append(f"{player.nickname} получает 300 блока.")
        return game
        
    def _effect_kontsentratsiia(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        player.energy = min(player.character.max_energy, player.energy + 8000)
        game.game_log.append(f"{player.nickname} восстанавливает 8000 Проклятой Энергии.")
        return game
        
    def _effect_chernaia_vspyshka(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        target = self._find_player(game, target_id)
        if not target: return game
        chance = 2 if player.character.name == "Юдзи Итадори" else 1
        guaranteed_effect = next((e for e in player.effects if e.name == "Глубокая Концентрация"), None)
        if guaranteed_effect or random.randint(1, 6) <= chance:
            self._deal_damage(game, player, target, 3500, card_type=CardType.TECHNIQUE)
            if guaranteed_effect: player.effects.remove(guaranteed_effect)
        else:
            self._deal_damage(game, player, target, 300, card_type=CardType.TECHNIQUE)
        return game

    def _effect_obratnaia_prokliataia_tekhnika(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        heal_amount = 1200
        player.hp = min(player.character.max_hp, player.hp + heal_amount)
        game.game_log.append(f"{player.nickname} восстанавливает {heal_amount} ХП.")
        return game

    def _effect_pesnopenie(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        self._apply_effect(game, player, player, "Песнопение", 1) # Lasts for one turn (until next card)
        return game

    def _effect_prostaia_territoriia(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        effect_name = "Сплетение Абсолютной Пустоты" if player.character.name == "Рёмен Сукуна" else "Простая Территория"
        self._apply_effect(game, player, player, effect_name, 2)
        return game

    def _effect_chuvstva_opadaiushchego_tsvetka(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        self._apply_effect(game, player, player, "Чувства Опадающего Цветка", 3)
        return game

    # Gojo
    def _effect_tekhnika_beskonechnosti(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        target = self._find_player(game, target_id)
        if not target: return game
        self._apply_effect(game, player, player, f"Бесконечность против {target.nickname}", 1)
        return game

    def _effect_sinii(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        opponents = [p for p in game.players if p.id != player.id and p.status == PlayerStatus.ALIVE]
        targets = random.sample(opponents, k=min(len(opponents), 2))
        for target in targets:
            self._deal_damage(game, player, target, 1000, card_type=CardType.TECHNIQUE)
        return game

    def _effect_krasnyi(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        main_target = self._find_player(game, target_id)
        if not main_target: return game
        self._deal_damage(game, player, main_target, 1200, card_type=CardType.TECHNIQUE)
        
        main_target_idx = self._get_player_index(game, main_target.id)
        right_player = self._get_right_player(game, main_target_idx)
        if right_player:
            self._deal_damage(game, player, right_player, 600, card_type=CardType.TECHNIQUE)
        return game

    def _effect_fioletovyi(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        opponents = [p for p in game.players if p.id != player.id and p.status == PlayerStatus.ALIVE]
        for opponent in opponents:
            self._deal_damage(game, player, opponent, 2200, ignores_block=True, card_type=CardType.TECHNIQUE)
        return game
    
    def _effect_neobiatnaia_bezdna(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        game.active_domain = Card(
            name="Необъятная Бездна",
            type=CardType.DOMAIN_EXPANSION,
            rarity=Rarity.LEGENDARY,
            cost=0,
            description="Расширение Территории",
            source_player_id=player.id,
            duration=3,
        )
        game.game_log.append(f"{player.nickname} активирует Расширение Территории: Необъятная Бездна!")
        opponents = [p for p in game.players if p.id != player.id and p.status == PlayerStatus.ALIVE]
        for opponent in opponents:
            self._apply_effect(game, player, opponent, "Информационная перегрузка", 3)
        return game
    
    # Sukuna
    def _effect_razrez(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        main_target = self._find_player(game, target_id)
        if not main_target: return game
        self._deal_damage(game, player, main_target, 600, card_type=CardType.TECHNIQUE)
        
        main_target_idx = self._get_player_index(game, main_target.id)
        left_player = self._get_left_player(game, main_target_idx)
        if left_player:
            self._deal_damage(game, player, left_player, 300, card_type=CardType.TECHNIQUE)
        return game

    def _effect_rasshcheplenie(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        target = self._find_player(game, target_id)
        if not target: return game
        self._deal_damage(game, player, target, 1600, card_type=CardType.TECHNIQUE)
        return game
        
    def _effect_kamino(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        is_shrine_active = game.active_domain and game.active_domain.name == "Злобное Святилище"
        if is_shrine_active:
            opponents = [p for p in game.players if p.id != player.id and p.status == PlayerStatus.ALIVE]
            for opponent in opponents:
                self._deal_damage(game, player, opponent, 1200, card_type=CardType.TECHNIQUE)
        else:
            target = self._find_player(game, target_id)
            if not target: return game
            
            target_hp_before = target.hp
            self._deal_damage(game, player, target, 1800, card_type=CardType.TECHNIQUE)
            if target.hp <= 0 and target_hp_before > 0:
                player.energy = min(player.character.max_energy, player.energy + 10000)
                game.game_log.append(f"{player.nickname} восстанавливает 10000 ПЭ за убийство.")
        return game

    def _effect_zlobnoe_sviatilishche(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        game.active_domain = Card(
            name="Злобное Святилище",
            type=CardType.DOMAIN_EXPANSION,
            rarity=Rarity.LEGENDARY,
            cost=0,
            description="Расширение Территории",
            source_player_id=player.id,
            duration=3,
        )
        self._apply_effect(game, player, player, "Злобное Святилище", 3)
        game.game_log.append(f"{player.nickname} активирует Расширение Территории: Злобное Святилище!")
        return game

    # Mahito
    def _effect_kasanie_dushi(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        target = self._find_player(game, target_id)
        if not target: return game
        self._deal_damage(game, player, target, 250, ignores_block=True, card_type=CardType.TECHNIQUE)
        return game

    def _effect_iskazhenie_dushi(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        target = self._find_player(game, target_id)
        if not target: return game
        if len(target.hand) > 0:
            cards_to_discard = random.sample(target.hand, k=min(len(target.hand), 2))
            for card in cards_to_discard:
                target.hand.remove(card)
                target.discard_pile.append(card)
            game.game_log.append(f"{player.nickname} заставляет {target.nickname} сбросить {len(cards_to_discard)} карты.")
        return game

    def _effect_polimorfnyi_dushevnyi_izomer(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        target = self._find_player(game, target_id)
        if not target: return game
        self._apply_effect(game, player, target, "Полиморфный Душевный Изомер", 2, 400)
        return game
        
    def _effect_samovoploshchenie_sovershenstva(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        game.active_domain = Card(
            name="Самовоплощение Совершенства",
            type=CardType.DOMAIN_EXPANSION,
            rarity=Rarity.LEGENDARY,
            cost=0,
            description="Расширение Территории",
            source_player_id=player.id,
            duration=3,
        )
        game.game_log.append(f"{player.nickname} активирует Расширение Территории: Самовоплощение Совершенства!")
        return game

    # Yuji
    def _effect_kulak_divergenta(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        target = self._find_player(game, target_id)
        if not target: return game
        self._deal_damage(game, player, target, 400, card_type=CardType.TECHNIQUE)
        # This is tricky. The effect needs to remember the target.
        # Let's add target_id to the effect model.
        # I will modify the model in the next step. For now, this is a placeholder.
        effect = Effect(name="Кулак Дивергента", duration=1, source_player_id=player.id, target_id=target.id)
        player.effects.append(effect)
        return game
        
    def _effect_zakhod_s_razvorota(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        udar_card = next((c for c in player.deck if c.name == "Удар"), None)
        if udar_card:
            player.deck.remove(udar_card)
            udar_card.cost = 0 # This should be temporary for one turn. Add effect.
            player.hand.append(udar_card)
            game.game_log.append(f"{player.nickname} берет 'Удар' из колоды.")
        return game
        
    def _effect_glubokaia_kontsentratsiia(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        self._apply_effect(game, player, player, "Глубокая Концентрация", 99) # Lasts until used
        return game
        
    def _effect_nesgibaemaia_volia(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        self._apply_effect(game, player, player, "Последний Бой", 5)
        return game
        
    # Jogo
    def _effect_ugolki(self, game: Game, player: Player, target_id: str, targets_ids: List[str]) -> Game:
        if not targets_ids:
            opponents = [p for p in game.players if p.id != player.id and p.status == PlayerStatus.ALIVE]
            targets_ids = [p.id for p in random.sample(opponents, k=min(len(opponents), 3))]
        
        for t_id in targets_ids:
            target = self._find_player(game, t_id)
            if target:
                self._deal_damage(game, player, target, 300, card_type=CardType.TECHNIQUE)
        return game

    def _effect_izverzhenie_vulkana(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        opponents = [p for p in game.players if p.id != player.id and p.status == PlayerStatus.ALIVE]
        for opponent in opponents:
            self._deal_damage(game, player, opponent, 600, card_type=CardType.TECHNIQUE)
        return game

    def _effect_maksimum_meteor(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        main_target = self._find_player(game, target_id)
        if not main_target: return game
        self._deal_damage(game, player, main_target, 2000, card_type=CardType.TECHNIQUE)
        
        main_target_idx = self._get_player_index(game, main_target.id)
        left_player = self._get_left_player(game, main_target_idx)
        right_player = self._get_right_player(game, main_target_idx)
        if left_player:
            self._deal_damage(game, player, left_player, 500, card_type=CardType.TECHNIQUE)
        if right_player:
            self._deal_damage(game, player, right_player, 500, card_type=CardType.TECHNIQUE)
        return game

    def _effect_grob_stalnoi_gory(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        game.active_domain = Card(
            name="Гроб Стальной Горы",
            type=CardType.DOMAIN_EXPANSION,
            rarity=Rarity.LEGENDARY,
            cost=0,
            description="Расширение Территории",
            source_player_id=player.id,
            duration=3,
        )
        game.game_log.append(f"{player.nickname} активирует Расширение Территории: Гроб Стальной Горы!")
        opponents = [p for p in game.players if p.id != player.id and p.status == PlayerStatus.ALIVE]
        for opponent in opponents:
             self._apply_effect(game, player, opponent, "Гроб Стальной Горы", 3)
        return game
        
    # Yuta
    def _effect_klinok_usilennyi_energiei(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        target = self._find_player(game, target_id)
        if not target: return game
        self._deal_damage(game, player, target, 500, card_type=CardType.TECHNIQUE)
        return game

    def _effect_polnoe_proiavlenie_rika(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        self._apply_effect(game, player, player, "Полное Проявление: Рика", 3)
        return game

    def _effect_istinnaia_i_vzaimnaia_liubov(self, game: Game, player: Player, target_id: str, targets_ids) -> Game:
        self._apply_effect(game, player, player, "Истинная и Взаимная Любовь", 3)
        game.game_log.append(f"{player.nickname} активирует Расширение Территории: Истинная и Взаимная Любовь!")
        return game

game_manager = GameManager()
