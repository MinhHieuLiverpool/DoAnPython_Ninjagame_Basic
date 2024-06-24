import pygame
import sys
import subprocess
# Định nghĩa lớp Button
class Button:
    def __init__(self, x, y, width, height, color, text=''):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.text = text
        self.font = pygame.font.Font(None, 32)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        if self.text:
            text_surface = self.font.render(self.text, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=self.rect.center)
            screen.blit(text_surface, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

# Khởi tạo pygame
pygame.init()

# Cài đặt kích thước cửa sổ
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 720
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Main Menu")

# Load hình ảnh làm background
background_image = pygame.image.load('background.jpg').convert()
background_rect = background_image.get_rect()

button_height = 50
spacing = 10  # Khoảng cách giữa các nút
total_button_height = button_height * 3 + spacing * 2
start_y = (SCREEN_HEIGHT - total_button_height) // 2  # Vị trí y bắt đầu để các nút nằm ở giữa

button1 = Button((SCREEN_WIDTH - 200) // 2, start_y, 200, 50, (0, 255, 0), 'Start Game')
button3 = Button((SCREEN_WIDTH - 200) // 2, start_y + (button_height + spacing) * 2, 200, 50, (0, 255, 0), 'Quit')

class OptionsScreen:
    def __init__(self):
        self.running = True

    def run(self):
        while self.running:
            # Vẽ các phần tử trên màn hình tùy chọn
            # Xử lý sự kiện cho màn hình tùy chọn
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            pygame.display.update()

# Trạng thái ban đầu của trò chơi là màn hình menu chính
current_state = "menu"
# Vòng lặp game
running = True
while running:
    # Hiển thị background image
    screen.blit(background_image, background_rect)

    # Vẽ các nút
    button1.draw(screen)
    button3.draw(screen)

    # Xử lý sự kiện
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            if button1.is_clicked(pos):
                print('Start Game clicked')
                # Xử lý khi nút "Start Game" được nhấp vào
                subprocess.Popen(['python', 'game.py'])
                pygame.quit()  # Tắt pygame
                sys.exit()     
            elif button3.is_clicked(pos):
                print('Quit clicked')
                running = False
                pygame.quit()
                sys.exit()

    pygame.display.update()
