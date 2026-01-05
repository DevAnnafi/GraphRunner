import pygame
import math
import heapq

# =====================
# Config
# =====================
WIDTH, HEIGHT = 800, 600
TILE = 40
GRID_W, GRID_H = WIDTH // TILE, HEIGHT // TILE
FPS = 60

PLAYER_SPEED = 220.0
ENEMY_SPEED = 160.0
RAIL_SPEED = 180.0

PLAYER_RADIUS = 12
ENEMY_RADIUS = 10

# Colors
BG = (20, 20, 25)
WALL = (70, 70, 80)
PLAYER_C = (240, 240, 255)
ENEMY_C = (255, 90, 90)
RAIL_C = (80, 160, 255)
GOAL_C = (120, 255, 160)
SAFE_C = (120, 255, 160)

# =====================
# Level
# =====================
LEVEL = [
    "####################",
    "#S.................#",
    "#..######..######..#",
    "#..................#",
    "#..######..######..#",
    "#................G.#",
    "#..######..######..#",
    "#..................#",
    "#..######..######..#",
    "#..................#",
    "#..######..######..#",
    "#..................#",
    "####################",
]

GRID_H = len(LEVEL)
GRID_W = len(LEVEL[0])

# =====================
# Dijkstra
# =====================
def dijkstra(start, goal, grid):
    pq = [(0, start)]
    dist = {start: 0}
    prev = {}

    while pq:
        d, u = heapq.heappop(pq)
        if u == goal:
            break
        if d > dist[u]:
            continue

        ux, uy = u
        for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
            vx, vy = ux + dx, uy + dy
            if 0 <= vx < GRID_W and 0 <= vy < GRID_H:
                if grid[vy][vx] != "#":
                    nd = d + 1
                    if nd < dist.get((vx,vy), 1e9):
                        dist[(vx,vy)] = nd
                        prev[(vx,vy)] = u
                        heapq.heappush(pq, (nd, (vx,vy)))

    path = []
    cur = goal
    while cur in prev:
        path.append(cur)
        cur = prev[cur]
    path.reverse()
    return path

# =====================
# Utility
# =====================
def grid_from_pixel(x, y):
    return int(x // TILE), int(y // TILE)

def pixel_center(cell):
    x, y = cell
    return x * TILE + TILE / 2, y * TILE + TILE / 2

def circle_rect_collision(cx, cy, r, rx, ry, rw, rh):
    closest_x = max(rx, min(cx, rx + rw))
    closest_y = max(ry, min(cy, ry + rh))
    dx = cx - closest_x
    dy = cy - closest_y
    return dx*dx + dy*dy < r*r

# =====================
# Entities
# =====================
class Player:
    def __init__(self, x, y):
        self.spawn_x = x
        self.spawn_y = y
        self.x = x
        self.y = y

    def die(self):
        self.x = self.spawn_x
        self.y = self.spawn_y

    def update(self, dt, grid):
        vx = vy = 0
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]: vx -= 1
        if keys[pygame.K_d]: vx += 1
        if keys[pygame.K_w]: vy -= 1
        if keys[pygame.K_s]: vy += 1

        length = math.hypot(vx, vy)
        if length > 0:
            vx /= length
            vy /= length

        nx = self.x + vx * PLAYER_SPEED * dt
        ny = self.y + vy * PLAYER_SPEED * dt

        if not self.collides(nx, self.y, grid):
            self.x = nx
        if not self.collides(self.x, ny, grid):
            self.y = ny

    def collides(self, x, y, grid):
        for gy in range(GRID_H):
            for gx in range(GRID_W):
                if grid[gy][gx] == "#":
                    if circle_rect_collision(
                        x, y, PLAYER_RADIUS,
                        gx*TILE, gy*TILE, TILE, TILE
                    ):
                        return True
        return False

    def draw(self, screen):
        pygame.draw.circle(screen, PLAYER_C, (int(self.x), int(self.y)), PLAYER_RADIUS)

class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.path = []
        self.path_index = 0
        self.repath_timer = 0

    def update(self, dt, grid, player):
        self.repath_timer -= dt
        if self.repath_timer <= 0:
            self.repath_timer = 0.5
            start = grid_from_pixel(self.x, self.y)
            goal = grid_from_pixel(player.x, player.y)
            self.path = dijkstra(start, goal, grid)
            self.path_index = 0

        if self.path_index < len(self.path):
            tx, ty = pixel_center(self.path[self.path_index])
            dx = tx - self.x
            dy = ty - self.y
            dist = math.hypot(dx, dy)

            if dist < 4:
                self.path_index += 1
            else:
                dx /= dist
                dy /= dist
                self.x += dx * ENEMY_SPEED * dt
                self.y += dy * ENEMY_SPEED * dt

    def draw(self, screen):
        pygame.draw.circle(screen, ENEMY_C, (int(self.x), int(self.y)), ENEMY_RADIUS)

class RailEnemy:
    def __init__(self, path):
        self.path = path
        self.i = 0
        self.dir = 1
        self.x, self.y = path[0]

    def update(self, dt):
        tx, ty = self.path[self.i]
        dx = tx - self.x
        dy = ty - self.y
        dist = math.hypot(dx, dy)

        if dist < 2:
            self.i += self.dir
            if self.i == len(self.path) or self.i < 0:
                self.dir *= -1
                self.i += self.dir * 2
            return

        dx /= dist
        dy /= dist
        self.x += dx * RAIL_SPEED * dt
        self.y += dy * RAIL_SPEED * dt

    def draw(self, screen):
        pygame.draw.circle(screen, RAIL_C, (int(self.x), int(self.y)), ENEMY_RADIUS)

class SafeZone:
    def __init__(self, rect):
        self.rect = rect

    def draw(self, screen):
        pygame.draw.rect(screen, SAFE_C, self.rect)

    def contains(self, x, y):
        return self.rect.collidepoint(x, y)

# =====================
# Main
# =====================
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Graph Runner")
    clock = pygame.time.Clock()

    grid = [list(r) for r in LEVEL]

    for y in range(GRID_H):
        for x in range(GRID_W):
            if grid[y][x] == "S":
                player = Player(*pixel_center((x,y)))
                grid[y][x] = "."
            if grid[y][x] == "G":
                goal_cell = (x,y)
                grid[y][x] = "."

    enemies = [
        Enemy(*pixel_center((10, 6))),
    ]

    rail_enemies = [
        RailEnemy([(200, 120), (600, 120)]),
        RailEnemy([(300, 300), (300, 500)]),
    ]

    safe_zones = [
        SafeZone(pygame.Rect(40, 40, 120, 120)),
    ]

    running = True
    while running:
        dt = clock.tick(FPS) / 1000

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False

        player.update(dt, grid)
        for en in enemies:
            en.update(dt, grid, player)
        for r in rail_enemies:
            r.update(dt)

        in_safe = any(z.contains(player.x, player.y) for z in safe_zones)
        if in_safe:
            player.spawn_x, player.spawn_y = player.x, player.y

        if not in_safe:
            for en in enemies + rail_enemies:
                if math.hypot(en.x - player.x, en.y - player.y) < PLAYER_RADIUS + ENEMY_RADIUS:
                    player.die()

        screen.fill(BG)

        for y in range(GRID_H):
            for x in range(GRID_W):
                if LEVEL[y][x] == "#":
                    pygame.draw.rect(screen, WALL, (x*TILE,y*TILE,TILE,TILE))

        for z in safe_zones:
            z.draw(screen)

        gx, gy = pixel_center(goal_cell)
        pygame.draw.circle(screen, GOAL_C, (int(gx), int(gy)), 14)

        player.draw(screen)
        for en in enemies:
            en.draw(screen)
        for r in rail_enemies:
            r.draw(screen)

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
