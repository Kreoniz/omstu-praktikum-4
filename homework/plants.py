from time_of_day import TimeOfDay
from colors import (
    COL_LUMIERE,
    COL_LUMIERE_P,
    COL_OBSCURITE,
    COL_OBSCURITE_P,
    COL_DEMI,
    COL_DEMI_P,
)
from ecosystem import EcosystemMeta
import rng

FULL_SPREAD_CHANCE = 0.08
MILD_SPREAD_CHANCE = 0.05


class PlantMeta(EcosystemMeta):
    """
    Метакласс растений.

    DSL-атрибуты, читаемые из namespace класса:
        _active_times   : dict[TimeOfDay, float]   — фаза → шанс распространения
        _color_active   : tuple                     — цвет активного состояния
        _color_passive  : tuple                     — цвет пассивного состояния

    Автоматически генерирует:
        update_behavior(tod) — переключает active / spread_chance
        get_color()          — возвращает текущий цвет
        spread(world)        — список (x, y, cls) для распространения
    """

    def __new__(mcs, name, bases, namespace):
        if bases and not namespace.get("_abstract", False):
            active_times = namespace.get("_active_times", {})
            ca = namespace.get("_color_active", (0, 200, 0))
            cp = namespace.get("_color_passive", (0, 80, 0))
            injected = []

            if "update_behavior" not in namespace and active_times:
                _at = dict(active_times)

                def _make_ub(at_map):
                    def update_behavior(self, tod):
                        if tod in at_map:
                            self.active = True
                            self.spread_chance = at_map[tod]
                        else:
                            self.active = False
                            self.spread_chance = 0.0

                    return update_behavior

                namespace["update_behavior"] = _make_ub(_at)
                injected.append("update_behavior")

            if "get_color" not in namespace:

                def _make_gc(c_act, c_pas):
                    def get_color(self):
                        return c_act if self.active else c_pas

                    return get_color

                namespace["get_color"] = _make_gc(ca, cp)
                injected.append("get_color")

            if "spread" not in namespace:

                def spread(self, world):
                    if not self.active or self.spread_chance <= 0:
                        return []
                    results = []
                    for dx, dy in ((0, 1), (0, -1), (1, 0), (-1, 0)):
                        nx, ny = self.x + dx, self.y + dy
                        if 0 <= nx < world.w and 0 <= ny < world.h:
                            if rng.random() < self.spread_chance:
                                existing = world.grid[ny][nx]
                                if existing is None:
                                    results.append((nx, ny, type(self)))
                                elif not existing.active and rng.random() < 0.25:
                                    results.append((nx, ny, type(self)))
                    return results

                namespace["spread"] = spread
                injected.append("spread")

            if injected:
                print(f"  [PlantMeta] → {name}: инжектированы {injected}")

        return super().__new__(mcs, name, bases, namespace)


class Plant(metaclass=PlantMeta):
    """Базовый класс растения (абстрактный — не регистрируется)."""

    _abstract = True

    def __init__(self, x, y):
        self.x, self.y = x, y
        self.active = False
        self.energy = 50
        self.spread_chance = 0.0

    def update_behavior(self, tod):
        pass

    def get_color(self):
        return (0, 200, 0)

    def tick(self, tod):
        self.update_behavior(tod)
        self.energy += 3 if self.active else -1
        self.energy = max(0, min(100, self.energy))

    def spread(self, world):
        return []


class Lumiere(Plant):
    """Растёт при солнце (утро / день)."""

    _active_times = {TimeOfDay.DAY: 0.08, TimeOfDay.MORNING: 0.05}
    _color_active = COL_LUMIERE
    _color_passive = COL_LUMIERE_P


class Obscurite(Plant):
    """Растёт при луне (вечер / ночь)."""

    _active_times = {TimeOfDay.NIGHT: 0.08, TimeOfDay.EVENING: 0.05}
    _color_active = COL_OBSCURITE
    _color_passive = COL_OBSCURITE_P


class Demi(Plant):
    """Растёт при низкой освещённости (утро / вечер)."""

    _active_times = {TimeOfDay.MORNING: 0.08, TimeOfDay.EVENING: 0.08}
    _color_active = COL_DEMI
    _color_passive = COL_DEMI_P
