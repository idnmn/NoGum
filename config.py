import pygame

# --- ЛОГИЧЕСКОЕ РАЗРЕШЕНИЕ ---
# Это размер холста на котором происходит вся физика и отрисовка игры.
INTERNAL_WIDTH: int = 1248
INTERNAL_HEIGHT: int = 720

# --- НАСТРОЙКИ ОКНА ---
FPS: int = 500
WINDOW_TITLE: str = "NoGum!"

# Режим отображения:
# True  -> Запуск на весь экран (автоматически под монитор)
# False -> Запуск в окне размером INTERNAL_WIDTH x INTERNAL_HEIGHT
FULLSCREEN: bool = False

# --- ГЕЙМПЛЕЙНЫЕ КОНСТАНТЫ ---
# Физика движения
PLAYER_MAX_SPEED: float = 600.0  # Пикселей в секунду
PLAYER_ACCELERATION: float = 3000.0
FRICTION: float = 20.0
PLAYER_TILT_MAX_ANGLE: float = 20.0   # Максимальный угол наклона в градусах
PLAYER_TILT_SMOOTHING: float = 40.0    # Скорость плавного перехода к целевому углу
# Рывок
PLAYER_DASH_SPEED: float = 2000.0  # Скорость во время рывка
PLAYER_DASH_DURATION: float = 0.15  # Длительность
PLAYER_DASH_COOLDOWN: float = 5.0  # Кд между рывками

# баланс
LEVEL_COEF = 1.02 # коэффициент увеличения стат мобов в зависимости от уровня

# --- ЦВЕТА ---
BACKGROUND_COLOR: tuple[int, int, int] = (30, 30, 30)

# --- РАЗМЕРЫ (в пикселях ВНУТРЕННЕГО разрешения) ---
PLAYER_SIZE: int = 40

# Комната
ROOM_COLS = 26
ROOM_ROWS = 15
ROOM_SYMBOL_WALL = "*"
ROOM_SYMBOL_EMPTY = "0"
TILE_SIZE: int = 48
LAYOUTS_DIR: str = "room layouts"

# Генерация
MAX_ROOMS: int = 12  # Лимит комнат для завершения генерации

# --- UI КОНСТАНТЫ ---
UI_HP_MAX: int = 100
UI_HP_BAR_WIDTH: int = 200
UI_HP_BAR_HEIGHT: int = 50
UI_HP_COLOR: tuple[int, int, int] = (255, 255, 40)
UI_HP_BG_COLOR: tuple[int, int, int] = (45, 45, 20)
UI_TEXT_COLOR: tuple[int, int, int] = (255, 255, 255)

UI_DASH_BAR_WIDTH: int = 30
UI_DASH_BAR_HEIGHT: int = 4
UI_DASH_COLOR: tuple[int, int, int] = (115, 245, 155)
UI_DASH_BG_COLOR: tuple[int, int, int] = (50, 100, 70)
UI_DASH_OFFSET_Y: float = 20.0
UI_DASH_HIDE_DELAY: float = 1.0

CAMERA_LERP_SPEED = 2.7 # Скорость движения камеры

DRAW_PATH = False # debug отрисовщик для pathfinder'а

# Mini-Map
MINIMAP_WIDTH: int = 400
MINIMAP_HEIGHT: int = 400
MINIMAP_BG_COLOR: tuple[int, int, int, int] = (30, 30, 30, 200)
MINIMAP_ROOM_BG_COLOR: tuple[int, int, int] = (30, 30, 30)  # Пол комнат
MINIMAP_PLAYER_COLOR: tuple[int, int, int] = (165, 175, 60)
MINIMAP_BORDER_COLOR: tuple[int, int, int] = (40, 40, 40)

MINIMAP_WALL_COLOR_LIST: list[tuple[int, int, int]] = [
                                            (150, 80, 50),  # 1 seed
                                            (145, 50, 100), # 2
                                            (70, 100, 100), # 3
                                            (100, 90, 55),  # 4
                                            (105, 55, 105), # 5
                                            (50, 90, 60)    # 6
                                          ]
MINIMAP_EXPLORED: bool = False # отладочная функция для открытия всей миникарты сразу

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
