from collections import deque
import copy
from plants import Lumiere, Obscurite, Demi
from animals import Animal, Pauvre, Malheureux
from time_of_day import TimeOfDay
from config import TICKS_PER_PHASE
import rng


class World:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.grid = [[None] * w for _ in range(h)]
        self.animals: list[Animal] = []
        self.new_animals: list[Animal] = []
        self.time_of_day = TimeOfDay.MORNING
        self.tick_count = 0
        self.day = 0
        self.phase_tick = 0
        self.history = {
            k: deque(maxlen=300)
            for k in ("lumiere", "obscurite", "demi", "pauvre", "malheureux")
        }
        self.state_history = deque(maxlen=300)

    def init(self, density=0.2, n_pauvre=20, n_malh=10):
        plant_types = [Lumiere, Obscurite, Demi]
        for y in range(self.h):
            for x in range(self.w):
                if rng.random() < density:
                    self.grid[y][x] = rng.choice(plant_types)(x, y)
        for _ in range(n_pauvre):
            self.animals.append(
                Pauvre(rng.randint(0, self.w - 1), rng.randint(0, self.h - 1))
            )
        for _ in range(n_malh):
            self.animals.append(
                Malheureux(rng.randint(0, self.w - 1), rng.randint(0, self.h - 1))
            )

    def tick(self):
        self.state_history.append(self._save_state())

        self.tick_count += 1
        self._advance_time()
        self.new_animals = []

        for y in range(self.h):
            for x in range(self.w):
                p = self.grid[y][x]
                if p:
                    p.tick(self.time_of_day)
                    if p.energy <= 0:
                        self.grid[y][x] = None

        rng.shuffle(self.animals)
        for a in self.animals:
            if a.alive:
                a.tick(self)
        self.animals.extend(self.new_animals)
        self.animals = [a for a in self.animals if a.alive]

        self._spread_plants()

        if rng.random() < 0.05:
            rx, ry = rng.randint(0, self.w - 1), rng.randint(0, self.h - 1)
            if self.grid[ry][rx] is None:
                self.grid[ry][rx] = rng.choice([Lumiere, Obscurite, Demi])(rx, ry)

        s = self.stats()
        for k in self.history:
            self.history[k].append(s[k])

    def back_tick(self):
        if not self.state_history:
            return

        state = self.state_history.pop()
        self._load_state(state)
        for k in self.history:
            if self.history[k]:
                self.history[k].pop()

    def _advance_time(self):
        self.phase_tick += 1
        if self.phase_tick >= TICKS_PER_PHASE:
            self.phase_tick = 0
            phases = list(TimeOfDay)
            i = (phases.index(self.time_of_day) + 1) % 4
            self.time_of_day = phases[i]
            if self.time_of_day == TimeOfDay.MORNING:
                self.day += 1

    def _spread_plants(self):
        spreads = []
        for y in range(self.h):
            for x in range(self.w):
                p = self.grid[y][x]
                if p and p.active and p.spread_chance > 0:
                    for dx, dy in ((0, 1), (0, -1), (1, 0), (-1, 0)):
                        nx, ny = x + dx, y + dy
                        if (
                            0 <= nx < self.w
                            and 0 <= ny < self.h
                            and rng.random() < p.spread_chance
                        ):
                            e = self.grid[ny][nx]
                            if e is None:
                                spreads.append((nx, ny, type(p)))
                            elif not e.active and rng.random() < 0.25:
                                spreads.append((nx, ny, type(p)))

        rng.shuffle(spreads)
        for nx, ny, cls in spreads:
            e = self.grid[ny][nx]
            if e is None or not e.active:
                self.grid[ny][nx] = cls(nx, ny)
                self.grid[ny][nx].update_behavior(self.time_of_day)

    def stats(self):
        lum = obs = dem = 0
        for y in range(self.h):
            for x in range(self.w):
                p = self.grid[y][x]
                if isinstance(p, Lumiere):
                    lum += 1
                elif isinstance(p, Obscurite):
                    obs += 1
                elif isinstance(p, Demi):
                    dem += 1
        pv = sum(1 for a in self.animals if isinstance(a, Pauvre))
        ml = sum(1 for a in self.animals if isinstance(a, Malheureux))
        return {
            "lumiere": lum,
            "obscurite": obs,
            "demi": dem,
            "pauvre": pv,
            "malheureux": ml,
        }

    def _save_state(self):
        return {
            "grid": copy.deepcopy(self.grid),
            "animals": copy.deepcopy(self.animals),
            "time_of_day": self.time_of_day,
            "tick_count": self.tick_count,
            "day": self.day,
            "phase_tick": self.phase_tick,
            "rng_state": rng.getstate(),
        }

    def _load_state(self, state):
        self.grid = state["grid"]
        self.animals = state["animals"]
        self.time_of_day = state["time_of_day"]
        self.tick_count = state["tick_count"]
        self.phase_tick = state["phase_tick"]
        self.day = state["day"]

        rng.setstate(state["rng_state"])
