from .models import Card, CardType, Rarity, Character

# --- Общие карты ---

common_cards = [
    Card(
        name="Удар",
        type=CardType.ACTION,
        rarity=Rarity.COMMON,
        cost=0,
        description="Наносит 300 урона одной цели."
    ),
    Card(
        name="Защита",
        type=CardType.ACTION,
        rarity=Rarity.COMMON,
        cost=0,
        description="Вы получаете 300 блока на этот раунд."
    ),
    Card(
        name="Концентрация",
        type=CardType.ACTION,
        rarity=Rarity.COMMON,
        cost=0,
        description="Вы восстанавливаете 8000 ПЭ."
    ),
    Card(
        name="Песнопение (Чант)",
        type=CardType.ACTION,
        rarity=Rarity.UNCOMMON,
        cost=1500,
        description="Следующая ваша карта Техники в этом ходу наносит на 50% больше урона или ее эффект усилен на 50%."
    ),
    Card(
        name="Простая Территория",
        type=CardType.TECHNIQUE,
        rarity=Rarity.UNCOMMON,
        cost=15000,
        description="В течение 2 раундов вы получаете иммунитет к эффекту 'верного попадания' вражеских Расширений Территории. Вы также получаете 200 блока в начале вашего хода."
    ),
    Card(
        name="Чувства Опадающего Цветка",
        type=CardType.TECHNIQUE,
        rarity=Rarity.UNCOMMON,
        cost=18000,
        description="В течение 3 раундов, когда вас атакуют картой Техники, вы автоматически наносите атакующему 400 урона."
    ),
    Card(
        name="Обратная Проклятая Техника",
        type=CardType.TECHNIQUE,
        rarity=Rarity.RARE,
        cost=12000,
        description="Вы восстанавливаете 1200 ХП."
    ),
    Card(
        name="Чёрная Вспышка",
        type=CardType.TECHNIQUE,
        rarity=Rarity.RARE,
        cost=6000,
        description="С шансом 1 к 6 вы наносите 3500 урона. В случае неудачи вы наносите 300 урона."
    ),
]

# --- Персонажи и их уникальные карты ---

characters = [
    Character(
        name="Сатору Годзё",
        max_hp=5500,
        max_energy=100000,
        passive_ability_name="Шесть глаз",
        passive_ability_description="Вы всегда видите точное количество ПЭ всех игроков. Ваша максимальная рука увеличена на 1 карту (6 вместо 5).",
        unique_cards=[
            Card(
                name="Техника Бесконечности: Нейтраль",
                type=CardType.TECHNIQUE,
                rarity=Rarity.RARE,
                cost=8000,
                description="В течение 1 раунда все атаки одной цели, нацеленные на вас, автоматически отменяются. AoE-атаки наносят урон как обычно."
            ),
            Card(
                name="Проклятая техника: 'Синий'",
                type=CardType.TECHNIQUE,
                rarity=Rarity.RARE,
                cost=10000,
                description="Наносит 1000 урона 2-м случайным противникам."
            ),
            Card(
                name="Обратная проклятая техника: 'Красный'",
                type=CardType.TECHNIQUE,
                rarity=Rarity.RARE,
                cost=12000,
                description="Наносит 1200 урона основной цели и 600 урона игроку, стоящему справа от основной цели."
            ),
            Card(
                name="Мнимая техника: 'Фиолетовый'",
                type=CardType.TECHNIQUE,
                rarity=Rarity.EPIC,
                cost=35000,
                description="Наносит 2200 урона всем противникам. Этот урон игнорирует блок."
            ),
            Card(
                name="Расширение Территории: Необъятная Бездна",
                type=CardType.DOMAIN_EXPANSION,
                rarity=Rarity.LEGENDARY,
                cost=50000,
                description="Все противники получают эффект 'Информационная перегрузка' на 3 раунда. В этом состоянии они не могут использовать карты Техник, Эпические и Легендарные карты."
            ),
        ]
    ),
    Character(
        name="Рёмен Сукуна",
        max_hp=7000,
        max_energy=60000,
        passive_ability_name="Дурное предзнаменование",
        passive_ability_description="Игроки слева и справа от вас наносят на 15% меньше урона.",
        unique_cards=[
            Card(name="Разрез", type=CardType.TECHNIQUE, rarity=Rarity.UNCOMMON, cost=4000, description="Наносит 600 урона основной цели и 300 урона игроку, стоящему слева от основной цели."),
            Card(name="Расщепление", type=CardType.TECHNIQUE, rarity=Rarity.RARE, cost=16000, description="Наносит 1600 урона одной цели."),
            Card(name="Камино (Пламенная стрела)", type=CardType.TECHNIQUE, rarity=Rarity.EPIC, cost=20000, description="Наносит 1800 урона одной цели. Если эта атака убивает цель, вы восстанавливаете 10 000 ПЭ. Синергия: если активна 'Злобное Святилище', эта техника наносит 1200 урона всем противникам."),
            Card(name="Расширение Территории: Злобное Святилище", type=CardType.DOMAIN_EXPANSION, rarity=Rarity.LEGENDARY, cost=40000, description="В течение 3 раундов в конце вашего хода наносит 1000 урона всем противникам. Этот урон игнорирует блок от карты 'Защита'."),
        ]
    ),
    Character(
        name="Махито",
        max_hp=4000,
        max_energy=45000,
        passive_ability_name="Праздная Трансфигурация",
        passive_ability_description="Карта 'Удар' наносит вам 0 урона.",
        unique_cards=[
            Card(name="Касание Души", type=CardType.TECHNIQUE, rarity=Rarity.UNCOMMON, cost=3000, description="Наносит 250 урона, который игнорирует блок."),
            Card(name="Искажение Души", type=CardType.TECHNIQUE, rarity=Rarity.RARE, cost=8000, description="Выберите 2 случайные карты в руке противника. Он должен их сбросить."),
            Card(name="Полиморфный Душевный Изомер", type=CardType.TECHNIQUE, rarity=Rarity.EPIC, cost=15000, description="В течение 2 раундов в начале хода цели она получает 400 урона, игнорирующего блок."),
            Card(name="Расширение Территории: Самовоплощение Совершенства", type=CardType.DOMAIN_EXPANSION, rarity=Rarity.LEGENDARY, cost=35000, description="На 3 раунда все противники получают эффект 'Искажение души'. Весь их текущий и будущий блок аннулируется. Их максимальный размер руки уменьшается с 5 до 4 карт."),
        ]
    ),
    Character(
        name="Юдзи Итадори",
        max_hp=7500,
        max_energy=35000,
        passive_ability_name="Сверхчеловеческая Сила",
        passive_ability_description="Ваши карты 'Удар' наносят на 150 больше урона. Шанс срабатывания вашей 'Чёрной Вспышки' увеличен до 2 к 6.",
        unique_cards=[
            Card(name="Кулак Дивергента", type=CardType.TECHNIQUE, rarity=Rarity.UNCOMMON, cost=2000, description="Наносит 400 урона. Второй удар Проклятой Энергией наносит дополнительные 200 урона в начале следующего хода цели."),
            Card(name="Заход с разворота", type=CardType.TECHNIQUE, rarity=Rarity.RARE, cost=1000, description="Возьмите из своей колоды карту 'Удар'. Она ничего не стоит в этом ходу."),
            Card(name="Глубокая Концентрация", type=CardType.TECHNIQUE, rarity=Rarity.EPIC, cost=18000, description="Следующая ваша карта 'Чёрная Вспышка' в этой игре гарантированно сработает."),
            Card(name="Несгибаемая Воля", type=CardType.TECHNIQUE, rarity=Rarity.LEGENDARY, cost=25000, description="Вы получаете эффект 'Последний Бой' на 5 ваших ходов. Пока он активен, ваше ХП может опускаться до -3500, и вы продолжаете сражаться. Как только эффект заканчивается, вы проигрываете."),
        ]
    ),
    Character(
        name="Дзёго",
        max_hp=5000,
        max_energy=55000,
        passive_ability_name="Прикосновение Лавы",
        passive_ability_description="Каждый раз, когда вы наносите урон противнику картой Техники, он получает эффект 'Горение' на 2 раунда (наносит 100 урона в начале его хода).",
        unique_cards=[
            Card(name="Сикигами: Угольки", type=CardType.TECHNIQUE, rarity=Rarity.UNCOMMON, cost=4000, description="Выберите до 3-х целей. Каждая получает 300 урона."),
            Card(name="Извержение Вулкана", type=CardType.TECHNIQUE, rarity=Rarity.RARE, cost=9000, description="Наносит 600 урона всем противникам."),
            Card(name="Максимум: Метеор", type=CardType.TECHNIQUE, rarity=Rarity.EPIC, cost=20000, description="Наносит 2000 урона основной цели и 500 урона игрокам слева и справа от нее."),
            Card(name="Расширение Территории: Гроб Стальной Горы", type=CardType.DOMAIN_EXPANSION, rarity=Rarity.LEGENDARY, cost=35000, description="В течение 3 раундов в начале хода каждого противника он получает 800 урона от жара."),
        ]
    ),
    Character(
        name="Юта Оккоцу",
        max_hp=6000,
        max_energy=80000,
        passive_ability_name="Копирование и Рика",
        passive_ability_description="Когда противник наносит вам урон картой Техники, копия этой карты добавляется в ваш сброс. Вы можете вытянуть её в следующих раундах. Стоимость скопированных техник увеличена на 4000 ПЭ. Дополнительно, в конце вашего хода Рика наносит 250 урона случайному противнику.",
        unique_cards=[
            Card(name="Клинок, Усиленный Энергией", type=CardType.TECHNIQUE, rarity=Rarity.UNCOMMON, cost=3000, description="Наносит 500 урона одной цели."),
            Card(name="Полное Проявление: Рика", type=CardType.TECHNIQUE, rarity=Rarity.EPIC, cost=25000, description="На 3 ваших хода урон от пассивной способности 'Рика' увеличивается с 250 до 1000 и наносится всем противникам."),
            Card(name="Расширение Территории: Истинная и Взаимная Любовь", type=CardType.DOMAIN_EXPANSION, rarity=Rarity.LEGENDARY, cost=45000, description="На 3 раунда стоимость всех скопированных карт техник в вашей руке и колоде делится на 3 (округляется до ближайшей сотни)."),
        ]
    ),
]
