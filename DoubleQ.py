import random

from Snake import *
import matplotlib

matplotlib.use("Agg")
import matplotlib.backends.backend_agg as agg
import pylab
import math


class Graph:
    red = []


def drawGraph():
    fig = pylab.figure(figsize=[7, 7],  # Inches
                       dpi=100)  # 100 dots per inch
    # fig.patch.set_alpha(0.1)  # make the surrounding of the plot 90% transparent to show what it does

    ax = fig.gca()
    ax.set_prop_cycle(color=['red'])
    ax.plot(Graph.red)

    canvas = agg.FigureCanvasAgg(fig)
    canvas.draw()
    renderer = canvas.get_renderer()
    raw_data = renderer.buffer_rgba()

    pygame.init()
    screen = pygame.display.get_surface()

    size = canvas.get_width_height()
    surf = pygame.image.frombuffer(raw_data, size, "RGBA")

    screen.blit(surf, (0, 0))  # x, y position on screen
    matplotlib.pyplot.close(fig)


if __name__ == "__main__":
    pygame.display.set_caption("Double Q Learning AI - Snake")

# Define the number of episodes to run
NUM_EPISODES = 100000000000

# Define the learning rate (alpha) and discount factor (gamma)
ALPHA = 0.001
GAMMA = 0.9
EPSILON = 0.1
ACTION_NUM = 4

# Define the possible actions
# ACTIONS = [(0, 1), (0, -1), (1, 0), (-1, 0)]

ACTIONS = {
    0: (-1, 0),
    1: (0, -1),
    2: (1, 0),
    3: (0, 1)
}

REWARDS = {
    "food": 2,
    "hit_wall": -5,
    "hit_body": -3,
    "normal-move": 0
}

EPISODES_TO_SHOW = [1000, 10000, 30000, 50000, 70000, 100000, 500000, 1000000, 2000000, 5000000, 7500000, 10000000]


def get_action_key_from_action(action):
    return list(ACTIONS.keys())[list(ACTIONS.values()).index(action)]


class SnakeGameState:
    def __init__(self, snake: Snake, food: Food):
        self.snake_pos = snake.position  # position of the snake's head
        self.snake_dir = snake.direction  # direction of the snake's movement
        self.food_pos = food.position  # position of the food
        self.obstacles = snake.body  # positions of snake's body

    def is_terminal(self):
        # Check if the snake has hit a wall
        if self.snake_pos[0] < 0 or self.snake_pos[0] >= SCREEN_WIDTH or self.snake_pos[1] < 0 or self.snake_pos[
            1] >= SCREEN_HEIGHT:
            return True
        # Check if the snake has hit its own body
        if self.snake_pos in self.obstacles[2:]:
            return True
        return False

    def get_reward(self):
        if self.is_terminal():
            if self.snake_pos in self.obstacles[2:]:
                return REWARDS["hit_body"]
            else:
                return REWARDS["hit_wall"]
        if self.snake_pos == self.food_pos:
            return REWARDS["food"]
        return REWARDS["normal-move"]

    def state_representation(self):
        # danger at snakes head
        danger_at_left = "0"
        danger_at_front = "0"
        danger_at_right = "0"
        # snake going left
        if self.snake_dir == (-1, 0):
            # look for danger on his left (below)
            if self.snake_pos[1] + BLOCK_SIZE >= SCREEN_HEIGHT or (
            self.snake_pos[0], self.snake_pos[1] + BLOCK_SIZE) in self.obstacles:
                danger_at_left = "1"
            # look for danger ahead (on the left)
            if self.snake_pos[0] - BLOCK_SIZE <= 0 or (
            self.snake_pos[0] - BLOCK_SIZE, self.snake_pos[1]) in self.obstacles:
                danger_at_front = "1"
            # look for danger on his right (above)
            if self.snake_pos[1] - BLOCK_SIZE <= 0 or (
            self.snake_pos[0], self.snake_pos[1] - BLOCK_SIZE) in self.obstacles:
                danger_at_right = "1"
        # snake going up
        if self.snake_dir == (0, -1):
            # look for danger on the left
            if self.snake_pos[0] - BLOCK_SIZE <= 0 or (
            self.snake_pos[0] - BLOCK_SIZE, self.snake_pos[1]) in self.obstacles:
                danger_at_left = "1"
            # look for danger ahead (above)
            if self.snake_pos[1] - BLOCK_SIZE <= 0 or (
            self.snake_pos[0], self.snake_pos[1] - BLOCK_SIZE) in self.obstacles:
                danger_at_front = "1"
            # look for danger on the right
            if self.snake_pos[0] + BLOCK_SIZE >= SCREEN_WIDTH or (
            self.snake_pos[0] + BLOCK_SIZE, self.snake_pos[1]) in self.obstacles:
                danger_at_right = "1"
        # snake going right
        if self.snake_dir == (1, 0):
            # look for danger on his right (below)
            if self.snake_pos[1] - BLOCK_SIZE <= 0 or (
            self.snake_pos[0], self.snake_pos[1] - BLOCK_SIZE) in self.obstacles:
                danger_at_left = "1"
            # look for danger ahead (on the right)
            if self.snake_pos[0] + BLOCK_SIZE >= SCREEN_WIDTH or (
            self.snake_pos[0] + BLOCK_SIZE, self.snake_pos[1]) in self.obstacles:
                danger_at_front = "1"
            # look for danger on his left (above)
            if self.snake_pos[1] + BLOCK_SIZE >= SCREEN_HEIGHT or (
            self.snake_pos[0], self.snake_pos[1] + BLOCK_SIZE) in self.obstacles:
                danger_at_right = "1"
        # snake going down
        if self.snake_dir == (0, 1):
            # look for danger on the left
            if self.snake_pos[0] + BLOCK_SIZE >= SCREEN_WIDTH or (
                    self.snake_pos[0] + BLOCK_SIZE, self.snake_pos[1]) in self.obstacles:
                danger_at_left = "1"
            # look for danger ahead (below)
            if self.snake_pos[1] + BLOCK_SIZE >= SCREEN_HEIGHT or (
                    self.snake_pos[0], self.snake_pos[1] + BLOCK_SIZE) in self.obstacles:
                danger_at_front = "1"
            # look for danger on the right
            if self.snake_pos[0] - BLOCK_SIZE <= 0 or (
                    self.snake_pos[0] - BLOCK_SIZE, self.snake_pos[1]) in self.obstacles:
                danger_at_right = "1"
        danger_at = danger_at_left + danger_at_front + danger_at_right
        # snake direction "left,up,right,down"
        snake_dir = "0000"
        if self.snake_dir == (-1, 0):
            snake_dir = "1000"
        if self.snake_dir == (0, -1):
            snake_dir = "0100"
        if self.snake_dir == (1, 0):
            snake_dir = "0010"
        if self.snake_dir == (0, 1):
            snake_dir = "0001"
        # food position "left,up,right,down"
        food_at_left = "0"
        food_at_up = "0"
        food_at_right = "0"
        food_at_down = "0"

        if self.food_pos[0] <= self.snake_pos[0]:
            food_at_left = "1"
        if self.food_pos[0] >= self.snake_pos[0]:
            food_at_right = "1"
        if self.food_pos[1] <= self.snake_pos[1]:
            food_at_up = "1"
        if self.food_pos[1] >= self.snake_pos[1]:
            food_at_down = "1"
        food_at = food_at_left + food_at_up + food_at_right + food_at_down
        return int((danger_at + snake_dir + food_at), 2)


class DoubleQLearningSnake(Snake):
    def __init__(self, learning_rate, discount_factor):
        super().__init__(INITIAL_POSITION, INITIAL_VELOCITY)
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.q1_table = [[0 for action in ACTIONS] for state in range(pow(2, 11))]
        self.q2_table = [[0 for action in ACTIONS] for state in range(pow(2, 11))]

    # epsilon-greedy action
    def get_action(self, state: SnakeGameState):
        num = random.uniform(0, 1)
        if num > EPSILON:
            # Choose the best action to take in the given state according to the Q-tables
            best_q1 = max(self.q1_table[state.state_representation()][action] for action in ACTIONS)
            best_q2 = max(self.q2_table[state.state_representation()][action] for action in ACTIONS)
            best_q = max(best_q1, best_q2)
            # Randomly choose one of the actions with the highest Q-value
            best_actions = [action for action in ACTIONS if
                            self.q1_table[state.state_representation()][action] == best_q or
                            self.q2_table[state.state_representation()][action] == best_q]
            return random.choice(best_actions)
        else:
            return math.floor((num * 1000) % ACTION_NUM)

    def get_greedy_action(self, bool, state: SnakeGameState):
        # Choose the best action to take in the given state according to the Q-tables
        if (bool):
            best_q = max(self.q1_table[state.state_representation()][action] for action in ACTIONS)

            best_actions = [action for action in ACTIONS if
                            self.q1_table[state.state_representation()][action] == best_q]

        else:
            best_q = max(self.q2_table[state.state_representation()][action] for action in ACTIONS)

            best_actions = [action for action in ACTIONS if
                            self.q2_table[state.state_representation()][action] == best_q]

        return random.choice(best_actions)

    def update(self, state: SnakeGameState, action, reward, next_state):
        # Choose the best action to take in the next state according to the two Q-tables

        if random.choice([True, False]):
            next_action = self.get_greedy_action(True, next_state)
            # Update the Q-value in the first Q-table using the Q-value in the second Q-table
            self.q1_table[state.state_representation()][action] = self.q1_table[state.state_representation()][
                                                                      action] + self.learning_rate * (
                                                                              reward + self.discount_factor *
                                                                              self.q2_table[
                                                                                  next_state.state_representation()][
                                                                                  next_action] - self.q1_table[
                                                                                  state.state_representation()][action])
        else:
            next_action = self.get_greedy_action(False, next_state)
            # Update the Q-value in the second Q-table using the Q-value in the first Q-table
            self.q2_table[state.state_representation()][action] = self.q2_table[state.state_representation()][
                                                                      action] + self.learning_rate * (
                                                                              reward + self.discount_factor *
                                                                              self.q1_table[
                                                                                  next_state.state_representation()][
                                                                                  next_action] - self.q2_table[
                                                                                  state.state_representation()][action])

    def reset_snake(self):
        self.position = INITIAL_POSITION
        self.velocity = INITIAL_VELOCITY
        self.body = [self.position]
        self.direction = INITIAL_VELOCITY


class SnakeGame:

    def __init__(self, snakeAI=None):
        if snakeAI is None:
            self.snake = DoubleQLearningSnake(ALPHA, GAMMA)
        else:
            self.snake = snakeAI

    def run(self):

        font = pygame.font.Font('freesansbold.ttf', 32)
        # Create the game clock
        clock = pygame.time.Clock()
        # Assign the snake
        snake = self.snake

        for episode in range(NUM_EPISODES):
            snake.reset_snake()
            food = Food(snake)
            gameState = SnakeGameState(snake, food)

            # Play the game for a specified number of time steps
            for t in range(MAX_TIME_STEPS):
                # Process the events in the game
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        # End the game if the user closes the window
                        pygame.quit()
                        quit()

                # Update the snake's direction based on AI chosen action
                snake.change_direction(ACTIONS.get(snake.get_action(gameState)))

                # Update the snake and food objects
                snake.move()

                new_state = SnakeGameState(snake, food)
                if new_state.is_terminal():
                    Graph.red.append(len(snake.body) - 1)
                    snake.update(gameState, snake.get_action(gameState), new_state.get_reward(), new_state)
                    break

                if snake.position == food.position:
                    # Create a new food object at a random position
                    food = Food(snake)
                    snake.body.append(snake.body[len(snake.body) - 1])

                snake.update(gameState, snake.get_action(gameState), new_state.get_reward(), new_state)

                gameState = new_state

                # if episode in EPISODES_TO_SHOW:
                #     screen.fill(BLACK)
                #     drawGraph()
                #     pygame.display.flip()
                #
                # if episode in EPISODES_TO_SHOW:
                if True:
                    # Clear the screen
                    screen.fill(BLACK)
                    # Draw the snake and food on the screen
                    snake.draw(screen)
                    food.draw(screen)

                    text = font.render(f"Episode: {episode}", True, (0, 255, 0))
                    text2 = font.render(f"Score: {len(snake.body)-1}", True, (0, 255, 0))
                    textRect = text.get_rect()
                    textRect2 = text2.get_rect()
                    textRect.topleft = (0, 0)
                    textRect2.topleft = textRect.bottomleft
                    screen.blit(text,textRect)
                    screen.blit(text2,textRect2)
                    # Update the game screen
                    pygame.display.update()
                    # Limit the frame rate to 15 FPS
                    if episode % 500 == 0:
                        clock.tick(15)
                    #
                    # screen.fill(BLACK)
                    # pygame.display.update()


snakeGame = SnakeGame()
snakeGame.run()
