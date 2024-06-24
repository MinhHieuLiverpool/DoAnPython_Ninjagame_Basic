import random
import pygame
import math

from scripts.particle import Particle
from scripts.spark import Spark

class PhysicsEntity:
    def __init__(self, game, e_type, pos, size):
        self.game = game
        self.type = e_type
        self.pos = list(pos)
        self.size = size
        self.velocity = [0, 0] #list chứa tốc độ ngang và dọc
        self.collision = {'up': False, 'down': False, 'right': False, 'left': False}
        
        self.action = ''
        self.anim_offset = (-3, -3) #kich thuoc nhan vat khac voi hinh anh animation (hit box ko dung)
        self.flip = False # nhin sang trai hay phai
        self.set_action('idle')
        
        self.last_movement = [0, 0]
        
    def rect(self): #dùng để phát hiện va chạm.
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])    
    
    def set_action(self, action):
        if action != self.action:
            self.action = action
            self.animation = self.game.assets[self.type + '/' + self.action].copy()
            
        
    def update(self, tilemap, movement = (0, 0)):
        self.collision = {'up': False, 'down': False, 'right': False, 'left': False}
        frame_movement = (movement[0] + self.velocity[0], movement[1] + self.velocity[1])
        self.pos[0] += frame_movement[0]
        
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[0] > 0: #di chuyen huong qua phai
                    entity_rect.right = rect.left
                    self.collision['right'] = True
                if frame_movement[0] < 0:
                    entity_rect.left = rect.right
                    self.collision['left'] = True
                self.pos[0] = entity_rect.x
        
        self.pos[1] += frame_movement[1]
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[1] > 0: #di chuyen huong qua phai
                    entity_rect.bottom = rect.top
                    self.collision['down'] = True
                if frame_movement[1] < 0:
                    entity_rect.top = rect.bottom
                    self.collision['up'] = True
                    
                self.pos[1] = entity_rect.y
        
        if movement[0] > 0:
            self.flip = False
        if movement[0] < 0:
            self.flip = True    
        
        self.last_movement = movement
        
        self.velocity[1] = min(5, self.velocity[1] + 0.1) #tang toc do roi xuong
        
        if self.collision['down'] or self.collision['up']:
            self.velocity[1] = 0
        
        
        self.animation.update()
        

        
    def render(self, surf, offset=(0, 0)):
        surf.blit(pygame.transform.flip(self.animation.img(), self.flip, False), (self.pos[0] - offset[0] + self.anim_offset[0], self.pos[1] - offset[1] + self.anim_offset[1])) #flip action
        #surf.blit(self.game.assets['player'], (self.pos[0] - offset[0], self.pos[1] - offset[1]))
        
        
        
class Enemy(PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, 'enemy', pos, size)
        
        self.walking = 0
        
    def update(self, tilemap, movement=(0, 0)):
        if self.walking:
            if tilemap.solid_check((self.rect().centerx + (-7 if self.flip else 7), self.pos[1] + 23)):
                if (self.collision['right'] or self.collision['left']):
                    self.flip = not self.flip
                else:
                    movement = (movement[0] - 0.5 if self.flip else 0.5, movement[1])
            else:
                self.flip = not self.flip
            self.walking = max(0, self.walking - 1)
            if not self.walking:
                dis = (self.game.player.pos[0] - self.pos[0], self.game.player.pos[1] - self.pos[1])
                if (abs(dis[1]) < 16):
                    if (self.flip and dis[0] < 0):
                        self.game.projectiles.append([[self.rect().centerx - 7, self.rect().centery], -1.5, 0])
                        for i in range(4):
                            self.game.sparks.append(Spark(self.game.projectiles[-1][0], random.random() - 0.5 + math.pi, 2 + random.random()))
                    if (not self.flip and dis[0] > 0):
                        self.game.projectiles.append([[self.rect().centerx + 7, self.rect().centery], 1.5, 0])
                        for i in range(4):
                            self.game.sparks.append(Spark(self.game.projectiles[-1][0], random.random() - 0.5, 2 + random.random()))
        elif random.random() < 0.01:
            self.walking = random.randint(30, 120)
        
        super().update(tilemap, movement=movement)

        if movement[0] != 0:
            self.set_action('run')
        else:
            self.set_action('idle')
            
        if abs(self.game.player.dashing) >= 50: #dashing
            if self.rect().colliderect(self.game.player.rect()): #hit some thing
                for i in range(30):
                    angle = random.random() * math.pi * 2
                    speed = random.random() * 5
                    self.game.sparks.append(Spark(self.rect().center, angle, 2 + random.random()))
                    self.game.particles.append(Particle(self.game, 'particle', self.rect().center, velocity=[math.cos(angle + math.pi) * speed * 0.5, math.sin(angle + math.pi) * speed * 0.5], frame=random.randint(0, 7)))
                self.game.sparks.append(Spark(self.rect().center, 0, 5 + random.random()))
                self.game.sparks.append(Spark(self.rect().center, math.pi, 5 + random.random()))
                return True
            
    def render(self, surf, offset=(0, 0)):
        super().render(surf, offset=offset)

class Player(PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, 'player', pos, size)
        self.air_time = 0 #thoi gian dang o tren khong
        self.jumps = 1 #co the nhay hay khong/so lan nhay (neu cham tuong dc reset lan nhay)
        self.wall_slide = False
        self.dashing = 0
        
    def update(self, tilemap, movement=(0, 0)):
        super().update(tilemap, movement=movement)
        self.air_time += 1
        if self.air_time > 210:
            if not self.game.dead:
                pass
            self.game.dead += 1
        
        if self.collision['down']:
            self.air_time = 0
            self.jumps = 1
            
        self.wall_slide = False
        if (self.collision['right'] or self.collision['left']) and self.air_time > 4: #2 ben trai or phai la tuong va dang tren khong
            self.wall_slide = True
            self.velocity[1] = min(self.velocity[1], 0.5) #roi cham lai
            if self.collision['right']:
                self.flip = False
            else:
                self.flip = True
            self.set_action('wall_slide')
      
        if not self.wall_slide:
            if self.air_time > 4:
                self.set_action('jump')
            elif movement[0] != 0:
                self.set_action('run')
            else:
                self.set_action('idle')
        
        if abs(self.dashing) in {60, 50}: #bat dau hay ket thuc dash
            for i in range(20):
                angle = random.random() * math.pi * 2
                speed = random.random() * 0.5 + 0.5 #chon 1 so giua 0.5 va 1
                pvelocity = [math.cos(angle) * speed, math.sin(angle) * speed]
                self.game.particles.append(Particle(self.game, 'particle', self.rect().center, velocity=pvelocity, frame=random.randint(0, 7)))
        if self.dashing > 0:
            self.dashing = max(0, self.dashing - 1)
        if self.dashing < 0:
            self.dashing = min(0, self.dashing + 1)
        if abs(self.dashing) > 50:
            self.velocity[0] = abs(self.dashing) / self.dashing * 8 #frame dau cua dash (co doan code la phan cooldown cua dash nua ?????)
            if abs(self.dashing) == 51: # ket thuc dash
                self.velocity[0] *= 0.1
            pvelocity = [abs(self.dashing) / self.dashing * random.random() * 3, 0] #random num from 0 to 3, k dong den y
            self.game.particles.append(Particle(self.game, 'particle', self.rect().center, velocity=pvelocity, frame=random.randint(0, 7)))
        
        
        
        if self.velocity[0] > 0:
            self.velocity[0] = max(0, self.velocity[0] - 0.1)
        else:
            self.velocity[0] = min(0, self.velocity[0] + 0.1)
            
    def render(self, surf, offset=(0, 0)):
        if abs(self.dashing) <= 50: # khuc nay la dang cooldown cai dash hoac la ko muon dash
            super().render(surf, offset=offset) # cu render nhu cu thoi :))
            
        
            
    def jump(self):
        if self.wall_slide:
            if self.flip and self.last_movement[0] < 0:  
                self.velocity[0] = 3.5 #thay 1.5 di toi cua tuong lai no on hay cai cu lin 3.5 nay
                self.velocity[1] = -2.5
                self.air_time = 5
                self.jumps = max(self.jumps - 1, 0)
                return True
            elif not self.flip and self.last_movement[0] > 0:
                self.velocity[0] = -3.5
                self.velocity[1] = -2.5
                self.air_time = 5
                self.jumps = max(self.jumps - 1, 0)
                return True
            
        elif self.jumps:
            self.velocity[1] = -3
            self.jumps -= 1
            self.air_time = 5
            return True
        
    
    def dash(self):
        if not self.dashing:
            if self.flip:
                self.dashing = -60
            else:
                self.dashing = 60
                