"""
Симуляция экосистемы с самоизменяющимися классами.
Растения: Lumiere, Obscurite, Demi
Животные: Pauvre (травоядные), Malheureux (всеядные хищники)
"""

import pygame
import sys
from time_of_day import TIME_BG, TIME_LABEL_COL, TIME_LABELS
from config import (
    GRID_W,
    GRID_H,
    CELL_SIZE,
    SIDEBAR_W,
    SCREEN_W,
    SCREEN_H,
    FPS,
    TOP_BAR_H,
    BOTTOM_BAR_H,
    MAP_OFFSET_Y,
    RANDOM_SEED,
)
from slider import PygameSlider
from world import World
from ecosystem import EcosystemMeta
from tests import run_tests
import rng

rng.seed(RANDOM_SEED)


def _text(screen, font, text, x, y, color):
    screen.blit(font.render(str(text), True, color), (x, y))


def draw_frame(
    screen, world, snap, font, bfont, slider, hovered, mouse_pos, follow_live
):
    """Отрисовка: верх (слайдер) + карта + сайдбар + низ (статистика)."""

    tod = snap.time_of_day if snap else world.time_of_day
    bg = TIME_BG[tod]

    pygame.draw.rect(screen, (30, 30, 40), (0, 0, SCREEN_W, TOP_BAR_H))
    _text(screen, bfont, "Tick:", 10, 16, (180, 180, 180))
    slider.draw(screen, font)

    tick_n = snap.tick if snap else 0
    day_n = snap.day if snap else 0
    _text(screen, font, f"Tick {tick_n}   Day {day_n}", 740, 8, (180, 180, 180))
    _text(screen, bfont, TIME_LABELS[tod], 740, 26, TIME_LABEL_COL[tod])

    lbl = ">> LIVE" if follow_live else "|| HISTORY"
    lcol = (100, 255, 100) if follow_live else (255, 200, 100)
    _text(screen, bfont, lbl, 900, 16, lcol)

    if snap:
        for y in range(snap.h):
            for x in range(snap.w):
                r = pygame.Rect(
                    x * CELL_SIZE, MAP_OFFSET_Y + y * CELL_SIZE, CELL_SIZE, CELL_SIZE
                )
                c = snap.grid_colors[y][x]
                pygame.draw.rect(screen, c if c else bg, r)
                pygame.draw.rect(screen, (50, 50, 50), r, 1)

        for ad in snap.animals_data:
            cx = ad["x"] * CELL_SIZE + CELL_SIZE // 2
            cy = MAP_OFFSET_Y + ad["y"] * CELL_SIZE + CELL_SIZE // 2
            base = CELL_SIZE // 4
            rad = max(3, int(base * (1 + ad["energy"] / 100.0)))
            pygame.draw.circle(screen, ad["color"], (cx, cy), rad)
            if ad["sleeping"]:
                _text(screen, font, "z", cx + 3, cy - 13, (220, 220, 220))
            elif ad["type"] == "Pauvre" and ad.get("aggression", 0) > 0.5:
                pygame.draw.circle(screen, (255, 0, 0), (cx, cy), rad + 2, 2)

        if hovered:
            cx = hovered["x"] * CELL_SIZE + CELL_SIZE // 2
            cy = MAP_OFFSET_Y + hovered["y"] * CELL_SIZE + CELL_SIZE // 2
            vr_px = hovered["vision_radius"] * CELL_SIZE
            vis = pygame.Surface((vr_px * 2, vr_px * 2), pygame.SRCALPHA)
            pygame.draw.circle(vis, (100, 200, 255, 40), (vr_px, vr_px), vr_px)
            pygame.draw.circle(vis, (100, 200, 255, 130), (vr_px, vr_px), vr_px, 2)
            screen.blit(vis, (cx - vr_px, cy - vr_px))

            for a2 in snap.animals_data:
                if a2 is hovered:
                    continue
                if (
                    abs(a2["x"] - hovered["x"]) <= hovered["vision_radius"]
                    and abs(a2["y"] - hovered["y"]) <= hovered["vision_radius"]
                ):
                    ax = a2["x"] * CELL_SIZE + CELL_SIZE // 2
                    ay = MAP_OFFSET_Y + a2["y"] * CELL_SIZE + CELL_SIZE // 2
                    pygame.draw.circle(
                        screen, (255, 255, 100), (ax, ay), CELL_SIZE // 2, 2
                    )

    sx = GRID_W * CELL_SIZE
    sy = MAP_OFFSET_Y
    sh = GRID_H * CELL_SIZE
    pygame.draw.rect(screen, (35, 35, 45), (sx, sy, SIDEBAR_W, sh))
    y0 = sy + 10

    _text(screen, bfont, "ECOSYSTEM  (HW)", sx + 10, y0, (255, 255, 255))
    y0 += 28

    reg = EcosystemMeta.get_registry()
    _text(screen, bfont, f"Registry ({len(reg)})", sx + 10, y0, (180, 255, 180))
    y0 += 20
    for cname in reg:
        c = (
            (100, 200, 100)
            if cname in ("Lumiere", "Obscurite", "Demi")
            else (200, 140, 140)
        )
        _text(screen, font, f"  * {cname}", sx + 10, y0, c)
        y0 += 15
    y0 += 6
    pygame.draw.line(screen, (80, 80, 80), (sx + 10, y0), (sx + 280, y0))
    y0 += 8

    if snap:
        st = snap.stats_data

        _text(screen, bfont, "PLANTS", sx + 10, y0, (150, 255, 150))
        y0 += 20
        for name, col, key in [
            ("Lumiere", (255, 220, 50), "lumiere"),
            ("Obscurite", (140, 40, 200), "obscurite"),
            ("Demi", (30, 200, 80), "demi"),
        ]:
            pygame.draw.rect(screen, col, (sx + 10, y0, 12, 12))
            _text(
                screen,
                font,
                f"{name}: {st.get(key, 0)}",
                sx + 28,
                y0 - 1,
                (220, 220, 220),
            )
            y0 += 17
        y0 += 6
        pygame.draw.line(screen, (80, 80, 80), (sx + 10, y0), (sx + 280, y0))
        y0 += 8

        _text(screen, bfont, "ANIMALS", sx + 10, y0, (255, 200, 150))
        y0 += 20

        pygame.draw.circle(screen, (60, 130, 255), (sx + 16, y0 + 6), 6)
        _text(
            screen, font, f"Pauvre: {st.get('pauvre', 0)}", sx + 28, y0, (180, 200, 255)
        )
        y0 += 16
        _text(
            screen,
            font,
            f"  vis:{st.get('pauvre_avg_vr', 0):.1f}"
            f"  H:{st.get('pauvre_avg_hunger', 0):.0f}"
            f"  E:{st.get('pauvre_avg_energy', 0):.0f}",
            sx + 10,
            y0,
            (140, 160, 200),
        )
        y0 += 20

        pygame.draw.circle(screen, (255, 60, 60), (sx + 16, y0 + 6), 6)
        _text(
            screen,
            font,
            f"Malheureux: {st.get('malheureux', 0)}",
            sx + 28,
            y0,
            (255, 180, 180),
        )
        y0 += 16
        _text(
            screen,
            font,
            f"  vis:{st.get('malh_avg_vr', 0):.1f}"
            f"  H:{st.get('malh_avg_hunger', 0):.0f}"
            f"  E:{st.get('malh_avg_energy', 0):.0f}",
            sx + 10,
            y0,
            (200, 140, 140),
        )
        y0 += 22
        pygame.draw.line(screen, (80, 80, 80), (sx + 10, y0), (sx + 280, y0))
        y0 += 8

    _text(screen, bfont, "POPULATION", sx + 10, y0, (200, 200, 200))
    y0 += 20
    gx, gy, gw, gh = sx + 10, y0, 270, min(140, sh - (y0 - sy) - 10)
    if gh > 30:
        pygame.draw.rect(screen, (25, 25, 35), (gx, gy, gw, gh))
        pygame.draw.rect(screen, (70, 70, 80), (gx, gy, gw, gh), 1)
        series = [
            ("lumiere", (255, 220, 50)),
            ("obscurite", (140, 40, 200)),
            ("demi", (30, 200, 80)),
            ("pauvre", (60, 130, 255)),
            ("malheureux", (255, 60, 60)),
        ]
        avals = []
        for k, _ in series:
            avals.extend(world.history[k])
        mx_v = max(avals) if avals else 1
        mx_v = max(mx_v, 1)

        for key, color in series:
            data = list(world.history[key])
            if len(data) < 2:
                continue
            pts = []
            for i, v in enumerate(data):
                px = gx + int(i * gw / max(len(data) - 1, 1))
                py = gy + gh - int(v * (gh - 4) / mx_v) - 2
                pts.append((px, py))
            pygame.draw.lines(screen, color, False, pts, 2)

        if snap and world.snapshots:
            hlen = len(list(world.history.values())[0])
            if hlen > 1:
                latest = world.tick_count
                earliest = latest - hlen + 1
                if snap.tick >= earliest:
                    frac = (snap.tick - earliest) / max(1, hlen - 1)
                    ix = gx + int(frac * gw)
                    pygame.draw.line(
                        screen, (255, 255, 255), (ix, gy), (ix, gy + gh), 1
                    )

    y0 += 20
    _text(screen, bfont, "CONTROLS", sx + 10, y0 + gh, (200, 200, 200))
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
        _text(screen, font, line, sx + 10, y0 + gh, (150, 150, 150))
        y0 += 16
    y0 += gh + 30

    by_start = MAP_OFFSET_Y + GRID_H * CELL_SIZE
    pygame.draw.rect(screen, (28, 28, 38), (0, by_start, SCREEN_W, BOTTOM_BAR_H))
    pygame.draw.line(screen, (80, 80, 80), (0, by_start), (SCREEN_W, by_start))
    by = by_start + 6
    _text(screen, bfont, "STATISTICS", 10, by, (200, 200, 200))
    by += 20

    if snap:
        st = snap.stats_data
        _text(
            screen,
            font,
            f"Pauvre: {st.get('pauvre', 0)}  |  avg vis: {
                st.get('pauvre_avg_vr', 0):.1f}"
            f"  |  avg hunger: {st.get('pauvre_avg_hunger', 0):.0f}"
            f"  |  avg energy: {st.get('pauvre_avg_energy', 0):.0f}",
            10,
            by,
            (180, 200, 255),
        )
        by += 17
        _text(
            screen,
            font,
            f"Malheureux: {st.get('malheureux', 0)}  |  avg vis: {
                st.get('malh_avg_vr', 0):.1f}"
            f"  |  avg hunger: {st.get('malh_avg_hunger', 0):.0f}"
            f"  |  avg energy: {st.get('malh_avg_energy', 0):.0f}",
            10,
            by,
            (255, 180, 180),
        )
        by += 17
        tp = st.get("lumiere", 0) + st.get("obscurite", 0) + st.get("demi", 0)
        _text(
            screen,
            font,
            f"Lumiere: {st.get('lumiere', 0)}   Obscurite: {st.get('obscurite', 0)}"
            f"   Demi: {st.get('demi', 0)}   |   Total plants: {tp}",
            10,
            by,
            (150, 255, 150),
        )
        by += 17

        if hovered:
            nb = sum(
                1
                for a2 in snap.animals_data
                if a2 is not hovered
                and abs(a2["x"] - hovered["x"]) <= hovered["vision_radius"]
                and abs(a2["y"] - hovered["y"]) <= hovered["vision_radius"]
            )
            sl = " [sleep]" if hovered["sleeping"] else ""
            _text(
                screen,
                font,
                f">> {hovered['type']} @ ({hovered['x']},{hovered['y']})"
                f"  H:{hovered['hunger']}  E:{hovered['energy']}"
                f"  Vis:{hovered['vision_radius']}  Age:{hovered['age']}"
                f"  Neighbors:{nb}{sl}",
                10,
                by,
                (255, 255, 100),
            )

    if hovered and snap:
        mx, my = mouse_pos
        nb = sum(
            1
            for a2 in snap.animals_data
            if a2 is not hovered
            and abs(a2["x"] - hovered["x"]) <= hovered["vision_radius"]
            and abs(a2["y"] - hovered["y"]) <= hovered["vision_radius"]
        )
        lines = [
            hovered["type"],
            f"Pos: ({hovered['x']}, {hovered['y']})",
            f"Hunger: {hovered['hunger']}   Energy: {hovered['energy']}",
            f"Vision: {hovered['vision_radius']}   Age: {hovered['age']}",
            f"Neighbors: {nb}",
            "Sleeping" if hovered["sleeping"] else "Active",
        ]
        tw, th = 230, len(lines) * 16 + 10
        tx = min(mx + 15, SCREEN_W - tw - 5)
        ty = max(5, min(my - th - 5, SCREEN_H - th - 5))
        tip = pygame.Surface((tw, th), pygame.SRCALPHA)
        tip.fill((15, 15, 25, 220))
        screen.blit(tip, (tx, ty))
        pygame.draw.rect(screen, (140, 140, 200), (tx, ty, tw, th), 1)
        for i, ln in enumerate(lines):
            _text(screen, font, ln, tx + 6, ty + 5 + i * 16, (220, 220, 220))


def main():
    print("\n=== Реестр EcosystemMeta ===")
    for name, cls in EcosystemMeta.get_registry().items():
        base = cls.__bases__[0].__name__
        injected = []
        for m in (
            "update_behavior",
            "spread",
            "get_color",
            "eat",
            "hunt",
            "move_toward_food",
            "reproduce",
            "_is_sleeping",
            "count_nearby",
        ):
            if m in cls.__dict__:
                injected.append(m)
        print(f"  {name} ({base}) → injected: {injected}")
    print()

    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Ecosystem Simulation")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("arial", 14)
    bfont = pygame.font.SysFont("arial", 17, bold=True)

    world = World(GRID_W, GRID_H)
    world.init(density=0.2, n_pauvre=20, n_malh=10)

    slider = PygameSlider(120, 18, 600, 14, 0, 0)
    paused = True
    follow_live = True

    render_clock = pygame.time.Clock()
    render_fps = 60

    sim_speed = FPS
    sim_step = 1.0 / sim_speed
    sim_accumulator = 0.0

    while True:
        dt = render_clock.tick(render_fps) / 1000.0

        mouse_pos = pygame.mouse.get_pos()

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
                    follow_live = True
                if ev.key in (pygame.K_PLUS, pygame.K_EQUALS, pygame.K_KP_PLUS):
                    sim_speed = min(60, sim_speed + 2)
                    sim_step = 1.0 / sim_speed
                if ev.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                    sim_speed = max(1, sim_speed - 2)
                    sim_step = 1.0 / sim_speed
                if ev.key == pygame.K_r:
                    world = World(GRID_W, GRID_H)
                    world.init()
                if ev.key == pygame.K_RIGHT or ev.key == pygame.K_d:
                    world.tick()
                    follow_live = True
                if ev.key == pygame.K_LEFT or ev.key == pygame.K_a:
                    world.back_tick()
                    follow_live = False
                if ev.key == pygame.K_r:
                    world = World(GRID_W, GRID_H)
                    world.init()
                    follow_live = True
                if ev.key == pygame.K_l:
                    follow_live = True

            changed = slider.handle_event(ev)
            if changed and slider.dragging:
                follow_live = False
            if (
                ev.type == pygame.MOUSEBUTTONUP
                and ev.button == 1
                and not slider.dragging
                and slider.value >= slider.max_val
            ):
                follow_live = True

        if not paused:
            sim_accumulator += dt
            while sim_accumulator >= sim_step:
                world.tick()
                sim_accumulator -= sim_step

        slider.max_val = max(0, len(world.snapshots) - 1) if world.snapshots else 0
        slider.value = max(0, min(slider.value, slider.max_val))
        if follow_live and world.snapshots:
            slider.value = slider.max_val

        snap = world.snapshots[slider.value] if world.snapshots else None

        hovered = None
        mx, my = mouse_pos
        if (
            snap
            and 0 <= mx < GRID_W * CELL_SIZE
            and MAP_OFFSET_Y <= my < MAP_OFFSET_Y + GRID_H * CELL_SIZE
        ):
            for ad in snap.animals_data:
                acx = ad["x"] * CELL_SIZE + CELL_SIZE // 2
                acy = MAP_OFFSET_Y + ad["y"] * CELL_SIZE + CELL_SIZE // 2
                if ((mx - acx) ** 2 + (my - acy) ** 2) ** 0.5 < CELL_SIZE // 2:
                    hovered = ad
                    break

        screen.fill((30, 30, 30))
        draw_frame(
            screen, world, snap, font, bfont, slider, hovered, mouse_pos, follow_live
        )
        pygame.display.flip()
        clock.tick(render_fps)


if __name__ == "__main__":
    if "--test" in sys.argv:
        success = run_tests()
        sys.exit(0 if success else 1)
    else:
        main()
