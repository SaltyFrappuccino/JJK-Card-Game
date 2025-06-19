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
import chantsImg from './cards/basic cards/Chants.jpg';
import concentrationImg from './cards/basic cards/concentration.webp';
import simpleDomainImg from './cards/basic cards/Simple Domain.jpg';
import blackFlashImg from './cards/basic cards/black flash.jpg';
import fallingBlossomImg from './cards/basic cards/Falling Blossom Emotion.jpg';
import reversedTechniqueImg from './cards/basic cards/Reversed Cursed Technique.jpg';

// Gojo
import gojoBlueImg from './cards/satoru/Blue.jpg';
import gojoRedImg from './cards/satoru/Reversal Red.jpg';
import gojoPurpleImg from './cards/satoru/Hollow Purple.jpg';
import gojoNoBlindfoldImg from './cards/satoru/no blindfold.jpg';
import gojoDomainImg from './cards/satoru/Unlimited Void Domain Expansion.jpg';
import infinityImg from './cards/satoru/Infinity.jpg';
import bluePunchImg from './cards/satoru/blue punch.jpg';

// Sukuna
import sukunaCleaveImg from './cards/sukuna/Cleave.jpg';
import sukunaDismantleImg from './cards/sukuna/Dismantle.jpg';
import sukunaWebImg from './cards/sukuna/Cleave Web.jpg';
import sukunaFuugaImg from './cards/sukuna/Kamino Fuuga.jpg';
import sukunaDomainImg from './cards/sukuna/Malevolent Shrine Domain Expansion.jpg';

// Mahito
import mahitoSoulTouchImg from './cards/mahito/Idle_Transfiguration.webp';
import mahitoSoulDistortionImg from './cards/mahito/Soul Deformation.webp';
import mahitoSoulIsomerImg from './cards/mahito/Polymorphic_Soul_Isomer.webp';
import mahitoBodyRepelImg from './cards/mahito/Body Repel.webp';
import mahitoTrueFormImg from './cards/mahito/Mahito_achieves_his_true_form.webp';
import mahitoDomainImg from './cards/mahito/Mahitos_Self-Embodiment_of_Perfection.webp';

// Jogo
import jogoEmberInsectsImg from './cards/jogo/Jogo_using_Ember_Insects.webp';
import jogoVolcanoEruptionImg from './cards/jogo/Jogo_using_flames.webp';
import jogoMaximumMeteorImg from './cards/jogo/Maximum_Meteor_crashing_into_Shibuya_29.webp';
import jogoDomainImg from './cards/jogo/Jogos_Coffin_of_the_Iron_Mountain.webp';

// Itadori
import itadoriDivergentFistImg from './cards/itadori/Divergent_Fist.webp';
import itadoriManjiKickImg from './cards/itadori/Manji kick.jpg';
import itadoriDeepConcentrationImg from './cards/itadori/Deep Concentration.webp';
import itadoriUnwaveringWillImg from './cards/itadori/Unbreakable Will.webp';

// Yuta
import yutaEnergyBladeImg from './cards/yuta/Yuta_Okkotsu_Better_Katana.webp';
import yutaRikaManifestationImg from './cards/yuta/Rika_Full_Manifestation.webp';
import yutaPureLoveImg from './cards/yuta/Pure_Love.webp';
import yutaDomainImg from './cards/yuta/Authentic_Mutual_Love.webp';

// Character accent colors for card highlighting
export const CHARACTER_ACCENT_COLORS = {
  'gojo_satoru': '#FFFFFF',        // Белый
  'sukuna_ryomen': '#DC143C',      // Алый
  'jogo': '#FF8C00',               // Оранжевый  
  'mahito': '#708090',             // Серо-голубой
  'yuta_okkotsu': '#FF69B4',      // Розовый
  'itadori_yuji': '#CD853F'       // Оттенок рыжего
} as const;

// IMPORTANT: ID's must be manually synchronized with backend/app/content.py

export const COMMON_CARDS: Card[] = [
  { id: 'common_strike', name: 'Удар', type: 'ACTION', rarity: 'COMMON', cost: 0, description: 'Наносит 300 урона одной цели.', image: attackImg },
  { id: 'common_defense', name: 'Защита', type: 'ACTION', rarity: 'COMMON', cost: 0, description: 'Вы получаете 300 блока на этот раунд.', image: shieldImg },
  { id: 'common_chant', name: 'Песнопения', type: 'ACTION', rarity: 'UNCOMMON', cost: 2000, description: 'Следующая ваша карта Техники в этом ходу будет стоить на 30% меньше.', image: chantsImg },
  { id: 'common_concentration', name: 'Концентрация', type: 'ACTION', rarity: 'COMMON', cost: 0, description: 'Вы восстанавливаете от 5 до 15% вашего ПЭ.', image: concentrationImg },
  { id: 'common_simple_domain', name: 'Простая Территория', type: 'TECHNIQUE', rarity: 'RARE', cost: 5000, description: 'Защищает вас от урона вражеской территории на 1 раунд.', image: simpleDomainImg },
  { id: 'common_black_flash_check', name: 'Чёрная Вспышка (Проверка)', type: 'ACTION', rarity: 'SPECIAL', cost: 0, description: "Проверка шанса на 'Чёрную Вспышку'. Базовый шанс: 1/6. При успехе вы берёте карту 'Чёрная Вспышка' в руку." },
  { id: 'common_black_flash', name: 'Чёрная Вспышка', type: 'TECHNIQUE', rarity: 'SPECIAL', cost: 20000, description: "Наносит урон, в 2.5 раза превышающий ваш обычный 'Удар'. Этот урон игнорирует блок. Если вы находитесь под эффектом 'Концентрация', ваш следующий 'Удар' будет заменён на 'Чёрную Вспышку' со 100% шансом.", image: blackFlashImg},
  { id: 'common_reverse_cursed_technique', name: 'Обратная проклятая техника', type: 'TECHNIQUE', rarity: 'EPIC', cost: 15000, description: 'Восстанавливает 25% от вашего максимального здоровья.', image: reversedTechniqueImg },
  { id: 'common_falling_blossom_emotion', name: 'Эмоция Падающего Цветка', type: 'TECHNIQUE', rarity: 'EPIC', cost: 10000, description: 'Автоматически защищает вас от атаки Расширения Территории, отменяя её эффект.', image: fallingBlossomImg },
];

export const ALL_CHARACTERS: Character[] = [
  {
    id: "gojo_satoru",
    name: 'Сатору Годзё',
    max_hp: 5500,
    max_energy: 75000,
    accent_color: CHARACTER_ACCENT_COLORS.gojo_satoru,
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
        description: 'Наносит 300 урона. Этот урон игнорирует блок.',
        image: bluePunchImg
      },
      {
        id: "gojo_infinity",
        name: 'Бесконечность',
        type: 'TECHNIQUE',
        rarity: 'RARE',
        cost: 8000,
        description: 'В течение 1 раунда все атаки одной цели, нацеленные на вас, автоматически отменяются. AoE-атаки наносят урон как обычно.',
        image: infinityImg
      },
      {
        id: "gojo_blue",
        name: 'Проклятая техника: "Синий"',
        type: 'TECHNIQUE',
        rarity: 'RARE',
        cost: 10000,
        description: 'Вы делаете два выбора цели: если выбраны два разных противника, каждый получает 500 урона и они меняются местами; если дважды выбран один противник, он получает 1000 урона. Активирует условие для "Фиолетового".',
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
        id: "gojo_blue_maximum",
        name: 'Максимальный Выброс: Синий',
        type: 'TECHNIQUE',
        rarity: 'EPIC',
        cost: 28000,
        description: 'Наносит 500 урона ВСЕМ противникам на поле. После этого позиции всех живых игроков случайно меняются местами.',
        image: gojoBlueImg
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
    accent_color: CHARACTER_ACCENT_COLORS.sukuna_ryomen,
    portrait: sukunaPortrait,
    passive_ability_name: 'Жажда Развлечений',
    passive_ability_description: 'Если вам наносит урон противник, чей текущий % ХП больше, чем ваш, вы немедленно восстанавливаете 5% от вашего максимального запаса ПЭ (5000 ПЭ).',
    unique_cards: [
      { id: "sukuna_cleave", name: 'Расщепление', type: 'TECHNIQUE', rarity: 'RARE', cost: 16000, description: 'Наносит 1600 урона одной цели.', image: sukunaCleaveImg },
      { id: "sukuna_dismantle", name: 'Рассечение', type: 'TECHNIQUE', rarity: 'UNCOMMON', cost: 4000, description: 'Наносит 600 урона основной цели и 300 урона игроку слева от неё.', image: sukunaDismantleImg },
      { id: 'sukuna_spiderweb', name: 'Расщепление: Паутина', type: 'TECHNIQUE', rarity: 'RARE', cost: 18000, description: 'Наносит 1000 урона основной цели и по 500 урона игрокам слева и справа от неё.', image: sukunaWebImg },
      { id: "sukuna_kamino", name: 'Камино (Пламенная стрела)', type: 'TECHNIQUE', rarity: 'EPIC', cost: 20000, description: "Наносит 1800 урона. Если атака убивает цель, вы восстанавливаете 10 000 ПЭ.\\nСинергия: если активна 'Гробница Зла', наносит 1200 урона всем.", image: sukunaFuugaImg },
      { id: "sukuna_malevolent_shrine", name: 'Расширение Территории: Гробница Зла', type: 'DOMAIN_EXPANSION', rarity: 'LEGENDARY', cost: 40000, description: "Накладывает на всех оппонентов эффект, который в конце их хода наносит им 1500 урона. Длится 3 раунда. Урон игнорируется, если у цели активна 'Простая Территория'.", image: sukunaDomainImg },
    ]
  },
  {
    id: "mahito",
    name: 'Махито',
    max_hp: 4000,
    max_energy: 50000,
    accent_color: CHARACTER_ACCENT_COLORS.mahito,
    portrait: mahitoPortrait,
    passive_ability_name: 'Праздная Трансфигурация',
    passive_ability_description: "Карта 'Удар' наносит вам 0 урона. Вы начинаете игру с 0 Искажённых Душ. Каждые 2 своих хода вы гарантированно получаете карту 'Касание Души' в руку. Карты Трансформации можно применять как на себя, так и на любого другого игрока.",
    unique_cards: [
      { id: "mahito_soul_touch", name: 'Касание Души', type: 'TECHNIQUE', rarity: 'UNCOMMON', cost: 3000, description: 'Наносит по 250 урона игрокам слева и справа от вас (игнорирует блок). За каждого пораженного игрока вы получаете 1 Искажённую Душу.', image: mahitoSoulTouchImg },
      { id: "mahito_transformation_nimble_legs", name: 'Трансформация: Ловкие Ноги', type: 'TECHNIQUE', rarity: 'RARE', cost: 0, description: 'Стоимость: 1 Искажённая Душа.\nЦель: Вы или другой игрок.\nЦель получает эффект "Ловкие Ноги" на 2 раунда.\n\nЭффект "Ловкие Ноги": Шанс 25% полностью уклониться от любой атаки по одной цели (не работает против AoE и урона от РТ).', image: mahitoSoulDistortionImg },
      { id: "mahito_transformation_big_hands", name: 'Трансформация: Большие Руки', type: 'TECHNIQUE', rarity: 'RARE', cost: 0, description: 'Стоимость: 1 Искажённая Душа.\nЦель: Вы или другой игрок.\nЦель получает эффект "Большие Руки" на 2 раунда.\n\nЭффект "Большие Руки": Максимальный размер руки цели увеличивается на 1.', image: mahitoBodyRepelImg },
      { id: "mahito_transformation_long_arms", name: 'Трансформация: Длинные Руки', type: 'TECHNIQUE', rarity: 'EPIC', cost: 0, description: 'Стоимость: 2 Искажённые Души.\nЦель: Вы или другой игрок.\nЦель получает эффект "Длинные Руки" на 2 раунда.\n\nЭффект "Длинные Руки": Каждый раз, когда другой игрок разыгрывает на вас карту, есть шанс 25% получить копию этой карты себе в руку (стоимость копии х1.5).', image: mahitoTrueFormImg },
      { id: "mahito_soul_distortion", name: 'Искажение Души', type: 'TECHNIQUE', rarity: 'RARE', cost: 8000, description: 'Цель: Один противник.\nЦель немедленно сбрасывает 1 случайную карту из руки.', image: mahitoSoulDistortionImg },
      { id: "mahito_hand_distortion", name: 'Искажение Рук', type: 'TECHNIQUE', rarity: 'RARE', cost: 0, description: 'Стоимость: 1 Искажённая Душа.\nЦель: Один противник.\nЦель получает эффект "Искажение Рук" на 2 раунда.\n\nЭффект "Искажение Рук": Максимальный размер руки цели уменьшен на 1. В начале своего хода цель, если у нее карт больше нового лимита, должна сбросить лишние.', image: mahitoSoulIsomerImg },
      { id: "mahito_distortion_crosseyes", name: 'Искажение: Косоглазие', type: 'TECHNIQUE', rarity: 'EPIC', cost: 0, description: 'Стоимость: 2 Искажённые Души.\nЦель: Один противник.\nВы получаете на себя эффект "Косоглазие" на 2 раунда, привязанный к этой цели.\n\nЭффект "Косоглазие": Каждый раз, когда вас атакуют, есть шанс 25%, что атака будет перенаправлена на цель, на которую вы наложили этот эффект.', image: mahitoTrueFormImg },
      { 
        id: "mahito_polymorphic_soul_isomer", 
        name: "Полиморфная Изомерная Душа", 
        type: 'TECHNIQUE', 
        rarity: 'RARE', 
        cost: 0, 
        description: "Стоимость: 1 Искажённая Душа. Дает 500 блока. Игроку, который наносит удар, снимающий этот блок, наносится 500 урона.",
        image: mahitoSoulIsomerImg
      },
      { id: "mahito_body_repel", name: 'Отталкивание Тела', type: 'TECHNIQUE', rarity: 'EPIC', cost: 0, description: 'Стоимость: 3 Искажённые Души. Наносит 1400 урона одной цели. Если у цели есть блок, урон увеличивается на 50%.', image: mahitoBodyRepelImg },
      { id: "mahito_true_form", name: 'Искажённое Тело Изорённых Убийств', type: 'TECHNIQUE', rarity: 'LEGENDARY', cost: 30000, description: 'Вы получаете постоянный эффект: урон от вражеских "Ударов" по вам снижен на 50%, вы получаете 500 блока в начале раунда, а ваш "Удар" наносит урон в 3 раза больше (900).\nУсловие: вы должны успешно использовать "Чёрную Вспышку".', image: mahitoTrueFormImg },
      { id: "mahito_self_embodiment_of_perfection", name: 'Расширение Территории: Самовоплощение Совершенства', type: 'DOMAIN_EXPANSION', rarity: 'LEGENDARY', cost: 35000, description: "На 3 раунда все противники получают эффект 'Искажение души': их блок аннулируется и на них накладывается эффект 'Искажение Рук'. В начале вашего хода вы получаете 1 Искажённую Душу за каждого противника под действием этой территории.", image: mahitoDomainImg },
    ]
  },
  {
    id: "itadori_yuji",
    name: 'Юдзи Итадори',
    max_hp: 7500,
    max_energy: 40000,
    accent_color: CHARACTER_ACCENT_COLORS.itadori_yuji,
    portrait: itadoriPortrait,
    passive_ability_name: 'Сверхчеловеческая Сила',
    passive_ability_description: "Ваши 'Удары' наносят +150 урона. Каждый раз, когда вы играете карту 'Удар', вы восстанавливаете 1000 ПЭ. Ваш базовый шанс 'Чёрной Вспышки' равен 2/6. Когда на вас есть эффект \"Зона\", ваш шанс становится 3/6.",
    unique_cards: [
      { id: "itadori_divergent_fist", name: 'Кулак Дивергента', type: 'TECHNIQUE', rarity: 'UNCOMMON', cost: 2000, description: 'Наносит 400 урона. В начале следующего хода цели наносит ещё 200.', image: itadoriDivergentFistImg },
      { id: "itadori_manji_kick", name: 'Манджи-Кик', type: 'TECHNIQUE', rarity: 'RARE', cost: 6000, description: 'Наносит 600 урона цели. Следующая атакующая карта (любая, кроме РТ), которую эта цель сыграет против вас, будет отменена.', image: itadoriManjiKickImg },
      { id: "itadori_deep_concentration", name: 'Глубокая Концентрация', type: 'TECHNIQUE', rarity: 'EPIC', cost: 18000, description: 'Вы получаете эффект "Концентрация" на 2 хода. Следующая ваша "Чёрная Вспышка", сыгранная пока эффект активен, гарантированно сработает.', image: itadoriDeepConcentrationImg },
      { id: "itadori_unwavering_will", name: 'Несгибаемая Воля', type: 'TECHNIQUE', rarity: 'LEGENDARY', cost: 25000, description: 'Получаете эффект "Последний Бой" на 5 ваших ходов. Пока он активен, ваше ХП может опускаться до -3500. Как только эффект заканчивается, вы проигрываете.', image: itadoriUnwaveringWillImg },
      { id: "itadori_let_him_out", name: 'Позволить Ему Выйти', type: 'TECHNIQUE', rarity: 'LEGENDARY', cost: 15000, description: 'Вы немедленно восстанавливаете 30% от вашего максимального ХП. Сразу после этого от вашего имени разыгрываются Расщепления (количество = половина от общего числа игроков, минимум 1) и от 1 до N Рассечений (где N = общее количество игроков) по случайным противникам. После завершения всех атак вы получаете эффект "Подавление Воли" на 2 раунда.\nУсловие: можно разыграть, только если ваше текущее ХП ниже 40% от максимального.', image: itadoriUnwaveringWillImg },
    ]
  },
  {
    id: "jogo",
    name: 'Дзёго',
    max_hp: 5000,
    max_energy: 65000,
    accent_color: CHARACTER_ACCENT_COLORS.jogo,
    portrait: jogoPortrait,
    passive_ability_name: 'Эскалация Жара',
    passive_ability_description: "Каждый раз, когда вы наносите урон картой Техники, вы накладываете на цель или улучшаете огненный дебафф: если на цели нет огненного дебаффа, она получает \"Тление\" (Уровень 1) на 3 раунда. Если на цели уже есть огненный дебафф, он улучшается до следующего уровня.",
    unique_cards: [
      { id: "jogo_lava_touch", name: 'Прикосновение Лавы', type: 'TECHNIQUE', rarity: 'UNCOMMON', cost: 5000, description: 'Наносит 400 урона игрокам слева и справа от вас. Накладывает на них "Горение" (Уровень 2) или улучшает существующий огненный дебафф до следующего уровня.', image: jogoVolcanoEruptionImg },
      { id: "jogo_ember_insects", name: 'Сикигами: Угольки', type: 'TECHNIQUE', rarity: 'UNCOMMON', cost: 4000, description: 'Атакует до 3 целей. Наносит каждой цели 200 урона и накладывает на них "Тление" (Уровень 1) или улучшает существующий огненный дебафф до следующего уровня.', image: jogoEmberInsectsImg },
      { id: "jogo_volcano_eruption", name: 'Извержение Вулкана', type: 'TECHNIQUE', rarity: 'RARE', cost: 9000, description: 'Наносит 600 урона всем противникам. (Эта карта активирует пассивку стандартным образом, накладывая "Тление" или улучшая существующий дебафф).', image: jogoVolcanoEruptionImg },
      { id: "jogo_maximum_meteor", name: 'Максимум: Метеор', type: 'TECHNIQUE', rarity: 'EPIC', cost: 20000, description: 'Наносит 2000 урона основной цели и 500 урона игрокам слева и справа от нее. Накладывает на основную цель "Пекло" (Уровень 3) или улучшает существующий огненный дебафф до следующего уровня.', image: jogoMaximumMeteorImg },
      { id: "jogo_coffin_of_the_iron_mountain", name: 'Расширение Территории: Гроб Стальной Горы', type: 'DOMAIN_EXPANSION', rarity: 'LEGENDARY', cost: 35000, description: 'В течение 3 раундов в начале хода каждого противника он получает 800 урона от жара. Дополнительно: пока активна эта территория, все ваши огненные дебаффы наносят на 50% больше урона.', image: jogoDomainImg },
    ]
  },
  {
    id: "yuta_okkotsu",
    name: 'Юта Оккоцу',
    max_hp: 6000,
    max_energy: 85000,
    accent_color: CHARACTER_ACCENT_COLORS.yuta_okkotsu,
    portrait: yutaPortrait,
    passive_ability_name: 'Копирование и Рика',
    passive_ability_description: 'Когда противник наносит вам урон картой Техники, копия этой карты добавляется в ваш сброс (стоимость х1.25). Дополнительно, в конце вашего хода Рика наносит 250 урона случайному противнику.',
    unique_cards: [
      { id: "yuta_energy_blade", name: 'Клинок, Усиленный Энергией', type: 'TECHNIQUE', rarity: 'UNCOMMON', cost: 3000, description: 'Наносит 500 урона одной цели.', image: yutaEnergyBladeImg },
      { id: "yuta_rika_manifestation", name: 'Проявление: Рика', type: 'TECHNIQUE', rarity: 'EPIC', cost: 25000, description: 'На 3 ваших хода урон от пассивной способности "Рика" увеличивается до 1000 и наносится противникам слева и справа от вас.', image: yutaRikaManifestationImg },
      { id: "yuta_pure_love", name: 'Чистая Любовь', type: 'TECHNIQUE', rarity: 'LEGENDARY', cost: 22000, description: "Наносит 2500 урона одной цели. После использования вы получаете эффект 'Откат Рики' на 2 раунда, который отключает вашу пассивную способность и не позволяет использовать 'Чистую Любовь' и 'Проявление: Рика'.", image: yutaPureLoveImg },
      { id: "yuta_true_mutual_love", name: 'Расширение Территории: Истинная и Взаимная Любовь', type: 'DOMAIN_EXPANSION', rarity: 'LEGENDARY', cost: 45000, description: 'На 3 раунда стоимость всех скопированных карт техник в вашей руке и колоде делится на 4 (округляется вверх). Ваша максимальная рука увеличивается до 8 карт.', image: yutaDomainImg },
    ]
  },
];

export const ALL_CARDS = ALL_CHARACTERS.reduce((acc, character) => {
  return acc.concat(character.unique_cards);
}, [] as Card[]).concat(COMMON_CARDS); 