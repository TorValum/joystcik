import pygame
import time
import serial

# ========== НАСТРОЙКИ ПОРТА ==========
try:
    ser = serial.Serial('/dev/ttyUSB7', 57600, timeout=0.05)
except:
    print("Ошибка порта")
    exit()

# ========== ИНИЦИАЛИЗАЦИЯ PYGAME ==========
pygame.init()
js = pygame.joystick.Joystick(0)
js.init()

# Настройки окна
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Наземная станция БПЛА")
clock = pygame.time.Clock()
font_small = pygame.font.Font(None, 20)
font_medium = pygame.font.Font(None, 28)
font_large = pygame.font.Font(None, 36)

# Цвета
COLOR_BG = (30, 30, 40)
COLOR_TEXT = (255, 255, 255)
COLOR_TEXT_DIM = (150, 150, 150)
COLOR_STICK_BG = (80, 80, 100)
COLOR_KREN = (100, 150, 255)
COLOR_TANGAZH = (255, 150, 100)
COLOR_PARACHUTE = (0, 200, 0)
COLOR_STOP = (200, 100, 0)

# ========== ФУНКЦИИ ОТРИСОВКИ ==========
def draw_stick(x, y, stick_x, stick_y):
    """Рисует положение стика"""
    pygame.draw.circle(screen, COLOR_STICK_BG, (x, y), 50)
    pygame.draw.circle(screen, COLOR_STICK_BG, (x, y), 50, 2)
    pygame.draw.circle(screen, COLOR_TEXT_DIM, (x, y), 3)
    pygame.draw.line(screen, COLOR_TEXT_DIM, (x, y - 40), (x, y + 40), 1)
    pygame.draw.line(screen, COLOR_TEXT_DIM, (x - 40, y), (x + 40, y), 1)
    
    px = int(x + stick_x * 40)
    py = int(y + stick_y * 40)
    pygame.draw.circle(screen, (100, 200, 255), (px, py), 8)
    pygame.draw.circle(screen, COLOR_TEXT, (px, py), 8, 2)

def draw_command(cmd, arg, x, y):
    """Рисует текущую команду"""
    bg_rect = pygame.Rect(x, y, 200, 50)
    pygame.draw.rect(screen, (50, 50, 60), bg_rect)
    pygame.draw.rect(screen, COLOR_TEXT_DIM, bg_rect, 2)
    
    if cmd == 9:
        text = font_medium.render(f"ПАРАШЮТ", True, COLOR_PARACHUTE)
    elif cmd == 8:
        text = font_medium.render(f"СТОП", True, COLOR_STOP)
    elif cmd in [1, 2]:
        text = font_medium.render(f"ТАНГАЖ {arg}", True, COLOR_TANGAZH)
    elif cmd in [3, 4]:
        text = font_medium.render(f"КРЕН {arg}", True, COLOR_KREN)
    elif cmd == 0:
        text = font_medium.render(f"НЕЙТРАЛЬ", True, COLOR_TEXT)
    else:
        text = font_medium.render(f"{cmd} {arg}", True, COLOR_TEXT)
    
    screen.blit(text, (x + 10, y + 12))

def draw_info(stick_x, stick_y, last_msg):
    """Информационная панель"""
    panel_rect = pygame.Rect(550, 350, 220, 150)
    pygame.draw.rect(screen, (50, 50, 60), panel_rect)
    pygame.draw.rect(screen, COLOR_TEXT_DIM, panel_rect, 2)
    
    lines = [
        f"X (крен): {stick_x:+.2f}",
        f"Y (тангаж): {stick_y:+.2f}",
        f"Команда: {last_msg}"
    ]
    y_offset = 370
    for line in lines:
        text = font_small.render(line, True, COLOR_TEXT)
        screen.blit(text, (565, y_offset))
        y_offset += 25

# ========== ОСНОВНОЙ ЦИКЛ ==========
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
            msg = "9 500\n"
            
        elif js.get_button(1):
            msg = "8 1500\n"
        
        # 4. Логика управления
        elif abs(stick_y) > abs(stick_x) and abs(stick_y) > threshold:
            val = int(1500 - stick_y * 500)
            cmd = "1" if stick_y < 0 else "2"
            msg = f"{cmd} {val}\n"
            
        elif abs(stick_x) > threshold:
            val = int(1500 + stick_x * 500)
            cmd = "3" if stick_x < 0 else "4"
            msg = f"{cmd} {val}\n"
            
        else:
            msg = "0 1500\n"

        # 5. Отправка команды только когда она изменилась по сравнению с предыдущей 
        if msg != last_msg:
            ser.write(msg.encode())
            last_msg = msg
            print(f"Отправлено: {msg.strip()}")

        # ========== ОТРИСОВКА  ==========
        screen.fill(COLOR_BG)
        
        # Заголовок
        title = font_large.render("Наземная станция БПЛА", True, COLOR_TEXT)
        screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, 10))
        
        # Стик
        draw_stick(200, 250, stick_x, stick_y)
        
        # Подписи осей
        x_label = font_small.render(f"Крен: {stick_x:+.2f}", True, COLOR_KREN)
        y_label = font_small.render(f"Тангаж: {stick_y:+.2f}", True, COLOR_TANGAZH)
        screen.blit(x_label, (150, 320))
        screen.blit(y_label, (150, 340))
        
        # Команда
        if msg:
            cmd_parts = msg.strip().split()
            if len(cmd_parts) == 2:
                draw_command(int(cmd_parts[0]), int(cmd_parts[1]), 550, 180)
        
        # Инфо
        draw_info(stick_x, stick_y, msg.strip())
        
        # Подвал
        footer = font_small.render("Esc - выход | A - Парашют | B - Стоп", True, COLOR_TEXT_DIM)
        screen.blit(footer, (WINDOW_WIDTH//2 - footer.get_width()//2, WINDOW_HEIGHT - 30))
        
        pygame.display.flip()
        clock.tick(60)
        
        time.sleep(0.02)

except KeyboardInterrupt:
    ser.close()
    pygame.quit()
