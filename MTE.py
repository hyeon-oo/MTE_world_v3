import random
import math
import sys
import os
from PIL import Image
import pygame
import pygame.mixer
import glob

pygame.mixer.init()

sound_files = glob.glob("sound/*.wav")
if not sound_files:
    print("사운드 파일이 존재하지 않습니다.")
else:
    print(f"사운드 파일이 {len(sound_files)}개 로드되었습니다.")
sounds = [pygame.mixer.Sound(file) for file in sound_files]

pygame.init()

WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
background_img = pygame.image.load("images/background.png")
background_img = pygame.transform.scale(background_img, (WINDOW_WIDTH, WINDOW_HEIGHT))

display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Ooong Nice!")
clock = pygame.time.Clock()

BLACK = (0, 0, 0)
RED   = (255, 0, 0)
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)

score_live = 11
TIME_LIMIT_MS = 60_000
ROTATE_START_MS = 30_000
OUTSIDE_MAX_MS = 3_000
outside_enter_time = None
rankings = []

TAZIRI_img_original = pygame.image.load("images/TAZIRI.png")
TAZIRI_img_original = pygame.transform.scale(TAZIRI_img_original, (210, 305))
TAZIRI_img_alt = pygame.image.load("images/TAZIRI_A.png")
TAZIRI_img_alt = pygame.transform.scale(TAZIRI_img_alt, (280, 380))
TAZIRI_direction = 1
TAZIRI_img = TAZIRI_img_original
TAZIRI_rect = TAZIRI_img.get_rect(centerx=WINDOW_WIDTH // 2, bottom=int(WINDOW_HEIGHT / 1.5))

projectile_img = pygame.image.load("images/green_juice.png")
projectile_img = pygame.transform.scale(projectile_img, (120, 50))
projectiles = []
projectile_speed = 15

gif = Image.open("images/Mouse2.gif")
gif_frames = []
try:
    while True:
        frame = gif.convert("RGBA")
        pg_img = pygame.image.fromstring(frame.tobytes(), frame.size, frame.mode)
        gif_frames.append(pg_img)
        gif.seek(gif.tell() + 1)
except EOFError:
    pass

gif_frame_index = 0
gif_last_update = pygame.time.get_ticks()
gif_frame_delay = 10

mouse_rect = gif_frames[0].get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))

font_path = "fonts/NanumGothic-Regular.ttf"
font = pygame.font.Font(font_path, 30)
game_font = font.render("WELCOME TO MTE WORLD!", True, GREEN, BLACK)
game_font_rect = game_font.get_rect(center=(WINDOW_WIDTH // 2, 25))

move_time = 0.0
last_move_time = 0
random_move_delay = 2000
relocation_distance = 200
min_speed, max_speed = 3, 12

start_time = pygame.time.get_ticks()

pygame.mixer.music.load("sound_back/Background.mp3")
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play(-1, 0.0)

last_sound_time = 0
sound_delay = 1000

running = True
while running:
    dt = clock.tick(60)
    dt_seconds = dt / 1000.0
    move_time += dt_seconds

    now = pygame.time.get_ticks()
    elapsed = now - start_time

    if elapsed >= TIME_LIMIT_MS:
        break

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False

    display_surface.blit(background_img, (0, 0))

    dx = mouse_rect.centerx - TAZIRI_rect.centerx
    dy = mouse_rect.centery - TAZIRI_rect.centery
    dist = math.hypot(dx, dy)

    if dist < relocation_distance and now - last_move_time > random_move_delay:
        mouse_rect.center = (
            random.randint(50, WINDOW_WIDTH - 50 - mouse_rect.width),
            random.randint(50, WINDOW_HEIGHT - 50 - mouse_rect.height)
        )
        last_move_time = now

    keys = pygame.key.get_pressed()
    SHIFT_KEY_PRESSED = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]

    if SHIFT_KEY_PRESSED:
        base_img = TAZIRI_img_alt
        direction_x = 0
        direction_y = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            direction_x = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            direction_x = 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            direction_y = -1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            direction_y = 1
        magnitude = math.hypot(direction_x, direction_y)
        if magnitude > 0:
            vx = direction_x / magnitude * projectile_speed
            vy = direction_y / magnitude * projectile_speed
            projectile_rect = projectile_img.get_rect(center=TAZIRI_rect.center)
            projectiles.append({"rect": projectile_rect, "vx": vx, "vy": vy})
    else:
        base_img = TAZIRI_img_original

    TAZIRI_img = pygame.transform.flip(base_img, TAZIRI_direction == -1, False)

    if dist != 0:
        nx, ny = dx / dist, dy / dist
    else:
        angle = random.random() * math.pi * 2
        nx, ny = math.cos(angle), math.sin(angle)

    base_speed = min_speed + (max_speed - min_speed) * max(0, (relocation_distance - dist) / relocation_distance)
    time_scale = (elapsed / TIME_LIMIT_MS)
    speed = (base_speed + (time_scale * 30)) * 0.8

    wobble_x = math.cos(move_time * 8) * 20
    wobble_y = math.sin(move_time * 8) * 20

    mouse_rect.x += nx * speed + wobble_x
    mouse_rect.y += ny * speed + wobble_y

    inside_bounds = pygame.Rect(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT).contains(mouse_rect)
    if not inside_bounds:
        if outside_enter_time is None:
            outside_enter_time = now
        elif now - outside_enter_time > OUTSIDE_MAX_MS:
            mouse_rect.center = (
                random.randint(50, WINDOW_WIDTH - 50 - mouse_rect.width),
                random.randint(50, WINDOW_HEIGHT - 50 - mouse_rect.height)
            )
            outside_enter_time = now
    else:
        outside_enter_time = None

    for projectile in projectiles[:]:
        projectile['rect'].x += projectile['vx']
        projectile['rect'].y += projectile['vy']
        display_surface.blit(projectile_img, projectile['rect'])

        if projectile['rect'].colliderect(mouse_rect):
            score_live = max(0, score_live - 1)
            projectiles.remove(projectile)
            mouse_rect.center = (
                random.randint(50, WINDOW_WIDTH - 50 - mouse_rect.width),
                random.randint(50, WINDOW_HEIGHT - 50 - mouse_rect.height)
            )
            last_move_time = now

            if now - last_sound_time >= sound_delay:
                sound = random.choice(sounds)
                sound.play()
                last_sound_time = now
        elif not pygame.Rect(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT).colliderect(projectile['rect']):
            projectiles.remove(projectile)

    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        TAZIRI_rect.x = max(0, TAZIRI_rect.x - 17)
        TAZIRI_direction = -1
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        TAZIRI_rect.x = min(WINDOW_WIDTH - TAZIRI_rect.width, TAZIRI_rect.x + 17)
        TAZIRI_direction = 1
    if keys[pygame.K_UP] or keys[pygame.K_w]:
        TAZIRI_rect.y = max(0, TAZIRI_rect.y - 17)
    if keys[pygame.K_DOWN] or keys[pygame.K_s]:
        TAZIRI_rect.y = min(WINDOW_HEIGHT - TAZIRI_rect.height, TAZIRI_rect.y + 17)

    if now - gif_last_update > gif_frame_delay:
        gif_frame_index = (gif_frame_index + 1) % len(gif_frames)
        gif_last_update = now

    if elapsed >= ROTATE_START_MS:
        mouse_angle = math.degrees(math.atan2(-ny, nx))
        frame_img = pygame.transform.rotate(gif_frames[gif_frame_index], mouse_angle)
        frame_rect = frame_img.get_rect(center=mouse_rect.center)
        display_surface.blit(frame_img, frame_rect)
    else:
        display_surface.blit(gif_frames[gif_frame_index], mouse_rect)

    display_surface.blit(TAZIRI_img, TAZIRI_rect)
    display_surface.blit(game_font, game_font_rect)

    remaining_ms = max(0, TIME_LIMIT_MS - elapsed)
    rem_sec = remaining_ms // 1000
    rem_min = rem_sec // 60
    rem_sec2 = rem_sec % 60
    timer_text = f"{rem_min:02d}:{rem_sec2:02d}"
    timer_surf = font.render(timer_text, True, WHITE)
    timer_rect = timer_surf.get_rect(center=(WINDOW_WIDTH//2, game_font_rect.bottom + 20))
    display_surface.blit(timer_surf, timer_rect)

    live_surf = font.render(f"아사람: {score_live}", True, RED, BLACK)
    display_surface.blit(live_surf, (10, 10))

    pygame.display.update()

    if score_live <= 0:
        rankings.append(elapsed / 1000)
        break

sound_played = False
game_clear = (score_live <= 0)
pygame.mixer.music.stop()

overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
overlay.fill((0, 0, 0, 180))
display_surface.blit(overlay, (0, 0))

end_font = pygame.font.Font(font_path, 80)
if game_clear:
    end_text = end_font.render("오옹나이스", True, GREEN)
    if not sound_played:
        sound_played = True
        pygame.mixer.Sound("sound/오옹나이스.wav").play()
else:
    end_text = end_font.render("나가", True, RED)
    if not sound_played:
        sound_played = True
        pygame.mixer.Sound("sound/나가.wav").play()

end_rect = end_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50))
display_surface.blit(end_text, end_rect)

play_time_text = f"Time: {elapsed / 1000:.2f}s"
play_time_surf = font.render(play_time_text, True, WHITE)
play_time_rect = play_time_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 20))
display_surface.blit(play_time_surf, play_time_rect)

if not game_clear:
    y_start = play_time_rect.bottom + 30
    button_font = pygame.font.Font(font_path, 50)
    button_text = button_font.render("다시하기", True, WHITE)
    button_rect = button_text.get_rect(center=(WINDOW_WIDTH // 2, y_start + 200))
    pygame.draw.rect(display_surface, (100, 100, 100), button_rect.inflate(40, 20))
    display_surface.blit(button_text, button_rect)

pygame.display.update()

if not game_clear:
    waiting = True
    while waiting:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                waiting = False
                running = False
            elif e.type == pygame.MOUSEBUTTONDOWN:
                if button_rect.collidepoint(e.pos):
                    pygame.quit()
                    os.execl(sys.executable, sys.executable, *sys.argv)
        pygame.time.delay(100)
else:
    pygame.time.delay(3000)

pygame.quit()
