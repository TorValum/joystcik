import pygame
import time
import serial

# Настройка порта (проверь скорость, в STM32 обычно 115200 или 9600)
try:
    ser = serial.Serial('/dev/ttyUSB5', 57600, timeout=0.05)
except:
    print("Ошибка порта")
    exit()

pygame.init()
js = pygame.joystick.Joystick(0)
js.init()

last_msg = ""

try:
    while True:
        pygame.event.pump()

        # 1. Получаем чистые значения стиков (-1.0 ... 1.0)
        stick_x = js.get_axis(0) 
        stick_y = js.get_axis(1)

        # 2. Определяем мертвую зону
        threshold = 0.1
        msg = ""

        # 3. Приоритет кнопкам (Парашют)
        if js.get_button(0):
            msg = "9 2000\n"
            
        elif js.get_button(1):
            msg = "8 1500\n"
        
        # 4. Логика управления (выбираем доминирующую ось)
        # Так как STM32 принимает либо Крен, либо Тангаж в один момент времени
        elif abs(stick_y) > abs(stick_x) and abs(stick_y) > threshold:
            # Тангаж (Команды 1 или 2)
            # Вверх на стике обычно -1, поэтому инвертируем для получения 1000-2000
            val = int(1500 - stick_y * 500)
            cmd = "1" if stick_y < 0 else "2"
            msg = f"{cmd} {val}\n"
            
        elif abs(stick_x) > threshold:
            # Крен (Команды 3 или 4)
            val = int(1500 + stick_x * 500)
            cmd = "3" if stick_x < 0 else "4"
            msg = f"{cmd} {val}\n"
            
        else:
            # Нейтраль
            msg = "0 1500\n"

        # 5. Отправка (только если значение изменилось, чтобы не спамить в UART)
        if msg != last_msg:
            ser.write(msg.encode())
            last_msg = msg
            print(f"Отправлено: {msg.strip()}")

        time.sleep(0.02) # 50 Гц — стандарт для сервоприводов

except KeyboardInterrupt:
    ser.close()

