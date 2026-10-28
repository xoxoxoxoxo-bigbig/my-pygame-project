import pygame
import random
import time

# 1. กำหนดค่าคงที่ (Constants)
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GAME_SPEED = 8
JUMP_VELOCITY = -28
GRAVITY = 1.5
# พื้นดินหนา 140px (Y=460)
FLOOR_Y = SCREEN_HEIGHT - 140
# Power Up 3 วินาที
POWER_UP_DURATION = 3

# 2. Pygame Setup
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Infinite Runner - Game Reset")
clock = pygame.time.Clock()
pygame.font.init()
FONT = pygame.font.Font(None, 36)
SMALL_FONT = pygame.font.Font(None, 24)

# 🌟 โหลดและปรับขนาด SPRITES
try:
    # 1. ผู้เล่น: 150x150
    PLAYER_SIZE = 150

    # 1a. รูปภาพปกติ
    PLAYER_IMAGE = pygame.image.load('ลิง.png').convert_alpha()
    PLAYER_IMAGE = pygame.transform.scale(PLAYER_IMAGE, (PLAYER_SIZE, PLAYER_SIZE))

    # 1b. รูปภาพ Power-Up
    PLAYER_POWERUP_IMAGE = pygame.image.load('ลิง power.png').convert_alpha()
    PLAYER_POWERUP_IMAGE = pygame.transform.scale(PLAYER_POWERUP_IMAGE, (PLAYER_SIZE, PLAYER_SIZE))

    # 2. สิ่งกีดขวาง (ภาพฐาน)
    OBSTACLE_BASE_IMAGE = pygame.image.load('หิน.png').convert_alpha()

    # 3. Power-Up: 60x60
    POWERUP_SIZE = 60
    POWERUP_IMAGE = pygame.image.load('กล้วย.png').convert_alpha()
    POWERUP_IMAGE = pygame.transform.scale(POWERUP_IMAGE, (POWERUP_SIZE, POWERUP_SIZE))

    #
    USE_SPRITES = True
except pygame.error as e:
    print(f"Error loading sprites: {e}. Using colored blocks instead.")
    USE_SPRITES = False
    PLAYER_SIZE = 60  # Fallback size

# ส่วนสำหรับพื้นหลัง
try:
    BACKGROUND_IMAGE = pygame.image.load('พื้นหลัง.png').convert()
    BACKGROUND_IMAGE = pygame.transform.scale(BACKGROUND_IMAGE, (SCREEN_WIDTH, SCREEN_HEIGHT))
    USE_IMAGE_BG = True
except pygame.error as e:
    print(f"Error loading background image: {e}. Using solid white background instead.")
    USE_IMAGE_BG = False

VIRTUAL_FLOOR_Y = FLOOR_Y

START_TIME = time.time()

# 3. กำหนดสี (สำหรับ Fallback และ Obstacle)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 150, 0)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)


# 4. คลาสผู้เล่น (Player Class)
class Player:
    def __init__(self):
        self.width = PLAYER_SIZE
        self.height = PLAYER_SIZE

        # Hitbox configuration (Hitbox กระชับ)
        self.hitbox_width = 120
        self.hitbox_height = 120
        self.hitbox_offset_x = 15
        self.hitbox_offset_y = 30

        self.x = 100
        self.y = FLOOR_Y - self.height

        # กำหนด Hitbox เริ่มต้น
        self.rect = pygame.Rect(
            self.x + self.hitbox_offset_x,
            self.y + self.hitbox_offset_y,
            self.hitbox_width,
            self.hitbox_height
        )
        self.vel_y = 0
        self.is_jumping = False

    def update(self):
        if self.is_jumping:
            self.y += self.vel_y
            self.vel_y += GRAVITY

        if self.y >= FLOOR_Y - self.height:
            self.y = FLOOR_Y - self.height
            self.is_jumping = False
            self.vel_y = 0

            # อัปเดตตำแหน่ง Hitbox ให้สอดคล้องกับตำแหน่งภาพ
        self.rect.x = self.x + self.hitbox_offset_x
        self.rect.y = self.y + self.hitbox_offset_y

    def jump(self):
        if not self.is_jumping:
            self.is_jumping = True
            self.vel_y = JUMP_VELOCITY

    def draw(self, is_powered_up, remaining_time=0):
        if USE_SPRITES:
            current_image = PLAYER_POWERUP_IMAGE if is_powered_up else PLAYER_IMAGE
            screen.blit(current_image, (self.x, self.y))

        else:
            color = (150, 150, 255) if is_powered_up else BLUE
            pygame.draw.rect(screen, color, self.rect)

        if is_powered_up and remaining_time > 0:
            timer_text = SMALL_FONT.render(f"{remaining_time:.1f}", True, RED)
            text_x = self.x + self.width // 2 - timer_text.get_width() // 2
            text_y = self.y - 20
            screen.blit(timer_text, (text_x, text_y))

        # # DEBUG: วาดกรอบ Hitbox เพื่อตรวจสอบ
        # pygame.draw.rect(screen, (0, 255, 0), self.rect, 2)


# 5. คลาสสิ่งกีดขวาง (Obstacle Class)
class Obstacle:
    def __init__(self, x, width, height):
        self.width = width
        self.height = height
        self.x = x
        self.y = FLOOR_Y - self.height
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def move(self):
        self.x -= GAME_SPEED
        self.rect.x = self.x

    def draw(self):
        if USE_SPRITES:
            scaled_image = pygame.transform.scale(OBSTACLE_BASE_IMAGE, (self.width, self.height))
            screen.blit(scaled_image, (self.x, self.y))
        else:
            pygame.draw.rect(screen, RED, self.rect)


# 6. คลาสไอเทมเพิ่มพลัง (PowerUp Class)
class PowerUp:
    def __init__(self):
        self.size = POWERUP_SIZE
        self.x = SCREEN_WIDTH + random.randint(1000, 3000)
        self.y = FLOOR_Y - self.size - random.randint(30, 80)
        self.rect = pygame.Rect(self.x, self.y, self.size, self.size)

    def move(self):
        self.x -= GAME_SPEED
        self.rect.x = self.x

    def draw(self):
        if USE_SPRITES:
            screen.blit(POWERUP_IMAGE, self.rect)
        else:
            pygame.draw.circle(screen, YELLOW, self.rect.center, self.size // 2)


# 7. ฟังก์ชันสร้างสิ่งกีดขวางใหม่ (ขนาดเล็กมาก)
def create_new_obstacle():
    width = random.randint(20, 60)
    height = random.randint(30, 90)
    x = SCREEN_WIDTH + random.randint(300, 600)
    return Obstacle(x, width, height)


# 8. ฟังก์ชันอัปเดต High Score
def update_high_score(current_score):
    global high_score
    if current_score > high_score:
        high_score = current_score


# 9. ฟังก์ชันเริ่มเกมใหม่
def reset_game():
    global player, obstacles, power_ups, game_over, score, START_TIME, is_powered_up, power_up_start_time, banana_score

    player = Player()
    obstacles = [create_new_obstacle()]
    power_ups = []
    score = 0
    game_over = False
    START_TIME = time.time()

    is_powered_up = False
    power_up_start_time = 0
    banana_score = 0
    print("Game Restarted!")


# 10. เริ่มต้นเกมและตัวแปรควบคุม
player = Player()
obstacles = [create_new_obstacle()]
power_ups = []
game_over = False
score = 0
high_score = 0
START_TIME = time.time()
banana_score = 0

is_powered_up = False
power_up_start_time = 0

# 11. Game Loop หลัก
running = True
while running:

    # 11.1. Event Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.K_ESCAPE:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not game_over:
                player.jump()

            if event.key == pygame.K_RETURN and game_over:
                reset_game()

    if not game_over:
        current_time = time.time()

        # 11.2. อัปเดตตรรกะเกม
        player.update()
        score = int((current_time - START_TIME) * 10)

        # จัดการ Power-Up
        remaining_time = 0
        if is_powered_up:
            elapsed = current_time - power_up_start_time
            if elapsed >= POWER_UP_DURATION:
                is_powered_up = False
            else:
                remaining_time = POWER_UP_DURATION - elapsed

        # 11.3 - 11.6 (อัปเดตสิ่งกีดขวาง/Power-Up และตรวจจับการชน)
        for obstacle in list(obstacles):
            obstacle.move()

            if player.rect.colliderect(obstacle.rect):
                if not is_powered_up:
                    update_high_score(score)
                    game_over = True
                else:
                    obstacles.remove(obstacle)

            if obstacle.x + obstacle.width < 0:
                obstacles.remove(obstacle)

        for pu in list(power_ups):
            pu.move()

            if player.rect.colliderect(pu.rect):
                is_powered_up = True
                power_up_start_time = current_time
                power_ups.remove(pu)
                banana_score += 1

            if pu.x + pu.size < 0:
                power_ups.remove(pu)

        if not obstacles or obstacles[-1].x < SCREEN_WIDTH - random.randint(250, 450):
            obstacles.append(create_new_obstacle())

        if random.randint(1, 10) == 1 and not power_ups:
            power_ups.append(PowerUp())

        # 11.7. การวาด (Drawing)
        # วาดพื้นหลังเต็มจอ
        if USE_IMAGE_BG:
            screen.blit(BACKGROUND_IMAGE, (0, 0))
        else:
            screen.fill(WHITE)

        # วาดพื้นโปร่งใสสมบูรณ์ (ไม่มีสี)
        ground_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT - FLOOR_Y), pygame.SRCALPHA)
        screen.blit(ground_surface, (0, FLOOR_Y))

        for obstacle in obstacles:
            obstacle.draw()

        for pu in power_ups:
            pu.draw()

        player.draw(is_powered_up, remaining_time)

        # แสดงคะแนน
        # 1. Score (Y=10)
        score_text = FONT.render(f"Score: {score}", True, YELLOW)
        screen.blit(score_text, (10, 10))

        # 2. Banana Score (Y=40)
        banana_score_text = FONT.render(f"Banana: {banana_score}", True, YELLOW)
        screen.blit(banana_score_text, (10, 40))

        # 3. High Score (Y=70)
        high_score_text = FONT.render(f"High Score: {high_score}", True, YELLOW)
        screen.blit(high_score_text, (10, 70))


    else:
        # 10.6. สถานะ Game Over (ใช้ Dimmed Background)

        # 1. วาดพื้นหลังเดิม
        if USE_IMAGE_BG:
            screen.blit(BACKGROUND_IMAGE, (0, 0))
        else:
            screen.fill(WHITE)

            # 2. วาด OVERLAY สีดำโปร่งใสเพื่อให้ข้อความโดดเด่น
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        # 3. วาดข้อความ Game Over และ Score
        font_large = pygame.font.Font(None, 74)

        # GAME OVER เป็นสีแดง
        game_over_text = font_large.render("GAME OVER", True, RED)
        screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 120))

        font_small = FONT

        # Final Score เป็นสีเหลือง
        final_score_display_text = font_small.render(f"Final Score: {score}", True, YELLOW)
        screen.blit(final_score_display_text,
                    (SCREEN_WIDTH // 2 - final_score_display_text.get_width() // 2, SCREEN_HEIGHT // 2 - 60))

        # Final Banana Score เป็นสีเหลือง
        final_banana_text = font_small.render(f"Banana Collected: {banana_score}", True, YELLOW)
        screen.blit(final_banana_text,
                    (SCREEN_WIDTH // 2 - final_banana_text.get_width() // 2, SCREEN_HEIGHT // 2 - 20))

        # High Score เป็นสีเหลือง
        high_score_display_text = font_small.render(f"High Score: {high_score}", True, YELLOW)
        screen.blit(high_score_display_text,
                    (SCREEN_WIDTH // 2 - high_score_display_text.get_width() // 2, SCREEN_HEIGHT // 2 + 20))

        # Restart Prompt เป็นสีเหลือง
        restart_prompt_text = FONT.render("Press ENTER to Restart", True, YELLOW)
        screen.blit(restart_prompt_text,
                    (SCREEN_WIDTH // 2 - restart_prompt_text.get_width() // 2, SCREEN_HEIGHT // 2 + 80))

        # Exit Prompt เป็นสีเหลือง
        exit_text = FONT.render("Press ESC to exit.", True, YELLOW)
        screen.blit(exit_text, (SCREEN_WIDTH // 2 - exit_text.get_width() // 2, SCREEN_HEIGHT // 2 + 120))

    # 10.7. อัปเดตหน้าจอและควบคุมเฟรมเรต
    pygame.display.flip()
    clock.tick(60)

pygame.quit()