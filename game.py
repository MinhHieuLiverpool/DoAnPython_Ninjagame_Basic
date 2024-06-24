import pygame
import sys
import os
import math
import random

# Import các lớp và hàm cần thiết từ các module khác
from scripts.spark import Spark
from scripts.utils import load_image, load_images, Animation
from scripts.entities import PhysicsEntity, Player, Enemy
from scripts.tilemap import Tilemap
from scripts.particle import Particle

class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("ninja game")
        self.screen = pygame.display.set_mode((1024, 720))
        self.display = pygame.Surface((512, 360))
        self.clock = pygame.time.Clock()
        self.movement = [False, False]
        self.assets = {
            'decor': load_images('tiles/decor'),
            'grass': load_images('grass'),
            'large_decor': load_images('large_decor'),
            'stone': load_images('stone'),
            'player': load_image('entities/player.png'),
            'background': load_image('background.png'),
            'enemy/idle': Animation(load_images('entities/enemy/idle'), img_dur=6),
            'enemy/run': Animation(load_images('entities/enemy/run'), img_dur=4),
            'player/idle' : Animation(load_images('entities/player/idle'), img_dur=6),
            'player/run' : Animation(load_images('entities/player/run'), img_dur=4),
            'player/jump' : Animation(load_images('entities/player/jump')),
            'player/slide' : Animation(load_images('entities/player/slide')),
            'player/wall_slide' : Animation(load_images('entities/player/wall_slide')),
            'particle/particle': Animation(load_images('particles/particle'), img_dur=6, loop=False),
            'projectile': load_image('projectile.png'),
        }
        self.player = Player(self, (50, 50), (8,15))
        self.tilemap = Tilemap(self, tile_size= 16)
        self.level = 0
        self.load_level(self.level)
        self.paused = False
        
    def load_level(self, map_id):   
        self.tilemap.load(f'data/maps/{map_id}.json')
        self.enemies = []
        for spawner in self.tilemap.extract([('spawners', 0), ('spawners', 1)]):
            if spawner['variant'] == 0:
                self.player.pos = spawner['pos']
            else: 
                self.enemies.append(Enemy(self, spawner['pos'], (8, 15)))
        self.particles = []
        self.projectiles = []
        self.sparks = []
        self.scroll = [0, 0]
        self.dead = 0
        self.transition = -30
    
    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.paused = not self.paused
                if not self.paused:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_LEFT:
                            self.movement[0] = True
                        if event.key == pygame.K_RIGHT:
                            self.movement[1] = True
                        if event.key == pygame.K_UP:
                            self.player.jump()
                        if event.key == pygame.K_x:
                            self.player.dash()
                    if event.type == pygame.KEYUP:
                        if event.key == pygame.K_LEFT:
                            self.movement[0] = False
                        if event.key == pygame.K_RIGHT:
                            self.movement[1] = False
            
            if not self.paused:
                self.display.blit(self.assets['background'], (0, 0))
                
                if not len(self.enemies):
                    self.transition += 1
                    if self.transition > 30:
                        self.level = min(self.level + 1, len(os.listdir('data/maps'))-1)
                        self.load_level(self.level)
                if self.transition < 0:
                    self.transition += 1
                
                if self.dead:
                    self.dead += 1
                    if self.dead >= 10:
                        self.transition = min(self.transition + 1,30)
                    if self.dead > 40:
                        self.load_level(self.level)
                
                self.scroll[0] += (self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0]) / 60
                self.scroll[1] += (self.player.rect().centery - self.display.get_height() / 2 - self.scroll[1]) / 60
                render_scroll = (int(self.scroll[0]), int(self.scroll[1]))
                
                self.tilemap.render(self.display, offset = render_scroll)
                
                for enemy in self.enemies.copy():
                    kill = enemy.update(self.tilemap, (0, 0))
                    enemy.render(self.display, offset=render_scroll)
                    if kill:
                        self.enemies.remove(enemy)
                
                if not self.dead:
                    self.player.update(self.tilemap, (self.movement[1] - self.movement[0], 0))
                    self.player.render(self.display, offset = render_scroll)    
                
                for projectile in self.projectiles.copy():
                    projectile[0][0] += projectile[1]
                    projectile[2] += 1
                    img = self.assets['projectile']
                    self.display.blit(img, (projectile[0][0] - img.get_width() / 2 - render_scroll[0], projectile[0][1] - img.get_height() / 2 - render_scroll[1]))
                    if self.tilemap.solid_check(projectile[0]):
                        self.projectiles.remove(projectile)
                        for i in range(4):
                            self.sparks.append(Spark(projectile[0] , random.random() - 0.5, 2 + random.random()))
                    elif projectile[2] > 360:
                        self.projectiles.remove(projectile)
                    elif abs(self.player.dashing) < 50:
                        if self.player.rect().collidepoint(projectile[0]):
                            self.projectiles.remove(projectile)
                            self.dead += 1
                            for i in range(30):
                                angle = random.random() * math.pi * 2
                                speed = random.random() * 5
                                self.sparks.append(Spark(self.player.rect().center, angle, 2 + random.random()))
                                self.particles.append(Particle(self, 'particle', self.player.rect().center, velocity=[math.cos(angle + math.pi) * speed * 0.5, math.sin(angle + math.pi) * speed * 0.5], frame=random.randint(0, 7)))
                
                for spark in self.sparks.copy():
                    kill = spark.update()
                    spark.render(self.display, offset=render_scroll)
                    if kill:
                        self.sparks.remove(spark)
                
                for particle in self.particles.copy():
                    kill = particle.update()
                    particle.render(self.display, offset=render_scroll)
                    if kill:
                        self.particles.remove(particle)
            
            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
            pygame.display.update()
            self.clock.tick(60)

def main():
    pygame.init()
    pygame.display.set_caption("ninja game")
    screen = pygame.display.set_mode((1024, 720))
    clock = pygame.time.Clock()
    
    game = Game()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            # Xử lý các sự kiện khác nếu cần
        
        # Gọi phương thức run của đối tượng Game
        game.run()
        
        pygame.display.update()
        clock.tick(60)

if __name__ == "__main__":
    main()
