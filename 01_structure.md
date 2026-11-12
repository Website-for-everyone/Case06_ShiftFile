# АРХИТЕКТУРА И СПЕЦИФИКАЦИЯ ПРОЕКТА: ShiftFile

> **Проект:** ShiftFile (Case 06) — Конвертер файлов в браузере (Teenage Engineering Industrial Style)  
> **Клиент / Заказчик:** B2B SaaS / Портфолио Даниэля Идрисова (@Idrisov_prod)  
> **Чек проекта:** 140 000 ₽ | **Срок:** 7 дней (Дедлайн: 2026-11-20)  
> **Дедлайн MVP (80%):** 2026-11-16  
> **Тип договора:** Договор СМЗ с ИП/ООО (Чек «Мой Налог»)

---

## 🛠 Технологический стек
- **Frontend / UI:** Vanilla JS / HTML5 / CSS3, WebAssembly (client-side transcode), Canvas 2D API, Web Audio API, SheetJS, Teenage Engineering industrial design system (#E8E8E8, #262626, #FF5722)
- **Backend & Logic:** Python 3.12, FastAPI, Uvicorn, Pillow, OpenPyXL, Pandas/CSV
- **Telegram Bot:** Aiogram 3.x, Asyncio, aiohttp, Inline Keyboards
- **Автоматизация & Интеграции:** Telegram Webhook, Owner Alert to @Idrisov_prod
- **Тестирование:** Pytest, Unit & Smoke Tests

---

## 🏛 Архитектурная схема
```
[ Клиент / Браузер ] ──► [ Client-Side WASM / Canvas Engine ] ──► [ Instant Blob Download ]
         │ (Опциональный Server / Bot Fallback)
         ▼
[ FastAPI Server ] ◄───► [ Telegram Mirror Bot (Aiogram 3.x) ]
         │
         ▼
   [ @Idrisov_prod Alert Telemetry ]
```

---

## 🔐 Переменные окружения (.env.example)
```env
BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
WEB_HOST=0.0.0.0
WEB_PORT=8006
OWNER_TG_ID=1387913438
ENVIRONMENT=production
```

---

## 🔗 Ресурсы и ссылки
- **Репозиторий GitHub:** https://github.com/Website-for-everyone/Case06_ShiftFile
- **Dev-сервер / Preview URL:** http://localhost:8006
- **Чат проекта в Telegram:** @Idrisov_prod
