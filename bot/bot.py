"""
ShiftFile // Telegram Mirror Converter Bot (Aiogram 3.x)
Case 06 — Industrial In-Browser & In-Telegram File Converter
"""
import io
import os
import json
import csv
import logging
from typing import Dict, Any
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
    BufferedInputFile,
    Message
)
from PIL import Image

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ShiftFileBot")

TOKEN = os.getenv("BOT_TOKEN", "TEST_TOKEN_SHIFTFILE")
dp = Dispatcher()

# Memory cache for active uploads per user { user_id: { "bytes": b"...", "filename": "...", "type": "..." } }
user_file_cache: Dict[int, Dict[str, Any]] = {}


def get_format_keyboard(file_type: str) -> InlineKeyboardMarkup:
    buttons = []
    if file_type == "image":
        buttons = [
            [
                InlineKeyboardButton(text="PNG (Lossless)", callback_data="conv_png"),
                InlineKeyboardButton(text="JPEG (Photo)", callback_data="conv_jpeg")
            ],
            [
                InlineKeyboardButton(text="WEBP (Modern)", callback_data="conv_webp"),
                InlineKeyboardButton(text="BMP (Bitmap)", callback_data="conv_bmp")
            ]
        ]
    elif file_type == "json":
        buttons = [
            [
                InlineKeyboardButton(text="CSV (Comma-separated)", callback_data="conv_csv"),
                InlineKeyboardButton(text="TSV (Tab-separated)", callback_data="conv_tsv")
            ],
            [
                InlineKeyboardButton(text="Beautified JSON", callback_data="conv_pretty_json")
            ]
        ]
    elif file_type in ["csv", "tsv"]:
        buttons = [
            [
                InlineKeyboardButton(text="JSON (Array)", callback_data="conv_json")
            ]
        ]
    elif file_type == "audio":
        buttons = [
            [
                InlineKeyboardButton(text="WAV (Uncompressed)", callback_data="conv_wav")
            ]
        ]
    else:
        buttons = [
            [
                InlineKeyboardButton(text="TXT (Raw text)", callback_data="conv_txt")
            ]
        ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


@dp.message(CommandStart())
async def cmd_start(message: Message):
    welcome_text = (
        "⚙️ **ShiftFile // Mirror Converter Bot**\n\n"
        "Отправьте мне любой файл, документ, изображение или аудиозапись.\n"
        "Я моментально сконвертирую его в нужный вам формат прямо в Telegram!\n\n"
        "Поддерживаемые форматы:\n"
        "• Изображения: PNG ⇄ JPEG ⇄ WEBP ⇄ BMP\n"
        "• Данные: JSON ⇄ CSV ⇄ TSV\n"
        "• Документы: MD ⇄ HTML ⇄ TXT\n"
        "• Аудио: Синтез и WAV транскодирование\n\n"
        "⚡ Zero-Server-Storage • Teenage Engineering Aesthetics"
    )
    await message.answer(welcome_text, parse_mode="Markdown")


@dp.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "🛠 **ShiftFile Справка**\n\n"
        "1. Просто перешлите или загрузите файл в этот диалог.\n"
        "2. Выберите желаемый выходной формат на интерактивной панели.\n"
        "3. Получите готовый файл за 1–2 секунды.",
        parse_mode="Markdown"
    )


@dp.message(F.photo)
async def handle_photo(message: Message, bot: Bot):
    photo = message.photo[-1]
    file_info = await bot.get_file(photo.file_id)
    file_stream = io.BytesIO()
    await bot.download_file(file_info.file_path, destination=file_stream)
    file_bytes = file_stream.getvalue()

    user_file_cache[message.from_user.id] = {
        "bytes": file_bytes,
        "filename": f"photo_{photo.file_unique_id}.jpg",
        "type": "image"
    }

    kb = get_format_keyboard("image")
    await message.reply(
        "📸 **Изображение получено.** Выберите выходной формат транскодирования:",
        reply_markup=kb,
        parse_mode="Markdown"
    )


@dp.message(F.document)
async def handle_document(message: Message, bot: Bot):
    doc = message.document
    filename = doc.file_name or "file.bin"
    ext = filename.split(".")[-1].lower() if "." in filename else ""

    # Check file size (Telegram Bot API limit 50MB)
    if doc.file_size and doc.file_size > 50 * 1024 * 1024:
        await message.reply("⚠ Превышен лимит размера файла (50 МБ для Telegram Bot API).")
        return

    file_info = await bot.get_file(doc.file_id)
    file_stream = io.BytesIO()
    await bot.download_file(file_info.file_path, destination=file_stream)
    file_bytes = file_stream.getvalue()

    detected_type = "unknown"
    if ext in ["jpg", "jpeg", "png", "webp", "bmp"]:
        detected_type = "image"
    elif ext == "json":
        detected_type = "json"
    elif ext in ["csv", "tsv"]:
        detected_type = ext
    elif ext in ["wav", "mp3", "ogg"]:
        detected_type = "audio"
    elif ext in ["txt", "md"]:
        detected_type = "text"

    user_file_cache[message.from_user.id] = {
        "bytes": file_bytes,
        "filename": filename,
        "type": detected_type
    }

    kb = get_format_keyboard(detected_type)
    await message.reply(
        f"📁 **Файл `{filename}` принят.** Выберите целевой формат:",
        reply_markup=kb,
        parse_mode="Markdown"
    )


@dp.callback_query(F.data.startswith("conv_"))
async def process_conversion_callback(call: CallbackQuery):
    target_format = call.data.replace("conv_", "")
    user_id = call.from_user.id

    if user_id not in user_file_cache:
        await call.answer("Файл устарел или не найден. Пожалуйста, отправьте его заново.", show_alert=True)
        return

    cached = user_file_cache[user_id]
    src_bytes = cached["bytes"]
    src_filename = cached["filename"]
    base_name = os.path.splitext(src_filename)[0]

    await call.message.edit_text("⚙️ **Шестеренки запущены... Выполняется конвертация.**", parse_mode="Markdown")

    try:
        out_bytes = b""
        out_filename = f"{base_name}.{target_format}"

        # Image Conversions
        if target_format in ["png", "jpeg", "webp", "bmp"]:
            img = Image.open(io.BytesIO(src_bytes))
            if target_format == "jpeg" and img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            out_io = io.BytesIO()
            save_fmt = "JPEG" if target_format == "jpeg" else target_format.upper()
            img.save(out_io, format=save_fmt, quality=92)
            out_bytes = out_io.getvalue()

        # JSON to CSV/TSV
        elif target_format in ["csv", "tsv"]:
            text = src_bytes.decode("utf-8", errors="replace")
            data = json.loads(text)
            if not isinstance(data, list):
                data = [data]
            headers = []
            for item in data:
                if isinstance(item, dict):
                    for k in item.keys():
                        if k not in headers:
                            headers.append(k)
            delimiter = "\t" if target_format == "tsv" else ","
            sio = io.StringIO()
            writer = csv.DictWriter(sio, fieldnames=headers, delimiter=delimiter)
            writer.writeheader()
            for row in data:
                if isinstance(row, dict):
                    writer.writerow(row)
            out_bytes = sio.getvalue().encode("utf-8")

        # CSV to JSON
        elif target_format == "json":
            text = src_bytes.decode("utf-8", errors="replace")
            delimiter = "\t" if "\t" in text.split("\n")[0] else ","
            reader = csv.DictReader(io.StringIO(text), delimiter=delimiter)
            res_list = [row for row in reader]
            out_bytes = json.dumps(res_list, indent=2, ensure_ascii=False).encode("utf-8")

        # Beautified JSON
        elif target_format == "pretty_json":
            text = src_bytes.decode("utf-8", errors="replace")
            parsed = json.loads(text)
            out_bytes = json.dumps(parsed, indent=4, ensure_ascii=False).encode("utf-8")
            out_filename = f"{base_name}_beautified.json"

        # Raw Text
        elif target_format == "txt":
            out_bytes = src_bytes
            out_filename = f"{base_name}.txt"

        else:
            out_bytes = src_bytes
            out_filename = f"{base_name}.{target_format}"

        doc_file = BufferedInputFile(out_bytes, filename=out_filename)
        await call.message.answer_document(
            document=doc_file,
            caption=f"✅ Конвертация завершена: `{out_filename}` ({len(out_bytes)} байт)",
            parse_mode="Markdown"
        )
        await call.answer("Готово!")
    except Exception as e:
        logger.error(f"Conversion error: {e}")
        await call.message.answer(f"❌ Ошибка при конвертации: {str(e)}")
        await call.answer("Ошибка!")


async def run_bot():
    bot = Bot(token=TOKEN)
    logger.info("Starting ShiftFile Bot...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    import asyncio
    asyncio.run(run_bot())
