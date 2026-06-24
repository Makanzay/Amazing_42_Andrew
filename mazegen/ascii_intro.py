"""Small ASCII intro animation for terminal mode."""

import math
import sys
import threading
import time
from collections.abc import Callable
from typing import TypeVar

FRAME_WIDTH = 64
FRAME_HEIGHT = 22
FRAME_DELAY = 1 / 24
LUMINANCE_CHARS = ".,-~:;=!*#$@"
T = TypeVar("T")


def render_donut_frame(angle_a: float, angle_b: float) -> str:
    """Return one frame of a rotating ASCII torus."""
    output = [" "] * (FRAME_WIDTH * FRAME_HEIGHT)
    zbuffer = [0.0] * (FRAME_WIDTH * FRAME_HEIGHT)

    cos_a = math.cos(angle_a)
    sin_a = math.sin(angle_a)
    cos_b = math.cos(angle_b)
    sin_b = math.sin(angle_b)

    theta = 0.0
    while theta < 2 * math.pi:
        cos_theta = math.cos(theta)
        sin_theta = math.sin(theta)

        phi = 0.0
        while phi < 2 * math.pi:
            cos_phi = math.cos(phi)
            sin_phi = math.sin(phi)

            circle_x = 2 + cos_theta
            circle_y = sin_theta

            x = (
                circle_x * (cos_b * cos_phi + sin_a * sin_b * sin_phi)
                - circle_y * cos_a * sin_b
            )
            y = (
                circle_x * (sin_b * cos_phi - sin_a * cos_b * sin_phi)
                + circle_y * cos_a * cos_b
            )
            z = cos_a * circle_x * sin_phi + circle_y * sin_a + 5
            inverse_z = 1 / z

            screen_x = int(FRAME_WIDTH / 2 + 30 * inverse_z * x)
            screen_y = int(FRAME_HEIGHT / 2 - 15 * inverse_z * y)
            index = screen_x + FRAME_WIDTH * screen_y

            luminance = (
                cos_phi * cos_theta * sin_b
                - cos_a * cos_theta * sin_phi
                - sin_a * sin_theta
                + cos_b * (
                    cos_a * sin_theta
                    - cos_theta * sin_a * sin_phi
                )
            )

            if 0 <= screen_y < FRAME_HEIGHT and 0 <= screen_x < FRAME_WIDTH:
                if inverse_z > zbuffer[index]:
                    char_index = max(0, int(luminance * 8))
                    char_index = min(char_index, len(LUMINANCE_CHARS) - 1)
                    zbuffer[index] = inverse_z
                    output[index] = LUMINANCE_CHARS[char_index]

            phi += 0.08
        theta += 0.18

    lines = [
        "".join(output[row:row + FRAME_WIDTH])
        for row in range(0, len(output), FRAME_WIDTH)
    ]
    return "\n".join(lines)


def play_ascii_donut(duration: float = 3.0) -> None:
    """Display the ASCII donut intro when stdout is an interactive terminal."""
    if not sys.stdout.isatty():
        return

    start = time.monotonic()
    animate_ascii_donut_until(start, duration, lambda: False)


def run_with_ascii_donut(
    action: Callable[[], T],
    minimum_duration: float = 3.0,
) -> T:
    """Run an action while the ASCII donut stays animated."""
    if not sys.stdout.isatty():
        return action()

    result: list[T] = []
    errors: list[BaseException] = []

    def run_action() -> None:
        try:
            result.append(action())
        except BaseException as error:
            errors.append(error)

    worker = threading.Thread(target=run_action)
    start = time.monotonic()
    worker.start()
    animate_ascii_donut_until(start, minimum_duration, worker.is_alive)
    worker.join()

    if errors:
        raise errors[0]
    return result[0]


def animate_ascii_donut_until(
    start: float,
    minimum_duration: float,
    should_continue: Callable[[], bool],
) -> None:
    """Animate until the action is done and the minimum duration has passed."""
    angle_a = 0.0
    angle_b = 0.0

    sys.stdout.write("\033[?25l")
    try:
        while should_continue() or time.monotonic() - start < minimum_duration:
            sys.stdout.write("\033[2J\033[3J\033[H")
            sys.stdout.write(render_donut_frame(angle_a, angle_b))
            sys.stdout.write("\n\nGenerating maze...\n")
            sys.stdout.flush()

            angle_a += 0.07
            angle_b += 0.04
            time.sleep(FRAME_DELAY)
    finally:
        sys.stdout.write("\033[?25h\033[2J\033[H")
        sys.stdout.flush()
