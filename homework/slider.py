import pygame


class PygameSlider:
    """Горизонтальный ползунок для навигации по истории тиков."""

    def __init__(self, x, y, w, h, min_val=0, max_val=0):
        self.x, self.y, self.w, self.h = x, y, w, h
        self.min_val = min_val
        self.max_val = max_val
        self.value = min_val
        self.dragging = False

    def handle_event(self, event):
        """Возвращает True, если значение изменилось."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            hit = pygame.Rect(self.x, self.y - 6, self.w, self.h + 12)
            if hit.collidepoint(event.pos):
                self.dragging = True
                self._set(event.pos[0])
                return True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            was = self.dragging
            self.dragging = False
            return was
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self._set(event.pos[0])
            return True
        return False

    def _set(self, mx):
        r = max(0.0, min(1.0, (mx - self.x) / max(1, self.w)))
        self.value = int(self.min_val + r * (self.max_val - self.min_val))

    def draw(self, screen, font):
        track = pygame.Rect(self.x, self.y, self.w, self.h)
        pygame.draw.rect(screen, (50, 50, 60), track, border_radius=4)
        ratio = (self.value - self.min_val) / max(1, self.max_val - self.min_val)
        fw = int(self.w * ratio)
        if fw > 0:
            pygame.draw.rect(
                screen, (70, 110, 170), (self.x, self.y, fw, self.h), border_radius=4
            )
        hx = self.x + fw
        pygame.draw.rect(
            screen,
            (200, 200, 220),
            (hx - 6, self.y - 3, 12, self.h + 6),
            border_radius=3,
        )
