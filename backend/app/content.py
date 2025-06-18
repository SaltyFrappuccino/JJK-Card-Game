from .models import Card, CardType, Rarity, Character

# --- Общие карты ---

common_cards = [
    Card(
        id="common_strike",
        name="Удар",
        type=CardType.ACTION,
        rarity=Rarity.COMMON,
        cost=0,
        description="Наносит 300 урона."
    ),
    Card(
        id="common_defense",
        name="Защита",
        type=CardType.ACTION,
        rarity=Rarity.COMMON,
        cost=0,
        description="Даёт 300 блока."
    ),
    Card(
        id="common_concentration",
        name="Концентрация",
        type=CardType.ACTION,
        rarity=Rarity.COMMON,
        cost=0,
        description="Вы восстанавливаете от 5 до 15% вашего ПЭ."
    ),
    Card(
        id="common_chant",
        name="Песнопение (Чант)",
        type=CardType.ACTION,
        rarity=Rarity.EPIC,
        cost=5000,
        description="Следующая разыгранная Техника будет усилена на 50%."
    ),
    Card(
        id="common_simple_domain",
        name="Простая Территория",
        type=CardType.ANTI_DOMAIN_TECHNIQUE,
        rarity=Rarity.UNCOMMON,
        cost=4000,
        description="Снимает с вас все эффекты вражеской территории и даёт невосприимчивость к ним на 2 раунда."
    ),
    Card(
        id="common_falling_blossom_emotion",
        name="Чувства Опадающего Цветка",
        type=CardType.ANTI_DOMAIN_TECHNIQUE,
        rarity=Rarity.RARE,
        cost=6000,
        description="На 3 раунда, когда вас атакуют картой Техники, наносящей урон, урон от неё режется на 33%, также работает с уроном от РТ. Округляется до целого числа."
    ),
    Card(
        id="common_reverse_cursed_technique",
        name="Обратная Проклятая Техника",
        type=CardType.TECHNIQUE,
        rarity=Rarity.EPIC,
        cost=10000,
        description="Восстанавливает от 5% до 15% от вашего максимального запаса здоровья."
    ),
    Card(
        id="common_black_flash",
        name="Чёрная Вспышка",
        type=CardType.ACTION,
        rarity=Rarity.EPIC,
        cost=0,
        description="С шансом 1 к 6 наносит 2500 урона вместо 100. Юдзи имеет шанс 2 к 6. При успехе накладывает на вас эффект \"Зона\" на 3 хода. Некоторые эффекты могут гарантировать успех."
    ),
]

# --- Персонажи и их уникальные карты (v1.1) ---

characters = [
    Character(
        id="gojo_satoru",
        name="Сатору Годзё",
        max_hp=5500,
        max_energy=75000,
        passive_ability_name="Шесть глаз и Бесконечность",
        passive_ability_description="Постоянно: вы видите точное количество ПЭ всех игроков, ваша максимальная рука увеличена до 6 карт. В начале игры вы получаете эффект \"Повязка\", который можно снять картой \"Снять Повязку\". После снятия \"Повязки\" в начале каждого вашего раунда стоимость всех ваших карт снижается на 5% от базовой, эффект накапливается до -90%.",
        unique_cards=[
            Card(
                id="gojo_remove_blindfold",
                name="Снять Повязку",
                type=CardType.TECHNIQUE,
                rarity=Rarity.LEGENDARY,
                cost=0,
                description="Снимает с вас эффект \"Повязка\".\nУсловие: ваше текущее ХП должно быть меньше или равно 33% от максимального."
            ),
            Card(
                id="gojo_strengthened_strike",
                name="Усиленный Удар",
                type=CardType.ACTION,
                rarity=Rarity.UNCOMMON,
                cost=0,
                description="Наносит 300 урона. Этот урон игнорирует блок."
            ),
            Card(
                id="gojo_infinity",
                name="Бесконечность",
                type=CardType.TECHNIQUE,
                rarity=Rarity.RARE,
                cost=8000,
                description="В течение 1 раунда все атаки одной цели, нацеленные на вас, автоматически отменяются. AoE-атаки наносят урон как обычно."
            ),
            Card(
                id="gojo_blue",
                name="Проклятая техника: \"Синий\"",
                type=CardType.TECHNIQUE,
                rarity=Rarity.RARE,
                cost=10000,
                description="Наносит 1000 урона 2-м случайным противникам. Активирует условие для \"Фиолетового\"."
            ),
            Card(
                id="gojo_red",
                name="Обратная проклятая техника: \"Красный\"",
                type=CardType.TECHNIQUE,
                rarity=Rarity.RARE,
                cost=12000,
                description="Наносит 1200 урона основной цели и 600 урона игроку справа от неё. Активирует условие для \"Фиолетового\"."
            ),
            Card(
                id="gojo_purple",
                name="Мнимая техника: \"Фиолетовый\"",
                type=CardType.TECHNIQUE,
                rarity=Rarity.EPIC,
                cost=30000,
                description="Наносит 4000 урона одной цели. Этот урон игнорирует блок.\nУсловие: ранее в игре должны быть использованы \"Синий\" и \"Красный\"."
            ),
            Card(
                id="gojo_unlimited_void",
                name="Расширение Территории: Необъятная Бездна",
                type=CardType.DOMAIN_EXPANSION,
                rarity=Rarity.LEGENDARY,
                cost=50000,
                description="Все противники получают эффект \"Информационная перегрузка\" на 3 раунда (не могут использовать карты Техник, Эпические и Легендарные)."
            ),
        ]
    ),
    Character(
        id="sukuna_ryomen",
        name="Рёмен Сукуна",
        max_hp=7000,
        max_energy=100000,
        passive_ability_name="Жажда Развлечений",
        passive_ability_description="Если вам наносит урон противник, чей текущий % ХП больше, чем ваш, вы немедленно восстанавливаете 5% от вашего максимального запаса ПЭ (5000 ПЭ).",
        unique_cards=[
            Card(
                id="sukuna_cleave",
                name="Разрез",
                type=CardType.TECHNIQUE,
                rarity=Rarity.UNCOMMON,
                cost=4000,
                description="Наносит 600 урона основной цели и 300 урона игроку слева от неё."
            ),
            Card(
                id="sukuna_dismantle",
                name="Расщепление",
                type=CardType.TECHNIQUE,
                rarity=Rarity.RARE,
                cost=16000,
                description="Наносит 1600 урона одной цели."
            ),
            Card(
                id="sukuna_spiderweb",
                name="Расщепление: Паутина",
                type=CardType.TECHNIQUE,
                rarity=Rarity.RARE,
                cost=18000,
                description="Наносит 1000 урона основной цели и по 500 урона игрокам слева и справа от неё."
            ),
            Card(
                id="sukuna_kamino",
                name="Камино (Пламенная стрела)",
                type=CardType.TECHNIQUE,
                rarity=Rarity.EPIC,
                cost=20000,
                description="Наносит 1800 урона. Если атака убивает цель, вы восстанавливаете 10 000 ПЭ.\nСинергия: если активна \"Гробница Зла\", наносит 1200 урона всем."
            ),
            Card(
                id="sukuna_malevolent_shrine",
                name="Расширение Территории: Гробница Зла",
                type=CardType.DOMAIN_EXPANSION,
                rarity=Rarity.LEGENDARY,
                cost=40000,
                description="Накладывает на всех оппонентов эффект, который в конце их хода наносит им 1500 урона. Длится 3 раунда. Урон игнорируется, если у цели активна 'Простая Территория'."
            ),
        ]
    ),
    Character(
        id="mahito",
        name="Махито",
        max_hp=4000,
        max_energy=50000,
        passive_ability_name="Праздная Трансфигурация",
        passive_ability_description="Карта \"Удар\" наносит вам 0 урона. Вы начинаете игру с 0 Искажённых Душ. Каждые 2 своих хода вы гарантированно получаете карту 'Касание Души' в руку.",
        unique_cards=[
            Card(
                id="mahito_soul_touch",
                name="Касание Души",
                type=CardType.TECHNIQUE,
                rarity=Rarity.UNCOMMON,
                cost=3000,
                description="Наносит по 250 урона игрокам слева и справа от вас (игнорирует блок). За каждого пораженного игрока вы получаете 1 Искажённую Душу."
            ),
            Card(
                id="mahito_soul_distortion",
                name="Искажение Души",
                type=CardType.TECHNIQUE,
                rarity=Rarity.RARE,
                cost=8000,
                description="Цель сбрасывает 1 случайную карту из руки."
            ),
            Card(
                id="mahito_polymorphic_soul_isomer",
                name="Полиморфная Изомерная Душа",
                type=CardType.TECHNIQUE,
                rarity=Rarity.RARE,
                cost=0,
                description="Стоимость: 1 Искажённая Душа. Дает 500 блока. Игроку, который наносит удар, снимающий этот блок, наносится 500 урона."
            ),
            Card(
                id="mahito_body_repel",
                name="Отталкивание Тела",
                type=CardType.TECHNIQUE,
                rarity=Rarity.EPIC,
                cost=0,
                description="Стоимость: 3 Искажённые Души. Наносит 1400 урона одной цели. Если у цели есть блок, урон увеличивается на 50%."
            ),
            Card(
                id="mahito_true_form",
                name="Искажённое Тело Изорённых Убийств",
                type=CardType.TECHNIQUE,
                rarity=Rarity.LEGENDARY,
                cost=30000,
                description="Вы получаете постоянный эффект: урон от вражеских \"Ударов\" по вам снижен на 50%, вы получаете 500 блока в начале раунда, а ваш \"Удар\" наносит урон в 3 раза больше (900).\nУсловие: вы должны успешно использовать \"Чёрную Вспышку\"."
            ),
            Card(
                id="mahito_self_embodiment_of_perfection",
                name="Расширение Территории: Самовоплощение Совершенства",
                type=CardType.DOMAIN_EXPANSION,
                rarity=Rarity.LEGENDARY,
                cost=35000,
                description="На 3 раунда все противники получают эффект \"Искажение души\": их блок аннулируется, и в начале их хода они сбрасывают 1 случайную карту. В начале вашего хода вы получаете 1 Искажённую Душу за каждого противника под действием этой территории."
            ),
        ]
    ),
    Character(
        id="itadori_yuji",
        name="Юдзи Итадори",
        max_hp=7500,
        max_energy=40000,
        passive_ability_name="Сверхчеловеческая Сила",
        passive_ability_description="Ваши 'Удары' наносят +150 урона. Каждый раз, когда вы играете карту 'Удар', вы восстанавливаете 1000 ПЭ. Ваш базовый шанс 'Чёрной Вспышки' равен 2/6. Когда на вас есть эффект \"Зона\", ваш шанс становится 3/6.",
        unique_cards=[
            Card(
                id="itadori_divergent_fist",
                name="Кулак Дивергента",
                type=CardType.TECHNIQUE,
                rarity=Rarity.UNCOMMON,
                cost=2000,
                description="Наносит 400 урона. В начале следующего хода цели наносит ещё 200."
            ),
            Card(
                id="itadori_manji_kick",
                name="Манджи-Кик",
                type=CardType.TECHNIQUE,
                rarity=Rarity.RARE,
                cost=6000,
                description="Наносит 600 урона цели. Следующая атакующая карта (любая, кроме РТ), которую эта цель сыграет против вас, будет отменена."
            ),
            Card(
                id="itadori_deep_concentration",
                name="Глубокая Концентрация",
                type=CardType.TECHNIQUE,
                rarity=Rarity.EPIC,
                cost=18000,
                description="Вы получаете эффект \"Концентрация\" на 2 хода. Следующая ваша \"Чёрная Вспышка\", сыгранная пока эффект активен, гарантированно сработает."
            ),
            Card(
                id="itadori_unwavering_will",
                name="Несгибаемая Воля",
                type=CardType.TECHNIQUE,
                rarity=Rarity.LEGENDARY,
                cost=25000,
                description="Получаете эффект \"Последний Бой\" на 5 ваших ходов. Пока он активен, ваше ХП может опускаться до -3500. Как только эффект заканчивается, вы проигрываете."
            ),
        ]
    ),
    Character(
        id="jogo",
        name="Дзёго",
        max_hp=5000,
        max_energy=65000,
        passive_ability_name="Прикосновение Лавы",
        passive_ability_description="Каждый раз, когда вы наносите урон картой Техники, цель получает эффект \"Горение\" на 2 раунда (100 урона в начале её хода).",
        unique_cards=[
            Card(
                id="jogo_ember_insects",
                name="Сикигами: Угольки",
                type=CardType.TECHNIQUE,
                rarity=Rarity.UNCOMMON,
                cost=4000,
                description="Атакует до 3 целей, нанося каждой по 300 урона."
            ),
            Card(
                id="jogo_volcano_eruption",
                name="Извержение Вулкана",
                type=CardType.TECHNIQUE,
                rarity=Rarity.RARE,
                cost=9000,
                description="Наносит 600 урона всем противникам."
            ),
            Card(
                id="jogo_maximum_meteor",
                name="Максимум: Метеор",
                type=CardType.TECHNIQUE,
                rarity=Rarity.EPIC,
                cost=20000,
                description="Наносит 2000 урона основной цели и 500 урона игрокам слева и справа от нее."
            ),
            Card(
                id="jogo_coffin_of_the_iron_mountain",
                name="Расширение Территории: Гроб Стальной Горы",
                type=CardType.DOMAIN_EXPANSION,
                rarity=Rarity.LEGENDARY,
                cost=35000,
                description="В течение 3 раундов в начале хода каждого противника он получает 800 урона от жара."
            ),
        ]
    ),
    Character(
        id="yuta_okkotsu",
        name="Юта Оккоцу",
        max_hp=6000,
        max_energy=85000,
        passive_ability_name="Копирование и Рика",
        passive_ability_description="Когда противник наносит вам урон картой Техники, копия этой карты добавляется в ваш сброс (стоимость х1.25). Дополнительно, в конце вашего хода Рика наносит 250 урона случайному противнику.",
        unique_cards=[
            Card(
                id="yuta_energy_blade",
                name="Клинок, Усиленный Энергией",
                type=CardType.TECHNIQUE,
                rarity=Rarity.UNCOMMON,
                cost=3000,
                description="Наносит 500 урона одной цели."
            ),
            Card(
                id="yuta_rika_manifestation",
                name="Проявление: Рика",
                type=CardType.TECHNIQUE,
                rarity=Rarity.EPIC,
                cost=25000,
                description='На 3 ваших хода урон от пассивной способности "Рика" увеличивается до 1000 и наносится противникам слева и справа от вас.'
            ),
            Card(
                id="yuta_pure_love",
                name="Чистая Любовь",
                type=CardType.TECHNIQUE,
                rarity=Rarity.LEGENDARY,
                cost=22000,
                description="Наносит 2500 урона одной цели. После использования вы получаете эффект 'Откат Рики' на 2 раунда, который отключает вашу пассивную способность и не позволяет использовать 'Чистую Любовь' и 'Проявление: Рика'."
            ),
            Card(
                id="yuta_true_mutual_love",
                name="Расширение Территории: Истинная и Взаимная Любовь",
                type=CardType.DOMAIN_EXPANSION,
                rarity=Rarity.LEGENDARY,
                cost=45000,
                description="На 3 раунда стоимость всех скопированных карт техник в вашей руке и колоде делится на 4 (округляется вверх). Ваша максимальная рука увеличивается до 8 карт."
            ),
        ]
    ),
]
