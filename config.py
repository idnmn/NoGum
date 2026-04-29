# --- ЛОГИЧЕСКОЕ РАЗРЕШЕНИЕ ---
# Это размер холста на котором происходит вся физика и отрисовка игры.
INTERNAL_WIDTH: int = 1280
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
PLAYER_ACCELERATION: float = 3000.0
PLAYER_FRICTION: float = 7.0
# Рывок
PLAYER_DASH_SPEED: float = 2000.0     # Скорость во время рывка
PLAYER_DASH_DURATION: float = 0.15   # Длительность
PLAYER_DASH_COOLDOWN: float = 1.0    # Кд между рывками

# --- ЦВЕТА ---
BACKGROUND_COLOR: tuple[int, int, int] = (30, 30, 30)



# Размеры (в пикселях ВНУТРЕННЕГО разрешения)
PLAYER_SIZE: int = 48