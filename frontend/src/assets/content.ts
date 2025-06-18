import type { Character, Card } from '../types';
import gojoPortrait from './portraits/Satoru Gojo portrait.png';
import gojoBlindfoldedPortrait from './portraits/Satoru Gojo blind portrait.png';
import sukunaPortrait from './portraits/Sukuna Portrait.png';
import mahitoPortrait from './portraits/Mahito portrait.png';
import itadoriPortrait from './portraits/Itadori Yuji portrait.png';
import jogoPortrait from './portraits/Jogo portrait.png';
import yutaPortrait from './portraits/Yuta Okkotsu Portrait.png';

// Card Images
// Basic
import attackImg from './cards/basic cards/Attack.jpg';
import shieldImg from './cards/basic cards/Shield.jpg';

// Gojo
import gojoBlueImg from './cards/satoru/Blue.jpg';
import gojoRedImg from './cards/satoru/Reversal Red.jpg';
import gojoPurpleImg from './cards/satoru/Hollow Purple.jpg';
import gojoNoBlindfoldImg from './cards/satoru/no blindfold.jpg';
import gojoDomainImg from './cards/satoru/Unlimited Void Domain Expansion.jpg';

// Sukuna
import sukunaCleaveImg from './cards/sukuna/Cleave.jpg';
import sukunaDismantleImg from './cards/sukuna/Dismantle.jpg';
import sukunaWebImg from './cards/sukuna/Cleave Web.jpg';
import sukunaFuugaImg from './cards/sukuna/Kamino Fuuga.jpg';
import sukunaDomainImg from './cards/sukuna/Malevolent Shrine Domain Expansion.jpg';

// IMPORTANT: ID's must be manually synchronized with backend/app/content.py

export const COMMON_CARDS: Card[] = [
  { id: 'common_strike', name: 'Удар', type: 'ACTION', rarity: 'COMMON', cost: 0, description: 'Наносит 300 урона одной цели.', image: attackImg },
  { id: 'common_shield', name: 'Защита', type: 'ACTION', rarity: 'COMMON', cost: 0, description: 'Вы получаете 300 блока на этот раунд.', image: shieldImg },
  { id: 'common_concentration', name: 'Концентрация', type: 'ACTION', rarity: 'COMMON', cost: 0, description: 'Вы восстанавливаете от 5 до 15% вашего ПЭ.'},
  { id: 'common_simple_domain', name: 'Простая Территория', type: 'TECHNIQUE', rarity: 'RARE', cost: 5000, description: 'Защищает вас от урона вражеской территории на 1 раунд.'},
  { id: 'common_black_flash_check', name: 'Чёрная Вспышка (Проверка)', type: 'ACTION', rarity: 'SPECIAL', cost: 0, description: "Проверка шанса на 'Чёрную Вспышку'. Базовый шанс: 1/6. При успехе вы берёте карту 'Чёрная Вспышка' в руку." },
  { id: 'common_black_flash', name: 'Чёрная Вспышка', type: 'TECHNIQUE', rarity: 'SPECIAL', cost: 20000, description: "Наносит урон, в 2.5 раза превышающий ваш обычный 'Удар'. Этот урон игнорирует блок. Если вы находитесь под эффектом 'Концентрация', ваш следующий 'Удар' будет заменён на 'Чёрную Вспышку' со 100% шансом."},
];

export const ALL_CHARACTERS: Character[] = [
  {
    id: "gojo_satoru",
    name: 'Сатору Годзё',
    max_hp: 5500,
    max_energy: 75000,
    portrait: gojoPortrait,
    portrait_blindfolded: gojoBlindfoldedPortrait,
    passive_ability_name: 'Шесть глаз и Бесконечность',
    passive_ability_description: 'Постоянно: вы видите точное количество ПЭ всех игроков, ваша максимальная рука увеличена до 6 карт. В начале игры вы получаете эффект "Повязка", который можно снять картой "Снять Повязку". После снятия "Повязки" в начале каждого вашего раунда стоимость всех ваших карт снижается на 5% от базовой, эффект накапливается до -90%.',
    unique_cards: [
      {
        id: "gojo_remove_blindfold",
        name: "Снять Повязку",
        type: 'TECHNIQUE',
        rarity: 'LEGENDARY',
        cost: 0,
        description: "Снимает с вас эффект \"Повязка\".\nУсловие: ваше текущее ХП должно быть меньше или равно 33% от максимального.",
        image: gojoNoBlindfoldImg
      },
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
        description: 'Наносит 1000 урона 2-м случайным противникам. Активирует условие для "Фиолетового".',
        image: gojoBlueImg
      },
      {
        id: "gojo_red",
        name: 'Обратная проклятая техника: "Красный"',
        type: 'TECHNIQUE',
        rarity: 'RARE',
        cost: 12000,
        description: 'Наносит 1200 урона основной цели и 600 урона игроку справа от неё. Активирует условие для "Фиолетового".',
        image: gojoRedImg
      },
      {
        id: "gojo_purple",
        name: 'Мнимая техника: "Фиолетовый"',
        type: 'TECHNIQUE',
        rarity: 'EPIC',
        cost: 30000,
        description: 'Наносит 4000 урона одной цели. Этот урон игнорирует блок. \n Условие: ранее в игре должны быть использованы "Синий" и "Красный".',
        image: gojoPurpleImg
      },
      {
        id: "gojo_unlimited_void",
        name: 'Расширение Территории: Необъятная Бездна',
        type: 'DOMAIN_EXPANSION',
        rarity: 'LEGENDARY',
        cost: 50000,
        description: "Все противники получают эффект 'Информационная перегрузка' на 3 раунда (не могут использовать карты Техник, Эпические и Легендарные).",
        image: gojoDomainImg
      },
    ]
  },
  {
    id: "sukuna_ryomen",
    name: 'Рёмен Сукуна',
    max_hp: 7000,
    max_energy: 100000,
    portrait: sukunaPortrait,
    passive_ability_name: 'Жажда Развлечений',
    passive_ability_description: 'Если вам наносит урон противник, чей текущий % ХП больше, чем ваш, вы немедленно восстанавливаете 5% от вашего максимального запаса ПЭ (5000 ПЭ).',
    unique_cards: [
      { id: "sukuna_cleave", name: 'Разрез', type: 'TECHNIQUE', rarity: 'UNCOMMON', cost: 4000, description: 'Наносит 600 урона основной цели и 300 урона игроку слева от неё.', image: sukunaCleaveImg },
      { id: "sukuna_dismantle", name: 'Расщепление', type: 'TECHNIQUE', rarity: 'RARE', cost: 16000, description: 'Наносит 1600 урона одной цели.', image: sukunaDismantleImg },
      { id: 'sukuna_cleave_web', name: 'Расщепление: Паутина', type: 'TECHNIQUE', rarity: 'RARE', cost: 18000, description: 'Наносит 1000 урона основной цели и по 500 урона игрокам слева и справа от неё.', image: sukunaWebImg },
      { id: "sukuna_kamino", name: 'Камино (Пламенная стрела)', type: 'TECHNIQUE', rarity: 'EPIC', cost: 20000, description: "Наносит 1800 урона. Если атака убивает цель, вы восстанавливаете 10 000 ПЭ.\\nСинергия: если активна 'Гробница Зла', наносит 1200 урона всем.", image: sukunaFuugaImg },
      { id: "sukuna_malevolent_shrine", name: 'Расширение Территории: Гробница Зла', type: 'DOMAIN_EXPANSION', rarity: 'LEGENDARY', cost: 40000, description: "Накладывает на всех оппонентов эффект, который в конце их хода наносит им 1500 урона. Длится 3 раунда. Урон игнорируется, если у цели активна 'Простая Территория'.", image: sukunaDomainImg },
    ]
  },
  {
    id: "mahito",
    name: 'Махито',
    max_hp: 4000,
    max_energy: 50000,
    portrait: mahitoPortrait,
    passive_ability_name: 'Праздная Трансфигурация',
    passive_ability_description: "Карта 'Удар' наносит вам 0 урона. Вы начинаете игру с 0 Искажённых Душ. Каждые 2 своих хода вы гарантированно получаете карту 'Касание Души' в руку.",
    unique_cards: [
      { id: "mahito_soul_touch", name: 'Касание Души', type: 'TECHNIQUE', rarity: 'UNCOMMON', cost: 3000, description: 'Наносит по 250 урона игрокам слева и справа от вас (игнорирует блок). За каждого пораженного игрока вы получаете 1 Искажённую Душу.' },
      { id: "mahito_soul_distortion", name: 'Искажение Души', type: 'TECHNIQUE', rarity: 'RARE', cost: 8000, description: 'Цель сбрасывает 1 случайную карту из руки.' },
      { 
        id: "mahito_polymorphic_soul_isomer", 
        name: "Полиморфная Изомерная Душа", 
        type: 'TECHNIQUE', 
        rarity: 'RARE', 
        cost: 0, 
        description: "Стоимость: 1 Искажённая Душа. Дает 500 блока. Игроку, который наносит удар, снимающий этот блок, наносится 500 урона."
      },
      { id: "mahito_body_repel", name: 'Отталкивание Тела', type: 'TECHNIQUE', rarity: 'EPIC', cost: 0, description: 'Стоимость: 3 Искажённые Души. Наносит 1400 урона одной цели. Если у цели есть блок, урон увеличивается на 50%.'},
      { id: "mahito_true_form", name: 'Искажённое Тело Изорённых Убийств', type: 'TECHNIQUE', rarity: 'LEGENDARY', cost: 30000, description: 'Вы получаете постоянный эффект: урон от вражеских "Ударов" по вам снижен на 50%, вы получаете 500 блока в начале раунда, а ваш "Удар" наносит урон в 3 раза больше (900).\nУсловие: вы должны успешно использовать "Чёрную Вспышку".'},
      { id: "mahito_self_embodiment_of_perfection", name: 'Расширение Территории: Самовоплощение Совершенства', type: 'DOMAIN_EXPANSION', rarity: 'LEGENDARY', cost: 35000, description: "На 3 раунда все противники получают эффект 'Искажение души': их блок аннулируется, и в начале их хода они сбрасывают 1 случайную карту. В начале вашего хода вы получаете 1 Искажённую Душу за каждого противника под действием этой территории." },
    ]
  },
  {
    id: "itadori_yuji",
    name: 'Юдзи Итадори',
    max_hp: 7500,
    max_energy: 40000,
    portrait: itadoriPortrait,
    passive_ability_name: 'Сверхчеловеческая Сила',
    passive_ability_description: "Ваши 'Удары' наносят +150 урона. Каждый раз, когда вы играете карту 'Удар', вы восстанавливаете 1000 ПЭ. Ваш базовый шанс 'Чёрной Вспышки' равен 2/6. Когда на вас есть эффект \"Зона\", ваш шанс становится 3/6.",
    unique_cards: [
      { id: "itadori_divergent_fist", name: 'Кулак Дивергента', type: 'TECHNIQUE', rarity: 'UNCOMMON', cost: 2000, description: 'Наносит 400 урона. В начале следующего хода цели наносит ещё 200.' },
      { id: "itadori_manji_kick", name: 'Манджи-Кик', type: 'TECHNIQUE', rarity: 'RARE', cost: 6000, description: 'Наносит 600 урона цели. Следующая атакующая карта (любая, кроме РТ), которую эта цель сыграет против вас, будет отменена.' },
      { id: "itadori_deep_concentration", name: 'Глубокая Концентрация', type: 'TECHNIQUE', rarity: 'EPIC', cost: 18000, description: 'Вы получаете эффект "Концентрация" на 2 хода. Следующая ваша "Чёрная Вспышка", сыгранная пока эффект активен, гарантированно сработает.' },
      { id: "itadori_unwavering_will", name: 'Несгибаемая Воля', type: 'TECHNIQUE', rarity: 'LEGENDARY', cost: 25000, description: 'Получаете эффект "Последний Бой" на 5 ваших ходов. Пока он активен, ваше ХП может опускаться до -3500. Как только эффект заканчивается, вы проигрываете.' },
    ]
  },
  {
    id: "jogo",
    name: 'Дзёго',
    max_hp: 5000,
    max_energy: 65000,
    portrait: jogoPortrait,
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
    portrait: yutaPortrait,
    passive_ability_name: 'Копирование и Рика',
    passive_ability_description: 'Когда противник наносит вам урон картой Техники, копия этой карты добавляется в ваш сброс (стоимость х1.25). Дополнительно, в конце вашего хода Рика наносит 250 урона случайному противнику.',
    unique_cards: [
      { id: "yuta_energy_blade", name: 'Клинок, Усиленный Энергией', type: 'TECHNIQUE', rarity: 'UNCOMMON', cost: 3000, description: 'Наносит 500 урона одной цели.' },
      { id: "yuta_rika_manifestation", name: 'Проявление: Рика', type: 'TECHNIQUE', rarity: 'EPIC', cost: 25000, description: 'На 3 ваших хода урон от пассивной способности "Рика" увеличивается до 1000 и наносится противникам слева и справа от вас.' },
      { id: "yuta_pure_love", name: 'Чистая Любовь', type: 'TECHNIQUE', rarity: 'LEGENDARY', cost: 22000, description: "Наносит 2500 урона одной цели. После использования вы получаете эффект 'Откат Рики' на 2 раунда, который отключает вашу пассивную способность и не позволяет использовать 'Чистую Любовь' и 'Проявление: Рика'." },
      { id: "yuta_true_mutual_love", name: 'Расширение Территории: Истинная и Взаимная Любовь', type: 'DOMAIN_EXPANSION', rarity: 'LEGENDARY', cost: 45000, description: 'На 3 раунда стоимость всех скопированных карт техник в вашей руке и колоде делится на 4 (округляется вверх). Ваша максимальная рука увеличивается до 8 карт.' },
    ]
  },
];

export const ALL_CARDS = ALL_CHARACTERS.reduce((acc, character) => {
  return acc.concat(character.unique_cards);
}, [] as Card[]).concat(COMMON_CARDS); 