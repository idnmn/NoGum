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
CAMERA_LERP_SPEED = 1.0 # Скорость движения камеры

# --- ГЕЙМПЛЕЙНЫЕ КОНСТАНТЫ ---
# Физика движения
PLAYER_MAX_SPEED: float = 500.0  # Пикселей в секунду
PLAYER_ACCELERATION: float = 1600.0
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
