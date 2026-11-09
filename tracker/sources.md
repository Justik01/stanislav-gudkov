# Источники запросов

Правило: источник живёт в таблице, если даёт ≥5 релевантных запросов в неделю.
Проверяем 1 раз в неделю, неактивные вычёркиваем.

**Валидация 2026-11-09** (скрипты: `probe_sources.py`, `probe2.py`, `probe3.py`):
поток есть, порог «≥5 релев/день» переваливают FL.ru в одиночку. Вердикт: ядро
«охотника» имеет смысл строить.

## Рабочие источники (проверено 09.11.2026)

| Источник | Тип | Ссылка | Релевантных/день | Вердикт |
|---|---|---|---|---|
| **FL.ru — RSS всех заказов** | RSS | https://www.fl.ru/rss/all.xml | **~21** (60 постов/24ч, 21 рел.) | ✅ главный кормилец, фильтр по ключам |
| **TG job_developer** | TG-канал | https://t.me/s/job_developer | ~17 (все рел., агрегатор с ссылками) | ✅ |
| **TG tilda_profiI** (Tilda Profi) | TG-канал | https://t.me/s/tilda_profiI | ~15 (все рел., узко Tilda) | ✅ нишево в профиль |
| **TG sova_freelance** | TG-канал | https://t.me/s/sova_freelance | ~7 (14/20 рел.) | ✅ |
| **TG freelance7** (PIXEL) | TG-канал | https://t.me/s/freelance7 | ~6.5 (10/20 рел.) | ✅ |
| **TG Koteyka_Freelancer** | TG-канал | https://t.me/s/Koteyka_Freelancer | ~3.4 (14/20 рел.) | ✅ на грани, держим |
| **TG freelance_orders** | TG-канал | https://t.me/s/freelance_orders | ~2.2 (6/16 рел.) | ⚠️ слабый |
| **TG digitaltender** | TG-канал | https://t.me/s/digitaltender | ~1 (13/20 рел.) | ⚠️ медленный, но чистый |
| Kwork — лента заказов | HTML | https://kwork.ru/orders | читается (нет RSS) | ✅ нужен парсинг HTML |
| Weblancer — проекты | HTML | https://www.weblancer.net/projects/ | читается (RSS мёртв) | ✅ парсинг HTML |
| Work24 — заказы | HTML | https://work24.ru/orders | читается (RSS мёртв) | ✅ парсинг HTML |
| Freelance.ru — проекты | HTML | https://freelance.ru/projects | читается (RSS мёртв) | ✅ парсинг HTML |

## Мёртвые / не подошли (09.11.2026)

- RSS Weblancer, Freelance.ru, Work24 — 404 (есть только HTML).
- Habr freelance RSS — работает, но 0 постов/24ч, мало активности → пропускаем.
- TG: `freelance_jobs_ru`, `distantsiya`, `programming_jobs` — приватные/имя не то
  (t.me/s/ пустой); `freelancebaraholka` — мёртв (5 постов за 2+ года);
  `work_finde` — ~0.4/день, `kadrof_work` — вакансии, не заказы.

## Кандидаты на расширение (не проверены глубоко)

- TG design_profiI — высокий поток (часто пачками), 8/20 рел. — дизайн-заказы,
  частично в профиль (лендинги).
- TG freelancetalk, TG job_copywriter / jobs_marketer / jobs_designer (сетка
  @job_developer) — соседние ниши, проверить после MVP.

## Как считаем релевантность

Ключи (regex, `probe_sources.py`): сайт/лендинг/верстка/Tilda/WordPress/боты/
автоматизация/парсеры/интеграции/CRM/n8n/редизайн/интернет-магазин.
LLM-фильтр в MVP заменит regex на «это запрос на сайт/бота? бюджет/сроки?».

## Telegram-каналы: как читать

Публичные каналы читаются без авторизации через превью `https://t.me/s/<username>` —
этот способ и используем в скрипте (закрытые/приватные — не читаются, не берём).

## Чек-лист пополнения

1. Нашёл канал/площадку → проверил `probe2.py`/`probe3.py` (добавил в SOURCES).
2. Считал релевантных/день → занёс в таблицу выше.
3. <5/нед — не добавляем.
