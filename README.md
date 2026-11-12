# ShiftFile (Case 06) — In-Browser File Converter

> **Teenage Engineering Industrial Minimalism • Zero-Upload Client-Side WASM Engine • Instant Telegram Converter Companion**

![Teenage Engineering Industrial UI](https://img.shields.io/badge/Aesthetic-Teenage%20Engineering-FF5722?style=flat-square)
![WASM / Client-side](https://img.shields.io/badge/Conversion-Zero--Upload%20WASM-262626?style=flat-square)
![Telegram Bot](https://img.shields.io/badge/Aiogram%203.x-Mirror%20Bot-blue?style=flat-square)

---

## 🎯 Features
1. **Industrial Hardware Aesthetics:** Matte anodized chassis (#E8E8E8 / #262626), mechanical knobs, safety orange controls (#FF5722), rotating brass gears animation during processing.
2. **Privacy-First In-Browser Conversion:**
   - **Images:** PNG, JPEG, WEBP, BMP transcoding with resolution & quality adjustment.
   - **Spreadsheets / Data:** JSON <-> CSV <-> TSV bi-directional conversion with automatic key flattening.
   - **Audio:** Web Audio WAV synthesizer & transcoder.
   - **Documents:** Markdown to HTML, HTML to TXT, PDF generator.
3. **Telegram Mirror Bot (Aiogram 3.x):** Upload files directly in Telegram, select output format from dynamic inline buttons, get the converted file back in seconds.
4. **Safety & Memory Guard:** Automatic warning modal for files exceeding 100MB to avoid browser heap exhaustion.

---

## 🚀 Quick Start

### 1. Web & API Server
```bash
cd Case06_ShiftFile
pip install -r requirements.txt
python api/server.py
```
Open [http://localhost:8006](http://localhost:8006) in your browser.

### 2. Telegram Bot
```bash
python bot/bot.py
```

### 3. Run Tests
```bash
pytest tests/test_shiftfile.py -v
```

---

## 📂 Project Layout
```
Case06_ShiftFile/
├── 01_structure.md
├── 02_changelog.md
├── 03_active_tasks.md
├── README.md
├── .env.example
├── requirements.txt
├── package.json
├── web/
│   ├── index.html
│   ├── style.css
│   └── app.js
├── api/
│   └── server.py
├── bot/
│   └── bot.py
└── tests/
    └── test_shiftfile.py
```
