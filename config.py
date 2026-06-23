import pygame

# --- ЛОГИЧЕСКОЕ РАЗРЕШЕНИЕ ---
# Это размер холста на котором происходит вся физика и отрисовка игры.
INTERNAL_WIDTH: int = 1248
INTERNAL_HEIGHT: int = 720

# --- НАСТРОЙКИ ОКНА ---
FPS: int = 144
WINDOW_TITLE: str = "NoGum!"

PRINT_FPS: bool = True # выводит счетчик FPS в реальном времени на экран

# --- ГЕЙМПЛЕЙНЫЕ КОНСТАНТЫ ---
PLAYER_TILT_MAX_ANGLE: float = 20.0   # Максимальный угол наклона в градусах
PLAYER_TILT_SMOOTHING: float = 40.0    # Скорость плавного перехода к целевому углу
FRICTION: float = 20.0
SKILLS_COOLDOWN_COEF_LIMIT = 0.75

# Рывок
STANDARD_DASH_SPEED: float = 2000.0  # Скорость во время рывка
STANDARD_DASH_DURATION: float = 0.15  # Длительность
STANDARD_DASH_COOLDOWN: float = 3.0  # Кд между рывками

# Слэш
SLASH_RADIUS: float = 150.0
SLASH_ANGLE_SPAN: int = 120
SLASH_DAMAGE: float = 10.0
SLASH_STUN_TIME: float = 0.3
SLASH_ATTACK_TIME: float = 0.06
SLASH_COOLDOWN: float = 5.0

# переход между этажами
TRANSITION_TIME: float = 0.5

# баланс
LEVEL_COEF: float = 1.15 # коэффициент увеличения стат мобов в зависимости от уровня
MAX_POWER_LIMIT: int = 1000

# --- ЦВЕТА ---
BACKGROUND_COLOR: tuple[int, int, int] = (10, 10, 10)

# индикатор рывка
UI_DASH_COLOR: tuple[int, int, int] = (115, 245, 155)
UI_DASH_BG_COLOR: tuple[int, int, int] = (50, 100, 70)

# индикатор слэша
UI_SLASH_COLOR: tuple[int, int, int] = (115, 190, 185)
UI_SLASH_BG_COLOR: tuple[int, int, int] = (50, 85, 100)

UI_HP_COLOR: tuple[int, int, int] = (255, 255, 40)
UI_HP_BG_COLOR: tuple[int, int, int] = (45, 45, 20)
UI_TEXT_COLOR: tuple[int, int, int] = (255, 255, 255)

MINIMAP_BG_COLOR: tuple[int, int, int, int] = (30, 30, 30, 200)
MINIMAP_ROOM_BG_COLOR: tuple[int, int, int] = (30, 30, 30)  # Пол комнат
MINIMAP_PLAYER_COLOR: tuple[int, int, int] = (165, 175, 60)
MINIMAP_BORDER_COLOR: tuple[int, int, int] = (40, 40, 40)
TERMINAL_MAP_COLOR: tuple[int, int, int] = (80, 220, 170)
TERMINAL_ACTIVE_COLOR: tuple[int, int, int] = (220, 255, 25)
TERMINAL_INACTIVE_COLOR: tuple[int, int, int] = (40, 110, 80)
EXIT_COLOR: tuple[int, int, int] = (255, 120, 100)
CHEST_COLOR: tuple[int, int, int] = (255, 235, 155)

MINIMAP_WALL_COLOR_LIST: list[tuple[int, int, int]] = [
                                            (150, 80, 50),    # 1 seed
                                            (145, 50, 100),   # 2
                                            (70, 100, 100),   # 3
                                            (100, 90, 55),    # 4
                                            (105, 55, 105),   # 5
                                            (50, 90, 60),     # 6
                                            (150, 40, 40),     # 7
                                            (70, 20, 125),     # 8
                                            (130, 125, 110)   # 9
                                          ]
# слайдеры
SLIDER_BACKGROUND_COLOR: tuple[int, int, int] = (40, 40, 55)
SLIDER_FILL_COLOR: tuple[int, int, int] = (155, 255, 135)
SLIDE_KNOB_INSIDE_COLOR: tuple[int, int, int] = (60, 60, 85)
SLIDE_KNOB_OUTSIDE_COLOR: tuple[int, int, int] = (100, 100, 125)
# кнопки
BUTTON_ACTIVE_COLOR_INSIDE: tuple[int, int, int] = (60, 60, 85)
BUTTON_ACTIVE_COLOR_OUTSIDE: tuple[int, int, int] = (100, 100, 125)

BUTTON_INACTIVE_COLOR_INSIDE: tuple[int, int, int] = (30, 30, 45)
BUTTON_INACTIVE_COLOR_OUTSIDE: tuple[int, int, int] = (65, 65, 80)

BUTTON_SELECTED_COLOR_INSIDE: tuple[int, int, int] = (60, 95, 85)
BUTTON_SELECTED_COLOR_OUTSIDE: tuple[int, int, int] = (100, 130, 125)

BUTTON_CLICKED_COLOR_INSIDE: tuple[int, int, int] = (35, 150, 105)
BUTTON_CLICKED_COLOR_OUTSIDE: tuple[int, int, int] = (65, 205, 130)

MENU_BUTTON_ACTIVE_COLOR: tuple[int, int, int] = (160, 160, 200)
MENU_BUTTON_SELECTED_COLOR: tuple[int, int, int] = (75, 180, 115)
MENU_BUTTON_CLICKED_COLOR: tuple[int, int, int] = (105, 255, 160)
MENU_BUTTON_INACTIVE_COLOR: tuple[int, int, int] = (50, 50, 60)


# индикаторы скилов
INDICATOR_ACTIVE_COLOR_INSIDE: tuple[int, int, int] = (60, 60, 85)
INDICATOR_ACTIVE_COLOR_OUTSIDE: tuple[int, int, int] = (100, 100, 125)

INDICATOR_INACTIVE_COLOR_INSIDE: tuple[int, int, int] = (30, 30, 45)
INDICATOR_INACTIVE_COLOR_OUTSIDE: tuple[int, int, int] = (65, 65, 80)

INDICATOR_FILL_COLOR: tuple[int, int, int] = (65, 65, 80)

# --- РАЗМЕРЫ (в пикселях ВНУТРЕННЕГО разрешения) ---
PLAYER_SIZE: int = 40

# Комната
ROOM_COLS = 26
ROOM_ROWS = 15
ROOM_SYMBOL_WALL = "*"
ROOM_SYMBOL_EMPTY = "0"
ROOM_SYMBOL_TERMINAL = "T"
TILE_SIZE: int = 48
EXIT_SIZE: int = 144
LAYOUTS_DIR: str = "room_layouts"
TERMINAL_CHANCE: int = 50 # шанс спавна терминала в комнате с максимальной глубиной

# Генерация
# лимиты количества комнат
MAX_ROOMS: int = 17
MIN_ROOMS: int = 13
# лимиты волн врагов в комнатах
MAX_WAVES: int = 3
MIN_WAVES: int = 1

EXIT_COUNT = 3
MAX_CHEST_COUNT = 4

# --- UI КОНСТАНТЫ ---
UI_HP_MAX: int = 100
UI_HP_BAR_WIDTH: int = 200
UI_HP_BAR_HEIGHT: int = 50

UI_SKILL_BAR_WIDTH: int = 30
UI_SKILL_BAR_HEIGHT: int = 4
UI_SKILL_OFFSET_Y: float = 20.0
UI_SKILL_HIDE_DELAY: float = 1.0

BUTTON_CLICKED_TIME = 0.1

CAMERA_LERP_SPEED = 2.7 # Скорость движения камеры

DRAW_PATH = False # debug отрисовщик для pathfinder'а
DRAW_SLASH = False

# Mini-Map
MINIMAP_WIDTH: int = 400
MINIMAP_HEIGHT: int = 400
MINIMAP_EXPLORED: bool = False # отладочная функция для открытия всей миникарты сразу

# Интерфейс терминалов
TERMINAL_HUD_WIDTH: int = 1000
TERMINAL_HUD_HEIGHT: int = 600

# Спрайты
ASSETS_DIR: str = "assets"

# --- ОРУЖИЕ И UI ---
WEAPON_UI_KEY: int = pygame.K_i

# Эффекты попаданий
WALL_IMPACT_PARTICLE_COUNT: int = 4
ENEMY_IMPACT_PARTICLE_COUNT: int = 10
IMPACT_PARTICLE_SPEED: float = 300.0
IMPACT_PARTICLE_LIFETIME: float = 0.3
IMPACT_SHAKE_AMOUNT: float = 1.5
IMPACT_SHAKE_DURATION: float = 0.04
IMPACT_HIT_PAUSE_FRAMES: int = 20
