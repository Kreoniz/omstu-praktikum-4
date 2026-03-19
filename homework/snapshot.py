class Snapshot:
    """Лёгкий снимок мира для отображения при навигации по истории."""

    __slots__ = (
        "tick",
        "day",
        "time_of_day",
        "phase_tick",
        "grid_colors",
        "animals_data",
        "stats_data",
        "w",
        "h",
    )

    def __init__(self, world):
        self.tick = world.tick_count
        self.day = world.day
        self.time_of_day = world.time_of_day
        self.phase_tick = world.phase_tick
        self.w, self.h = world.w, world.h

        self.grid_colors = [
            [
                world.grid[y][x].get_color() if world.grid[y][x] else None
                for x in range(world.w)
            ]
            for y in range(world.h)
        ]

        self.animals_data = [
            {
                "type": type(a).__name__,
                "x": a.x,
                "y": a.y,
                "hunger": a.hunger,
                "energy": a.energy,
                "sleeping": a.sleeping,
                "aggression": getattr(a, "aggression", 0.0),
                "vision_radius": getattr(a, "vision_radius", 5),
                "age": a.age,
                "color": a.color,
            }
            for a in world.animals
            if a.alive
        ]

        self.stats_data = world.stats_extended()
