import types
from config import GRID_W, GRID_H
from time_of_day import TimeOfDay
from ecosystem import EcosystemMeta
from colors import COL_PAUVRE, COL_MALHEUREUX
import rng


class AnimalMeta(EcosystemMeta):
    """
    Метакласс животных.

    DSL-атрибуты:
        _diet_plants      : list[str]              — имена классов-растений в рационе
        _diet_animals     : list[str]              — имена классов-животных (добыча)
        _sleep_times      : list[TimeOfDay]        — фазы сна
        _eat_schedule     : dict[TimeOfDay, int]   — фаза → количество еды
        _search_radius    : int
        _repro_cooldown   : int
        _repro_chance     : float
        _repro_min_energy : int
        _repro_max_hunger : int
        _repro_min_age    : int
        _repro_energy_cost: int
        _repro_range      : int
        _color            : tuple

    Автоматически генерирует:
        eat(world)              — поедание растения на текущей клетке
        hunt(world)             — поиск и атака добычи
        move_toward_food(world) — движение к ближайшей еде
        reproduce(world)        — размножение
        _is_sleeping(world)     — проверка сна
        count_nearby(world, r)  — подсчёт сородичей рядом
    """

    def __new__(mcs, name, bases, namespace):
        if bases and not namespace.get("_abstract", False):
            dp = namespace.get("_diet_plants", [])
            da = namespace.get("_diet_animals", [])
            st = namespace.get("_sleep_times", [])
            es = namespace.get("_eat_schedule", {})
            sr = namespace.get("_search_radius", 8)
            rc = namespace.get("_repro_cooldown", 20)
            rch = namespace.get("_repro_chance", 0.08)
            rme = namespace.get("_repro_min_energy", 50)
            rmh = namespace.get("_repro_max_hunger", 50)
            rma = namespace.get("_repro_min_age", 15)
            rec = namespace.get("_repro_energy_cost", 20)
            rr = namespace.get("_repro_range", 2)
            injected = []

            if "eat" not in namespace:

                def _make_eat(dp_, es_):
                    def eat(self, world):
                        plant = world.grid[self.y][self.x]
                        if plant and type(plant).__name__ in dp_:
                            amt = es_.get(world.time_of_day, 20)
                            self.hunger = max(0, self.hunger - amt)
                            self.energy = min(100, self.energy + 10)
                            world.grid[self.y][self.x] = None
                            return True
                        return False

                    return eat

                namespace["eat"] = _make_eat(list(dp), dict(es))
                injected.append("eat")

            if "hunt" not in namespace and da:

                def _make_hunt(da_, sr_):
                    def hunt(self, world):
                        best, md = None, 999
                        for a in world.animals:
                            if type(a).__name__ in da_ and a.alive and a is not self:
                                d = abs(a.x - self.x) + abs(a.y - self.y)
                                if d < md and d <= sr_:
                                    md, best = d, a
                        if best:
                            self.move_towards(best.x, best.y)
                            if abs(best.x - self.x) <= 1 and abs(best.y - self.y) <= 1:
                                best.energy -= 35
                                if best.energy <= 0:
                                    best.alive = False
                                    self.hunger = max(0, self.hunger - 40)
                                    self.energy = min(100, self.energy + 15)
                                else:
                                    self.hunger = max(0, self.hunger - 10)
                            return True
                        return False

                    return hunt

                namespace["hunt"] = _make_hunt(list(da), sr)
                injected.append("hunt")

            if "move_toward_food" not in namespace:

                def _make_mtf(dp_, sr_):
                    def move_toward_food(self, world):
                        best, md = None, 999
                        for dy_ in range(-sr_, sr_ + 1):
                            for dx_ in range(-sr_, sr_ + 1):
                                nx, ny = self.x + dx_, self.y + dy_
                                if 0 <= nx < world.w and 0 <= ny < world.h:
                                    p = world.grid[ny][nx]
                                    if p and type(p).__name__ in dp_:
                                        d = abs(dx_) + abs(dy_)
                                        if d < md:
                                            md, best = d, (nx, ny)
                        if best:
                            self.move_towards(*best)
                            return True
                        return False

                    return move_toward_food

                namespace["move_toward_food"] = _make_mtf(list(dp), sr)
                injected.append("move_toward_food")

            if "reproduce" not in namespace:

                def _make_repro(rc_, rch_, rme_, rmh_, rma_, rec_, rr_):
                    def reproduce(self, world):
                        if (
                            self.repro_cd > 0
                            or self.hunger > rmh_
                            or self.energy < rme_
                            or self.age < rma_
                        ):
                            return False
                        for a in world.animals:
                            if (
                                type(a) is type(self)
                                and a.alive
                                and a is not self
                                and abs(a.x - self.x) <= rr_
                                and abs(a.y - self.y) <= rr_
                                and a.repro_cd <= 0
                            ):
                                if rng.random() < rch_:
                                    baby = type(self)(self.x, self.y)
                                    world.new_animals.append(baby)
                                    self.repro_cd = rc_
                                    a.repro_cd = rc_
                                    self.energy -= rec_
                                    return True
                        return False

                    return reproduce

                namespace["reproduce"] = _make_repro(rc, rch, rme, rmh, rma, rec, rr)
                injected.append("reproduce")

            if "_is_sleeping" not in namespace:
                _st_copy = list(st)

                def _make_sleep(st_):
                    def _is_sleeping(self, world):
                        return world.time_of_day in st_

                    return _is_sleeping

                namespace["_is_sleeping"] = _make_sleep(_st_copy)
                injected.append("_is_sleeping")

            if "count_nearby" not in namespace:

                def count_nearby(self, world, radius=None):
                    r = (
                        radius
                        if radius is not None
                        else getattr(self, "vision_radius", 3)
                    )
                    return sum(
                        1
                        for a in world.animals
                        if type(a) is type(self)
                        and a.alive
                        and a is not self
                        and abs(a.x - self.x) <= r
                        and abs(a.y - self.y) <= r
                    )

                namespace["count_nearby"] = count_nearby
                injected.append("count_nearby")

            if "get_visible_neighbors" not in namespace:

                def get_visible_neighbors(self, world):
                    """Все живые животные (любого типа) в пределах vision_radius."""
                    vr = getattr(self, "vision_radius", 5)
                    return [
                        a
                        for a in world.animals
                        if a is not self
                        and a.alive
                        and abs(a.x - self.x) <= vr
                        and abs(a.y - self.y) <= vr
                    ]

                namespace["get_visible_neighbors"] = get_visible_neighbors
                injected.append("get_visible_neighbors")

            if injected:
                print(f"  [AnimalMeta] → {name}: инжектированы {injected}")

        return super().__new__(mcs, name, bases, namespace)


class Animal(metaclass=AnimalMeta):
    """Базовый класс животного (абстрактный — не регистрируется)."""

    _abstract = True

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
        self.color = getattr(type(self), "_color", (255, 255, 255))
        self.vision_radius = getattr(type(self), "_vision_radius", 5)

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
    Группируются, агрессивны при голоде, спят ночью.
    """

    _color = COL_PAUVRE
    _diet_plants = ["Lumiere"]
    _diet_animals = []
    _sleep_times = [TimeOfDay.NIGHT]
    _eat_schedule = {
        TimeOfDay.MORNING: 35,
        TimeOfDay.DAY: 25,
        TimeOfDay.EVENING: 10,
    }
    _search_radius = 10
    _group_min = 2
    _group_max = 6
    _aggression_hunger_threshold = 40
    _can_attack_own = True
    _repro_cooldown = 20
    _repro_chance = 0.08
    _repro_min_energy = 50
    _repro_max_hunger = 50
    _repro_min_age = 15
    _repro_energy_cost = 20
    _repro_range = 2
    _vision_radius = 5

    def _update_behavior(self, world):
        if self._is_sleeping(world):
            self.sleeping = True
            self.act = types.MethodType(Pauvre._act_sleep, self)
            return
        self.sleeping = False
        self.aggression = max(
            0.0, (self.hunger - self._aggression_hunger_threshold) / 60.0
        )
        nearby = self.count_nearby(world, 3)

        if self.hunger > 75:
            self.act = types.MethodType(Pauvre._act_aggressive, self)
        elif self.hunger > 45:
            self.act = types.MethodType(Pauvre._act_hungry, self)
        elif nearby < self._group_min:
            self.act = types.MethodType(Pauvre._act_seek_group, self)
        elif nearby > self._group_max:
            self.act = types.MethodType(Pauvre._act_disperse, self)
        else:
            self.act = types.MethodType(Pauvre._act_normal, self)

    def _act_sleep(self, world):
        self.energy = min(100, self.energy + 2)

    def _act_normal(self, world):
        if not self.eat(world):
            if not self.move_toward_food(world):
                self.move_random()
        self.reproduce(world)

    def _act_hungry(self, world):
        if not self.eat(world):
            self.move_toward_food(world)
            if not self.eat(world):
                self.move_toward_food(world)

    def _act_aggressive(self, world):
        if self.eat(world):
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
        if not self.move_toward_food(world):
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
        elif not self.eat(world):
            self.move_random()
        self.reproduce(world)

    def _act_disperse(self, world):
        self.move_random()
        self.move_random()
        self.eat(world)


class Malheureux(Animal):
    """
    Всеядные хищники — едят Demi, Obscurite и Pauvre.
    Стайные, активны утром и вечером.
    """

    _color = COL_MALHEUREUX
    _diet_plants = ["Demi", "Obscurite"]
    _diet_animals = ["Pauvre"]
    _sleep_times = [TimeOfDay.DAY, TimeOfDay.NIGHT]
    _eat_schedule = {TimeOfDay.MORNING: 20, TimeOfDay.EVENING: 20}
    _search_radius = 10
    _repro_cooldown = 25
    _repro_chance = 0.06
    _repro_min_energy = 55
    _repro_max_hunger = 45
    _repro_min_age = 15
    _repro_energy_cost = 25
    _repro_range = 3
    _vision_radius = 7

    def _update_behavior(self, world):
        if self._is_sleeping(world):
            self.sleeping = True
            self.act = types.MethodType(Malheureux._act_sleep, self)
            return
        self.sleeping = False
        self.speed = 1 if self.hunger > 60 else 2
        pack = self.count_nearby(world, 4)

        if pack >= 4:
            self.act = types.MethodType(Malheureux._act_pack_hunt, self)
        elif self.hunger > 50:
            self.act = types.MethodType(Malheureux._act_hunt, self)
        else:
            self.act = types.MethodType(Malheureux._act_wander, self)

    def _act_sleep(self, world):
        self.energy = min(100, self.energy + 3)

    def _act_wander(self, world):
        if not self.eat(world):
            self.move_random()
        self.reproduce(world)

    def _act_hunt(self, world):
        if not self.hunt(world):
            if not self.eat(world):
                if not self.move_toward_food(world):
                    self.move_random()

    def _act_pack_hunt(self, world):
        best, md = None, 999
        for a in world.animals:
            if type(a).__name__ in self._diet_animals and a.alive and a is not self:
                d = abs(a.x - self.x) + abs(a.y - self.y)
                if d < md and d <= 12:
                    md, best = d, a
        if best:
            for _ in range(self.speed):
                self.move_towards(best.x, best.y)
            if abs(best.x - self.x) <= 1 and abs(best.y - self.y) <= 1:
                best.energy -= 35
                if best.energy <= 0:
                    best.alive = False
                    self.hunger = max(0, self.hunger - 40)
                    self.energy = min(100, self.energy + 15)
                else:
                    self.hunger = max(0, self.hunger - 10)
        elif not self.eat(world):
            self.move_random()
        self.reproduce(world)
