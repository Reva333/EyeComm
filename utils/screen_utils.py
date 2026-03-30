from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT


def normalize_to_screen(x: float, y: float) -> tuple[int, int]:
    sx = int(x * SCREEN_WIDTH)
    sy = int(y * SCREEN_HEIGHT)
    sx = max(0, min(SCREEN_WIDTH - 1, sx))
    sy = max(0, min(SCREEN_HEIGHT - 1, sy))
    return sx, sy


def clamp_to_screen(x: int, y: int) -> tuple[int, int]:
    return (
        max(0, min(SCREEN_WIDTH - 1, x)),
        max(0, min(SCREEN_HEIGHT - 1, y))
    )


def screen_center() -> tuple[int, int]:
    return SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2