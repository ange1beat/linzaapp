/**
 * Каталог сегментов, типов контента, платформ и источников для мастера настройки организации.
 */

export const WIZARD_SEGMENTS = [
  { id: 'tv', ico: '📺', n: 'Телеканал', d: 'Эфирное вещание, архивы, предэфирная и постэфирная проверка' },
  { id: 'production', ico: '🎬', n: 'Продакшн-студия', d: 'Фильмы, сериалы, форматы. Прокатное удостоверение' },
  { id: 'ott', ico: '🖥', n: 'Онлайн-кинотеатр', d: 'Каталог, batch-проверка, API-интеграция' },
  { id: 'ugc', ico: '👥', n: 'UGC-платформа', d: 'Загрузки пользователей, модерация потока' },
]

export const WIZARD_CONTENT_TYPES = [
  { id: 'film', sym: '◆', n: 'Худож. кино и сериалы', c: '#9888d8' },
  { id: 'doc', sym: '▣', n: 'Документальное кино', c: '#7ca6ee' },
  { id: 'news', sym: '▲', n: 'Новостной контент', c: '#30d89c' },
  { id: 'ad', sym: '●', n: 'Реклама (вкл. трейлеры)', c: '#ec6080' },
  { id: 'live', sym: '◈', n: 'Live-эфир', c: '#d88050' },
  { id: 'ugc', sym: '◇', n: 'UGC (пользовательский)', c: '#dcc040' },
  { id: 'archive', sym: '◇', n: 'Архивный (до 1991)', c: '#40c8dc' },
]

export const WIZARD_PLATFORMS = [
  { id: 'fed_tv', n: 'Федеральный ТВ-эфир', d: 'Все 7 классов. Абс. запрет мата в эфире.', npa: ['436-ФЗ', '38-ФЗ', 'Закон о СМИ', 'КоАП 13.21'], c: '#30d89c' },
  { id: 'online', n: 'Онлайн-платформа', d: 'Усиленный контроль. Оборотные штрафы.', npa: ['149-ФЗ', '436-ФЗ', 'КоАП 13.41', 'Указ №809'], c: '#7ca6ee' },
  { id: 'cinema', n: 'Кинопрокат', d: 'Прокатное удостоверение. ФЗ №324 с 01.03.2026.', npa: ['126-ФЗ', 'ФЗ №324', 'Указ №809', '436-ФЗ'], c: '#9888d8' },
  { id: 'digital_tv', n: 'Цифровое ТВ / IPTV', d: 'Онлайн-версии каналов.', npa: ['149-ФЗ', '436-ФЗ', 'Указ №809'], c: '#40c8dc' },
]

export const SEGMENT_CONTENT_REC = {
  tv: ['film', 'news', 'ad', 'archive', 'live', 'doc'],
  production: ['film', 'doc', 'ad'],
  ott: ['film', 'doc', 'ad', 'archive'],
  ugc: ['ugc', 'live', 'ad'],
}

export const SEGMENT_PLATFORM_REC = {
  tv: ['fed_tv', 'online', 'digital_tv'],
  production: ['cinema', 'online'],
  ott: ['online'],
  ugc: ['online'],
}

/** Источники, согласованные с «Добавить файлы» (AddFilesModal) и org-config. */
export const WIZARD_SOURCES = [
  { id: 'local', n: 'Локальное хранилище', d: '/media/archive · NAS', ico: '◧' },
  { id: 'yadisk', n: 'Яндекс.Диск', d: 'OAuth · импорт из облака в «Добавить файлы»', ico: '◎' },
  { id: 'google', n: 'Google Диск', d: 'OAuth · импорт файлов из Google Drive', ico: '◳' },
  { id: 's3', n: 'S3-совместимое хранилище', d: 'Профили в «Настройках» · Timeweb и др.', ico: '☁' },
]

export const ROLES_BY_SEGMENT = {
  tv: [
    { id: 'chief_editor', n: 'Главный редактор', d: 'Контроль всех направлений', c: '#9888d8' },
    { id: 'operator', n: 'Оператор вещания', d: 'Загрузка, ревизия результатов', c: '#30d89c' },
    { id: 'lawyer', n: 'Юрист', d: 'Правовая оценка, заключения', c: '#7ca6ee' },
    { id: 'administrator', n: 'Администратор', d: 'Настройки, пользователи, тариф', c: '#40c8dc' },
  ],
  production: [
    { id: 'chief_editor', n: 'Продюсер', d: 'Инициирует проверку, утверждает', c: '#9888d8' },
    { id: 'operator', n: 'Выпускающий редактор', d: 'Работает с результатами AI', c: '#30d89c' },
    { id: 'lawyer', n: 'Юрист', d: 'Правовая оценка, прокатное удост.', c: '#7ca6ee' },
    { id: 'administrator', n: 'Администратор', d: 'Настройки, интеграции', c: '#40c8dc' },
  ],
  ott: [
    { id: 'operator', n: 'Контент-менеджер', d: 'Управление каталогом, batch', c: '#30d89c' },
    { id: 'lawyer', n: 'Юрист', d: 'Compliance-решения, отчётность', c: '#7ca6ee' },
    { id: 'administrator', n: 'CTO / Интеграции', d: 'API, Webhook, CMS', c: '#40c8dc' },
    { id: 'chief_editor', n: 'Руководитель', d: 'Аналитика, тренды', c: '#9888d8' },
  ],
  ugc: [
    { id: 'chief_editor', n: 'Head of Trust & Safety', d: 'Политики, массовые инциденты', c: '#ec6080' },
    { id: 'operator', n: 'Тимлид модерации', d: 'Управление командой', c: '#dcc040' },
    { id: 'administrator', n: 'Администратор', d: 'Настройки, интеграции', c: '#40c8dc' },
  ],
}

/** Классы и типы контента для матрицы соответствия. */
export const COMPLIANCE_CLASSES = [
  { id: 'К1', n: 'Наркотические вещества, курение, инъекции, алкоголь', subs: [
    { id: '1.1', n: 'Демонстрация табачных / курительных изделий', m: { film: 'mark', doc: 'mark', news: 'check', ad: 'block', live: 'mark', ugc: 'check', archive: 'exempt' } },
    { id: '1.2', n: 'Демонстрация алкоголя в рекламном контексте', m: { film: 'mark', doc: 'mark', news: 'check', ad: 'special', live: 'mark', ugc: 'check', archive: 'exempt' } },
    { id: '1.3', n: 'Демонстрация / пропаганда веществ, изменяющих сознание', m: { film: 'block', doc: 'block', news: 'block', ad: 'block', live: 'block', ugc: 'block', archive: 'special' } },
    { id: '1.4', n: 'Вовлечение н/л в употребление запрещённых веществ', m: { film: 'block', doc: 'block', news: 'block', ad: 'block', live: 'block', ugc: 'block', archive: 'block' } },
  ] },
  { id: 'К2', n: 'Девиантное и асоциальное поведение', subs: [
    { id: '2.1', n: 'Воровство, разбой, вандализм — романтизация', m: { film: 'check', doc: 'check', news: 'check', ad: 'check', live: 'check', ugc: 'block', archive: 'exempt' } },
    { id: '2.2', n: 'Нецензурная брань / ненормативная лексика', m: { film: 'mark', doc: 'mark', news: 'block', ad: 'block', live: 'block', ugc: 'mark', archive: 'exempt' } },
    { id: '2.3', n: 'Призывы к насилию / разжигание ненависти', m: { film: 'block', doc: 'block', news: 'block', ad: 'block', live: 'block', ugc: 'block', archive: 'block' } },
    { id: '2.4', n: 'Психологическое давление: травля, буллинг, запугивание', m: { film: 'check', doc: 'check', news: 'check', ad: 'check', live: 'check', ugc: 'block', archive: 'check' } },
    { id: '2.5', n: 'Насилие в отношении детей', m: { film: 'block', doc: 'block', news: 'block', ad: 'block', live: 'block', ugc: 'block', archive: 'block' } },
    { id: '2.6', n: 'Побуждение детей к суициду / причинению вреда здоровью', m: { film: 'block', doc: 'block', news: 'block', ad: 'block', live: 'block', ugc: 'block', archive: 'block' } },
  ] },
  { id: 'К3', n: 'Терроризм, экстремизм, нацизм — КоАП ст.20.3', subs: [
    { id: '3.1', n: 'Нацистская символика и атрибутика', m: { film: 'special', doc: 'special', news: 'special', ad: 'block', live: 'block', ugc: 'block', archive: 'exempt' } },
    { id: '3.2', n: 'Реабилитация нацизма / фальсификация истории ВОВ', m: { film: 'block', doc: 'block', news: 'block', ad: 'block', live: 'block', ugc: 'block', archive: 'block' } },
    { id: '3.3', n: 'Пропаганда терроризма и запрещённых организаций', m: { film: 'block', doc: 'block', news: 'block', ad: 'block', live: 'block', ugc: 'block', archive: 'block' } },
    { id: '3.4', n: 'Дискредитация ВС РФ / фейки о деятельности армии', m: { film: 'block', doc: 'block', news: 'block', ad: 'block', live: 'block', ugc: 'block', archive: 'check' } },
    { id: '3.5', n: 'Призывы к массовым беспорядкам / экстремизму', m: { film: 'block', doc: 'block', news: 'block', ad: 'block', live: 'block', ugc: 'block', archive: 'block' } },
  ] },
  { id: 'К4', n: 'Эротика / порнография', subs: [
    { id: '4.1', n: 'Информация эротического характера', m: { film: 'mark', doc: 'mark', news: 'block', ad: 'block', live: 'block', ugc: 'mark', archive: 'mark' } },
    { id: '4.2', n: 'Информация порнографического характера (незаконный оборот)', m: { film: 'block', doc: 'block', news: 'block', ad: 'block', live: 'block', ugc: 'block', archive: 'block' } },
    { id: '4.3', n: 'Детская порнография / педофилия', m: { film: 'block', doc: 'block', news: 'block', ad: 'block', live: 'block', ugc: 'block', archive: 'block' } },
  ] },
  { id: 'К5', n: 'Уничижение традиций и семейных ценностей', subs: [
    { id: '5.1', n: 'Пропаганда ЛГБТ+ отношений и идентичности', m: { film: 'block', doc: 'block', news: 'block', ad: 'block', live: 'block', ugc: 'block', archive: 'exempt' } },
    { id: '5.2', n: 'Пропаганда смены пола / трансгендерности', m: { film: 'block', doc: 'block', news: 'block', ad: 'block', live: 'block', ugc: 'block', archive: 'exempt' } },
    { id: '5.3', n: 'Пропаганда отказа от деторождения (чайлдфри)', m: { film: 'block', doc: 'block', news: 'block', ad: 'block', live: 'block', ugc: 'block', archive: 'check' } },
    { id: '5.4', n: 'Пропаганда педофилии', m: { film: 'block', doc: 'block', news: 'block', ad: 'block', live: 'block', ugc: 'block', archive: 'block' } },
    { id: '5.5', n: 'Дискредитация института семьи и традиционных ценностей', m: { film: 'block', doc: 'special', news: 'check', ad: 'check', live: 'check', ugc: 'check', archive: 'exempt' } },
  ] },
  { id: 'К6', n: 'Антипатриотический контент: иноагенты, реклама, религия', subs: [
    { id: '6.1', n: 'Нарушение требований к материалам иностранных агентов', m: { film: 'check', doc: 'check', news: 'block', ad: 'block', live: 'block', ugc: 'block', archive: 'na' } },
    { id: '6.2', n: 'Нарушения в рекламе: ЕРИР, запрещённые ресурсы', m: { film: 'na', doc: 'na', news: 'check', ad: 'block', live: 'check', ugc: 'special', archive: 'na' } },
    { id: '6.3', n: 'Оскорбление религиозных чувств / дискредитация традиций', m: { film: 'block', doc: 'block', news: 'block', ad: 'block', live: 'block', ugc: 'block', archive: 'special' } },
  ] },
  { id: 'К7', n: 'Тотализаторы, букмекеры, казино — лудомания', subs: [
    { id: '7.1', n: 'Реклама и продвижение нелегальных онлайн-казино', m: { film: 'na', doc: 'na', news: 'check', ad: 'block', live: 'check', ugc: 'block', archive: 'na' } },
    { id: '7.2', n: 'Реклама букмекеров и тотализаторов с нарушениями', m: { film: 'na', doc: 'na', news: 'special', ad: 'block', live: 'special', ugc: 'check', archive: 'na' } },
    { id: '7.3', n: 'Вовлечение несовершеннолетних в азартные игры', m: { film: 'block', doc: 'block', news: 'block', ad: 'block', live: 'block', ugc: 'block', archive: 'block' } },
    { id: '7.4', n: 'Пропаганда лудомании / симуляторы казино без лицензии', m: { film: 'na', doc: 'check', news: 'check', ad: 'check', live: 'special', ugc: 'block', archive: 'na' } },
  ] },
]

export const MATRIX_CELL_ICONS = {
  block: '⛔',
  mark: '⚠️',
  check: '✓',
  na: '—',
  special: '◈',
  exempt: '🛡',
}

export const MATRIX_CELL_COLORS = {
  block: '#e45878',
  mark: '#d4b838',
  check: '#2cd494',
  na: '#64748b',
  special: '#8c7cd0',
  exempt: '#38c0d4',
}
