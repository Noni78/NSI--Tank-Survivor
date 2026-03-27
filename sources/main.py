import math
import os
import random
import sys
from dataclasses import dataclass
from typing import Optional
import pygame

BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "datas")

WIDTH, HEIGHT = 1500, 800
FPS = 60

#################
# --- Color --- #
#################
BG_COLOR = (18, 20, 24)
WHITE = (240, 240, 240)
GREEN = (80, 220, 120)
RED = (230, 70, 70)
BLUE = (80, 170, 240)
YELLOW = (240, 210, 90)
PURPLE = (160, 120, 240)
CYAN = (120, 220, 255)

####################
# --- Fonction --- #
####################
def clamp(value, minimum, maximum):
    return max(minimum, min(value, maximum))

def vec_from_angle(angle):
    return math.cos(angle), math.sin(angle)

def distance(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])

def point_segment_distance(px, py, ax, ay, bx, by):
    abx = bx - ax
    aby = by - ay
    apx = px - ax
    apy = py - ay
    ab_len2 = abx * abx + aby * aby
    if ab_len2 <= 1e-9:
        return math.hypot(apx, apy)
    t = (apx * abx + apy * aby) / ab_len2
    t = max(0.0, min(1.0, t))
    cx = ax + abx * t
    cy = ay + aby * t
    return math.hypot(px - cx, py - cy)

def random_spawn_point():
    side = random.choice(["top", "bottom", "left", "right"])
    if side == "top":
        return random.randint(0, WIDTH), -30
    if side == "bottom":
        return random.randint(0, WIDTH), HEIGHT + 30
    if side == "left":
        return -30, random.randint(0, HEIGHT)
    return WIDTH + 30, random.randint(0, HEIGHT)

###################
# --- Classes --- #
###################

class Projectile:
    def __init__(self, x, y, vx, vy, damage, color=YELLOW, radius=4, owner="player"):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.damage = damage
        self.radius = radius
        self.color = color
        self.owner = owner

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt

    def offscreen(self):
        return self.x < -50 or self.x > WIDTH + 50 or self.y < -50 or self.y > HEIGHT + 50

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

class Rocket:
    _sprite_base = None
    _sprite_missing = False

    def __init__(self, x, y, vx, vy, damage, target, get_target, explosion_radius=60, radius=10):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.damage = damage
        self.explosion_radius = explosion_radius
        self.radius = radius
        self.rotation = math.degrees(math.atan2(vy, vx)) - 90
        self.target = target
        self.get_target = get_target
        self.speed = math.hypot(vx, vy)
        self.turn_rate = 1.4
        self.sprite = self.load_sprite()
        self.life = 10.0

    def load_sprite(self):
        if Rocket._sprite_base is None and not Rocket._sprite_missing:
            path = os.path.join(DATA_DIR, "rocket.png")
            if os.path.exists(path):
                try:
                    Rocket._sprite_base = pygame.image.load(path).convert_alpha()
                except pygame.error:
                    Rocket._sprite_missing = True
            else:
                Rocket._sprite_missing = True
        if Rocket._sprite_base is None:
            return None
        size = self.radius * 2
        return pygame.transform.smoothscale(Rocket._sprite_base, (size, size))

    def update(self, dt):
        self.life -= dt
        if self.target is None or self.target.hp <= 0:
            self.target = self.get_target()
        if self.target and self.target.hp > 0:
            dx = self.target.x - self.x
            dy = self.target.y - self.y
            dist = math.hypot(dx, dy) or 1
            desired_vx = dx / dist * self.speed
            desired_vy = dy / dist * self.speed
            ax = (desired_vx - self.vx) * self.turn_rate
            ay = (desired_vy - self.vy) * self.turn_rate
            self.vx += ax * dt
            self.vy += ay * dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.rotation = math.degrees(math.atan2(self.vy, self.vx)) - 90

    def offscreen(self):
        return (
            self.life <= 0
            or self.x < -60
            or self.x > WIDTH + 60
            or self.y < -60
            or self.y > HEIGHT + 60
        )

    def draw(self, screen):
        if self.sprite:
            rotated = pygame.transform.rotate(self.sprite, self.rotation)
            rect = rotated.get_rect(center=(int(self.x), int(self.y)))
            screen.blit(rotated, rect.topleft)
        else:
            pygame.draw.circle(screen, (255, 180, 80), (int(self.x), int(self.y)), self.radius)


class Explosion:
    def __init__(self, x, y, radius, duration=0.25):
        self.x = x
        self.y = y
        self.radius = radius
        self.duration = duration
        self.time_left = duration

    def update(self, dt):
        self.time_left -= dt

    def draw(self, screen):
        t = max(0.0, 1.0 - self.time_left / self.duration)
        r = int(self.radius * (0.3 + 0.7 * t))
        alpha = int(180 * (1.0 - t))
        surf = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(surf, (255, 200, 120, alpha), (r + 2, r + 2), r)
        pygame.draw.circle(surf, (255, 120, 60, alpha), (r + 2, r + 2), int(r * 0.7))
        screen.blit(surf, (int(self.x - r - 2), int(self.y - r - 2)))

# --- Items au sol --- #
class UpgradePickup:
    def __init__(self, x, y, upgrade_type):
        self.x = x
        self.y = y
        self.type = upgrade_type
        self.radius = 16
        self.time_left = 15.0
        self.sprite = self.load_sprite()
        self.color = {
            "shield": PURPLE,
            "multishot": WHITE,
            "haste": (120, 240, 200),
            "heal": GREEN,
        }.get(upgrade_type, WHITE)

    def load_sprite(self):
        if self.type == "shield":
            filename = "shieldicon.png"
        elif self.type == "heal":
            filename = "heal.png"
        elif self.type == "haste":
            filename = "haste.png"
        elif self.type == "multishot":
            filename = "multishot.png"
        else:
            return None
        path = os.path.join(DATA_DIR, filename)
        if os.path.exists(path):
            try:
                img = pygame.image.load(path).convert_alpha()
                size = self.radius * 2
                return pygame.transform.smoothscale(img, (size, size))
            except pygame.error:
                return None
        return None

    def draw(self, screen):
        if self.type == "haste":
            halo = pygame.Surface((self.radius * 5, self.radius * 5), pygame.SRCALPHA)
            pygame.draw.circle(
                halo,
                (180, 120, 255, 40),
                (halo.get_width() // 2, halo.get_height() // 2),
                self.radius * 2,
            )
            rect = halo.get_rect(center=(int(self.x), int(self.y)))
            screen.blit(halo, rect.topleft)
        if self.sprite:
            rect = self.sprite.get_rect(center=(int(self.x), int(self.y)))
            screen.blit(self.sprite, rect.topleft)
        else:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

    def update(self, dt):
        self.time_left -= dt

class ExpGem:
    _sprite_base = None
    _sprite_missing = False

    def __init__(self, x, y, amount=1):
        self.x = x
        self.y = y
        self.amount = amount
        self.radius = 6
        self.collect_radius = 30
        self.vx = 0.0
        self.vy = 0.0
        self.attract = 140.0
        self.max_speed = 160.0
        self.drag = 0.9
        self.pickup_range = 50.0
        self.time_left = 12.0
        self.rush_active = False
        self.rush_time = 0.0
        self.rush_duration = 0.0
        self.sprite = self.load_sprite()

    def load_sprite(self):
        if ExpGem._sprite_base is None and not ExpGem._sprite_missing:
            path = os.path.join(DATA_DIR, "gem.png")
            if os.path.exists(path):
                try:
                    ExpGem._sprite_base = pygame.image.load(path).convert_alpha()
                except pygame.error:
                    ExpGem._sprite_missing = True
            else:
                ExpGem._sprite_missing = True
        if ExpGem._sprite_base is None:
            return None
        size = self.radius * 2
        return pygame.transform.smoothscale(ExpGem._sprite_base, (size, size))

    def update(self, dt, player_pos):
        self.time_left -= dt
        if self.rush_active:
            self.rush_time += dt
            dx = player_pos[0] - self.x
            dy = player_pos[1] - self.y
            dist = math.hypot(dx, dy)
            if dist <= 0.1:
                return
            time_left = max(0.05, self.rush_duration - self.rush_time)
            speed = dist / time_left
            move = min(dist, speed * dt)
            self.x += dx / dist * move
            self.y += dy / dist * move
            return
        dx = player_pos[0] - self.x
        dy = player_pos[1] - self.y
        dist = math.hypot(dx, dy)
        if dist > self.pickup_range:
            self.vx = 0.0
            self.vy = 0.0
            return
        dist = dist or 1.0
        ax = dx / dist * self.attract
        ay = dy / dist * self.attract
        self.vx += ax * dt
        self.vy += ay * dt
        self.vx *= self.drag
        self.vy *= self.drag
        speed = math.hypot(self.vx, self.vy)
        if speed > self.max_speed:
            scale = self.max_speed / speed
            self.vx *= scale
            self.vy *= scale
        self.x += self.vx * dt
        self.y += self.vy * dt

    def start_rush(self, duration):
        self.rush_active = True
        self.rush_time = 0.0
        self.rush_duration = duration

    def draw(self, screen):
        if self.sprite:
            rect = self.sprite.get_rect(center=(int(self.x), int(self.y)))
            screen.blit(self.sprite, rect.topleft)
        else:
            pygame.draw.circle(screen, CYAN, (int(self.x), int(self.y)), self.radius)

# --- Ennemi --- #


class Enemy:
    def __init__(self, x, y, kind, wave):
        self.x = x
        self.y = y
        self.kind = kind
        base_speed = 70 + wave * 3
        self.speed = base_speed
        self.radius = 14
        self.max_hp = 20
        self.shoot_cooldown = 0.0
        self.target_height = int(HEIGHT * 0.06)
        self.sprite = None
        self.rotation = 0.0
        self.beam_timer = 0.0
        self.beam_charge = 0.0
        self.beam_active = 0.0
        self.beam_angle = 0.0
        self.beam_length = WIDTH
        self.beam_width = 14

        if kind == "fast":
            self.speed *= 3.0
            self.target_height = int(HEIGHT * 0.05)
            self.max_hp = 20 + wave * 6
        elif kind == "tank":
            self.speed *= 0.65
            self.target_height = int(HEIGHT * 0.12)
            self.max_hp = 75 + wave * 12
            self.beam_timer = 2.0
        elif kind == "shooter":
            self.speed *= 0.9
            self.target_height = int(HEIGHT * 0.065)
            self.max_hp = 30 + wave * 8
            self.shoot_cooldown = random.uniform(0.2, 0.8)
        else:
            self.max_hp = 25 + wave * 6

        self.sprite = self.load_sprite()
        if self.sprite:
            self.radius = self.sprite.get_width() / 2

        self.hp = self.max_hp
        self.burn_timer = 0.0
        self.burn_dps = 0.0
        self.fire_orb_hit_cd = 0.0

    def load_sprite(self):
        if self.kind == "basic":
            filename = "dronebleu.png"
        elif self.kind == "fast":
            filename = "drone.png"
        elif self.kind == "tank":
            filename = "tank.png"
        elif self.kind == "shooter":
            filename = "shooter.png"
        else:
            return None
        path = os.path.join(DATA_DIR, filename)
        if os.path.exists(path):
            try:
                img = pygame.image.load(path).convert_alpha()
                scale = self.target_height / img.get_height()
                size = (int(img.get_width() * scale), int(img.get_height() * scale))
                return pygame.transform.smoothscale(img, size)
            except pygame.error:
                return None
        return None
    
    def angle_toward(self, player_pos):
        dx = self.x - player_pos[0]
        dy = player_pos[1] - self.y
        return math.atan2(dy, dx)
    
    def update(self, dt, player_pos, projectiles, wave):
        dx = player_pos[0] - self.x
        dy = player_pos[1] - self.y
        dist = math.hypot(dx, dy) or 1
        vx = dx / dist * self.speed
        vy = dy / dist * self.speed
        self.x += vx * dt
        self.y += vy * dt
        self.rotation = math.degrees(self.angle_toward(player_pos)) + 180

        if self.burn_timer > 0:
            self.burn_timer -= dt
            self.hp -= self.burn_dps * dt
        self.fire_orb_hit_cd = max(0.0, self.fire_orb_hit_cd - dt)

        if self.kind == "tank":
            if self.beam_active > 0:
                self.beam_active -= dt
            elif self.beam_charge > 0:
                self.beam_charge -= dt
                if self.beam_charge <= 0:
                    self.beam_active = 0.35
            else:
                self.beam_timer -= dt
                if self.beam_timer <= 0:
                    self.beam_timer = 10.0
                    self.beam_charge = 1.0
                    self.beam_angle = math.atan2(dy, dx)

        if self.kind == "shooter":
            self.shoot_cooldown -= dt
            if self.shoot_cooldown <= 0:
                self.shoot_cooldown = max(0.4, 1.8 - wave * 0.05) + random.random() * 0.5
                angle = math.atan2(dy, dx)
                sx, sy = vec_from_angle(angle)
                proj = Projectile(
                    self.x,
                    self.y,
                    sx * (220 + wave * 6),
                    sy * (220 + wave * 6),
                    damage=10 + wave * 0.35,
                    color=RED,
                    radius=4,
                    owner="enemy",
                )
                projectiles.append(proj)

    def draw(self, screen):
        if self.sprite:
            rotated = pygame.transform.rotate(self.sprite, self.rotation)
            rect = rotated.get_rect(center=(int(self.x), int(self.y)))
            screen.blit(rotated, rect.topleft)
        else:
            pygame.draw.circle(screen, (200, 200, 200), (int(self.x), int(self.y)), self.radius)
        if self.kind == "tank":
            if self.beam_charge > 0:
                self._draw_beam(screen, (255, 200, 80), 4)
            if self.beam_active > 0:
                self._draw_beam(screen, (255, 80, 40), 6)
        if self.burn_timer > 0:
            pygame.draw.circle(screen, (255, 120, 60), (int(self.x), int(self.y)), self.radius + 4, 2)
        hp_ratio = self.hp / self.max_hp
        if hp_ratio < 1:
            bar_w = self.radius * 2
            bar_h = 4
            x = self.x - self.radius
            y = self.y - self.radius - 8
            pygame.draw.rect(screen, (60, 60, 60), (x, y, bar_w, bar_h))
            pygame.draw.rect(screen, GREEN, (x, y, bar_w * hp_ratio, bar_h))

    def _draw_beam(self, screen, color, width):
        ex = self.x + math.cos(self.beam_angle) * self.beam_length
        ey = self.y + math.sin(self.beam_angle) * self.beam_length
        pygame.draw.line(screen, color, (self.x, self.y), (ex, ey), width)

    def beam_hits_player(self, player_pos):
        if self.beam_active <= 0:
            return False
        dx = player_pos[0] - self.x
        dy = player_pos[1] - self.y
        dir_x = math.cos(self.beam_angle)
        dir_y = math.sin(self.beam_angle)
        proj = dx * dir_x + dy * dir_y
        if proj < 0 or proj > self.beam_length:
            return False
        perp = abs(dx * dir_y - dy * dir_x)
        return perp <= self.beam_width


class BossZone:
    def __init__(self, x, y, radius, damage, charge_time=0.8, duration=0.4):
        self.x = x
        self.y = y
        self.radius = radius
        self.damage = damage
        self.charge_time = charge_time
        self.duration = duration
        self.time_left = charge_time + duration
        self.triggered = False
        self.should_damage = False

    def update(self, dt):
        self.time_left -= dt
        if not self.triggered and self.time_left <= self.duration:
            self.triggered = True
            self.should_damage = True

    def draw(self, screen):
        if self.time_left <= 0:
            return
        if self.time_left > self.duration:
            t = 1.0 - (self.time_left - self.duration) / self.charge_time
            alpha = int(80 + 120 * t)
            surf = pygame.Surface((self.radius * 2 + 6, self.radius * 2 + 6), pygame.SRCALPHA)
            pygame.draw.circle(
                surf,
                (255, 120, 60, alpha),
                (surf.get_width() // 2, surf.get_height() // 2),
                self.radius,
                3,
            )
            screen.blit(surf, (int(self.x - self.radius - 3), int(self.y - self.radius - 3)))
        else:
            alpha = int(200 * (self.time_left / self.duration))
            surf = pygame.Surface((self.radius * 2 + 8, self.radius * 2 + 8), pygame.SRCALPHA)
            pygame.draw.circle(
                surf,
                (255, 80, 40, alpha),
                (surf.get_width() // 2, surf.get_height() // 2),
                int(self.radius * 1.1),
            )
            screen.blit(surf, (int(self.x - self.radius - 4), int(self.y - self.radius - 4)))


class Boss:
    def __init__(self, wave):
        self.x = WIDTH / 2
        self.y = HEIGHT * 0.18
        self.max_hp = 1200 + wave * 450
        self.hp = self.max_hp
        self.radius = 42
        self.speed = 70 * 0.65
        self.attack_cooldown = 2.0
        self.attack_timer = 0.0
        self.spawn_delay = 5.0
        self.state = "idle"
        self.state_time = 0.0
        self.laser_angle = 0.0
        self.laser_duration = 5.0
        self.laser_hit_timer = 0.0
        self.projectile_burst = 0
        self.projectile_timer = 0.0
        self.zone_burst = 0
        self.zone_timer = 0.0
        self.burn_timer = 0.0
        self.burn_dps = 0.0
        self.fire_orb_hit_cd = 0.0

    def phase(self):
        ratio = max(0.0, min(1.0, self.hp / self.max_hp))
        return int((1.0 - ratio) * 4)

    def update(self, dt, player_pos, projectiles, zones, wave, damage_value):
        if self.burn_timer > 0:
            self.burn_timer -= dt
            self.hp -= self.burn_dps * dt
        self.fire_orb_hit_cd = max(0.0, self.fire_orb_hit_cd - dt)
        if self.spawn_delay > 0:
            self.spawn_delay = max(0.0, self.spawn_delay - dt)
            return
        dx = player_pos[0] - self.x
        dy = player_pos[1] - self.y
        dist = math.hypot(dx, dy) or 1
        self.x += dx / dist * self.speed * dt
        self.y += dy / dist * self.speed * dt

        phase = self.phase()

        if self.state == "idle":
            self.attack_timer -= dt
            if self.attack_timer <= 0:
                self.attack_timer = self.attack_cooldown
                self.state = random.choice(["laser", "projectiles", "zones"])
                self.state_time = 0.0
                self.projectile_burst = 0
                self.projectile_timer = 0.0
                self.zone_burst = 0
                self.zone_timer = 0.0
        elif self.state == "laser":
            self.state_time += dt
            self.laser_hit_timer = max(0.0, self.laser_hit_timer - dt)
            self.laser_angle += (0.45 + 0.125 * phase) * dt
            if self.state_time >= self.laser_duration:
                self.state = "idle"
                self.laser_hit_timer = 0.0
        elif self.state == "projectiles":
            self.state_time += dt
            self.projectile_timer -= dt
            total = 10 + phase * 2
            if self.projectile_burst < total and self.projectile_timer <= 0:
                self.projectile_timer = 0.18
                self.projectile_burst += 1
                ang = math.atan2(dy, dx) + random.uniform(-0.3, 0.3)
                vx, vy = vec_from_angle(ang)
                proj = Projectile(
                    self.x,
                    self.y,
                    vx * (200 + 25 * phase),
                    vy * (200 + 25 * phase),
                    damage=damage_value,
                    color=(255, 140, 80),
                    radius=10,
                    owner="enemy",
                )
                projectiles.append(proj)
            if self.projectile_burst >= total:
                self.state = "idle"
        elif self.state == "zones":
            self.state_time += dt
            self.zone_timer -= dt
            total = 3 + phase
            if self.zone_burst < total and self.zone_timer <= 0:
                self.zone_timer = 0.45
                self.zone_burst += 1
                zx = player_pos[0] + random.uniform(-40, 40)
                zy = player_pos[1] + random.uniform(-40, 40)
                radius = 70 + phase * 12
                zones.append(BossZone(zx, zy, radius, damage_value))
            if self.zone_burst >= total:
                self.state = "idle"

    def laser_hits_player(self, player_pos):
        if self.state != "laser":
            return False
        phase = self.phase()
        width = 12 + phase * 3.5
        for i in range(6):
            ang = self.laser_angle + i * (math.tau / 6)
            ex = self.x + math.cos(ang) * WIDTH
            ey = self.y + math.sin(ang) * WIDTH
            dist = point_segment_distance(player_pos[0], player_pos[1], self.x, self.y, ex, ey)
            if dist <= width:
                return True
        return False

    def can_laser_damage(self):
        if self.laser_hit_timer > 0:
            return False
        self.laser_hit_timer = 0.45
        return True

    def draw(self, screen):
        body = pygame.Rect(0, 0, 140, 80)
        body.center = (int(self.x), int(self.y))
        pygame.draw.rect(screen, (45, 55, 70), body, border_radius=12)
        pygame.draw.rect(screen, (90, 110, 140), body, 3, border_radius=12)
        pygame.draw.rect(screen, (30, 35, 45), (body.x - 18, body.y + 10, 18, 60), border_radius=8)
        pygame.draw.rect(screen, (30, 35, 45), (body.right, body.y + 10, 18, 60), border_radius=8)
        turret = pygame.Rect(0, 0, 60, 36)
        turret.center = (int(self.x), int(self.y - 12))
        pygame.draw.rect(screen, (70, 90, 120), turret, border_radius=8)
        pygame.draw.rect(screen, (120, 150, 190), turret, 2, border_radius=8)
        pygame.draw.circle(screen, (140, 200, 230), (int(self.x + 26), int(self.y - 12)), 8)
        if self.burn_timer > 0:
            pygame.draw.circle(
                screen,
                (255, 120, 60),
                (int(self.x), int(self.y)),
                int(self.radius + 12),
                3,
            )
        if self.state == "laser":
            phase = self.phase()
            for i in range(6):
                ang = self.laser_angle + i * (math.tau / 6)
                ex = self.x + math.cos(ang) * WIDTH
                ey = self.y + math.sin(ang) * WIDTH
                width = 8 + phase * 2.5
                pygame.draw.line(screen, (255, 160, 90), (self.x, self.y), (ex, ey), int(width))


class Player:
    def __init__(self):
        self.x = WIDTH / 2
        self.y = HEIGHT / 2
        self.radius = 32
        self.color = BLUE
        self.base_speed = 220
        self.speed_bonus = 0
        self.max_hp = 100
        self.hp = self.max_hp
        self.damage = 18
        self.projectile_speed = 300
        self.fire_rate = 0.9
        self.fire_timer = 0.0
        self.bullets_per_shot = 1
        self.shield = 0.0
        self.invincible = 0.0
        self.multishot = 0.0
        self.haste = 0.0
        self.heal_boost = 0.0
        self.hurt_timer = 0.0
        self.shield_hit_timer = 0.0
        self.hurt_fx_timer = 0.0
        self.sprite_base = self.load_sprite()
        self.shield_sprite = self.load_shield_sprite()
        self.aim_angle = 0.0
        self.fire_orb_level = 0
        self.fire_orbiters = []
        self.fire_ring = False
        self.fire_ring_level = 0
        self.fire_ring_radius = 70.0
        self.fire_ring_burn_dps = 18.0
        self.fire_ring_outer_offset = 24.0
        self.laser_orb: Optional["LaserOrb"] = None
        self.laser_orb_level = 0
        self.laser_orb_damage = 14
        self.laser_orb_cooldown = 3.0
        self.laser_orb_timer = 0.0
        self.laser_orb_beam_timer = 0.0
        self.laser_orb_beam_tick = 0.0
        self.laser_orb_beam_pos: Optional[tuple[float, float]] = None
        self.laser_orb_beam_target = None
        self.electroelf: Optional["ElectroElf"] = None
        self.electroelf_level = 0
        self.electroelf_damage = 180.0
        self.electroelf_range = 110
        self.electroelf_cooldown = 3.0
        self.electroelf_timer = 0.0
        self.ultimate_charge = 0
        self.ultimate_max = 20
        self.ultimate_beam_time = 0.0
        self.ultimate_cooldown = 0.0
        self.ultimate_cooldown_max = 10.0
        self.shockwave_cooldown = 7.0
        self.shockwave_timer = self.shockwave_cooldown
        self.shockwave_radius = 240
        self.shockwave_damage = 0.9
        self.rocket_level = 0
        self.rocket_count = 0
        self.rocket_cooldown = 5.0
        self.rocket_timer = 0.0
        self.level = 1
        self.xp = 0
        self.next_xp = 5
        
    def load_sprite(self):
        path = os.path.join(DATA_DIR, "character.png")
        if os.path.exists(path):
            try:
                img = pygame.image.load(path).convert_alpha()
                size = self.radius * 2
                return pygame.transform.smoothscale(img, (size, size))
            except pygame.error:
                return None
        return None

    def load_shield_sprite(self):
        path = os.path.join(DATA_DIR, "shield.png")
        if os.path.exists(path):
            try:
                img = pygame.image.load(path).convert_alpha()
                size = int(self.radius * 2.6)
                sprite = pygame.transform.smoothscale(img, (size, size))
                sprite.set_alpha(160)
                return sprite
            except pygame.error:
                return None
        return None

    def update(self, dt, keys):
        vx = 0
        vy = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_q]:
            vx -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            vx += 1
        if keys[pygame.K_UP] or keys[pygame.K_z]:
            vy -= 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            vy += 1

        if vx or vy:
            norm = math.hypot(vx, vy)
            vx /= norm
            vy /= norm
        speed = self.base_speed + self.speed_bonus
        if self.haste > 0:
            speed *= 1.35

        self.x += vx * speed * dt
        self.y += vy * speed * dt

        self.x = clamp(self.x, self.radius, WIDTH - self.radius)
        self.y = clamp(self.y, self.radius, HEIGHT - self.radius)

        self.fire_timer = max(0.0, self.fire_timer - dt)
        self.invincible = max(0.0, self.invincible - dt)
        self.multishot = max(0.0, self.multishot - dt)
        self.haste = max(0.0, self.haste - dt)
        self.heal_boost = max(0.0, self.heal_boost - dt)
        self.hurt_timer = max(0.0, self.hurt_timer - dt)
        self.shield_hit_timer = max(0.0, self.shield_hit_timer - dt)
        self.hurt_fx_timer = max(0.0, self.hurt_fx_timer - dt)
        heal_mult = 5.0 if self.heal_boost > 0 else 1.0
        self.hp = min(self.max_hp, self.hp + self.max_hp * 0.01 * heal_mult * dt)
        if self.laser_orb_beam_timer > 0:
            self.laser_orb_beam_timer = max(0.0, self.laser_orb_beam_timer - dt)
        if self.ultimate_beam_time > 0:
            ultimate_just_ended = self.ultimate_beam_time - dt <= 0
            self.ultimate_beam_time = max(0.0, self.ultimate_beam_time - dt)
            if ultimate_just_ended and self.ultimate_cooldown <= 0:
                self.ultimate_cooldown = self.ultimate_cooldown_max
        self.ultimate_cooldown = max(0.0, self.ultimate_cooldown - dt)

    def set_aim(self, target_pos):
        dx = target_pos[0] - self.x
        dy = target_pos[1] - self.y
        self.aim_angle = math.atan2(dy, dx)

    def sync_orbiters(self):
        count = len(self.fire_orbiters)
        if count == 0:
            return
        if self.fire_ring:
            orbit_radius = self.fire_ring_radius + self.fire_ring_outer_offset
            step = math.tau / count
            for i, orb in enumerate(self.fire_orbiters):
                orb.radius = orbit_radius
                orb.speed = 2.2
                orb.angle = i * step
                orb.rel_x = orbit_radius * math.cos(orb.angle)
                orb.rel_y = orbit_radius * math.sin(orb.angle)
            return

        inner_count = min(count, 6)
        outer_count = min(max(0, count - inner_count), 8)

        inner_radius = 54.0
        outer_radius = 94.0
        inner_step = math.tau / inner_count if inner_count > 0 else 0.0
        outer_step = math.tau / outer_count if outer_count > 0 else 0.0

        for i, orb in enumerate(self.fire_orbiters):
            if i < inner_count:
                orb.radius = inner_radius
                orb.speed = 2.6
                orb.angle = i * inner_step
            else:
                j = i - inner_count
                orb.radius = outer_radius
                orb.speed = 1.8
                offset = (outer_step * 0.5) if outer_count > 1 else 0.0
                orb.angle = j * outer_step + offset
            orb.rel_x = orb.radius * math.cos(orb.angle)
            orb.rel_y = orb.radius * math.sin(orb.angle)

    def can_fire(self):
        return self.fire_timer <= 0

    def fire(self, target_pos, projectiles):
        if not self.can_fire():
            return
        self.fire_timer = self.fire_rate * (0.35 if self.haste > 0 else 1.0)
        angle = math.atan2(target_pos[1] - self.y, target_pos[0] - self.x)

        pickup_bonus = 6 if self.multishot > 0 else 0
        shots = clamp(self.bullets_per_shot + pickup_bonus, 1, 80)
        max_spread = 0.35 + (shots / 80) * 0.95
        if shots == 1:
            offsets = [0.0]
        else:
            step = (2 * max_spread) / (shots - 1)
            offsets = [(-max_spread + i * step) for i in range(shots)]

        dmg_mult = 1.4 if self.haste > 0 else 1.0
        base_radius = 7 if self.haste > 0 else 4

        for offset in offsets:
            proj_radius = base_radius
            damage = self.damage * dmg_mult
            ax = math.cos(angle + offset)
            ay = math.sin(angle + offset)
            projectiles.append(
                Projectile(
                    self.x,
                    self.y,
                    ax * self.projectile_speed,
                    ay * self.projectile_speed,
                    damage,
                    color=YELLOW,
                    radius=proj_radius,
                    owner="player",
                )
            )

    def take_damage(self, amount):
        if self.invincible > 0 or self.hurt_timer > 0:
            return "none"
        if self.shield > 0:
            self.shield = max(0, self.shield - amount * 0.08)
            self.shield_hit_timer = 0.14
            return "shield"
        self.hp -= amount
        self.hurt_timer = 0.6
        self.hurt_fx_timer = 0.16
        return "hp"

    def draw(self, screen):
        for orb in self.fire_orbiters:
            orb.draw(screen)
        if self.fire_ring:
            self.draw_fire_ring(screen)
        if self.laser_orb:
            self.laser_orb.draw(screen)
        if self.laser_orb_beam_timer > 0 and self.laser_orb and self.laser_orb_beam_pos:
            pygame.draw.line(
                screen,
                CYAN,
                (int(self.laser_orb.x), int(self.laser_orb.y)),
                (int(self.laser_orb_beam_pos[0]), int(self.laser_orb_beam_pos[1])),
                4,
            )
        if self.shield > 0:
            if self.shield_sprite:
                rect = self.shield_sprite.get_rect(center=(int(self.x), int(self.y)))
                screen.blit(self.shield_sprite, rect.topleft)
            else:
                pygame.draw.circle(
                    screen, PURPLE, (int(self.x), int(self.y)), self.radius + 6, 2
                )
            if self.shield_hit_timer > 0:
                ratio = self.shield_hit_timer / 0.14
                pulse_r = int(self.radius + 6 + (1.0 - ratio) * 8)
                alpha = int(95 * ratio)
                surf = pygame.Surface((pulse_r * 2 + 8, pulse_r * 2 + 8), pygame.SRCALPHA)
                center = (surf.get_width() // 2, surf.get_height() // 2)
                pygame.draw.circle(surf, (170, 145, 255, max(12, int(alpha * 0.22))), center, pulse_r)
                pygame.draw.circle(surf, (220, 200, 255, alpha), center, pulse_r, 2)
                screen.blit(surf, (int(self.x - center[0]), int(self.y - center[1])))
        if self.sprite_base:
            rotated = pygame.transform.rotate(self.sprite_base, -math.degrees(self.aim_angle))
            rect = rotated.get_rect(center=(int(self.x), int(self.y)))
            screen.blit(rotated, rect.topleft)
        else:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        if self.hurt_fx_timer > 0:
            ratio = self.hurt_fx_timer / 0.16
            pulse_r = int(self.radius + 4 + (1.0 - ratio) * 8)
            alpha = int(90 * ratio)
            surf = pygame.Surface((pulse_r * 2 + 8, pulse_r * 2 + 8), pygame.SRCALPHA)
            center = (surf.get_width() // 2, surf.get_height() // 2)
            pygame.draw.circle(surf, (255, 95, 95, max(8, int(alpha * 0.18))), center, pulse_r)
            pygame.draw.circle(surf, (255, 130, 130, alpha), center, pulse_r, 2)
            screen.blit(surf, (int(self.x - center[0]), int(self.y - center[1])))

    def draw_fire_ring(self, screen):
        ring_radius = int(self.fire_ring_radius)
        time_s = pygame.time.get_ticks() * 0.002
        glow = pygame.Surface((ring_radius * 2 + 40, ring_radius * 2 + 40), pygame.SRCALPHA)
        center = (glow.get_width() // 2, glow.get_height() // 2)
        for r, alpha in [(ring_radius + 12, 40), (ring_radius + 6, 70), (ring_radius, 110)]:
            pygame.draw.circle(glow, (255, 120, 30, alpha), center, r, 6)
        screen.blit(glow, (int(self.x - center[0]), int(self.y - center[1]))

        )

        flames = 40
        for i in range(flames):
            theta = time_s + (i * (math.tau / flames))
            wobble = math.sin(time_s * 1.7 + i) * 3
            r = ring_radius + wobble
            x = self.x + math.cos(theta) * r
            y = self.y + math.sin(theta) * r
            pygame.draw.circle(screen, (255, 160, 40), (int(x), int(y)), 4)
            pygame.draw.circle(screen, (255, 220, 120), (int(x), int(y)), 2)

# --- Boule de feu --- #
class FireOrbiter:
    _sprite_base = None
    _sprite_missing = False

    def __init__(self, angle):
        self.angle = angle
        self.radius = 52
        self.speed = 2.6
        self.size = 16
        self.sprite = self.load_sprite()
        self.rotation = 0.0
        self.x = 0.0
        self.y = 0.0
        self.rel_x = self.radius
        self.rel_y = 0.0

    def load_sprite(self):
        if FireOrbiter._sprite_base is None and not FireOrbiter._sprite_missing:
            path = os.path.join(DATA_DIR, "fireball.png")
            if os.path.exists(path):
                try:
                    FireOrbiter._sprite_base = pygame.image.load(path).convert_alpha()
                except pygame.error:
                    FireOrbiter._sprite_missing = True
            else:
                FireOrbiter._sprite_missing = True
        if FireOrbiter._sprite_base is None:
            return None
        size = self.size * 3
        return pygame.transform.smoothscale(FireOrbiter._sprite_base, (size, size))
    
    def angle_tangente(self, theta, direction):
        _ = direction
        if abs(math.sin(theta)) < 1e-6:
            return direction * (math.pi / 2)
        return 3 * math.pi / 2 - math.atan(-math.cos(theta) / math.sin(theta)) + (
            math.pi if math.sin(theta) < 0 else 0
        )
    
    def update(self, dt, rel_x, rel_y):
        r = math.hypot(rel_x, rel_y) or self.radius
        theta = math.atan2(rel_y, rel_x)
        theta += self.speed * dt
        rel_x = r * math.cos(theta)
        rel_y = r * math.sin(theta)
        self.angle = theta
        direction = 1 if self.speed >= 0 else -1
        orientation = self.angle_tangente(theta, direction)
        self.rotation = math.degrees(orientation)
        self.rel_x = rel_x
        self.rel_y = rel_y
        return rel_x, rel_y

    def draw(self, screen):
        if self.sprite:
            rotated = pygame.transform.rotate(self.sprite, self.rotation)
            rect = rotated.get_rect(center=(int(self.x), int(self.y)))
            screen.blit(rotated, rect.topleft)
        else:
            pygame.draw.circle(screen, (255, 120, 60), (int(self.x), int(self.y)), self.size)
            pygame.draw.circle(screen, (255, 200, 120), (int(self.x), int(self.y)), self.size - 4)


class LaserOrb:
    _sprite_base = None
    _sprite_missing = False

    def __init__(self):
        self.orbit_radius = 95
        self.angle = -0.7
        self.orbit_speed = 0.8
        self.radius = 8
        self.x = 0.0
        self.y = 0.0
        self.sprite = self.load_sprite()
        if self.sprite:
            self.radius = self.sprite.get_width() / 2

    def load_sprite(self):
        if LaserOrb._sprite_base is None and not LaserOrb._sprite_missing:
            path = os.path.join(DATA_DIR, "laser_orb.png")
            if os.path.exists(path):
                try:
                    LaserOrb._sprite_base = pygame.image.load(path).convert_alpha()
                except pygame.error:
                    LaserOrb._sprite_missing = True
            else:
                LaserOrb._sprite_missing = True
        if LaserOrb._sprite_base is None:
            return None
        size = self.radius * 4
        return pygame.transform.smoothscale(LaserOrb._sprite_base, (size, size))

    def update(self, dt, player_x, player_y):
        self.angle = (self.angle + self.orbit_speed * dt) % math.tau
        self.x = player_x + math.cos(self.angle) * self.orbit_radius
        self.y = player_y + math.sin(self.angle) * self.orbit_radius

    def draw(self, screen):
        if self.sprite:
            rect = self.sprite.get_rect(center=(int(self.x), int(self.y)))
            screen.blit(self.sprite, rect.topleft)
        else:
            pygame.draw.circle(screen, BLUE, (int(self.x), int(self.y)), self.radius)

# --- Foudre de l'elfe electrique --- #
class LightningStrike:
    def __init__(self, start_pos, end_pos, radius, damage, target=None, charge_time=0.35, duration=0.25):
        self.sx, self.sy = start_pos
        self.ex, self.ey = end_pos
        self.radius = radius
        self.damage = damage
        self.target = target
        self.charge_time = charge_time
        self.duration = duration
        self.time_left = charge_time + duration
        self.struck = False
        self.should_damage = False
        self.points = self._build_points()

    def _build_points(self):
        points = [(self.sx, self.sy)]
        segments = 7
        for i in range(1, segments):
            t = i / segments
            x = self.sx + (self.ex - self.sx) * t
            y = self.sy + (self.ey - self.sy) * t
            jitter = 18 * (1 - abs(0.5 - t))
            x += random.uniform(-jitter, jitter)
            y += random.uniform(-jitter, jitter)
            points.append((x, y))
        points.append((self.ex, self.ey))
        return points

    def update(self, dt):
        if self.target is not None and self.target.hp > 0:
            self.ex, self.ey = self.target.x, self.target.y
            self.sx, self.sy = self.ex, max(-40, self.ey - 260)
        self.time_left -= dt
        if not self.struck and self.time_left <= self.duration:
            self.struck = True
            self.should_damage = True

    def draw(self, screen):
        if self.time_left <= 0:
            return
        if self.time_left > self.duration:
            t = 1.0 - (self.time_left - self.duration) / self.charge_time
            ring_r = int(self.radius * (0.4 + 0.6 * t))
            alpha = int(140 + 80 * t)
            glow = pygame.Surface((ring_r * 2 + 8, ring_r * 2 + 8), pygame.SRCALPHA)
            pygame.draw.circle(
                glow,
                (160, 210, 255, alpha),
                (glow.get_width() // 2, glow.get_height() // 2),
                ring_r,
                2,
            )
            screen.blit(glow, (int(self.ex - ring_r - 4), int(self.ey - ring_r - 4)))
            pygame.draw.circle(screen, (200, 240, 255), (int(self.ex), int(self.ey)), 3)
        else:
            alpha = int(255 * (self.time_left / self.duration))
            self.points = self._build_points()
            bolt = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            pygame.draw.lines(bolt, (80, 140, 255, int(alpha * 0.6)), False, self.points, 10)
            pygame.draw.lines(bolt, (120, 180, 255, int(alpha * 0.8)), False, self.points, 7)
            pygame.draw.lines(bolt, (230, 245, 255, alpha), False, self.points, 4)
            pygame.draw.lines(bolt, (255, 255, 255, alpha), False, self.points, 2)
            pygame.draw.circle(
                bolt, (220, 240, 255, alpha), (int(self.ex), int(self.ey)), int(self.radius * 1.4)
            )
            pygame.draw.circle(
                bolt, (255, 255, 255, alpha), (int(self.ex), int(self.ey)), int(self.radius * 0.6)
            )
            pygame.draw.lines(screen, (255, 255, 255), False, self.points, 3)
            pygame.draw.lines(screen, (180, 220, 255), False, self.points, 5)
            screen.blit(bolt, (0, 0))


class UltimateBeam:
    def __init__(self, start_pos, end_pos, duration=0.12):
        self.sx, self.sy = start_pos
        self.ex, self.ey = end_pos
        self.time_left = duration
        self.duration = duration

    def update(self, dt):
        self.time_left -= dt

    def draw(self, screen):
        if self.time_left <= 0:
            return
        alpha = int(220 * (self.time_left / self.duration))
        surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pygame.draw.line(surf, (255, 220, 80, alpha), (self.sx, self.sy), (self.ex, self.ey), 10)
        pygame.draw.line(surf, (255, 245, 160, alpha), (self.sx, self.sy), (self.ex, self.ey), 5)
        pygame.draw.line(surf, (255, 255, 220, alpha), (self.sx, self.sy), (self.ex, self.ey), 2)
        screen.blit(surf, (0, 0))


class UltimateZone:
    def __init__(self, x, y, radius=90, duration=3.0, tick_interval=0.2):
        self.x = x
        self.y = y
        self.radius = radius
        self.duration = duration
        self.time_left = duration
        self.tick_interval = tick_interval
        self.tick_timer = 0.0

    def update(self, dt):
        self.time_left -= dt
        self.tick_timer -= dt

    def should_tick(self):
        if self.tick_timer <= 0:
            self.tick_timer += self.tick_interval
            return True
        return False

    def draw(self, screen):
        if self.time_left <= 0:
            return
        t = 1.0 - (self.time_left / self.duration)
        pulse = 0.85 + 0.15 * math.sin(t * math.tau * 2)
        r = int(self.radius * pulse)
        alpha = int(160 + 60 * (1.0 - t))
        surf = pygame.Surface((r * 2 + 8, r * 2 + 8), pygame.SRCALPHA)
        pygame.draw.circle(surf, (255, 220, 80, alpha), (r + 4, r + 4), r, 5)
        pygame.draw.circle(surf, (255, 245, 170, alpha), (r + 4, r + 4), max(2, r // 8))
        screen.blit(surf, (int(self.x - r - 4), int(self.y - r - 4)))


class UltimatePulse:
    def __init__(self, x, y, radius, duration=0.45):
        self.x = x
        self.y = y
        self.radius = radius
        self.time_left = duration
        self.duration = duration

    def update(self, dt):
        self.time_left -= dt

    def draw(self, screen):
        if self.time_left <= 0:
            return
        t = 1.0 - (self.time_left / self.duration)
        r = int(self.radius * (0.4 + 0.6 * t))
        alpha = int(220 * (1.0 - t))
        surf = pygame.Surface((r * 2 + 8, r * 2 + 8), pygame.SRCALPHA)
        pygame.draw.circle(surf, (255, 220, 80, alpha), (r + 4, r + 4), r, 6)
        pygame.draw.circle(surf, (255, 255, 200, alpha), (r + 4, r + 4), max(2, r // 6))
        screen.blit(surf, (int(self.x - r - 4), int(self.y - r - 4)))


class Shockwave:
    def __init__(self, x, y, radius, duration=0.35):
        self.x = x
        self.y = y
        self.radius = radius
        self.duration = duration
        self.time_left = duration

    def update(self, dt):
        self.time_left -= dt

    def draw(self, screen):
        if self.time_left <= 0:
            return
        t = 1.0 - (self.time_left / self.duration)
        r = int(self.radius * t)
        alpha = int(200 * (1.0 - t))
        surf = pygame.Surface((r * 2 + 8, r * 2 + 8), pygame.SRCALPHA)
        pygame.draw.circle(surf, (120, 220, 255, alpha), (r + 4, r + 4), r, 6)
        pygame.draw.circle(surf, (180, 240, 255, alpha), (r + 4, r + 4), max(2, r // 6), 2)
        screen.blit(surf, (int(self.x - r - 4), int(self.y - r - 4)))


class ElectroElf:
    def __init__(self):
        self.x = random.uniform(60, WIDTH - 60)
        self.y = random.uniform(60, HEIGHT - 60)
        self.speed = 160.0
        self.radius = 14
        self.color = (200, 240, 255)
        self.target_x = self.x
        self.target_y = self.y
        self.target = None
        self.sprite = self.load_sprite()
        if self.sprite:
            self.radius = self.sprite.get_width() / 2
        self._pick_new_target()

    def load_sprite(self):
        path = os.path.join(DATA_DIR, "electroelf.png")
        if os.path.exists(path):
            try:
                img = pygame.image.load(path).convert_alpha()
                size = int(self.radius * 3)
                return pygame.transform.smoothscale(img, (size, size))
            except pygame.error:
                return None
        return None

    def _pick_new_target(self):
        margin = 50
        self.target_x = random.uniform(margin, WIDTH - margin)
        self.target_y = random.uniform(margin, HEIGHT - margin)

    def update(self, dt, targets):
        if self.target is None or self.target not in targets or self.target.hp <= 0:
            if targets:
                self.target = min(
                    targets,
                    key=lambda e: (e.x - self.x) ** 2 + (e.y - self.y) ** 2,
                )
            else:
                self.target = None

        if self.target is not None:
            self.target_x = self.target.x
            self.target_y = self.target.y
        else:
            if math.hypot(self.target_x - self.x, self.target_y - self.y) < 12:
                self._pick_new_target()

        dx = self.target_x - self.x
        dy = self.target_y - self.y
        dist = math.hypot(dx, dy)
        if dist <= 0.1:
            return
        vx = dx / dist * self.speed
        vy = dy / dist * self.speed
        self.x += vx * dt
        self.y += vy * dt

    def draw(self, screen):
        if self.sprite:
            rect = self.sprite.get_rect(center=(int(self.x), int(self.y)))
            screen.blit(self.sprite, rect.topleft)
        else:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
            pygame.draw.circle(screen, (120, 200, 255), (int(self.x), int(self.y)), self.radius + 6, 2)


class DamageNumber:
    def __init__(self, x, y, amount, color=(255, 225, 120), duration=0.7):
        self.x = x + random.uniform(-10, 10)
        self.y = y - random.uniform(6, 16)
        self.amount = max(0.0, amount)
        self.duration = duration
        self.time_left = duration
        self.float_speed = 46.0
        self.color = color
        size_bonus = min(40.0, math.sqrt(self.amount) * 2.4)
        self.font_size = int(clamp(18 + size_bonus, 18, 64))

    def update(self, dt):
        self.time_left -= dt
        self.y -= self.float_speed * dt


class PulseEffect:
    def __init__(
        self,
        x,
        y,
        color=(255, 120, 90),
        start_radius=12,
        end_radius=80,
        duration=0.3,
        width=4,
        fill_alpha=60,
    ):
        self.x = x
        self.y = y
        self.color = color
        self.start_radius = start_radius
        self.end_radius = end_radius
        self.duration = duration
        self.time_left = duration
        self.width = width
        self.fill_alpha = fill_alpha

    def update(self, dt):
        self.time_left -= dt

    def draw(self, screen):
        if self.time_left <= 0:
            return
        t = 1.0 - (self.time_left / self.duration)
        radius = int(self.start_radius + (self.end_radius - self.start_radius) * t)
        alpha = int(220 * (1.0 - t))
        surf = pygame.Surface((radius * 2 + 8, radius * 2 + 8), pygame.SRCALPHA)
        center = (surf.get_width() // 2, surf.get_height() // 2)
        pygame.draw.circle(
            surf,
            (self.color[0], self.color[1], self.color[2], int(min(alpha, self.fill_alpha))),
            center,
            radius,
        )
        pygame.draw.circle(
            surf,
            (self.color[0], self.color[1], self.color[2], alpha),
            center,
            radius,
            self.width,
        )
        screen.blit(surf, (int(self.x - center[0]), int(self.y - center[1])))

@dataclass
class UpgradeChoice:
    key: str
    label: str
    desc: str


UPGRADE_POOL = [
    UpgradeChoice("speed", "Vitesse+", "Bonus de vitesse."),
    UpgradeChoice("proj_speed", "Proj Speed+", "Projectiles plus rapide."),
    UpgradeChoice("damage", "Degats+", "Degats augmentes."),
    UpgradeChoice("max_hp", "PV Max+", "Augmente la vie max."),
    UpgradeChoice("fire_rate", "Cadence+", "Tire plus souvent."),
    UpgradeChoice("bullets", "Multi-tir+", "Plus de projectiles par tir."),
    UpgradeChoice("fire_orb", "Orbe de feu", "Ajoute une boule de feu orbitale."),
    UpgradeChoice("rockets", "Lance roquette", "Lance des roquettes."),
]

EPIC_UPGRADES = [
    UpgradeChoice("laser_orb", "Orbe laser", "Une orbe tire des lasers bleus."),
    UpgradeChoice("electroelf", "Electroelf", "Familier qui lance des eclairs."),
    UpgradeChoice("fire_ring","EVO: Cercle de feu+","Debloque le cercle de feu",
    ),
]

TEMP_PICKUP_POOL = ["shield", "haste", "multishot", "heal"]

####################
# --- Mainloop --- #
####################
class Game:
    def __init__(self):
        global WIDTH, HEIGHT
        pygame.init()
        pygame.display.set_caption("Tank Survivor")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
        WIDTH, HEIGHT = self.screen.get_size()
        self.clock = pygame.time.Clock()
        self.font_path = os.path.join(DATA_DIR, "genshin.ttf")
        self.font = pygame.font.Font(self.font_path, 18)
        self.big_font = pygame.font.Font(self.font_path, 28)
        self.damage_fonts = {}

        self.player = Player()
        self.enemies = []
        self.projectiles = []
        self.rockets = []
        self.explosions = []
        self.lightning_effects = []
        self.ultimate_beams = []
        self.ultimate_pulses = []
        self.ultimate_zones = []
        self.shockwaves = []
        self.boss = None
        self.boss_zones = []
        self.pickups = []
        self.gems = []
        self.damage_numbers = []
        self.pulse_effects = []
        self.wave = 1
        self.state = "playing"
        self.score = 0
        self.upgrade_choices = []
        self.ui_icons = self.load_ui_icons()
        self.upgrade_icons = self.load_upgrade_icons()
        self.reset_game()
        self.ui_buttons = []
        self.cheats_enabled = False
        self.cheat_buttons = []
        self.pending_upgrades = 0
        self.pending_wave_spawns = 0
        self.wave_total = 0
        self.wave_killed = 0
        self.gem_rush_timer = 0.0
        self.boss_death_timer = 0.0

    def upgrade_level(self, key):
        if key == "speed":
            return int(round(self.player.speed_bonus / 25))
        if key == "proj_speed":
            return int(round((self.player.projectile_speed - 300) / 60))
        if key == "damage":
            return int(round((self.player.damage - 18) / 4))
        if key == "max_hp":
            return int(round((self.player.max_hp - 100) / 15))
        if key == "fire_rate":
            return int(round((0.9 - self.player.fire_rate) / 0.02))
        if key == "bullets":
            return max(0, int((self.player.bullets_per_shot - 1) / 2))
        if key == "fire_orb":
            return self.player.fire_orb_level
        if key == "laser_orb":
            return self.player.laser_orb_level
        if key == "electroelf":
            return self.player.electroelf_level
        if key == "rockets":
            return self.player.rocket_level
        if key == "fire_ring":
            return self.player.fire_ring_level
        return 0

    def upgrade_max_level(self, key):
        if key == "fire_rate":
            return int(round((0.9 - 0.08) / 0.02))
        if key == "bullets":
            return 30
        if key == "fire_orb":
            return 14
        if key == "laser_orb":
            return 10
        if key == "electroelf":
            return 5
        if key == "rockets":
            return 19
        if key == "fire_ring":
            return 10
        return None

    def upgrade_is_maxed(self, key):
        max_level = self.upgrade_max_level(key)
        if max_level is None:
            return False
        return self.upgrade_level(key) >= max_level

    def upgrade_label_with_level(self, choice):
        level = self.upgrade_level(choice.key)
        max_level = self.upgrade_max_level(choice.key)
        if max_level is None:
            return f"{choice.label} ({level})"
        return f"{choice.label} ({level}/{max_level})"

    def gain_xp(self, amount):
        self.player.xp += amount
        while self.player.xp >= self.player.next_xp:
            self.player.xp -= self.player.next_xp
            self.player.level += 1
            self.player.damage += 4
            self.player.max_hp += 5
            self.player.hp = min(self.player.max_hp, self.player.hp + 5)
            self.player.next_xp = int(6 + (self.player.level ** 1.6) * 4)
            self.pending_upgrades += 1
        if self.pending_upgrades > 0 and self.state == "playing":
            self.start_upgrade()

    def start_upgrade(self):
        if self.pending_upgrades <= 0:
            return False
        if self.prepare_upgrade_choices():
            self.state = "upgrade"
            return True
        return False

    def reset_game(self):
        self.player = Player()
        self.enemies.clear()
        self.projectiles.clear()
        self.rockets.clear()
        self.explosions.clear()
        self.lightning_effects.clear()
        self.ultimate_beams.clear()
        self.ultimate_pulses.clear()
        self.ultimate_zones.clear()
        self.shockwaves.clear()
        self.boss = None
        self.boss_zones.clear()
        self.pickups.clear()
        self.gems.clear()
        self.damage_numbers.clear()
        self.pulse_effects.clear()
        self.wave = 1
        self.score = 0
        self.upgrade_choices = []
        self.pending_upgrades = 0
        self.pending_wave_spawns = 0
        self.wave_total = 0
        self.wave_killed = 0
        self.gem_rush_timer = 0.0
        self.boss_death_timer = 0.0
        self.spawn_wave(self.wave)
        self.state = "playing"


    def load_ui_icons(self):
        icons = {}
        base = DATA_DIR
        for key, filename in [
            ("multishot", "multishot.png"),
            ("haste", "haste.png"),
            ("heal", "heal.png"),
        ]:
            path = os.path.join(base, filename)
            if os.path.exists(path):
                try:
                    img = pygame.image.load(path).convert_alpha()
                    icons[key] = pygame.transform.smoothscale(img, (26, 26))
                except pygame.error:
                    icons[key] = None
            else:
                icons[key] = None
        return icons

    def load_upgrade_icons(self):
        icons = {}
        base = DATA_DIR
        mapping = {
            "speed": "speed.png",
            "proj_speed": "bullet_speed.png",
            "damage": "damage.png",
            "max_hp": "maxhp.png",
            "fire_rate": "attack_speed.png",
            "bullets": "multishot.png",
            "fire_orb": "fireball.png",
            "rockets": "rocket.png",
            "fire_ring": "fire_ring.png",
            "laser_orb":"laser_orb.png",
            "electroelf":"electroelf.png",
        }
        for key, filename in mapping.items():
            path = os.path.join(base, filename)
            if os.path.exists(path):
                try:
                    icons[key] = pygame.image.load(path).convert_alpha()
                except pygame.error:
                    icons[key] = None
            else:
                icons[key] = None
        return icons


    def spawn_wave(self, wave):
        self.enemies.clear()
        self.boss = None
        self.boss_zones.clear()
        total = 8 + int(wave * 1.3)
        self.wave_total = total
        self.wave_killed = 0
        for _ in range(total):
            x, y = random_spawn_point()
            kind = random.choices(
                ["basic", "fast", "tank", "shooter"],
                weights=[70, 10, 10, 10],
            )[0]
            self.enemies.append(Enemy(x, y, kind, wave))
        if wave % 5 == 0:
            self.boss = Boss(wave)

    def drop_pickup(self, x, y):
        if random.random() < 0.12:
            choice = random.choices(
                TEMP_PICKUP_POOL,
                weights=[38, 7, 30, 25],
            )[0]
            self.pickups.append(UpgradePickup(x, y, choice))

    def apply_upgrade(self, key):
        if key == "speed":
            self.player.speed_bonus += 25
        elif key == "proj_speed":
            self.player.projectile_speed += 60
        elif key == "damage":
            self.player.damage += 4
        elif key == "max_hp":
            self.player.max_hp += 50
            self.player.hp += 50
        elif key == "fire_rate":
            self.player.fire_rate = max(0.08, self.player.fire_rate - 0.02)
        elif key == "bullets":
            self.player.bullets_per_shot = min(61, self.player.bullets_per_shot + 2)
        elif key == "fire_orb":
            if self.player.fire_ring or self.player.fire_orb_level >= 14:
                return
            self.player.fire_orb_level += 1
            orb = FireOrbiter(0.0)
            orb.x = self.player.x + orb.radius
            orb.y = self.player.y
            self.player.fire_orbiters.append(orb)
            self.player.sync_orbiters()
        elif key == "laser_orb":
            if self.player.laser_orb is None:
                self.player.laser_orb = LaserOrb()
            self.player.laser_orb_level += 1
            self.player.laser_orb_damage += 4
            self.player.laser_orb_cooldown = max(0.8, self.player.laser_orb_cooldown - 0.06)
        elif key == "electroelf":
            if self.player.electroelf is None:
                self.player.electroelf = ElectroElf()
            self.player.electroelf_level = min(5, self.player.electroelf_level + 1)
            base_damage = 180
            self.player.electroelf_damage = base_damage * (1.0 + 0.35 * (self.player.electroelf_level - 1))
            self.player.electroelf_range = 110 + 25 * (self.player.electroelf_level - 1)
        elif key == "fire_ring":
            if not self.player.fire_ring:
                self.player.fire_ring = True
                self.player.fire_ring_level = 0
                self.player.fire_orbiters.clear()
            else:
                if self.player.fire_ring_level >= 10:
                    return
                self.player.fire_ring_level += 1
                self.player.fire_ring_radius = min(220.0, self.player.fire_ring_radius + 8.0)
                self.player.fire_ring_burn_dps += 3.0
            desired_orbs = min(10, self.player.fire_ring_level)
            self.player.fire_orbiters = self.player.fire_orbiters[:desired_orbs]
            while len(self.player.fire_orbiters) < desired_orbs:
                self.player.fire_orbiters.append(FireOrbiter(0.0))
            self.player.sync_orbiters()
        elif key == "rockets":
            self.player.rocket_level += 1
            if self.player.rocket_level % 2 == 1:
                self.player.rocket_count = min(10, self.player.rocket_count + 1)
            else:
                self.player.rocket_cooldown = max(1.0, self.player.rocket_cooldown - 0.5)

    def prepare_upgrade_choices(self):
        pool = [
            u
            for u in UPGRADE_POOL
            if not (self.player.fire_ring and u.key == "fire_orb") and not self.upgrade_is_maxed(u.key)
        ]
        if self.player.laser_orb_level <= 0 and not self.upgrade_is_maxed("laser_orb"):
            pool.append(EPIC_UPGRADES[0])
        if not self.upgrade_is_maxed("electroelf"):
            pool.append(EPIC_UPGRADES[1])
        if (self.player.fire_orb_level >= 14 and not self.player.fire_ring) or self.player.fire_ring:
            pool.append(EPIC_UPGRADES[2])
        pool = [u for u in pool if not self.upgrade_is_maxed(u.key)]
        if not pool:
            return False
        self.upgrade_choices = random.sample(pool, k=min(3, len(pool)))
        self.build_upgrade_buttons()
        return True

    def build_upgrade_buttons(self):
        self.ui_buttons = []
        panel_w = int(WIDTH * 0.8)
        panel_h = int(HEIGHT * 0.8)
        panel_x = (WIDTH - panel_w) / 2
        panel_y = (HEIGHT - panel_h) / 2
        gap = 20
        count = max(1, len(self.upgrade_choices))
        card_w = (panel_w - gap * (count + 1)) / count
        card_h = panel_h - gap * 2
        for i, choice in enumerate(self.upgrade_choices):
            x = panel_x + gap + i * (card_w + gap)
            y = panel_y + gap
            rect = pygame.Rect(x, y, card_w, card_h)
            self.ui_buttons.append({"rect": rect, "choice": choice})

    def build_game_over_buttons(self):
        self.ui_buttons = []
        w, h = 200, 50
        panel_w = 520
        panel_h = 240
        panel_x = WIDTH / 2 - panel_w / 2
        panel_y = 120
        y = panel_y + panel_h - h - 24
        x1 = panel_x + panel_w / 2 - w - 10
        x2 = panel_x + panel_w / 2 + 10
        self.ui_buttons.append({"rect": pygame.Rect(x1, y, w, h), "action": "replay"})
        self.ui_buttons.append({"rect": pygame.Rect(x2, y, w, h), "action": "quit"})

    def build_pause_buttons(self):
        self.ui_buttons = []
        w, h = 200, 50
        panel_w = 520
        panel_h = 220
        panel_x = WIDTH / 2 - panel_w / 2
        panel_y = HEIGHT / 2 - panel_h / 2
        gap = 16
        block_h = h * 2 + gap
        row_y = panel_y + (panel_h - block_h) / 2 + 10
        x1 = panel_x + panel_w / 2 - w - 10
        x2 = panel_x + panel_w / 2 + 10
        self.ui_buttons.append({"rect": pygame.Rect(x1, row_y, w, h), "action": "resume"})
        self.ui_buttons.append({"rect": pygame.Rect(x2, row_y, w, h), "action": "quit"})
        self.ui_buttons.append(
            {
                "rect": pygame.Rect(panel_x + panel_w / 2 - w / 2, row_y + h + gap, w, h),
                "action": "replay",
            }
        )

    def build_cheat_buttons(self):
        buttons = []
        upgrades = [
            u
            for u in (list(UPGRADE_POOL) + EPIC_UPGRADES)
            if not self.upgrade_is_maxed(u.key)
        ]
        w, h = 170, 30
        padding = 8
        total_h = (len(upgrades) + 2) * (h + padding) - padding
        x = WIDTH - w - 20
        y = HEIGHT - total_h - 20
        for i, up in enumerate(upgrades):
            rect = pygame.Rect(x, y + i * (h + padding), w, h)
            buttons.append(
                {"rect": rect, "key": up.key, "label": self.upgrade_label_with_level(up)}
            )
        level_rect = pygame.Rect(x, y + len(upgrades) * (h + padding), w, h)
        buttons.append({"rect": level_rect, "key": "level_up", "label": "Niveau +1"})
        ult_rect = pygame.Rect(x, y + (len(upgrades) + 1) * (h + padding), w, h)
        buttons.append({"rect": ult_rect, "key": "ult_full", "label": "ULT Max"})
        self.cheat_buttons = buttons

    def spawn_gems(self, x, y, count=1, amount=1, spread=10):
        for _ in range(count):
            ox = random.uniform(-spread, spread)
            oy = random.uniform(-spread * 0.8, spread * 0.8)
            self.gems.append(ExpGem(x + ox, y + oy, amount=amount))

    def attract_all_gems(self, duration):
        for gem in self.gems:
            gem.pickup_range = max(gem.pickup_range, 99999.0)
            gem.attract = max(gem.attract, 900.0)
            gem.max_speed = max(gem.max_speed, 900.0)
            gem.start_rush(duration)

    def start_gem_rush(self, duration=0.7):
        self.gem_rush_timer = duration
        self.attract_all_gems(duration)

    def on_enemy_killed(self, enemy):
        self.score += 1
        self.wave_killed = min(self.wave_total, self.wave_killed + 1)
        self.spawn_pulse(
            enemy.x,
            enemy.y,
            color=(255, 190, 110),
            start_radius=12,
            end_radius=44,
            duration=0.2,
            width=3,
            fill_alpha=36,
        )
        self.explosions.append(Explosion(enemy.x, enemy.y, max(18, int(enemy.radius + 8)), duration=0.2))
        self.drop_pickup(enemy.x, enemy.y)
        self.spawn_gems(enemy.x, enemy.y, count=random.randint(1, 3), amount=1)
        if self.player.ultimate_beam_time <= 0:
            self.player.ultimate_charge = min(
                self.player.ultimate_max, self.player.ultimate_charge + 1
            )

    def on_boss_killed(self):
        if self.boss is None:
            return
        bx, by = self.boss.x, self.boss.y
        self.boss = None
        self.boss_zones.clear()
        for enemy in list(self.enemies):
            self.explosions.append(Explosion(enemy.x, enemy.y, 40, duration=0.3))
        self.enemies.clear()
        self.explosions.append(Explosion(bx, by, 90, duration=0.45))
        gem_count = self.wave * self.wave + 30
        self.spawn_gems(bx, by, count=gem_count, amount=1, spread=60)
        self.wave_killed = self.wave_total
        self.boss_death_timer = 0.8
        self.state = "boss_death"

    def boss_attack_damage(self):
        return 18 + self.wave * 1.8

    def boss_contact_damage(self):
        return self.boss_attack_damage() * 0.35

    def get_damage_font(self, size):
        size = int(clamp(size, 16, 72))
        if size not in self.damage_fonts:
            self.damage_fonts[size] = pygame.font.Font(self.font_path, size)
        return self.damage_fonts[size]

    def spawn_damage_number(self, x, y, amount, color=(255, 225, 120)):
        if amount <= 0:
            return
        self.damage_numbers.append(DamageNumber(x, y, amount, color=color))

    def spawn_pulse(
        self,
        x,
        y,
        color=(255, 130, 90),
        start_radius=10,
        end_radius=32,
        duration=0.12,
        width=2,
        fill_alpha=28,
    ):
        self.pulse_effects.append(
            PulseEffect(
                x,
                y,
                color=color,
                start_radius=start_radius,
                end_radius=end_radius,
                duration=duration,
                width=width,
                fill_alpha=fill_alpha,
            )
        )

    def damage_player(self, amount):
        result = self.player.take_damage(amount)
        if result == "shield":
            self.spawn_pulse(
                self.player.x,
                self.player.y,
                color=(180, 150, 255),
                start_radius=self.player.radius + 6,
                end_radius=self.player.radius + 20,
                duration=0.12,
                width=2,
                fill_alpha=18,
            )
        elif result == "hp":
            self.spawn_pulse(
                self.player.x,
                self.player.y,
                color=(255, 105, 105),
                start_radius=self.player.radius + 4,
                end_radius=self.player.radius + 16,
                duration=0.12,
                width=2,
                fill_alpha=16,
            )
        return result

    def damage_enemy(self, enemy, amount):
        if enemy not in self.enemies or amount <= 0 or enemy.hp <= 0:
            return
        enemy.hp -= amount
        self.spawn_damage_number(enemy.x, enemy.y, amount)
        self.spawn_pulse(enemy.x, enemy.y, color=(255, 150, 95), start_radius=8, end_radius=24, duration=0.11, width=2, fill_alpha=24)
        if enemy.hp <= 0 and enemy in self.enemies:
            self.enemies.remove(enemy)
            self.on_enemy_killed(enemy)

    def damage_boss(self, amount):
        if self.boss is None or amount <= 0 or self.boss.hp <= 0:
            return
        self.boss.hp -= amount
        self.spawn_damage_number(self.boss.x, self.boss.y, amount, color=(255, 175, 90))
        if self.boss.hp <= 0:
            self.on_boss_killed()

    def try_activate_ultimate(self):
        if self.player.ultimate_charge < self.player.ultimate_max:
            return False
        if self.player.ultimate_beam_time > 0:
            return False
        if self.player.ultimate_cooldown > 0:
            return False
        self.player.ultimate_charge = 0
        self.player.ultimate_beam_time = 10.0
        self.player.ultimate_cooldown = 0.0
        radius = 220
        self.ultimate_pulses.append(UltimatePulse(self.player.x, self.player.y, radius))
        for enemy in list(self.enemies):
            if distance((enemy.x, enemy.y), (self.player.x, self.player.y)) <= radius:
                self.damage_enemy(enemy, self.player.damage * 2.2)
        if self.boss is not None:
            if distance((self.boss.x, self.boss.y), (self.player.x, self.player.y)) <= radius:
                self.damage_boss(self.player.damage * 2.2)
        return True

    def try_activate_shockwave(self):
        if self.player.shockwave_timer < self.player.shockwave_cooldown:
            return False
        self.player.shockwave_timer = 0.0
        radius = self.player.shockwave_radius
        damage = self.player.damage * self.player.shockwave_damage + self.wave * 4.0
        self.shockwaves.append(Shockwave(self.player.x, self.player.y, radius))
        for enemy in list(self.enemies):
            dist = distance((enemy.x, enemy.y), (self.player.x, self.player.y))
            if dist <= radius:
                self.damage_enemy(enemy, damage)
        if self.boss is not None:
            dist = distance((self.boss.x, self.boss.y), (self.player.x, self.player.y))
            if dist <= radius:
                self.damage_boss(damage)
        return True

    def fire_ultimate_beam(self, target_pos):
        if not self.player.can_fire():
            return
        self.player.fire_timer = 0.18 if self.player.haste > 0 else 0.22
        sx, sy = self.player.x, self.player.y
        base_angle = math.atan2(target_pos[1] - sy, target_pos[0] - sx)
        level = max(0, int((self.player.bullets_per_shot - 1) / 2))
        pickup_bonus = 1 if self.player.multishot > 0 else 0
        beams = clamp(1 + level + pickup_bonus, 1, 12)
        max_spread = 0.35 + (beams / 80) * 0.95
        if beams == 1:
            offsets = [0.0]
        else:
            step = (2 * max_spread) / (beams - 1)
            offsets = [(-max_spread + i * step) for i in range(beams)]

        base_dist = math.hypot(target_pos[0] - sx, target_pos[1] - sy) or 1.0
        beam_width = 8

        for offset in offsets:
            ang = base_angle + offset
            ex = sx + math.cos(ang) * base_dist
            ey = sy + math.sin(ang) * base_dist
            self.ultimate_beams.append(UltimateBeam((sx, sy), (ex, ey)))

            dx = ex - sx
            dy = ey - sy
            seg_len = math.hypot(dx, dy) or 1.0
            dir_x = dx / seg_len
            dir_y = dy / seg_len
            best_proj = None
            impact_pos = None

            def consider_target(tx, ty, radius):
                nonlocal best_proj, impact_pos
                vx = tx - sx
                vy = ty - sy
                proj = vx * dir_x + vy * dir_y
                if proj < 0 or proj > seg_len:
                    return
                perp = abs(vx * dir_y - vy * dir_x)
                if perp <= radius + beam_width:
                    if best_proj is None or proj < best_proj:
                        best_proj = proj
                        impact_pos = (tx, ty)

            for enemy in self.enemies:
                consider_target(enemy.x, enemy.y, enemy.radius)
            if self.boss is not None:
                consider_target(self.boss.x, self.boss.y, self.boss.radius)

            if impact_pos is not None:
                self.ultimate_zones.append(UltimateZone(impact_pos[0], impact_pos[1]))

    def handle_collisions(self):
        for proj in list(self.projectiles):
            if proj.owner == "player":
                for enemy in list(self.enemies):
                    if distance((proj.x, proj.y), (enemy.x, enemy.y)) < proj.radius + enemy.radius:
                        self.damage_enemy(enemy, proj.damage)
                        if proj in self.projectiles:
                            self.projectiles.remove(proj)
                        break
                if proj in self.projectiles and self.boss is not None:
                    if distance((proj.x, proj.y), (self.boss.x, self.boss.y)) < proj.radius + self.boss.radius:
                        self.damage_boss(proj.damage)
                        self.projectiles.remove(proj)
            else:
                if distance((proj.x, proj.y), (self.player.x, self.player.y)) < proj.radius + self.player.radius:
                    self.damage_player(10)
                    if proj in self.projectiles:
                        self.projectiles.remove(proj)

        for enemy in self.enemies:
            if distance((enemy.x, enemy.y), (self.player.x, self.player.y)) < enemy.radius + self.player.radius:
                contact_damage = max(5, int(self.player.max_hp * 0.06))
                self.damage_player(contact_damage)

        if self.boss is not None:
            if distance((self.boss.x, self.boss.y), (self.player.x, self.player.y)) < self.boss.radius + self.player.radius:
                self.damage_player(self.boss_contact_damage())

        for orb in self.player.fire_orbiters:
            for enemy in self.enemies:
                if distance((orb.x, orb.y), (enemy.x, enemy.y)) < orb.size + enemy.radius:
                    if enemy.fire_orb_hit_cd <= 0:
                        orb_impact_damage = self.player.damage * 0.45
                        self.damage_enemy(enemy, orb_impact_damage)
                        enemy.fire_orb_hit_cd = 0.35
                    enemy.burn_timer = max(enemy.burn_timer, 3.0)
                    orb_burn_dps = 4.0 + enemy.max_hp * 0.05
                    enemy.burn_dps = max(enemy.burn_dps, orb_burn_dps)
            if self.boss is not None:
                if distance((orb.x, orb.y), (self.boss.x, self.boss.y)) < orb.size + self.boss.radius:
                    if self.boss.fire_orb_hit_cd <= 0:
                        orb_impact_damage = self.player.damage * 0.45
                        self.damage_boss(orb_impact_damage)
                        self.boss.fire_orb_hit_cd = 0.35
                    self.boss.burn_timer = max(self.boss.burn_timer, 3.0)
                    orb_burn_dps = 6.0 + self.boss.max_hp * 0.012
                    self.boss.burn_dps = max(self.boss.burn_dps, orb_burn_dps)

        if self.player.fire_ring:
            ring_radius = self.player.fire_ring_radius
            ring_thickness = 10
            for enemy in self.enemies:
                dist = distance((enemy.x, enemy.y), (self.player.x, self.player.y))
                if ring_radius - ring_thickness <= dist <= ring_radius + ring_thickness:
                    enemy.burn_timer = max(enemy.burn_timer, 4.0)
                    enemy.burn_dps = max(enemy.burn_dps, self.player.fire_ring_burn_dps)
            if self.boss is not None:
                dist = distance((self.boss.x, self.boss.y), (self.player.x, self.player.y))
                if ring_radius - ring_thickness <= dist <= ring_radius + ring_thickness:
                    self.boss.burn_timer = max(self.boss.burn_timer, 4.0)
                    self.boss.burn_dps = max(self.boss.burn_dps, self.player.fire_ring_burn_dps)

        for pickup in list(self.pickups):
            if distance((pickup.x, pickup.y), (self.player.x, self.player.y)) < pickup.radius + self.player.radius:
                if pickup.type == "shield":
                    self.player.shield = 6.0
                elif pickup.type == "multishot":
                    self.player.multishot = 12.0
                elif pickup.type == "haste":
                    self.player.haste = 6.0
                elif pickup.type == "heal":
                    self.player.heal_boost = 5.0
                self.pickups.remove(pickup)

        for gem in list(self.gems):
            if distance((gem.x, gem.y), (self.player.x, self.player.y)) < gem.collect_radius:
                self.gain_xp(gem.amount)
                self.gems.remove(gem)

    def get_nearest_enemy(self):
        px, py = self.player.x, self.player.y
        candidates = list(self.enemies)
        if self.boss is not None:
            candidates.append(self.boss)
        if not candidates:
            return None
        return min(candidates, key=lambda e: (e.x - px) ** 2 + (e.y - py) ** 2)

    def fire_rockets(self):
        target = self.get_nearest_enemy()
        if not target:
            return
        dx = target.x - self.player.x
        dy = target.y - self.player.y
        dist = math.hypot(dx, dy) or 1
        base_angle = math.atan2(dy, dx)
        count = self.player.rocket_count
        if count == 1:
            angles = [base_angle]
        else:
            spread = math.radians(60)
            step = spread * 2 / (count - 1)
            angles = [base_angle - spread + i * step for i in range(count)]
        for ang in angles:
            vx = math.cos(ang)
            vy = math.sin(ang)
            rocket = Rocket(
                self.player.x,
                self.player.y,
                vx * 320,
                vy * 320,
                damage=35 + self.player.damage * 0.4,
                target=target,
                get_target=self.get_nearest_enemy,
                explosion_radius=70,
                radius=12,
            )
            self.rockets.append(rocket)

    def update(self, dt):
        if self.state == "boss_death":
            self.boss_death_timer -= dt
            if self.boss_death_timer <= 0:
                self.boss_death_timer = 0.0
                self.wave += 1
                self.pending_upgrades += 1
                self.pending_wave_spawns += 1
                self.start_gem_rush()
                self.state = "wave_clear"

        keys = pygame.key.get_pressed()
        self.player.update(dt, keys)
        if self.player.rocket_count > 0:
            self.player.rocket_timer += dt
            while self.player.rocket_timer >= self.player.rocket_cooldown:
                self.player.rocket_timer -= self.player.rocket_cooldown
                self.fire_rockets()
        if self.player.shockwave_timer < self.player.shockwave_cooldown:
            self.player.shockwave_timer = min(
                self.player.shockwave_cooldown, self.player.shockwave_timer + dt
            )
        manual_fire = pygame.mouse.get_pressed(num_buttons=3)[0] or keys[pygame.K_SPACE]
        target_pos = pygame.mouse.get_pos()
        if not manual_fire:
            nearest = self.get_nearest_enemy()
            if nearest:
                target_pos = (nearest.x, nearest.y)
        self.player.set_aim(target_pos)
        for orb in self.player.fire_orbiters:
            rel_x, rel_y = orb.update(dt, orb.rel_x, orb.rel_y)
            orb.x = self.player.x + rel_x
            orb.y = self.player.y + rel_y
        if self.player.laser_orb_level > 0:
            if self.player.laser_orb is None:
                self.player.laser_orb = LaserOrb()
            self.player.laser_orb.update(dt, self.player.x, self.player.y)
            self.player.laser_orb_timer += dt
            if (
                self.player.laser_orb_beam_timer <= 0
                and self.player.laser_orb_timer >= self.player.laser_orb_cooldown
            ):
                target = self.get_nearest_enemy()
                if target:
                    self.player.laser_orb_timer -= self.player.laser_orb_cooldown
                    self.player.laser_orb_beam_timer = 1.0
                    self.player.laser_orb_beam_tick = 0.0
                    self.player.laser_orb_beam_pos = (target.x, target.y)
                    self.player.laser_orb_beam_target = target
                else:
                    self.player.laser_orb_timer = self.player.laser_orb_cooldown

            if self.player.laser_orb_beam_timer > 0 and self.player.laser_orb_beam_pos:
                beam_target = self.player.laser_orb_beam_target
                candidates = list(self.enemies)
                if self.boss is not None:
                    candidates.append(self.boss)
                if (
                    beam_target is None
                    or beam_target not in candidates
                    or beam_target.hp <= 0
                ):
                    if candidates:
                        px, py = self.player.laser_orb_beam_pos
                        beam_target = min(
                            candidates,
                            key=lambda e: (e.x - px) ** 2 + (e.y - py) ** 2,
                        )
                        self.player.laser_orb_beam_target = beam_target
                    else:
                        beam_target = None
                        self.player.laser_orb_beam_target = None
                if beam_target is not None:
                    self.player.laser_orb_beam_pos = (beam_target.x, beam_target.y)

                self.player.laser_orb_beam_tick -= dt
                while self.player.laser_orb_beam_timer > 0 and self.player.laser_orb_beam_tick <= 0:
                    self.player.laser_orb_beam_tick += 0.1
                    sx, sy = self.player.laser_orb.x, self.player.laser_orb.y
                    ex, ey = self.player.laser_orb_beam_pos
                    beam_width = 8
                    for enemy in list(self.enemies):
                        dist = point_segment_distance(enemy.x, enemy.y, sx, sy, ex, ey)
                        if dist <= enemy.radius + beam_width:
                            self.damage_enemy(enemy, self.player.laser_orb_damage)
                    if self.boss is not None:
                        dist = point_segment_distance(self.boss.x, self.boss.y, sx, sy, ex, ey)
                        if dist <= self.boss.radius + beam_width:
                            self.damage_boss(self.player.laser_orb_damage)
        if self.player.electroelf_level > 0:
            if self.player.electroelf is None:
                self.player.electroelf = ElectroElf()
            targets = list(self.enemies)
            if self.boss is not None:
                targets.append(self.boss)
            self.player.electroelf.update(dt, targets)
            self.player.electroelf_timer += dt
            if self.player.electroelf_timer >= self.player.electroelf_cooldown:
                self.player.electroelf_timer -= self.player.electroelf_cooldown
                if targets:
                    elf = self.player.electroelf
                    target = elf.target or min(
                        targets,
                        key=lambda e: (e.x - elf.x) ** 2 + (e.y - elf.y) ** 2,
                    )
                    strike_radius = self.player.electroelf_range
                    strike = LightningStrike(
                        (elf.x, elf.y),
                        (target.x, target.y),
                        radius=strike_radius,
                        damage=self.player.electroelf_damage,
                        target=target,
                        charge_time=0.45,
                        duration=0.28,
                    )
                    self.lightning_effects.append(strike)
        if manual_fire:
            if self.player.ultimate_beam_time > 0:
                self.fire_ultimate_beam(pygame.mouse.get_pos())
            else:
                self.player.fire(pygame.mouse.get_pos(), self.projectiles)
        else:
            if self.get_nearest_enemy():
                if self.player.ultimate_beam_time > 0:
                    self.fire_ultimate_beam(target_pos)
                else:
                    self.player.fire(target_pos, self.projectiles)

        for enemy in self.enemies:
            enemy.update(dt, (self.player.x, self.player.y), self.projectiles, self.wave)
            if enemy.kind == "tank" and enemy.beam_hits_player((self.player.x, self.player.y)):
                self.damage_player(20)

        for enemy in list(self.enemies):
            if enemy.hp <= 0:
                self.enemies.remove(enemy)
                self.on_enemy_killed(enemy)

        if self.boss is not None:
            self.boss.update(
                dt,
                (self.player.x, self.player.y),
                self.projectiles,
                self.boss_zones,
                self.wave,
                self.boss_attack_damage(),
            )
            if self.boss.laser_hits_player((self.player.x, self.player.y)) and self.boss.can_laser_damage():
                self.damage_player(self.boss_attack_damage())
            if self.boss is not None and self.boss.hp <= 0:
                self.on_boss_killed()

        for pickup in list(self.pickups):
            pickup.update(dt)
            if pickup.time_left <= 0:
                self.pickups.remove(pickup)

        for gem in list(self.gems):
            gem.update(dt, (self.player.x, self.player.y))
            if gem.time_left <= 0:
                self.gems.remove(gem)

        for proj in list(self.projectiles):
            proj.update(dt)
            if proj.offscreen():
                self.projectiles.remove(proj)

        for rocket in list(self.rockets):
            rocket.update(dt)
            if rocket.offscreen():
                if rocket.life <= 0:
                    self.explosions.append(
                        Explosion(rocket.x, rocket.y, rocket.explosion_radius, duration=0.25)
                    )
                self.rockets.remove(rocket)
                continue
            hit = None
            for enemy in self.enemies:
                if distance((rocket.x, rocket.y), (enemy.x, enemy.y)) < rocket.radius + enemy.radius:
                    hit = enemy
                    break
            hit_boss = False
            if self.boss is not None:
                if distance((rocket.x, rocket.y), (self.boss.x, self.boss.y)) < rocket.radius + self.boss.radius:
                    hit_boss = True
            if hit or hit_boss:
                for enemy in list(self.enemies):
                    if distance((rocket.x, rocket.y), (enemy.x, enemy.y)) <= rocket.explosion_radius:
                        self.damage_enemy(enemy, rocket.damage)
                if self.boss is not None:
                    if distance((rocket.x, rocket.y), (self.boss.x, self.boss.y)) <= rocket.explosion_radius:
                        self.damage_boss(rocket.damage)
                self.explosions.append(
                    Explosion(rocket.x, rocket.y, rocket.explosion_radius, duration=0.25)
                )
                self.rockets.remove(rocket)

        for explosion in list(self.explosions):
            explosion.update(dt)
            if explosion.time_left <= 0:
                self.explosions.remove(explosion)

        for shock in list(self.shockwaves):
            shock.update(dt)
            if shock.time_left <= 0:
                self.shockwaves.remove(shock)

        for beam in list(self.ultimate_beams):
            beam.update(dt)
            if beam.time_left <= 0:
                self.ultimate_beams.remove(beam)

        for pulse in list(self.ultimate_pulses):
            pulse.update(dt)
            if pulse.time_left <= 0:
                self.ultimate_pulses.remove(pulse)

        for zone in list(self.ultimate_zones):
            zone.update(dt)
            if zone.should_tick():
                damage = self.player.damage * 0.6
                for enemy in list(self.enemies):
                    if distance((enemy.x, enemy.y), (zone.x, zone.y)) <= zone.radius:
                        self.damage_enemy(enemy, damage)
                if self.boss is not None:
                    if distance((self.boss.x, self.boss.y), (zone.x, zone.y)) <= zone.radius:
                        self.damage_boss(damage)
            if zone.time_left <= 0:
                self.ultimate_zones.remove(zone)

        for zone in list(self.boss_zones):
            zone.update(dt)
            if zone.should_damage:
                zone.should_damage = False
                if distance((zone.x, zone.y), (self.player.x, self.player.y)) <= zone.radius + self.player.radius:
                    self.damage_player(zone.damage)
            if zone.time_left <= 0:
                self.boss_zones.remove(zone)

        for strike in list(self.lightning_effects):
            strike.update(dt)
            if strike.should_damage:
                strike.should_damage = False
                for enemy in list(self.enemies):
                    if distance((enemy.x, enemy.y), (strike.ex, strike.ey)) <= strike.radius:
                        self.damage_enemy(enemy, strike.damage)
                if self.boss is not None:
                    if distance((self.boss.x, self.boss.y), (strike.ex, strike.ey)) <= strike.radius:
                        self.damage_boss(strike.damage)
            if strike.time_left <= 0:
                self.lightning_effects.remove(strike)

        self.handle_collisions()

        for dmg in list(self.damage_numbers):
            dmg.update(dt)
            if dmg.time_left <= 0:
                self.damage_numbers.remove(dmg)
        for pulse in list(self.pulse_effects):
            pulse.update(dt)
            if pulse.time_left <= 0:
                self.pulse_effects.remove(pulse)

        if self.state == "playing" and not self.enemies and self.boss is None:
            self.wave += 1
            self.pending_upgrades += 1
            self.pending_wave_spawns += 1
            self.start_gem_rush()
            self.state = "wave_clear"
            return

        if self.state == "wave_clear":
            self.gem_rush_timer -= dt
            if self.gem_rush_timer <= 0 or not self.gems:
                if self.pending_upgrades > 0 and self.start_upgrade():
                    pass
                else:
                    self.state = "playing"
                self.gem_rush_timer = 0.0

    def draw_ui(self):
        def draw_panel(rect, accent=True):
            panel = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            panel.fill((18, 22, 30, 210))
            pygame.draw.rect(panel, (60, 90, 130, 220), panel.get_rect(), 2, border_radius=10)
            if accent:
                inner = panel.get_rect().inflate(-8, -8)
                pygame.draw.rect(panel, (90, 200, 255, 160), inner, 1, border_radius=8)
            self.screen.blit(panel, rect.topleft)

        def draw_bar(x, y, w, h, ratio, fill, back):
            pygame.draw.rect(self.screen, back, (x, y, w, h), border_radius=4)
            pygame.draw.rect(self.screen, fill, (x, y, w * ratio, h), border_radius=4)

        margin = 16
        top_y = 12

        # Left panel #
        left_w = 380
        left_h = 68
        left_rect = pygame.Rect(margin, top_y, left_w, left_h)
        draw_panel(left_rect)

        hp_ratio = clamp(self.player.hp / self.player.max_hp, 0, 1)
        fire_ratio = 1.0
        if self.player.fire_rate > 0:
            fire_ratio = clamp(1.0 - (self.player.fire_timer / self.player.fire_rate), 0, 1)

        bar_x = left_rect.x + 14
        hp_y = left_rect.y + 12
        fire_y = left_rect.y + 36
        main_bar_w = 230
        draw_bar(bar_x, hp_y, main_bar_w, 14, hp_ratio, (230, 90, 90), (30, 36, 46))
        draw_bar(bar_x, fire_y, main_bar_w, 10, fire_ratio, (240, 210, 90), (30, 36, 46))

        hp_text = self.font.render(f"PV {int(self.player.hp)}", True, WHITE)
        self.screen.blit(hp_text, (bar_x + 6, hp_y - 4))

        mini_w = 96
        mini_x = left_rect.right - mini_w - 12
        shield_ratio = clamp(self.player.shield / 6.0, 0, 1)
        rocket_ratio = 0.0
        if self.player.rocket_count > 0:
            rocket_ratio = clamp(self.player.rocket_timer / self.player.rocket_cooldown, 0, 1)
        draw_bar(mini_x, hp_y + 2, mini_w, 10, shield_ratio, PURPLE, (30, 36, 46))
        draw_bar(mini_x, fire_y, mini_w, 10, rocket_ratio, (255, 150, 60), (30, 36, 46))
        shield_label = self.font.render("SHD", True, WHITE)
        rocket_label = self.font.render("RKT", True, WHITE)
        self.screen.blit(shield_label, (mini_x + 4, hp_y - 6))
        self.screen.blit(rocket_label, (mini_x + 4, fire_y - 6))

        # wave panel #
        wave_w = 560
        wave_h = 40
        wave_x = WIDTH / 2 - wave_w / 2
        wave_rect = pygame.Rect(wave_x, top_y, wave_w, wave_h)
        draw_panel(wave_rect)
        wave_bar_w = wave_w - 40
        wave_bar_h = 12
        wave_bar_x = wave_rect.x + 20
        wave_bar_y = wave_rect.y + 18
        if self.boss is not None and self.boss.max_hp > 0:
            wave_ratio = clamp(1.0 - (self.boss.hp / self.boss.max_hp), 0, 1)
            wave_label = "BOSS"
            wave_fill = (230, 90, 90)
        elif self.wave_total > 0:
            wave_ratio = clamp(self.wave_killed / self.wave_total, 0, 1)
            wave_label = f"Vague {self.wave}"
            wave_fill = (120, 200, 255)
        else:
            wave_ratio = 0.0
            wave_label = f"Vague {self.wave}"
            wave_fill = (120, 200, 255)
        draw_bar(wave_bar_x, wave_bar_y, wave_bar_w, wave_bar_h, wave_ratio, wave_fill, (30, 36, 46))
        wave_text = self.font.render(wave_label, True, WHITE)
        self.screen.blit(
            wave_text,
            (wave_rect.centerx - wave_text.get_width() / 2, wave_rect.y + 2),
        )

        # Score panel #
        score_w = 210
        score_h = 40
        score_rect = pygame.Rect(WIDTH - score_w - margin, top_y, score_w, score_h)
        draw_panel(score_rect)
        score_text = self.font.render(f"SCORE {self.score}", True, WHITE)
        self.screen.blit(
            score_text,
            (score_rect.centerx - score_text.get_width() / 2, score_rect.y + 10),
        )

        # Buff panel #
        buff_x = margin
        buff_y = left_rect.bottom + 10
        buff_w = 220
        row_h = 22
        buffs = []
        if self.player.multishot > 0:
            buffs.append(
                {
                    "key": "multishot",
                    "time": self.player.multishot,
                    "max_time": 12.0,
                    "color": (90, 220, 140),
                    "fallback": WHITE,
                }
            )
        if self.player.haste > 0:
            buffs.append(
                {
                    "key": "haste",
                    "time": self.player.haste,
                    "max_time": 6.0,
                    "color": (240, 210, 90),
                    "fallback": GREEN,
                }
            )
        if self.player.heal_boost > 0:
            buffs.append(
                {
                    "key": "heal",
                    "time": self.player.heal_boost,
                    "max_time": 5.0,
                    "color": (80, 220, 120),
                    "fallback": GREEN,
                }
            )
        if buffs:
            buffs.sort(key=lambda b: b["time"], reverse=True)
            buff_h = 20 + row_h * len(buffs)
            buff_rect = pygame.Rect(buff_x, buff_y, buff_w, buff_h)
            draw_panel(buff_rect, accent=False)
            row_y = buff_rect.y + 10
            for buff in buffs:
                ratio = clamp(buff["time"] / buff["max_time"], 0, 1)
                draw_bar(
                    buff_rect.x + 32,
                    row_y,
                    buff_w - 48,
                    10,
                    ratio,
                    buff["color"],
                    (30, 36, 46),
                )
                icon = self.ui_icons.get(buff["key"])
                if icon:
                    self.screen.blit(icon, (buff_rect.x + 6, row_y - 6))
                else:
                    pygame.draw.circle(
                        self.screen, buff["fallback"], (buff_rect.x + 14, row_y + 4), 5
                    )
                row_y += row_h

        # XP panel (bottom-left)
        xp_w = 360
        xp_h = 34
        xp_rect = pygame.Rect(margin, HEIGHT - xp_h - 14, xp_w, xp_h)
        draw_panel(xp_rect)
        xp_ratio = clamp(self.player.xp / max(1, self.player.next_xp), 0, 1)
        draw_bar(xp_rect.x + 12, xp_rect.y + 12, xp_w - 24, 10, xp_ratio, CYAN, (30, 36, 46))
        lvl_text = self.font.render(f"NIV {self.player.level}", True, WHITE)
        self.screen.blit(lvl_text, (xp_rect.right + 8, xp_rect.y + 6))

        # Ultimate panel (bottom-right)
        ult_w = 300
        ult_h = 34
        ult_rect = pygame.Rect(WIDTH - ult_w - margin, HEIGHT - ult_h - 14, ult_w, ult_h)
        draw_panel(ult_rect)
        ult_ratio = clamp(self.player.ultimate_charge / max(1, self.player.ultimate_max), 0, 1)
        ult_color = (255, 220, 80) if ult_ratio >= 1 else (160, 170, 120)
        draw_bar(ult_rect.x + 12, ult_rect.y + 12, ult_w - 24, 10, ult_ratio, ult_color, (30, 36, 46))
        ult_label = self.font.render("ULT (A)", True, WHITE)
        self.screen.blit(ult_label, (ult_rect.centerx - ult_label.get_width() / 2, ult_rect.y - 8))
        # Ultimate cooldown display
        if self.player.ultimate_cooldown > 0:
            cooldown_text = self.font.render(f"{self.player.ultimate_cooldown:.1f}", True, (255, 100, 100))
            self.screen.blit(cooldown_text, (ult_rect.x + 12, ult_rect.y + 12))

        # Shockwave panel (above ULT)
        shock_w = 240
        shock_h = 28
        shock_rect = pygame.Rect(
            WIDTH - shock_w - margin, ult_rect.y - shock_h - 10, shock_w, shock_h
        )
        draw_panel(shock_rect, accent=False)
        shock_ratio = clamp(
            self.player.shockwave_timer / max(0.01, self.player.shockwave_cooldown), 0, 1
        )
        draw_bar(
            shock_rect.x + 10,
            shock_rect.y + 10,
            shock_w - 20,
            8,
            shock_ratio,
            (120, 220, 255),
            (30, 36, 46),
        )
        shock_label = self.font.render("ONDE (E)", True, WHITE)
        self.screen.blit(
            shock_label,
            (shock_rect.centerx - shock_label.get_width() / 2, shock_rect.y - 8),
        )

    def draw_cheat_buttons(self):
        if not self.cheats_enabled:
            return
        if not self.cheat_buttons:
            self.build_cheat_buttons()
        mouse_pos = pygame.mouse.get_pos()
        for btn in self.cheat_buttons:
            rect = btn["rect"]
            hovered = rect.collidepoint(mouse_pos)
            color = (40, 50, 70) if hovered else (28, 34, 46)
            pygame.draw.rect(self.screen, color, rect, border_radius=6)
            pygame.draw.rect(self.screen, (90, 160, 220), rect, 2, border_radius=6)
            label = self.font.render(btn["label"], True, (220, 235, 255))
            self.screen.blit(label, (rect.x + 8, rect.y + 6))

    def draw_upgrade_screen(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((8, 10, 16, 225))
        self.screen.blit(overlay, (0, 0))
        panel_w = int(WIDTH * 0.8)
        panel_h = int(HEIGHT * 0.8)
        panel_x = (WIDTH - panel_w) / 2
        panel_y = (HEIGHT - panel_h) / 2
        panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
        pygame.draw.rect(self.screen, (18, 22, 30), panel_rect, border_radius=14)
        pygame.draw.rect(self.screen, (70, 110, 160), panel_rect, 2, border_radius=14)
        inner = panel_rect.inflate(-16, -16)
        pygame.draw.rect(self.screen, (90, 200, 255), inner, 1, border_radius=12)

        title = self.big_font.render("Choisis un upgrade", True, (200, 230, 255))
        self.screen.blit(
            title, (panel_x + panel_w / 2 - title.get_width() / 2, panel_y - 36)
        )

        mouse_pos = pygame.mouse.get_pos()
        epic_keys = {u.key for u in EPIC_UPGRADES}
        for btn in self.ui_buttons:
            rect = btn["rect"]
            choice = btn["choice"]
            hovered = rect.collidepoint(mouse_pos)
            is_epic = choice.key in epic_keys
            if is_epic:
                color = (60, 50, 90) if hovered else (45, 40, 70)
                border = (150, 120, 230)
            else:
                color = (35, 40, 55) if hovered else (26, 30, 42)
                border = (90, 140, 190)
            pygame.draw.rect(self.screen, color, rect, border_radius=10)
            pygame.draw.rect(self.screen, border, rect, 2, border_radius=8)
            label = self.big_font.render(choice.label, True, (230, 240, 255))
            desc = self.font.render(choice.desc, True, (190, 210, 230))
            name_h = int(rect.height * 0.12)
            img_h = int(rect.height * 0.8)
            name_y = rect.y + 10
            self.screen.blit(label, (rect.x + 16, name_y))

            img_area = pygame.Rect(rect.x + 16, rect.y + name_h, rect.width - 32, img_h)
            icon = self.upgrade_icons.get(choice.key)
            if icon:
                scale = min(img_area.width / icon.get_width(), img_area.height / icon.get_height())
                size = (int(icon.get_width() * scale), int(icon.get_height() * scale))
                sprite = pygame.transform.smoothscale(icon, size)
                sprite_rect = sprite.get_rect(center=img_area.center)
                self.screen.blit(sprite, sprite_rect.topleft)
            else:
                pygame.draw.rect(self.screen, (30, 30, 38), img_area, border_radius=8)
                pygame.draw.rect(self.screen, (70, 70, 90), img_area, 2, border_radius=8)

            desc_y = rect.y + name_h + img_h + 6
            self.screen.blit(desc, (rect.x + 16, desc_y))

    def draw_game_over(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((8, 10, 16, 230))
        self.screen.blit(overlay, (0, 0))
        panel_w = 520
        panel_h = 240
        panel_rect = pygame.Rect(WIDTH / 2 - panel_w / 2, 120, panel_w, panel_h)
        pygame.draw.rect(self.screen, (18, 22, 30), panel_rect, border_radius=14)
        pygame.draw.rect(self.screen, (90, 140, 200), panel_rect, 2, border_radius=14)
        inner = panel_rect.inflate(-16, -16)
        pygame.draw.rect(self.screen, (120, 210, 255), inner, 1, border_radius=12)

        title = self.big_font.render("Game Over", True, (230, 90, 90))
        self.screen.blit(title, (panel_rect.centerx - title.get_width() / 2, panel_rect.y + 26))
        score = self.font.render(f"Score: {self.score}  |  Vague: {self.wave}", True, (200, 220, 240))
        self.screen.blit(score, (panel_rect.centerx - score.get_width() / 2, panel_rect.y + 76))
        hint = self.font.render("Choisis un bouton pour continuer", True, (180, 200, 220))
        self.screen.blit(hint, (panel_rect.centerx - hint.get_width() / 2, panel_rect.y + 110))

        mouse_pos = pygame.mouse.get_pos()
        for btn in self.ui_buttons:
            rect = btn["rect"]
            action = btn["action"]
            hovered = rect.collidepoint(mouse_pos)
            color = (45, 55, 75) if hovered else (30, 36, 48)
            pygame.draw.rect(self.screen, color, rect, border_radius=10)
            pygame.draw.rect(self.screen, (90, 160, 220), rect, 2, border_radius=10)
            text = "Rejouer" if action == "replay" else "Quitter"
            label = self.big_font.render(text, True, (220, 235, 255))
            self.screen.blit(
                label, (rect.x + rect.width / 2 - label.get_width() / 2, rect.y + 14)
            )

    def draw_pause(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((8, 10, 16, 220))
        self.screen.blit(overlay, (0, 0))
        panel_w = 520
        panel_h = 220
        panel_rect = pygame.Rect(WIDTH / 2 - panel_w / 2, HEIGHT / 2 - panel_h / 2, panel_w, panel_h)
        pygame.draw.rect(self.screen, (18, 22, 30), panel_rect, border_radius=14)
        pygame.draw.rect(self.screen, (90, 140, 200), panel_rect, 2, border_radius=14)
        inner = panel_rect.inflate(-16, -16)
        pygame.draw.rect(self.screen, (120, 210, 255), inner, 1, border_radius=12)

        title = self.big_font.render("Pause", True, (210, 230, 255))
        self.screen.blit(title, (panel_rect.centerx - title.get_width() / 2, panel_rect.y + 26))

        mouse_pos = pygame.mouse.get_pos()
        for btn in self.ui_buttons:
            rect = btn["rect"]
            action = btn["action"]
            hovered = rect.collidepoint(mouse_pos)
            color = (45, 55, 75) if hovered else (30, 36, 48)
            pygame.draw.rect(self.screen, color, rect, border_radius=10)
            pygame.draw.rect(self.screen, (90, 160, 220), rect, 2, border_radius=10)
            text = "Reprendre" if action == "resume" else ("Rejouer" if action == "replay" else "Quitter")
            label = self.big_font.render(text, True, (220, 235, 255))
            self.screen.blit(
                label, (rect.x + rect.width / 2 - label.get_width() / 2, rect.y + 14)
            )

    def draw(self):
        self.screen.fill(BG_COLOR)
        for pickup in self.pickups:
            pickup.draw(self.screen)
        for gem in self.gems:
            gem.draw(self.screen)
        for zone in self.boss_zones:
            zone.draw(self.screen)
        for enemy in self.enemies:
            enemy.draw(self.screen)
        if self.boss is not None:
            self.boss.draw(self.screen)
        for proj in self.projectiles:
            proj.draw(self.screen)
        for rocket in self.rockets:
            rocket.draw(self.screen)
        for explosion in self.explosions:
            explosion.draw(self.screen)
        for shock in self.shockwaves:
            shock.draw(self.screen)
        for pulse in self.ultimate_pulses:
            pulse.draw(self.screen)
        for zone in self.ultimate_zones:
            zone.draw(self.screen)
        for beam in self.ultimate_beams:
            beam.draw(self.screen)
        for strike in self.lightning_effects:
            strike.draw(self.screen)
        for pulse in self.pulse_effects:
            pulse.draw(self.screen)
        for dmg in self.damage_numbers:
            ratio = clamp(dmg.time_left / max(0.001, dmg.duration), 0.0, 1.0)
            alpha = int(255 * ratio)
            value = max(1, int(round(dmg.amount)))
            font = self.get_damage_font(dmg.font_size)
            text = str(value)
            text_surf = font.render(text, True, dmg.color)
            shadow_surf = font.render(text, True, (25, 18, 18))
            if alpha < 255:
                text_surf.set_alpha(alpha)
                shadow_surf.set_alpha(alpha)
            x = int(dmg.x - text_surf.get_width() / 2)
            y = int(dmg.y - text_surf.get_height() / 2)
            self.screen.blit(shadow_surf, (x + 2, y + 2))
            self.screen.blit(text_surf, (x, y))
        if self.player.electroelf:
            self.player.electroelf.draw(self.screen)
        self.player.draw(self.screen)
        self.draw_ui()
        self.draw_cheat_buttons()
        if self.state == "upgrade":
            self.draw_upgrade_screen()
        if self.state == "game_over":
            self.draw_game_over()
        if self.state == "pause":
            self.draw_pause()

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_o:
                    self.cheats_enabled = not self.cheats_enabled
                    self.cheat_buttons = []
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    if self.state == "playing":
                        self.state = "pause"
                        self.build_pause_buttons()
                    elif self.state == "pause":
                        self.state = "playing"
                if event.type == pygame.KEYDOWN and event.key == pygame.K_a:
                    if self.state == "playing":
                        self.try_activate_ultimate()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                    if self.state == "playing":
                        self.try_activate_shockwave()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.state == "upgrade":
                        for btn in self.ui_buttons:
                            if btn["rect"].collidepoint(event.pos):
                                self.apply_upgrade(btn["choice"].key)
                                if self.pending_upgrades > 0:
                                    self.pending_upgrades -= 1
                                if self.pending_wave_spawns > 0:
                                    self.projectiles.clear()
                                    self.spawn_wave(self.wave)
                                    self.pending_wave_spawns -= 1
                                if self.pending_upgrades > 0 and self.start_upgrade():
                                    pass
                                else:
                                    self.state = "playing"
                                    self.ui_buttons = []
                                break
                    elif self.state == "game_over":
                        for btn in self.ui_buttons:
                            if btn["rect"].collidepoint(event.pos):
                                if btn["action"] == "replay":
                                    self.reset_game()
                                else:
                                    running = False
                                break
                    elif self.state == "pause":
                        for btn in self.ui_buttons:
                            if btn["rect"].collidepoint(event.pos):
                                if btn["action"] == "resume":
                                    self.state = "playing"
                                elif btn["action"] == "replay":
                                    self.reset_game()
                                else:
                                    running = False
                                break
                    elif self.state == "playing" and self.cheats_enabled:
                        for btn in self.cheat_buttons:
                            if btn["rect"].collidepoint(event.pos):
                                if btn["key"] == "level_up":
                                    self.gain_xp(self.player.next_xp)
                                elif btn["key"] == "ult_full":
                                    self.player.ultimate_charge = self.player.ultimate_max
                                else:
                                    self.apply_upgrade(btn["key"])
                                self.cheat_buttons = []
                                break

            if self.state in ("playing", "wave_clear", "boss_death"):
                self.update(dt)

            if self.player.hp <= 0:
                self.state = "game_over"
                self.build_game_over_buttons()

            self.draw()
            pygame.display.flip()

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    Game().run()
