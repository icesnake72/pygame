import pygame
from queue import PriorityQueue
import math

# Pygame 초기화
pygame.init()

# 화면 크기 설정
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("캐릭터 이동 예제")

# 색깔 정의
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
GREEN = (0, 255, 0)

# 격자 크기 및 개수
grid_size = 40
grid_rows = screen_height // grid_size
grid_cols = screen_width // grid_size

# 격자 생성
grid = []
for row in range(grid_rows):
    grid.append([])
    for col in range(grid_cols):
        grid[row].append(0)

# 시작 지점과 도착 지점 설정
start = (0, 0)
end = (grid_rows - 1, grid_cols - 1)

# 이웃 노드 이동 방향 (상, 하, 좌, 우, 대각선)
neighbor_directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]

def draw_grid():
    # 격자 그리기
    for row in range(grid_rows):
        for col in range(grid_cols):
            rect = pygame.Rect(col * grid_size, row * grid_size, grid_size, grid_size)
            pygame.draw.rect(screen, WHITE, rect, 1)

def draw_path(came_from, current):
    # 최단 경로 그리기
    while current in came_from:
        current = came_from[current]
        row, col = current
        rect = pygame.Rect(col * grid_size, row * grid_size, grid_size, grid_size)
        pygame.draw.rect(screen, GREEN, rect)


def heuristic(node1, node2):
    # 휴리스틱 함수 (여기서는 맨해튼 거리 사용)
    x1, y1 = node1
    x2, y2 = node2
    return abs(x1 - x2) + abs(y1 - y2)


def a_star():
    # A* 알고리즘을 통해 최단 경로 탐색
    open_set = PriorityQueue()
    open_set.put((0, start))
    came_from = {}
    g_score = {position: float('inf') for position in [(row, col) for row in range(grid_rows) for col in range(grid_cols)]}
    g_score[start] = 0
    f_score = {position: float('inf') for position in [(row, col) for row in range(grid_rows) for col in range(grid_cols)]}
    f_score[start] = heuristic(start, end)

    while not open_set.empty():
        current = open_set.get()[1]

        if current == end:
            draw_path(came_from, current)
            break

        for direction in neighbor_directions:
            row, col = current
            new_row = row + direction[0]
            new_col = col + direction[1]

            if 0 <= new_row < grid_rows and 0 <= new_col < grid_cols:
                neighbor = (new_row, new_col)
                tentative_g_score = g_score[current] + 1

                if tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + heuristic(neighbor, end)
                    open_set.put((f_score[neighbor], neighbor))

    pygame.display.update()


# 캐릭터 이미지 로드
character_image = pygame.Surface((grid_size, grid_size))
character_image.fill(GRAY)

# 캐릭터 초기 위치
character_x = 0
character_y = 0

# 게임 루프
running = True
a_star_complete = False
clock = pygame.time.Clock()
while running:
    # 이벤트 처리
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and not a_star_complete:
            # 마우스 클릭 시 A* 알고리즘 실행
            a_star()
            a_star_complete = True

    # 게임 화면 업데이트
    screen.fill(BLACK)

    # 격자 그리기
    draw_grid()

    # 캐릭터 그리기
    screen.blit(character_image, (character_x * grid_size, character_y * grid_size))

    pygame.display.flip()

    # 초당 프레임 설정
    clock.tick(60)

# Pygame 종료
pygame.quit()
