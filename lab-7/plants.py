from time_of_day import TimeOfDay
from colors import (
    COL_LUMIERE,
    COL_LUMIERE_P,
    COL_OBSCURITE,
    COL_OBSCURITE_P,
    COL_DEMI,
    COL_DEMI_P,
)

FULL_SPREAD_CHANCE = 0.08
MILD_SPREAD_CHANCE = 0.05


class Plant:
    """Базовый класс растения с самоизменяющимся поведением."""

    def __init__(self, x, y):
        self.x, self.y = x, y
        self.active = False
        self.energy = 50
        self.spread_chance = 0.0
        self.color = (0, 200, 0)
        self.passive_color = (0, 80, 0)

    def update_behavior(self, tod):
        """Self-modifying: поведение меняется от времени суток."""

    def tick(self, tod):
        self.update_behavior(tod)
        if self.active:
            self.energy = min(100, self.energy + 3)
        else:
            self.energy = max(0, self.energy - 1)

    def get_color(self):
        return self.color if self.active else self.passive_color


class Lumiere(Plant):
    """Растёт при солнце (утро / день). При луне — не растёт."""

    def __init__(self, x, y):
        super().__init__(x, y)
        self.color = COL_LUMIERE
        self.passive_color = COL_LUMIERE_P

    def update_behavior(self, tod):
        if tod == TimeOfDay.DAY:
            self.active = True
            self.spread_chance = FULL_SPREAD_CHANCE
        elif tod == TimeOfDay.MORNING:
            self.active = True
            self.spread_chance = MILD_SPREAD_CHANCE
        else:
            self.active = False
            self.spread_chance = 0.0


class Obscurite(Plant):
    """Растёт при луне (вечер / ночь). При солнце — не растёт."""

    def __init__(self, x, y):
        super().__init__(x, y)
        self.color = COL_OBSCURITE
        self.passive_color = COL_OBSCURITE_P

    def update_behavior(self, tod):
        if tod == TimeOfDay.NIGHT:
            self.active = True
            self.spread_chance = FULL_SPREAD_CHANCE
        elif tod == TimeOfDay.EVENING:
            self.active = True
            self.spread_chance = MILD_SPREAD_CHANCE
        else:
            self.active = False
            self.spread_chance = 0.0


class Demi(Plant):
    """Растёт при низкой освещённости (утро / вечер)."""

    def __init__(self, x, y):
        super().__init__(x, y)
        self.color = COL_DEMI
        self.passive_color = COL_DEMI_P

    def update_behavior(self, tod):
        if tod in (TimeOfDay.MORNING, TimeOfDay.EVENING):
            self.active = True
            self.spread_chance = FULL_SPREAD_CHANCE
        else:
            self.active = False
            self.spread_chance = 0.0
