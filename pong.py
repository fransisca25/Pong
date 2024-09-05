import pygame
import sys

# constants
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
BALL_DELAY = 300
FONT = 'Comic Sans MS'
FONT_SIZE = 50
SCALE_IMG = (250, 250)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)


class Pong:
    def __init__(self, icon_img, win_caption="Pong!"):
        super().__init__()
        self.window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.icon_img = pygame.image.load(icon_img).convert_alpha()
        self.logo_scaled = pygame.transform.scale(self.icon_img, SCALE_IMG)
        self.logo_rect = self.logo_scaled.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3 + 75))
        self.win_caption = win_caption

        self.text = pygame.font.SysFont(FONT, FONT_SIZE)
        self.title = self.text.render("Pong!", False, BLACK)

        self.state = 'main_menu'
        self.menu_opt = ['Play', 'Exit']
        self.selected = 0

        self.running = True

    def window_display(self):
        pygame.display.set_caption(self.win_caption)
        pygame.display.set_icon(self.icon_img)

    def draw_main_menu(self):
        self.window.fill(WHITE)
        self.window.blit(self.title, (SCREEN_WIDTH // 2 - self.title.get_width() // 2, 50))
        self.window.blit(self.logo_scaled, self.logo_rect)

        for idx, opt in enumerate(self.menu_opt):
            color = BLACK
            if idx == self.selected:
                color = RED
            opt_text = self.text.render(opt, False, color)
            self.window.blit(opt_text, (SCREEN_WIDTH // 2 - opt_text.get_width() // 2, 500 + idx * 60))

    def main_menu_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected = (self.selected - 1) % len(self.menu_opt)
            elif event.key == pygame.K_DOWN:
                self.selected = (self.selected + 1) % len(self.menu_opt)
            elif event.key == pygame.K_RETURN:
                if self.selected == 0:
                    self.state = 'main_game'
                elif self.selected == 1:
                    pygame.quit()
                    sys.exit()

    def draw_game(self):
        # player movements (detect input keys)
        players.input_keys()

        # clamp players within screen bounds
        players.clamp(self.window)

        # ball movements
        ball.ball_movement()
        ball.check_collision(players.player_rect1, players.player_rect2)

        # fill screen with black color
        self.window.fill(BLACK)

        # count score
        score.score_counter()

        # draw players
        players.draw(self.window)

        # draw ball
        ball.draw(self.window)

        # reset ball
        ball.ball_reset()

        # draw score
        score.draw(self.window)

    def main(self):
        clock = pygame.time.Clock()

        # change window caption and icon
        self.window_display()

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                    self.state = 'main_menu'
                    score.reset_score()
                if self.state == 'main_menu':
                    self.main_menu_input(event)

            if self.state == 'main_menu':
                self.draw_main_menu()
            elif self.state == 'main_game':
                self.draw_game()

            clock.tick(FPS)
            pygame.display.flip()


class Players:
    def __init__(self, color=WHITE, velocity=6):
        super().__init__()
        self.player_rect1 = pygame.Rect(30, SCREEN_HEIGHT // 2 - 60, 10, 75)
        self.player_rect2 = pygame.Rect(SCREEN_WIDTH - 40, SCREEN_HEIGHT // 2 - 60, 10, 75)
        self.velocity = velocity
        self.color = color

    def input_keys(self):
        key_pressed = pygame.key.get_pressed()
        if key_pressed[pygame.K_w]:
            self.player_rect1.y -= self.velocity
        if key_pressed[pygame.K_s]:
            self.player_rect1.y += self.velocity
        if key_pressed[pygame.K_i]:
            self.player_rect2.y -= self.velocity
        if key_pressed[pygame.K_k]:
            self.player_rect2.y += self.velocity

    def clamp(self, win):
        # keep rects on the screen
        self.player_rect1.clamp_ip(win.get_rect())
        self.player_rect2.clamp_ip(win.get_rect())

    def draw(self, win):
        pygame.draw.rect(win, self.color, self.player_rect1)
        pygame.draw.rect(win, self.color, self.player_rect2)


class Ball:
    def __init__(self,
                 bounce,
                 center_x=SCREEN_WIDTH // 2,
                 center_y=SCREEN_HEIGHT // 2,
                 radius=10,
                 color=WHITE,
                 velocity_x=5,
                 velocity_y=5):
        super().__init__()
        self.center_x = center_x
        self.center_y = center_y
        self.radius = radius

        self.velocity_x = velocity_x
        self.velocity_y = velocity_y

        self.sound = pygame.mixer.Sound(bounce)
        self.color = color

    def ball_movement(self):
        self.center_x += self.velocity_x
        self.center_y += self.velocity_y

    def check_collision(self, p1, p2):
        # ball rectangle
        ball_rect = pygame.Rect(
            self.center_x - self.radius,
            self.center_y - self.radius,
            self.radius * 2,
            self.radius * 2
        )

        # bounce when collide with top and bottom walls
        if self.center_y - self.radius <= 0 or self.center_y + self.radius >= SCREEN_HEIGHT:
            self.velocity_y = -self.velocity_y

        # bounce when collide with the players
        if ball_rect.colliderect(p1):
            self.velocity_x = -self.velocity_x
            self.sound.play()
        if ball_rect.colliderect(p2):
            self.velocity_x = -self.velocity_x
            self.sound.play()

    def ball_reset(self):
        if self.center_x - self.radius <= -20 or self.center_x + self.radius >= SCREEN_WIDTH + 20:
            self.center_x = SCREEN_WIDTH // 2
            self.center_y = SCREEN_HEIGHT // 2

    def draw(self, win):
        pygame.draw.circle(win, self.color, (self.center_x, self.center_y), self.radius)


class Score:
    def __init__(self, score_sound, color=WHITE, font=FONT):
        super().__init__()
        self.score_p1 = 0
        self.score_p2 = 0

        self.color = color
        self.score_text = pygame.font.SysFont(font, 50)

        self.scoring_sound = pygame.mixer.Sound(score_sound)

    def score_counter(self):
        if ball.center_x - ball.radius <= -20:
            self.score_p2 += 1
            self.scoring_sound.play()
        if ball.center_x + ball.radius >= SCREEN_WIDTH + 20:
            self.score_p1 += 1
            self.scoring_sound.play()

    def reset_score(self):
        self.score_p1 = 0
        self.score_p2 = 0

    def draw(self, win):
        # Render score text
        render_p1 = self.score_text.render(f"{self.score_p1}", True, self.color)
        render_p2 = self.score_text.render(f"{self.score_p2}", True, self.color)

        # Draw score text
        score_p1_rect = render_p1.get_rect(center=(SCREEN_WIDTH // 4, 50))
        score_p2_rect = render_p2.get_rect(center=(SCREEN_WIDTH // 4 * 3, 50))

        win.blit(render_p1, score_p1_rect)
        win.blit(render_p2, score_p2_rect)


if __name__ == "__main__":
    pygame.init()
    pygame.font.init()
    pygame.mixer.init()

    pong = Pong('src/pong_icon.png')
    players = Players()
    ball = Ball('src/audio/bounce.wav')
    score = Score('src/audio/point.mp3')

    pong.main()

