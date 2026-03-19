"""Игра «Изгиб Питона» — классическая змейка на Pygame с использованием ООП."""

import sys
import random

import pygame

SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

BOARD_BACKGROUND_COLOR = (0, 0, 0)
BORDER_COLOR = (93, 216, 228)
APPLE_COLOR = (255, 0, 0)
SNAKE_COLOR = (0, 255, 0)

SPEED = 20

CENTER = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Изгиб Питона')
clock = pygame.time.Clock()


class GameObject:
    """Базовый класс для всех игровых объектов.

    Содержит общие атрибуты (позиция, цвет) и заготовку метода отрисовки.
    """

    def __init__(self, position=CENTER, body_color=None):
        """Инициализирует объект с позицией и цветом.

        Args:
            position: Координаты объекта на игровом поле (кортеж).
            body_color: RGB-цвет объекта или None.
        """
        self.position = position
        self.body_color = body_color

    def draw(self):
        """Абстрактный метод отрисовки. Переопределяется в потомках."""
        pass


class Apple(GameObject):
    """Яблоко — игровой объект, который змейка должна съесть.

    Появляется в случайном месте поля. После поедания перемещается
    на новое случайное место.
    """

    def __init__(self):
        """Инициализирует яблоко: задаёт цвет и случайную позицию."""
        super().__init__(body_color=APPLE_COLOR)
        self.randomize_position()

    def randomize_position(self, occupied=None):
        """Устанавливает случайную позицию яблока в пределах поля.

        Args:
            occupied: Список позиций, которые нельзя занимать.
        """
        occupied = occupied or []
        while True:
            position = (
                random.randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                random.randint(0, GRID_HEIGHT - 1) * GRID_SIZE,
            )
            if position not in occupied:
                self.position = position
                break

    def draw(self):
        """Отрисовывает яблоко на игровом поле."""
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


class Snake(GameObject):
    """Змейка — главный игровой объект, управляемый игроком.

    Движется по полю, растёт после поедания яблок, сбрасывается
    при столкновении с самой собой.
    """

    def __init__(self):
        """Инициализирует начальное состояние змейки."""
        super().__init__(position=CENTER, body_color=SNAKE_COLOR)
        self.length = 1
        self.positions = [CENTER]
        self.direction = RIGHT
        self.next_direction = None
        self.last = None

    def get_head_position(self):
        """Возвращает позицию головы змейки.

        Returns:
            Кортеж (x, y) — координаты головы.
        """
        return self.positions[0]

    def update_direction(self):
        """Применяет следующее направление движения, если оно задано."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self):
        """Перемещает змейку на одну ячейку в текущем направлении.

        Добавляет новую голову в начало списка позиций. Если змейка
        достигла края — появляется с противоположной стороны.
        При столкновении с собой вызывает reset().
        """
        head_x, head_y = self.get_head_position()
        dx, dy = self.direction
        new_head = (
            (head_x + dx * GRID_SIZE) % SCREEN_WIDTH,
            (head_y + dy * GRID_SIZE) % SCREEN_HEIGHT,
        )

        if new_head in self.positions[2:]:
            self.reset()
            return

        self.positions.insert(0, new_head)

        if len(self.positions) > self.length:
            self.last = self.positions.pop()
        else:
            self.last = None

    def draw(self):
        """Отрисовывает змейку и затирает след последнего сегмента."""
        if self.last:
            last_rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)

        head_rect = pygame.Rect(
            self.get_head_position(), (GRID_SIZE, GRID_SIZE)
        )
        pygame.draw.rect(screen, self.body_color, head_rect)
        pygame.draw.rect(screen, BORDER_COLOR, head_rect, 1)

        if len(self.positions) > 1:
            second_rect = pygame.Rect(
                self.positions[1], (GRID_SIZE, GRID_SIZE)
            )
            pygame.draw.rect(screen, self.body_color, second_rect)
            pygame.draw.rect(screen, BORDER_COLOR, second_rect, 1)

    def reset(self):
        """Сбрасывает змейку в начальное состояние.

        Длина становится 1, позиция — центр экрана,
        направление выбирается случайным образом.
        """
        self.length = 1
        self.positions = [CENTER]
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
        self.next_direction = None
        screen.fill(BOARD_BACKGROUND_COLOR)


def handle_keys(snake):
    """Обрабатывает нажатия клавиш для управления змейкой.

    Args:
        snake: Экземпляр класса Snake.
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and snake.direction != DOWN:
                snake.next_direction = UP
            elif event.key == pygame.K_DOWN and snake.direction != UP:
                snake.next_direction = DOWN
            elif event.key == pygame.K_LEFT and snake.direction != RIGHT:
                snake.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and snake.direction != LEFT:
                snake.next_direction = RIGHT


def main():
    """Основной игровой цикл.

    Создаёт объекты змейки и яблока, запускает бесконечный цикл,
    в котором обрабатываются события, обновляется состояние игры
    и перерисовывается экран.
    """
    snake = Snake()
    apple = Apple()

    screen.fill(BOARD_BACKGROUND_COLOR)

    while True:
        clock.tick(SPEED)

        handle_keys(snake)
        snake.update_direction()
        snake.move()

        if snake.get_head_position() == apple.position:
            snake.length += 1
            apple.randomize_position(occupied=snake.positions)

        apple.draw()
        snake.draw()
        pygame.display.update()


if __name__ == '__main__':
    main()
