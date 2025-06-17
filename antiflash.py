import pymem
import pymem.process
import time
import requests

# Инициализация pymem и получение client.dll
pm = pymem.Pymem("cs2.exe")
client = pymem.process.module_from_name(pm.process_handle, "client.dll").lpBaseOfDll

# Получение оффсетов из GitHub
try:
    offsets = requests.get("https://raw.githubusercontent.com/a2x/cs2-dumper/main/output/offsets.json").json()
    clientdll = requests.get("https://raw.githubusercontent.com/a2x/cs2-dumper/main/output/client_dll.json").json()
except Exception as e:
    print(f"Failed to fetch offsets: {e}")
    offsets = {}
    clientdll = {}

# Основной цикл
while True:
    try:
        # Получение оффсета локального игрока и флеша
        dwLocalPlayerPawn = offsets.get("client.dll", {}).get("dwLocalPlayerPawn", 0)
        flash = clientdll.get("client.dll", {}).get("classes", {}).get("C_CSPlayerPawnBase", {}).get("fields", {}).get("m_flFlashDuration", 0)


        localPlayer = pm.read_longlong(client + dwLocalPlayerPawn)

        # Проверка валидности адреса игрока
        if localPlayer and localPlayer > 0x10000:
            flashDur = pm.read_float(localPlayer + flash)

            if flashDur > 0.0:
                pm.write_float(localPlayer + flash, 0.0)
    except (pymem.exception.MemoryReadError, pymem.exception.WinAPIError) as e:
        print(f"Memory read error: {e}. Retrying...")
        time.sleep(0.01)
    except Exception as e:
        print(f"Unexpected error: {e}")
        time.sleep(0.01)
