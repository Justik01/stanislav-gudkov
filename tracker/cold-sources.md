# Источники лидов (холодный поиск) — валидация 2026-11-16

Логика: найти компании, которым нужен сайт/лендинг/бот, а не ждать заказ в очередь.
Скрипты: `probe_cold*.py`, `probe_overpass*.py` (запуск `py -3 <имя>`).

## Годные

| Источник | Что даёт | Статус |
|---|---|---|
| **2GIS API** (`catalog.api.2gis.com/3.0/items`) | Фильтр `has_site` (true/false) → организации с сайтом или БЕЗ; рубрики + города РФ/РБ, структурированный JSON, телефон в данных | ⏳ нужен бесплатный ключ (dev.2gis.com, регистрация ~2 мин). Подтверждено по докам (ctx7): `has_site`, `rubric_id`, `search_type=one_branch` |
| **Google Places API** (Text Search + Place Details) | `websiteUri`, телефоны, глобально | ⏳ ключ Stas'а отвергнут (`REQUEST_DENIED` — API не включён в консоли Google Cloud). Включить Places API → free quota. Риск: геоблок Google, как у Gemini |
| **Yandex Maps** (рендер в браузере) | Орг-карточки, сайт, телефон | 🟡 HTML-страница отдаётся (200, 1.9М), но ссылки /org/N грузятся JS — нужен браузерный рендер (in-app browser). Медленно, точечно, не для пачек |

## Мёртвые (проверено, не использовать)

| Источник | Почему |
|---|---|
| `firmy.ru` | SSL handshake failure |
| `yell.ru` | таймаут |
| `blizko.ru` | 403 |
| `zoon.ru` / `gomel.zoon.ru` | корень живой, но секции и карточки — SPA (шаблоны `${item.url}`, ссылок на организации в HTML нет); резвиться не стоит |
| `onliner.by` catalog | SPA, публичный JSON API не найден (404 на /search/shops и др.) |
| **Overpass OSM** | `overpass-api.de` — стабильный 406 (WAF режет urllib); зеркала — таймауты/только Швейцария. Источник отложен |
| `2gis.by` HTML | живой, но SPA; данные — только через API |

## Следующий шаг

1. **Stas:** регистрация на `dev.2gis.com` → ключ (бесплатный тариф, квоту смотрим в консоли).
2. Я: коллектор `hunter/cold_leads.py` (rubric → `has_site=false` → фильтр городов → `tracker/leads.json`), проверка ключа в selftest.
3. Параллельно (опционально): включение Places API в Google Cloud Console — как страховка.
