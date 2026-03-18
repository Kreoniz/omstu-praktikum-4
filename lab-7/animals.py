import types
from config import GRID_W, GRID_H
from plants import Lumiere, Obscurite, Demi
from time_of_day import TimeOfDay
from colors import COL_PAUVRE, COL_MALHEUREUX
import rng


class Animal:
    """Базовый класс животного с self-modifying поведением."""

    def __init__(self, x, y):
        self.x, self.y = x, y
        self.hunger = 20
        self.energy = 80
        self.age = 0
        self.alive = True
        self.sleeping = False
        self.aggression = 0.0
        self.repro_cd = 0
        self.speed = 1
        self.color = (255, 255, 255)

    def act(self, world):
        pass

    def move_towards(self, tx, ty):
        dx = 1 if tx > self.x else -1 if tx < self.x else 0
        dy = 1 if ty > self.y else -1 if ty < self.y else 0
        nx, ny = self.x + dx, self.y + dy
        if 0 <= nx < GRID_W and 0 <= ny < GRID_H:
            self.x, self.y = nx, ny

    def move_random(self):
        dx, dy = rng.choice([(0, 1), (0, -1), (1, 0), (-1, 0), (0, 0)])
        nx, ny = self.x + dx, self.y + dy
        if 0 <= nx < GRID_W and 0 <= ny < GRID_H:
            self.x, self.y = nx, ny

    def _count_nearby(self, world, cls, radius):
        return sum(
            1
            for a in world.animals
            if isinstance(a, cls)
            and a.alive
            and a is not self
            and abs(a.x - self.x) <= radius
            and abs(a.y - self.y) <= radius
        )

    def tick(self, world):
        self.age += 1
        self.hunger = min(100, self.hunger + 1)
        if self.repro_cd > 0:
            self.repro_cd -= 1
        if self.hunger >= 95:
            self.energy -= 5
        if self.energy <= 0:
            self.alive = False
            return
        self._update_behavior(world)
        self.act(world)

    def _update_behavior(self, world):
        pass


class Pauvre(Animal):
    """
    Травоядные — едят Lumiere.
    • Утром едят много, вечером почти не едят.
    • Формируют группы; при перенаселении — распадаются.
    • Голод повышает агрессию (могут атаковать сородичей).
    • Спят ночью.
    • Размножаются внутри групп.
    """

    def __init__(self, x, y):
        super().__init__(x, y)
        self.color = COL_PAUVRE
        self.eat_amount = 25

    def _update_behavior(self, world):
        tod = world.time_of_day

        if tod == TimeOfDay.NIGHT:
            self.sleeping = True
            self.act = types.MethodType(Pauvre._act_sleep, self)
            return

        self.sleeping = False

        self.eat_amount = {
            TimeOfDay.MORNING: 35,
            TimeOfDay.DAY: 25,
            TimeOfDay.EVENING: 10,
        }.get(tod, 20)

        self.aggression = max(0.0, (self.hunger - 40) / 60.0)

        nearby = self._count_nearby(world, Pauvre, 3)

        if self.hunger > 75:
            self.act = types.MethodType(Pauvre._act_aggressive, self)
        elif self.hunger > 45:
            self.act = types.MethodType(Pauvre._act_hungry, self)
        elif nearby < 2:
            self.act = types.MethodType(Pauvre._act_seek_group, self)
        elif nearby > 6:
            self.act = types.MethodType(Pauvre._act_disperse, self)
        else:
            self.act = types.MethodType(Pauvre._act_normal, self)

    def _act_sleep(self, world):
        self.energy = min(100, self.energy + 2)

    def _act_normal(self, world):
        if isinstance(world.grid[self.y][self.x], Lumiere):
            self._eat(world)
        else:
            t = self._find_food(world, 7)
            if t:
                self.move_towards(*t)
            else:
                self.move_random()
        self._try_repro(world)

    def _act_hungry(self, world):
        if isinstance(world.grid[self.y][self.x], Lumiere):
            self._eat(world)
        else:
            t = self._find_food(world, 10)
            if t:
                self.move_towards(*t)
                self.move_towards(*t)
            else:
                self.move_random()

    def _act_aggressive(self, world):
        if isinstance(world.grid[self.y][self.x], Lumiere):
            self._eat(world)
            return

        if rng.random() < self.aggression * 0.2:
            for a in world.animals:
                if (
                    isinstance(a, Pauvre)
                    and a.alive
                    and a is not self
                    and abs(a.x - self.x) <= 1
                    and abs(a.y - self.y) <= 1
                    and a.energy < self.energy
                ):
                    a.energy -= 25
                    self.hunger = max(0, self.hunger - 15)
                    break
        t = self._find_food(world, 12)
        if t:
            self.move_towards(*t)
        else:
            self.move_random()

    def _act_seek_group(self, world):
        nearest, md = None, 999
        for a in world.animals:
            if isinstance(a, Pauvre) and a.alive and a is not self:
                d = abs(a.x - self.x) + abs(a.y - self.y)
                if d < md:
                    md, nearest = d, a
        if nearest and md > 2:
            self.move_towards(nearest.x, nearest.y)
        elif isinstance(world.grid[self.y][self.x], Lumiere):
            self._eat(world)
        else:
            self.move_random()
        self._try_repro(world)

    def _act_disperse(self, world):
        self.move_random()
        self.move_random()
        if isinstance(world.grid[self.y][self.x], Lumiere):
            self._eat(world)

    def _eat(self, world):
        self.hunger = max(0, self.hunger - self.eat_amount)
        self.energy = min(100, self.energy + 10)
        world.grid[self.y][self.x] = None

    def _find_food(self, world, r):
        best, md = None, 999
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                nx, ny = self.x + dx, self.y + dy
                if 0 <= nx < GRID_W and 0 <= ny < GRID_H:
                    if isinstance(world.grid[ny][nx], Lumiere):
                        d = abs(dx) + abs(dy)
                        if d < md:
                            md, best = d, (nx, ny)
        return best

    def _try_repro(self, world):
        if self.repro_cd > 0 or self.hunger > 50 or self.energy < 50 or self.age < 15:
            return
        for a in world.animals:
            if (
                isinstance(a, Pauvre)
                and a.alive
                and a is not self
                and abs(a.x - self.x) <= 2
                and abs(a.y - self.y) <= 2
                and a.repro_cd <= 0
                and a.hunger < 50
            ):
                if rng.random() < 0.08:
                    world.new_animals.append(Pauvre(self.x, self.y))
                    self.repro_cd = 20
                    a.repro_cd = 20
                    self.energy -= 20
                    break


class Malheureux(Animal):
    """
    Всеядные охотники — едят Demi, Obscurite и Pauvre.
    • Активны утром и вечером; спят днём и ночью.
    • Медлительны при голоде.
    • Образуют стаи; большие стаи охотятся эффективнее.
    • Размножаются между стаями.
    """

    def __init__(self, x, y):
        super().__init__(x, y)
        self.color = COL_MALHEUREUX
        self.speed = 1

    def _update_behavior(self, world):
        tod = world.time_of_day

        if tod in (TimeOfDay.DAY, TimeOfDay.NIGHT):
            self.sleeping = True
            self.act = types.MethodType(Malheureux._act_sleep, self)
            return

        self.sleeping = False
        self.speed = 1 if self.hunger > 60 else 2

        pack = self._count_nearby(world, Malheureux, 4)

        if pack >= 4:
            self.act = types.MethodType(Malheureux._act_pack_hunt, self)
        elif self.hunger > 50:
            self.act = types.MethodType(Malheureux._act_hunt, self)
        else:
            self.act = types.MethodType(Malheureux._act_wander, self)

    def _act_sleep(self, world):
        self.energy = min(100, self.energy + 3)

    def _act_wander(self, world):
        if isinstance(world.grid[self.y][self.x], (Demi, Obscurite)):
            self._eat_plant(world)
        else:
            self.move_random()
        self._try_repro(world)

    def _act_hunt(self, world):
        prey = self._find_prey(world, 8)
        if prey:
            self.move_towards(prey.x, prey.y)
            if abs(prey.x - self.x) <= 1 and abs(prey.y - self.y) <= 1:
                self._attack(prey)
        elif isinstance(world.grid[self.y][self.x], (Demi, Obscurite)):
            self._eat_plant(world)
        else:
            t = self._find_plant(world, 6)
            if t:
                self.move_towards(*t)
            else:
                self.move_random()

    def _act_pack_hunt(self, world):
        prey = self._find_prey(world, 12)
        if prey:
            for _ in range(self.speed):
                self.move_towards(prey.x, prey.y)
            if abs(prey.x - self.x) <= 1 and abs(prey.y - self.y) <= 1:
                self._attack(prey)
        elif isinstance(world.grid[self.y][self.x], (Demi, Obscurite)):
            self._eat_plant(world)
        else:
            self.move_random()
        self._try_repro(world)

    def _find_prey(self, world, r):
        best, md = None, 999
        for a in world.animals:
            if isinstance(a, Pauvre) and a.alive:
                d = abs(a.x - self.x) + abs(a.y - self.y)
                if d < md and d <= r:
                    md, best = d, a
        return best

    def _find_plant(self, world, r):
        best, md = None, 999
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                nx, ny = self.x + dx, self.y + dy
                if 0 <= nx < GRID_W and 0 <= ny < GRID_H:
                    if isinstance(world.grid[ny][nx], (Demi, Obscurite)):
                        d = abs(dx) + abs(dy)
                        if d < md:
                            md, best = d, (nx, ny)
        return best

    def _eat_plant(self, world):
        self.hunger = max(0, self.hunger - 20)
        self.energy = min(100, self.energy + 8)
        world.grid[self.y][self.x] = None

    def _attack(self, prey):
        prey.energy -= 35
        if prey.energy <= 0:
            prey.alive = False
            self.hunger = max(0, self.hunger - 40)
            self.energy = min(100, self.energy + 15)
        else:
            self.hunger = max(0, self.hunger - 10)

    def _try_repro(self, world):
        if self.repro_cd > 0 or self.hunger > 45 or self.energy < 55 or self.age < 15:
            return
        for a in world.animals:
            if (
                isinstance(a, Malheureux)
                and a.alive
                and a is not self
                and abs(a.x - self.x) <= 3
                and abs(a.y - self.y) <= 3
                and a.repro_cd <= 0
            ):
                if rng.random() < 0.06:
                    world.new_animals.append(Malheureux(self.x, self.y))
                    self.repro_cd = 25
                    a.repro_cd = 25
                    self.energy -= 25
                    break
