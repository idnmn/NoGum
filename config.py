# --- ЛОГИЧЕСКОЕ РАЗРЕШЕНИЕ ---
# Это размер холста на котором происходит вся физика и отрисовка игры.
INTERNAL_WIDTH: int = 1248
INTERNAL_HEIGHT: int = 720

# --- НАСТРОЙКИ ОКНА ---
FPS: int = 144
WINDOW_TITLE: str = "NoGum!"

# Режим отображения:
# True  -> Запуск на весь экран (автоматически под монитор)
# False -> Запуск в окне размером INTERNAL_WIDTH x INTERNAL_HEIGHT
FULLSCREEN: bool = False

# --- ГЕЙМПЛЕЙНЫЕ КОНСТАНТЫ ---
# Физика движения
PLAYER_MAX_SPEED: float = 600.0  # Пикселей в секунду
PLAYER_ACCELERATION: float = 2500.0
PLAYER_FRICTION: float = 15.0
# Рывок
PLAYER_DASH_SPEED: float = 2000.0  # Скорость во время рывка
PLAYER_DASH_DURATION: float = 0.15  # Длительность
PLAYER_DASH_COOLDOWN: float = 5.0  # Кд между рывками

# --- ЦВЕТА ---
BACKGROUND_COLOR: tuple[int, int, int] = (30, 30, 30)

# --- РАЗМЕРЫ (в пикселях ВНУТРЕННЕГО разрешения) ---
PLAYER_SIZE: int = 32

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
UI_HP_BAR_HEIGHT: int = 24
UI_HP_COLOR: tuple[int, int, int] = (220, 50, 50)
UI_HP_BG_COLOR: tuple[int, int, int] = (60, 20, 20)
UI_TEXT_COLOR: tuple[int, int, int] = (255, 255, 255)

UI_DASH_BAR_WIDTH: int = 30
UI_DASH_BAR_HEIGHT: int = 4
UI_DASH_COLOR: tuple[int, int, int] = (60, 120, 255)
UI_DASH_BG_COLOR: tuple[int, int, int] = (20, 40, 80)
UI_DASH_OFFSET_Y: float = 20.0
UI_DASH_HIDE_DELAY: float = 1.0

CAMERA_LERP_SPEED = 1.7 # Скорость движения камеры

# Mini-Map
MINIMAP_WIDTH: int = 400
MINIMAP_HEIGHT: int = 400
MINIMAP_PADDING: int = 20
MINIMAP_BG_COLOR: tuple[int, int, int, int] = (30, 30, 30, 200)
MINIMAP_ROOM_BG_COLOR: tuple[int, int, int] = (30, 30, 30)  # Пол комнат
MINIMAP_WALL_COLOR: tuple[int, int, int] = (200, 200, 200)  # Стены
MINIMAP_PLAYER_COLOR: tuple[int, int, int] = (255, 210, 60)
MINIMAP_BORDER_COLOR: tuple[int, int, int] = (40, 40, 60)

