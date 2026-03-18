"""
Симуляция экосистемы с самоизменяющимися классами.
Растения: Lumiere, Obscurite, Demi
Животные: Pauvre (травоядные), Malheureux (всеядные хищники)
"""

import pygame
import sys
from time_of_day import TIME_BG, TIME_LABEL_COL, TIME_LABELS
from animals import Pauvre, Malheureux
from colors import (
    COL_LUMIERE,
    COL_OBSCURITE,
    COL_DEMI,
    COL_PAUVRE,
    COL_MALHEUREUX,
)
from config import (
    GRID_W,
    GRID_H,
    CELL_SIZE,
    SIDEBAR_W,
    SCREEN_W,
    SCREEN_H,
    FPS,
    TICKS_PER_PHASE,
    RANDOM_SEED,
)
from world import World
import rng

rng.seed(RANDOM_SEED)


def _text(screen, font, text, x, y, color):
    screen.blit(font.render(str(text), True, color), (x, y))


def draw(screen, world, font, bfont):
    tod = world.time_of_day
    bg = TIME_BG[tod]

    for y in range(world.h):
        for x in range(world.w):
            r = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            p = world.grid[y][x]
            pygame.draw.rect(screen, p.get_color() if p else bg, r)
            pygame.draw.rect(screen, (50, 50, 50), r, 1)

    for a in world.animals:
        if not a.alive:
            continue
        cx = a.x * CELL_SIZE + CELL_SIZE // 2
        cy = a.y * CELL_SIZE + CELL_SIZE // 2
        rad = CELL_SIZE // 3
        pygame.draw.circle(screen, a.color, (cx, cy), rad)
        if a.sleeping:
            _text(screen, font, "z", cx + 2, cy - 12, (220, 220, 220))
        elif isinstance(a, Pauvre) and a.aggression > 0.5:
            pygame.draw.circle(screen, (255, 0, 0), (cx, cy), rad + 2, 2)

    sx = GRID_W * CELL_SIZE
    pygame.draw.rect(screen, (35, 35, 45), (sx, 0, SIDEBAR_W, SCREEN_H))
    y0 = 12

    _text(screen, bfont, "ECOSYSTEM SIM", sx + 10, y0, (255, 255, 255))
    y0 += 30

    _text(screen, bfont, TIME_LABELS[tod], sx + 10, y0, TIME_LABEL_COL[tod])
    y0 += 25
    _text(
        screen,
        font,
        f"Day {world.day}   Tick {world.tick_count}",
        sx + 10,
        y0,
        (180, 180, 180),
    )
    y0 += 20

    bw = 220
    pygame.draw.rect(screen, (60, 60, 70), (sx + 10, y0, bw, 8))
    pygame.draw.rect(
        screen,
        TIME_LABEL_COL[tod],
        (sx + 10, y0, int(bw * world.phase_tick / TICKS_PER_PHASE), 8),
    )
    y0 += 18

    pygame.draw.line(screen, (80, 80, 80), (sx + 10, y0), (sx + 280, y0))
    y0 += 10

    st = world.stats()

    _text(screen, bfont, "PLANTS", sx + 10, y0, (150, 255, 150))
    y0 += 22
    for name, col, key in [
        ("Lumiere", COL_LUMIERE, "lumiere"),
        ("Obscurite", COL_OBSCURITE, "obscurite"),
        ("Demi", COL_DEMI, "demi"),
    ]:
        pygame.draw.rect(screen, col, (sx + 10, y0, 12, 12))
        _text(screen, font, f"{name}: {st[key]}", sx + 28, y0 - 1, (220, 220, 220))
        y0 += 18
    y0 += 5

    pygame.draw.line(screen, (80, 80, 80), (sx + 10, y0), (sx + 280, y0))
    y0 += 10

    _text(screen, bfont, "ANIMALS", sx + 10, y0, (255, 200, 150))
    y0 += 22

    plist = [a for a in world.animals if isinstance(a, Pauvre)]
    mlist = [a for a in world.animals if isinstance(a, Malheureux)]

    pygame.draw.circle(screen, COL_PAUVRE, (sx + 16, y0 + 6), 6)
    _text(screen, font, f"Pauvre: {len(plist)}", sx + 28, y0 - 1, (180, 200, 255))
    y0 += 18
    if plist:
        ah = sum(a.hunger for a in plist) / len(plist)
        ae = sum(a.energy for a in plist) / len(plist)
        _text(
            screen,
            font,
            f"  hunger:{ah:.0f}  energy:{ae:.0f}",
            sx + 10,
            y0,
            (140, 160, 200),
        )
    y0 += 20

    pygame.draw.circle(screen, COL_MALHEUREUX, (sx + 16, y0 + 6), 6)
    _text(screen, font, f"Malheureux: {len(mlist)}", sx + 28, y0 - 1, (255, 180, 180))
    y0 += 18
    if mlist:
        ah = sum(a.hunger for a in mlist) / len(mlist)
        ae = sum(a.energy for a in mlist) / len(mlist)
        _text(
            screen,
            font,
            f"  hunger:{ah:.0f}  energy:{ae:.0f}",
            sx + 10,
            y0,
            (200, 140, 140),
        )
    y0 += 22

    pygame.draw.line(screen, (80, 80, 80), (sx + 10, y0), (sx + 280, y0))
    y0 += 10

    _text(screen, bfont, "POPULATION", sx + 10, y0, (200, 200, 200))
    y0 += 22

    gx, gy, gw, gh = sx + 10, y0, 270, 130
    pygame.draw.rect(screen, (25, 25, 35), (gx, gy, gw, gh))
    pygame.draw.rect(screen, (70, 70, 80), (gx, gy, gw, gh), 1)

    series = [
        ("lumiere", COL_LUMIERE),
        ("obscurite", COL_OBSCURITE),
        ("demi", COL_DEMI),
        ("pauvre", COL_PAUVRE),
        ("malheureux", COL_MALHEUREUX),
    ]
    all_vals = []
    for k, _ in series:
        all_vals.extend(world.history[k])
    mx = max(all_vals) if all_vals else 1
    mx = max(mx, 1)

    for key, color in series:
        data = list(world.history[key])
        if len(data) < 2:
            continue
        pts = []
        for i, v in enumerate(data):
            px = gx + int(i * gw / max(len(data) - 1, 1))
            py = gy + gh - int(v * (gh - 4) / mx) - 2
            pts.append((px, py))
        pygame.draw.lines(screen, color, False, pts, 2)

    y0 += gh + 10

    pygame.draw.line(screen, (80, 80, 80), (sx + 10, y0), (sx + 280, y0))
    y0 += 10
    _text(screen, bfont, "CONTROLS", sx + 10, y0, (200, 200, 200))
    y0 += 22

    tips = [
        "SPACE - pause",
        "+/- speed",
        "R - restart",
        "ESC - quit",
        "Right arrow/D - tick forward",
        "Left arrow/A - tick backwards",
    ]

    for line in tips:
        _text(screen, font, line, sx + 10, y0, (150, 150, 150))
        y0 += 16


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Ecosystem Simulation")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("arial", 14)
    bfont = pygame.font.SysFont("arial", 17, bold=True)

    world = World(GRID_W, GRID_H)
    world.init(density=0.2, n_pauvre=20, n_malh=10)

    paused = True
    speed = FPS

    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if ev.key == pygame.K_SPACE:
                    paused = not paused
                if ev.key in (pygame.K_PLUS, pygame.K_EQUALS, pygame.K_KP_PLUS):
                    speed = min(60, speed + 2)
                if ev.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                    speed = max(1, speed - 2)
                if ev.key == pygame.K_r:
                    world = World(GRID_W, GRID_H)
                    world.init()
                if ev.key == pygame.K_RIGHT or ev.key == pygame.K_d:
                    world.tick()
                if ev.key == pygame.K_LEFT or ev.key == pygame.K_a:
                    world.back_tick()

        if not paused:
            world.tick()

        screen.fill((30, 30, 30))
        draw(screen, world, font, bfont)
        pygame.display.flip()
        clock.tick(speed)


if __name__ == "__main__":
    main()
