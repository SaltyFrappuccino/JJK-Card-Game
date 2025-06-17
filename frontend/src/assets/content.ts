import type { Character } from '../types';

// IMPORTANT: ID's must be manually synchronized with backend/app/content.py

export const ALL_CHARACTERS: Character[] = [
  {
    id: "gojo_satoru",
    name: 'Сатору Годзё',
    max_hp: 5500,
    max_energy: 75000,
    passive_ability_name: 'Шесть глаз и Бесконечность',
    passive_ability_description: 'Вы всегда видите точное количество ПЭ всех игроков. Ваша максимальная рука увеличена до 6 карт. Кроме того, в начале игры стоимость всех ваших карт составляет 90% от базовой. Каждый новый раунд этот множитель уменьшается на 5% (Раунд 2: 85%, Раунд 3: 80%...), вплоть до минимального значения в 10%.',
    unique_cards: [
      {
        id: "gojo_strengthened_strike",
        name: 'Усиленный Удар',
        type: 'ACTION',
        rarity: 'UNCOMMON',
        cost: 0,
        description: 'Наносит 300 урона. Этот урон игнорирует блок.'
      },
      {
        id: "gojo_infinity",
        name: 'Бесконечность',
        type: 'TECHNIQUE',
        rarity: 'RARE',
        cost: 8000,
        description: 'В течение 1 раунда все атаки одной цели, нацеленные на вас, автоматически отменяются. AoE-атаки наносят урон как обычно.'
      },
      {
        id: "gojo_blue",
        name: 'Проклятая техника: "Синий"',
        type: 'TECHNIQUE',
        rarity: 'RARE',
        cost: 10000,
        description: 'Наносит 1000 урона 2-м случайным противникам. Активирует условие для "Фиолетового".'
      },
      {
        id: "gojo_red",
        name: 'Обратная проклятая техника: "Красный"',
        type: 'TECHNIQUE',
        rarity: 'RARE',
        cost: 12000,
        description: 'Наносит 1200 урона основной цели и 600 урона игроку справа от неё. Активирует условие для "Фиолетового".'
      },
      {
        id: "gojo_purple",
        name: 'Мнимая техника: "Фиолетовый"',
        type: 'TECHNIQUE',
        rarity: 'EPIC',
        cost: 30000,
        description: 'Наносит 4000 урона одной цели. Этот урон игнорирует блок. \n Условие: ранее в игре должны быть использованы "Синий" и "Красный".'
      },
      {
        id: "gojo_unlimited_void",
        name: 'Расширение Территории: Необъятная Бездна',
        type: 'DOMAIN_EXPANSION',
        rarity: 'LEGENDARY',
        cost: 50000,
        description: "Все противники получают эффект 'Информационная перегрузка' на 3 раунда (не могут использовать карты Техник, Эпические и Легендарные)."
      },
    ]
  },
  {
    id: "sukuna_ryomen",
    name: 'Рёмен Сукуна',
    max_hp: 7000,
    max_energy: 100000,
    passive_ability_name: 'Жажда Развлечений',
    passive_ability_description: 'Если вам наносит урон противник, чей текущий % ХП больше, чем ваш, вы немедленно восстанавливаете 5% от вашего максимального запаса ПЭ (5000 ПЭ).',
    unique_cards: [
      { id: "sukuna_cleave", name: 'Разрез', type: 'TECHNIQUE', rarity: 'UNCOMMON', cost: 4000, description: 'Наносит 600 урона основной цели и 300 урона игроку слева от неё.' },
      { id: "sukuna_dismantle", name: 'Расщепление', type: 'TECHNIQUE', rarity: 'RARE', cost: 16000, description: 'Наносит 1600 урона одной цели.' },
      { id: "sukuna_spiderweb", name: 'Расщепление: Паутина', type: 'TECHNIQUE', rarity: 'RARE', cost: 18000, description: 'Наносит 1000 урона основной цели и по 500 урона игрокам слева и справа от неё.'},
      { id: "sukuna_kamino", name: 'Камино (Пламенная стрела)', type: 'TECHNIQUE', rarity: 'EPIC', cost: 20000, description: "Наносит 1800 урона. Если атака убивает цель, вы восстанавливаете 10 000 ПЭ.\nСинергия: если активна 'Гробница Зла', наносит 1200 урона всем." },
      { id: "sukuna_malevolent_shrine", name: 'Расширение Территории: Гробница Зла', type: 'DOMAIN_EXPANSION', rarity: 'LEGENDARY', cost: 40000, description: "3 раунда в конце вашего хода наносит 1500 урона всем противникам (игнорирует блок от карты 'Защита')." },
    ]
  },
  {
    id: "mahito",
    name: 'Махито',
    max_hp: 4000,
    max_energy: 50000,
    passive_ability_name: 'Праздная Трансфигурация',
    passive_ability_description: "Карта 'Удар' наносит вам 0 урона.",
    unique_cards: [
      { id: "mahito_soul_touch", name: 'Касание Души', type: 'TECHNIQUE', rarity: 'UNCOMMON', cost: 3000, description: 'Наносит 250 урона, который игнорирует блок.' },
      { id: "mahito_soul_distortion", name: 'Искажение Души', type: 'TECHNIQUE', rarity: 'RARE', cost: 8000, description: 'Цель сбрасывает 2 случайные карты из руки.' },
      { id: "mahito_body_repel", name: 'Отталкивание Тела', type: 'TECHNIQUE', rarity: 'EPIC', cost: 14000, description: 'Наносит 1400 урона одной цели. Если у цели есть блок, урон увеличивается на 50%.'},
      { id: "mahito_true_form", name: 'Искажённое Тело Изорённых Убийств', type: 'TECHNIQUE', rarity: 'LEGENDARY', cost: 30000, description: 'Вы получаете постоянный эффект: урон от вражеских "Ударов" по вам снижен на 50%, вы получаете 500 блока в начале раунда, а ваш "Удар" наносит урон в 3 раза больше (900).\nУсловие: вы должны атаковать 5 раз картами, игнорирующими блок.'},
      { id: "mahito_self_embodiment_of_perfection", name: 'Расширение Территории: Самовоплощение Совершенства', type: 'DOMAIN_EXPANSION', rarity: 'LEGENDARY', cost: 35000, description: "На 3 раунда все противники получают эффект 'Искажение души': их блок аннулируется, и в начале их хода они сбрасывают 1 случайную карту." },
    ]
  },
  {
    id: "itadori_yuji",
    name: 'Юдзи Итадори',
    max_hp: 7500,
    max_energy: 40000,
    passive_ability_name: 'Сверхчеловеческая Сила',
    passive_ability_description: "Ваши 'Удары' наносят +150 урона. Каждый раз, когда вы играете карту 'Удар', вы восстанавливаете 1000 ПЭ. Шанс 'Чёрной Вспышки' увеличен до 2/6.",
    unique_cards: [
      { id: "itadori_divergent_fist", name: 'Кулак Дивергента', type: 'TECHNIQUE', rarity: 'UNCOMMON', cost: 2000, description: 'Наносит 400 урона. В начале следующего хода цели наносит ещё 200.' },
      { id: "itadori_slaughter_demon", name: 'Заход с разворота', type: 'TECHNIQUE', rarity: 'UNCOMMON', cost: 1000, description: 'Возьмите из своей колоды 2 карты "Удар".' },
      { id: "itadori_deep_concentration", name: 'Глубокая Концентрация', type: 'TECHNIQUE', rarity: 'EPIC', cost: 18000, description: 'Вы получаете эффект "Концентрация" на 2 хода. Следующая ваша "Чёрная Вспышка", сыгранная пока эффект активен, гарантированно сработает.' },
      { id: "itadori_unwavering_will", name: 'Несгибаемая Воля', type: 'TECHNIQUE', rarity: 'LEGENDARY', cost: 25000, description: 'Получаете эффект "Последний Бой" на 5 ваших ходов. Пока он активен, ваше ХП может опускаться до -3500. Как только эффект заканчивается, вы проигрываете.' },
    ]
  },
  {
    id: "jogo",
    name: 'Дзёго',
    max_hp: 5000,
    max_energy: 65000,
    passive_ability_name: 'Прикосновение Лавы',
    passive_ability_description: "Каждый раз, когда вы наносите урон картой Техники, цель получает эффект 'Горение' на 2 раунда (100 урона в начале её хода).",
    unique_cards: [
      { id: "jogo_ember_insects", name: 'Сикигами: Угольки', type: 'TECHNIQUE', rarity: 'UNCOMMON', cost: 4000, description: 'Атакует до 3 целей, нанося каждой по 300 урона.' },
      { id: "jogo_volcano_eruption", name: 'Извержение Вулкана', type: 'TECHNIQUE', rarity: 'RARE', cost: 9000, description: 'Наносит 600 урона всем противникам.' },
      { id: "jogo_maximum_meteor", name: 'Максимум: Метеор', type: 'TECHNIQUE', rarity: 'EPIC', cost: 20000, description: 'Наносит 2000 урона основной цели и 500 урона игрокам слева и справа от нее.' },
      { id: "jogo_coffin_of_the_iron_mountain", name: 'Расширение Территории: Гроб Стальной Горы', type: 'DOMAIN_EXPANSION', rarity: 'LEGENDARY', cost: 35000, description: 'В течение 3 раундов в начале хода каждого противника он получает 800 урона от жара.' },
    ]
  },
  {
    id: "yuta_okkotsu",
    name: 'Юта Оккоцу',
    max_hp: 6000,
    max_energy: 85000,
    passive_ability_name: 'Копирование и Рика',
    passive_ability_description: 'Когда противник наносит вам урон картой Техники, копия этой карты добавляется в ваш сброс (стоимость х1.25). Дополнительно, в конце вашего хода Рика наносит 250 урона случайному противнику.',
    unique_cards: [
      { id: "yuta_energy_blade", name: 'Клинок, Усиленный Энергией', type: 'TECHNIQUE', rarity: 'UNCOMMON', cost: 3000, description: 'Наносит 500 урона одной цели.' },
      { id: "yuta_rika_manifestation", name: 'Проявление: Рика', type: 'TECHNIQUE', rarity: 'EPIC', cost: 25000, description: 'На 3 ваших хода урон от пассивной способности "Рика" увеличивается до 1000 и наносится противникам слева и справа от вас.' },
      { id: "yuta_true_mutual_love", name: 'Расширение Территории: Истинная и Взаимная Любовь', type: 'DOMAIN_EXPANSION', rarity: 'LEGENDARY', cost: 45000, description: 'На 3 раунда стоимость всех скопированных карт техник в вашей руке и колоде делится на 4 (округляется вверх). Ваша максимальная рука увеличивается до 8 карт.' },
    ]
  },
]; 