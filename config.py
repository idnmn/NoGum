# --- ЛОГИЧЕСКОЕ РАЗРЕШЕНИЕ ---
# Это размер холста на котором происходит вся физика и отрисовка игры.
INTERNAL_WIDTH: int = 1280
INTERNAL_HEIGHT: int = 720

# --- НАСТРОЙКИ ОКНА ---
FPS: int = 60
WINDOW_TITLE: str = "NoGum!"

# Режим отображения:
# True  -> Запуск на весь экран (автоматически под монитор)
# False -> Запуск в окне размером INTERNAL_WIDTH x INTERNAL_HEIGHT
FULLSCREEN: bool = False

# --- ГЕЙМПЛЕЙНЫЕ КОНСТАНТЫ ---
PLAYER_SPEED: float = 300.0  # Пикселей в секунду

# --- ЦВЕТА ---
BACKGROUND_COLOR: tuple[int, int, int] = (30, 30, 30)



# Размеры (в пикселях ВНУТРЕННЕГО разрешения)
PLAYER_SIZE: int = 48