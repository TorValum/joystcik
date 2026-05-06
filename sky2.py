import pygame
import time
import serial

# 1. Настройка порта
try:
    ser = serial.Serial('/dev/ttyUSB2', 57600, timeout=0.05)
    print("Порт открыт. Связь с STM32 установлена.")
except Exception as e:
    print(f"Ошибка порта: {e}")
    exit()

# 2. Инициализация джойстика
pygame.init()
pygame.joystick.init()

if pygame.joystick.get_count() == 0:
    print("Ошибка! Джойстик не подключен!")
    exit()

js = pygame.joystick.Joystick(0)
js.init()

# Переменная для хранения последней отправленной команды
last_cmd = ""

print(f"Обнаружен: {js.get_name()}")
print("Управление активно. Нажмите Ctrl+C для выхода.")

try:
    while True:
        pygame.event.pump()

        # Читаем стики
        stick_x = js.get_axis(0) # Ось 0: влево (-1) / вправо (1)
        stick_y = js.get_axis(1) # Ось 1: вверх (-1) / вниз (1)

        # Логика выбора команды
        current_cmd = '0' # По умолчанию нейтраль
        threshold = 0.5   # Порог срабатывания

        if stick_y < -threshold:   # Стик вверх
            current_cmd = '1'
        elif stick_y > threshold:  # Стик вниз
            current_cmd = '2'
        elif stick_x < -threshold: # Стик влево
            current_cmd = '3'
        elif stick_x > threshold:  # Стик вправо
            current_cmd = '4'
        
        # Проверка нажатия кнопок (парашют)
        if js.get_button(0):
            current_cmd = '9'
        if js.get_button(1):
            current_cmd = '8'

        # ОТПРАВКА: Шлем байт только если команда изменилась
        if current_cmd != last_cmd:
            ser.write(current_cmd.encode())
            last_cmd = current_cmd
            print(f"\n[SEND] Команда: {current_cmd}")

        # Вывод текущего состояния стиков
        print(f"X: {stick_x:.2f} | Y: {stick_y:.2f} | Команда: {current_cmd}   ", end='\r')
        
        time.sleep(0.01)

except KeyboardInterrupt:
    print("\nПрограмма остановлена.")
finally:
    ser.close()
    print("Порт закрыт.")

