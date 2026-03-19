from enum import Enum


class TimeOfDay(Enum):
    MORNING = 0
    DAY = 1
    EVENING = 2
    NIGHT = 3


TIME_LABELS = {
    TimeOfDay.MORNING: "Утро",
    TimeOfDay.DAY: "День",
    TimeOfDay.EVENING: "Вечер",
    TimeOfDay.NIGHT: "Ночь",
}

TIME_BG = {
    TimeOfDay.MORNING: (70, 60, 40),
    TimeOfDay.DAY: (45, 58, 35),
    TimeOfDay.EVENING: (60, 45, 40),
    TimeOfDay.NIGHT: (20, 20, 38),
}

TIME_LABEL_COL = {
    TimeOfDay.MORNING: (255, 210, 100),
    TimeOfDay.DAY: (255, 255, 150),
    TimeOfDay.EVENING: (255, 150, 80),
    TimeOfDay.NIGHT: (120, 120, 220),
}
