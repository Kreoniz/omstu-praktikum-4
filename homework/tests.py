import unittest
from ecosystem import EcosystemMeta
from plants import Plant, Lumiere, Obscurite, Demi
from animals import Animal, Pauvre, Malheureux
from time_of_day import TimeOfDay
from world import World
from slider import PygameSlider


class TestRegistry(unittest.TestCase):
    """1. Корректная регистрация классов в реестре."""

    def test_all_plants_registered(self):
        reg = EcosystemMeta.get_registry()
        for name in ("Lumiere", "Obscurite", "Demi"):
            self.assertIn(name, reg, f"{name} не найден в реестре")

    def test_all_animals_registered(self):
        reg = EcosystemMeta.get_registry()
        for name in ("Pauvre", "Malheureux"):
            self.assertIn(name, reg, f"{name} не найден в реестре")

    def test_base_not_registered(self):
        reg = EcosystemMeta.get_registry()
        self.assertNotIn("Plant", reg)
        self.assertNotIn("Animal", reg)

    def test_get_by_name(self):
        self.assertIs(EcosystemMeta.get_by_name("Lumiere"), Lumiere)
        self.assertIs(EcosystemMeta.get_by_name("Pauvre"), Pauvre)
        self.assertIsNone(EcosystemMeta.get_by_name("НесуществующийВид"))

    def test_registry_count(self):
        reg = EcosystemMeta.get_registry()
        self.assertEqual(len(reg), 5)


class TestInjectedMethods(unittest.TestCase):
    """2. Присутствие автоматически сгенерированных методов."""

    def test_plant_has_update_behavior(self):
        for cls in (Lumiere, Obscurite, Demi):
            self.assertTrue(
                hasattr(cls, "update_behavior"),
                f"{cls.__name__} без update_behavior",
            )

    def test_plant_has_spread(self):
        for cls in (Lumiere, Obscurite, Demi):
            self.assertTrue(hasattr(cls, "spread"), f"{cls.__name__} без spread")

    def test_plant_has_get_color(self):
        for cls in (Lumiere, Obscurite, Demi):
            self.assertTrue(hasattr(cls, "get_color"), f"{cls.__name__} без get_color")

    def test_animal_has_eat(self):
        for cls in (Pauvre, Malheureux):
            self.assertTrue(hasattr(cls, "eat"), f"{cls.__name__} без eat")

    def test_animal_has_reproduce(self):
        for cls in (Pauvre, Malheureux):
            self.assertTrue(hasattr(cls, "reproduce"), f"{cls.__name__} без reproduce")

    def test_animal_has_move_toward_food(self):
        for cls in (Pauvre, Malheureux):
            self.assertTrue(
                hasattr(cls, "move_toward_food"),
                f"{cls.__name__} без move_toward_food",
            )

    def test_animal_has_count_nearby(self):
        for cls in (Pauvre, Malheureux):
            self.assertTrue(
                hasattr(cls, "count_nearby"),
                f"{cls.__name__} без count_nearby",
            )

    def test_animal_has_is_sleeping(self):
        for cls in (Pauvre, Malheureux):
            self.assertTrue(
                hasattr(cls, "_is_sleeping"),
                f"{cls.__name__} без _is_sleeping",
            )

    def test_malheureux_has_hunt(self):
        self.assertTrue(hasattr(Malheureux, "hunt"))

    def test_pauvre_no_hunt(self):
        p = Pauvre(0, 0)
        self.assertFalse(hasattr(p, "hunt"))


class TestBehavior(unittest.TestCase):
    """3. Правильность поведения в разных режимах времени."""

    def _make_world(self, tod=TimeOfDay.MORNING):
        w = World(10, 10)
        w.time_of_day = tod
        return w

    def test_lumiere_active_day(self):
        lum = Lumiere(0, 0)
        lum.update_behavior(TimeOfDay.DAY)
        self.assertTrue(lum.active)
        self.assertGreater(lum.spread_chance, 0)

    def test_lumiere_passive_night(self):
        lum = Lumiere(0, 0)
        lum.update_behavior(TimeOfDay.NIGHT)
        self.assertFalse(lum.active)
        self.assertEqual(lum.spread_chance, 0.0)

    def test_obscurite_active_night(self):
        obs = Obscurite(0, 0)
        obs.update_behavior(TimeOfDay.NIGHT)
        self.assertTrue(obs.active)

    def test_obscurite_passive_day(self):
        obs = Obscurite(0, 0)
        obs.update_behavior(TimeOfDay.DAY)
        self.assertFalse(obs.active)

    def test_demi_active_morning(self):
        d = Demi(0, 0)
        d.update_behavior(TimeOfDay.MORNING)
        self.assertTrue(d.active)

    def test_demi_passive_day(self):
        d = Demi(0, 0)
        d.update_behavior(TimeOfDay.DAY)
        self.assertFalse(d.active)

    def test_spread_returns_list(self):
        w = self._make_world(TimeOfDay.DAY)
        lum = Lumiere(5, 5)
        lum.update_behavior(TimeOfDay.DAY)
        result = lum.spread(w)
        self.assertIsInstance(result, list)

    def test_spread_empty_when_passive(self):
        w = self._make_world(TimeOfDay.NIGHT)
        lum = Lumiere(5, 5)
        lum.update_behavior(TimeOfDay.NIGHT)
        result = lum.spread(w)
        self.assertEqual(result, [])

    def test_get_color_active_vs_passive(self):
        lum = Lumiere(0, 0)
        lum.active = True
        self.assertEqual(lum.get_color(), (255, 220, 50))
        lum.active = False
        self.assertEqual(lum.get_color(), (120, 100, 30))

    def test_pauvre_sleeps_night(self):
        w = self._make_world(TimeOfDay.NIGHT)
        p = Pauvre(5, 5)
        w.animals.append(p)
        self.assertTrue(p._is_sleeping(w))

    def test_pauvre_awake_morning(self):
        w = self._make_world(TimeOfDay.MORNING)
        p = Pauvre(5, 5)
        w.animals.append(p)
        self.assertFalse(p._is_sleeping(w))

    def test_malheureux_sleeps_day(self):
        w = self._make_world(TimeOfDay.DAY)
        m = Malheureux(5, 5)
        w.animals.append(m)
        self.assertTrue(m._is_sleeping(w))

    def test_malheureux_awake_evening(self):
        w = self._make_world(TimeOfDay.EVENING)
        m = Malheureux(5, 5)
        w.animals.append(m)
        self.assertFalse(m._is_sleeping(w))

    def test_eat_on_food(self):
        w = self._make_world(TimeOfDay.MORNING)
        w.grid[5][5] = Lumiere(5, 5)
        p = Pauvre(5, 5)
        p.hunger = 50
        w.animals.append(p)
        result = p.eat(w)
        self.assertTrue(result)
        self.assertLess(p.hunger, 50)
        self.assertIsNone(w.grid[5][5])

    def test_eat_wrong_food(self):
        w = self._make_world(TimeOfDay.MORNING)
        w.grid[5][5] = Obscurite(5, 5)
        p = Pauvre(5, 5)
        p.hunger = 50
        w.animals.append(p)
        result = p.eat(w)
        self.assertFalse(result)
        self.assertEqual(p.hunger, 50)

    def test_malheureux_eat_demi(self):
        w = self._make_world(TimeOfDay.MORNING)
        w.grid[3][3] = Demi(3, 3)
        m = Malheureux(3, 3)
        m.hunger = 50
        w.animals.append(m)
        result = m.eat(w)
        self.assertTrue(result)
        self.assertLess(m.hunger, 50)

    def test_count_nearby(self):
        w = self._make_world()
        p1 = Pauvre(5, 5)
        p2 = Pauvre(6, 5)
        p3 = Pauvre(5, 6)
        w.animals = [p1, p2, p3]
        self.assertEqual(p1.count_nearby(w, 3), 2)

    def test_self_modifying_act(self):
        """act подменяется в зависимости от состояния."""
        w = self._make_world(TimeOfDay.MORNING)
        p = Pauvre(5, 5)
        p.hunger = 80
        w.animals = [p]
        w.new_animals = []
        p._update_behavior(w)
        self.assertIn("aggressive", p.act.__func__.__name__)

    def test_self_modifying_sleep(self):
        w = self._make_world(TimeOfDay.NIGHT)
        p = Pauvre(5, 5)
        w.animals = [p]
        w.new_animals = []
        p._update_behavior(w)
        self.assertTrue(p.sleeping)
        self.assertIn("sleep", p.act.__func__.__name__)


class TestDynamicSpecies(unittest.TestCase):
    """4. Динамическое создание нового вида через метакласс."""

    def test_new_plant_species(self):
        """Создаём новый вид растения — метакласс должен зарегистрировать и
        инжектировать методы."""

        class Solaris(Plant):
            _active_times = {TimeOfDay.DAY: 0.1}
            _color_active = (255, 255, 0)
            _color_passive = (80, 80, 0)

        self.assertIn("Solaris", EcosystemMeta.get_registry())
        s = Solaris(0, 0)
        s.update_behavior(TimeOfDay.DAY)
        self.assertTrue(s.active)
        s.update_behavior(TimeOfDay.NIGHT)
        self.assertFalse(s.active)
        self.assertEqual(s.get_color(), (80, 80, 0))

        del EcosystemMeta._registry["Solaris"]

    def test_new_animal_species(self):
        """Создаём новый вид животного — eat/reproduce/move генерируются."""

        class Timide(Animal):
            _color = (200, 200, 200)
            _diet_plants = ["Lumiere", "Demi"]
            _diet_animals = []
            _sleep_times = [TimeOfDay.NIGHT, TimeOfDay.DAY]
            _eat_schedule = {TimeOfDay.MORNING: 30, TimeOfDay.EVENING: 30}
            _repro_cooldown = 15
            _repro_chance = 0.1
            _repro_min_energy = 40
            _repro_max_hunger = 60
            _repro_min_age = 10
            _repro_energy_cost = 15
            _repro_range = 3
            _search_radius = 6

        self.assertIn("Timide", EcosystemMeta.get_registry())
        t = Timide(5, 5)
        self.assertTrue(hasattr(t, "eat"))
        self.assertTrue(hasattr(t, "reproduce"))
        self.assertTrue(hasattr(t, "move_toward_food"))
        self.assertTrue(hasattr(t, "count_nearby"))

        w = World(10, 10)
        w.time_of_day = TimeOfDay.NIGHT
        self.assertTrue(t._is_sleeping(w))
        w.time_of_day = TimeOfDay.MORNING
        self.assertFalse(t._is_sleeping(w))

        del EcosystemMeta._registry["Timide"]


class TestHomework(unittest.TestCase):
    """Тесты для домашнего задания."""

    def test_vision_radius_pauvre(self):
        p = Pauvre(0, 0)
        self.assertEqual(p.vision_radius, 5)

    def test_vision_radius_malheureux(self):
        m = Malheureux(0, 0)
        self.assertEqual(m.vision_radius, 7)

    def test_get_visible_neighbors_injected(self):
        self.assertTrue(hasattr(Pauvre, "get_visible_neighbors"))
        self.assertTrue(hasattr(Malheureux, "get_visible_neighbors"))

    def test_get_visible_neighbors_correct(self):
        w = World(20, 20)
        w.time_of_day = TimeOfDay.MORNING
        p1 = Pauvre(10, 10)
        p2 = Pauvre(12, 10)
        p3 = Pauvre(16, 10)
        m1 = Malheureux(11, 11)
        w.animals = [p1, p2, p3, m1]
        nb = p1.get_visible_neighbors(w)
        self.assertIn(p2, nb)
        self.assertIn(m1, nb)
        self.assertNotIn(p3, nb)

    def test_count_nearby_default_vision(self):
        w = World(20, 20)
        w.time_of_day = TimeOfDay.MORNING
        p1 = Pauvre(10, 10)
        p2 = Pauvre(12, 10)
        p3 = Pauvre(16, 10)
        w.animals = [p1, p2, p3]
        self.assertEqual(p1.count_nearby(w), 1)
        self.assertEqual(p1.count_nearby(w, 10), 2)

    def test_snapshot_creation(self):
        w = World(10, 10)
        w.init(density=0.1, n_pauvre=5, n_malh=3)
        initial = len(w.snapshots)
        w.tick()
        self.assertEqual(len(w.snapshots), initial + 1)
        snap = w.snapshots[-1]
        self.assertEqual(snap.tick, 1)
        self.assertEqual(snap.w, 10)
        self.assertEqual(snap.h, 10)

    def test_snapshot_has_stats(self):
        w = World(10, 10)
        w.init(density=0.1, n_pauvre=4, n_malh=2)
        w.tick()
        snap = w.snapshots[-1]
        self.assertIn("pauvre_avg_vr", snap.stats_data)
        self.assertIn("malh_avg_vr", snap.stats_data)
        self.assertIn("lumiere", snap.stats_data)

    def test_snapshot_animals_have_vision(self):
        w = World(10, 10)
        w.init(density=0.1, n_pauvre=3, n_malh=2)
        w.tick()
        snap = w.snapshots[-1]
        for ad in snap.animals_data:
            self.assertIn("vision_radius", ad)
            self.assertGreater(ad["vision_radius"], 0)

    def test_stats_extended(self):
        w = World(10, 10)
        w.init(density=0.1, n_pauvre=5, n_malh=3)
        s = w.stats_extended()
        self.assertIn("pauvre_avg_vr", s)
        self.assertIn("malh_avg_vr", s)
        self.assertIn("pauvre_avg_hunger", s)
        self.assertIn("malh_avg_energy", s)
        self.assertEqual(s["pauvre_avg_vr"], 5.0)
        self.assertEqual(s["malh_avg_vr"], 7.0)

    def test_dynamic_species_has_vision(self):
        """Новый вид через DSL автоматически получает vision_radius."""

        class Rapide(Animal):
            _color = (100, 100, 100)
            _vision_radius = 10
            _diet_plants = ["Lumiere"]
            _diet_animals = []
            _sleep_times = []
            _eat_schedule = {}

        r = Rapide(0, 0)
        self.assertEqual(r.vision_radius, 10)
        self.assertTrue(hasattr(r, "get_visible_neighbors"))

        del EcosystemMeta._registry["Rapide"]

    def test_slider_basics(self):
        s = PygameSlider(100, 20, 500, 14, 0, 100)
        self.assertEqual(s.value, 0)
        s.max_val = 200
        s._set(350)
        self.assertEqual(s.value, 100)


def run_tests():
    print("\n" + "=" * 60)
    print("         ЗАПУСК ЮНИТ-ТЕСТОВ")
    print("=" * 60)
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(TestRegistry))
    suite.addTests(loader.loadTestsFromTestCase(TestInjectedMethods))
    suite.addTests(loader.loadTestsFromTestCase(TestBehavior))
    suite.addTests(loader.loadTestsFromTestCase(TestDynamicSpecies))
    suite.addTests(loader.loadTestsFromTestCase(TestHomework))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()
