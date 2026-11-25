import pygame
import random
import time
import os

# ========== 常量 ==========
GRID_SIZE = 70
CELL_PX = 10
WIN_SIZE = GRID_SIZE * CELL_PX

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

DIR_KEYS = {
    pygame.K_UP:    (0, -1),
    pygame.K_DOWN:  (0, 1),
    pygame.K_LEFT:  (-1, 0),
    pygame.K_RIGHT: (1, 0),
}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def load_image(filename):
    path = os.path.join(BASE_DIR, filename)
    if not os.path.exists(path):
        print(f"[警告] 找不到图片：{path}，将使用纯色替代")
        return None
    img = pygame.image.load(path).convert_alpha()
    return pygame.transform.scale(img, (CELL_PX, CELL_PX))


def generate_maze(w, h):
    maze = [[1 for _ in range(w)] for _ in range(h)]
    sx, sy = 1, 1
    maze[sy][sx] = 0

    walls = []
    if sx + 1 < w - 1:
        walls.append((sx + 1, sy, 1, 0))
    if sy + 1 < h - 1:
        walls.append((sx, sy + 1, 0, 1))

    while walls:
        idx = random.randint(0, len(walls) - 1)
        wx, wy, dx, dy = walls.pop(idx)
        nx, ny = wx + dx, wy + dy

        if 0 < nx < w - 1 and 0 < ny < h - 1 and maze[ny][nx] == 1:
            maze[wy][wx] = 0
            maze[ny][nx] = 0

            if ny - 1 > 0 and maze[ny - 1][nx] == 1:
                walls.append((nx, ny - 1, 0, -1))
            if ny + 1 < h - 1 and maze[ny + 1][nx] == 1:
                walls.append((nx, ny + 1, 0, 1))
            if nx - 1 > 0 and maze[ny][nx - 1] == 1:
                walls.append((nx - 1, ny, -1, 0))
            if nx + 1 < w - 1 and maze[ny][nx + 1] == 1:
                walls.append((nx + 1, ny, 1, 0))

    return maze


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIN_SIZE, WIN_SIZE))
    pygame.display.set_caption("50×50 走迷宫 - MC材质版")
    clock = pygame.time.Clock()

    font = pygame.font.Font(None, 22)

    # 材质替换
    player_img = load_image("observer_front.png")       # 人物
    floor_img = load_image("smooth_stone.png")           # 地面
    wall_img = load_image("mossy_stone_bricks.png")     # 墙壁
    diamond_img = load_image("diamond.png")             # 终点

    move_interval = 120
    last_move_tick = 0
    key_stack = []
    markers = []

    maze = generate_maze(GRID_SIZE, GRID_SIZE)
    px, py = 1, 1
    start_time = time.time()
    finished = False
    finish_t = 0.0

    end_x = GRID_SIZE - 3
    end_y = GRID_SIZE - 3

    running = True
    while running:
        current_tick = pygame.time.get_ticks()
        dt = time.time() - start_time

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                if event.key in (pygame.K_SPACE, pygame.K_LALT, pygame.K_RALT):
                    maze = generate_maze(GRID_SIZE, GRID_SIZE)
                    px, py = 1, 1
                    start_time = time.time()
                    finished = False
                    finish_t = 0.0
                    key_stack.clear()
                    last_move_tick = 0
                    markers.clear()

                if event.key in (pygame.K_LCTRL, pygame.K_RCTRL):
                    markers.clear()

                if event.key in DIR_KEYS and event.key not in key_stack:
                    key_stack.append(event.key)

            if event.type == pygame.KEYUP:
                if event.key in DIR_KEYS and event.key in key_stack:
                    key_stack.remove(event.key)

            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                gx = mx // CELL_PX
                gy = my // CELL_PX

                if 0 <= gx < GRID_SIZE and 0 <= gy < GRID_SIZE:
                    if event.button == 1:
                        if (gx, gy) not in markers:
                            markers.append((gx, gy))
                    elif event.button == 3:
                        if (gx, gy) in markers:
                            markers.remove((gx, gy))

        if not finished and key_stack and current_tick - last_move_tick >= move_interval:
            dx, dy = DIR_KEYS[key_stack[-1]]
            nx = px + dx
            ny = py + dy
            if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE and maze[ny][nx] == 0:
                px, py = nx, ny
                last_move_tick = current_tick

        if not finished and px == end_x and py == end_y:
            finished = True
            finish_t = dt

        # ========== 绘制 ==========
        screen.fill(BLACK)

        # 地面 / 墙壁
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                pos = (x * CELL_PX, y * CELL_PX)
                if maze[y][x] == 0:
                    if floor_img:
                        screen.blit(floor_img, pos)
                    else:
                        pygame.draw.rect(screen, WHITE, (*pos, CELL_PX, CELL_PX))
                else:
                    if wall_img:
                        screen.blit(wall_img, pos)
                    else:
                        pygame.draw.rect(screen, BLACK, (*pos, CELL_PX, CELL_PX))

        # 标记连线
        if len(markers) >= 2:
            line_points = [
                (x * CELL_PX + CELL_PX // 2, y * CELL_PX + CELL_PX // 2)
                for x, y in markers
            ]
            pygame.draw.lines(screen, YELLOW, False, line_points, 2)

        # 标记点
        for x, y in markers:
            cx = x * CELL_PX + CELL_PX // 2
            cy = y * CELL_PX + CELL_PX // 2
            pygame.draw.circle(screen, YELLOW, (cx, cy), CELL_PX // 2 - 2)

        # 终点钻石
        if diamond_img:
            screen.blit(diamond_img, (end_x * CELL_PX, end_y * CELL_PX))
        else:
            end_cx = end_x * CELL_PX + CELL_PX // 2
            end_cy = end_y * CELL_PX + CELL_PX // 2
            pygame.draw.circle(screen, GREEN, (end_cx, end_cy), CELL_PX // 2 - 1)

        # 玩家
        if player_img:
            screen.blit(player_img, (px * CELL_PX, py * CELL_PX))
        else:
            cx = px * CELL_PX + CELL_PX // 2
            cy = py * CELL_PX + CELL_PX // 2
            pygame.draw.circle(screen, RED, (cx, cy), CELL_PX // 2 - 1)

        # 时间
        show_t = finish_t if finished else dt
        text_surf = font.render(f"Time: {show_t:.2f} s", True, (255, 255, 255))
        screen.blit(text_surf, (4, 4))

        if finished:
            clear_text = font.render(
                f"Cleared! {finish_t:.2f}s  Press Alt/Space Restart",
                True, (0, 255, 0)
            )
            screen.blit(clear_text, (WIN_SIZE // 2 - 170, WIN_SIZE // 2))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
