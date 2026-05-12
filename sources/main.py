import math
import os
import random
import sys
from dataclasses import dataclass
from typing import Optional
import pygame

BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "datas")

WIDTH, HEIGHT = 1920, 1080
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

def draw_sword(surf, x, y, angle, sword_length, beam_width, alpha_ratio, hilt_ratio=0.22):
    """
    Dessine l'épée (pour classe maitre d'épée)
    
    Args:
        surf: Surface pygame sur laquelle dessiner
        x, y: Position de la garde (base de l'épée)
        angle: Angle en radians de l'orientation de l'épée
        sword_length: Longueur totale de l'épée
        beam_width: Largeur de base de l'épée
        alpha_ratio: Ratio d'opacité (0 à 1)
        hilt_ratio: Proportion du manche (défaut 0.22)
    """
    ux = math.cos(angle)
    uy = math.sin(angle)
    px = -uy
    py = ux
    ratio = clamp(alpha_ratio, 0.0, 1.0)
    
    hilt_len = sword_length * hilt_ratio
    blade_len = sword_length * (1.0 - hilt_ratio)
    blade_base_x = x + ux * 2.0
    blade_base_y = y + uy * 2.0
    tip_x = blade_base_x + ux * blade_len
    tip_y = blade_base_y + uy * blade_len
    handle_end_x = x - ux * hilt_len
    handle_end_y = y - uy * hilt_len

    guard_half = max(24.0, beam_width * 1.32)
    handle_w = max(18.0, beam_width * 1.04)
    blade_w = max(18.0, beam_width * 0.88)
    blade_mid_w = blade_w * 0.82
    blade_mid_x = blade_base_x + ux * blade_len * 0.72
    blade_mid_y = blade_base_y + uy * blade_len * 0.72
    blade_near_tip_w = blade_w * 0.62
    blade_near_tip_x = blade_base_x + ux * blade_len * 0.92
    blade_near_tip_y = blade_base_y + uy * blade_len * 0.92

    pygame.draw.line(
        surf,
        (150, 222, 255, int(85 + 65 * ratio)),
        (int(x), int(y)),
        (int(tip_x), int(tip_y)),
        max(4, int(beam_width * 0.34)),
    )
    pygame.draw.line(
        surf,
        (250, 252, 255, int(120 + 80 * ratio)),
        (int(x), int(y)),
        (int(tip_x), int(tip_y)),
        2,
    )

    blade_pts = [
        (int(blade_base_x + px * blade_w), int(blade_base_y + py * blade_w)),
        (int(blade_mid_x + px * blade_mid_w), int(blade_mid_y + py * blade_mid_w)),
        (int(blade_near_tip_x + px * blade_near_tip_w), int(blade_near_tip_y + py * blade_near_tip_w)),
        (int(tip_x), int(tip_y)),
        (int(blade_near_tip_x - px * blade_near_tip_w), int(blade_near_tip_y - py * blade_near_tip_w)),
        (int(blade_mid_x - px * blade_mid_w), int(blade_mid_y - py * blade_mid_w)),
        (int(blade_base_x - px * blade_w), int(blade_base_y - py * blade_w)),
    ]
    pygame.draw.polygon(surf, (105, 205, 255, int(138 + 82 * ratio)), blade_pts)
    pygame.draw.polygon(surf, (228, 246, 255, int(205 + 40 * ratio)), blade_pts, 2)

    fuller_end_x = blade_base_x + ux * blade_len * 0.83
    fuller_end_y = blade_base_y + uy * blade_len * 0.83
    pygame.draw.line(
        surf,
        (255, 255, 255, int(170 + 70 * ratio)),
        (int(blade_base_x), int(blade_base_y)),
        (int(fuller_end_x), int(fuller_end_y)),
        max(1, int(beam_width * 0.12)),
    )

    guard_l = (x + px * guard_half, y + py * guard_half)
    guard_r = (x - px * guard_half, y - py * guard_half)
    pygame.draw.line(
        surf,
        (115, 225, 255, int(150 + 72 * ratio)),
        (int(guard_l[0]), int(guard_l[1])),
        (int(guard_r[0]), int(guard_r[1])),
        max(6, int(beam_width * 0.32)),
    )
    pygame.draw.line(
        surf,
        (255, 255, 255, int(175 + 65 * ratio)),
        (int(guard_l[0]), int(guard_l[1])),
        (int(guard_r[0]), int(guard_r[1])),
        2,
    )

    pygame.draw.line(
        surf,
        (66, 44, 92, int(178 + 60 * ratio)),
        (int(x), int(y)),
        (int(handle_end_x), int(handle_end_y)),
        int(handle_w + 5),
    )
    pygame.draw.line(
        surf,
        (230, 182, 255, int(188 + 52 * ratio)),
        (int(x), int(y)),
        (int(handle_end_x), int(handle_end_y)),
        3,
    )

    pommel_r = max(5, int(handle_w * 1.05))
    pygame.draw.circle(
        surf,
        (95, 210, 255, int(170 + 68 * ratio)),
        (int(handle_end_x), int(handle_end_y)),
        pommel_r + 2,
    )
    pygame.draw.circle(
        surf,
        (255, 255, 255, int(192 + 56 * ratio)),
        (int(handle_end_x), int(handle_end_y)),
        max(2, pommel_r // 2 + 1),
    )

###################
# --- Classes --- #
###################
class Projectile:
    def __init__(self, x, y, vx, vy, damage, color=YELLOW, radius=4, owner="player", ricochet_bounces=0):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.damage = damage
        self.radius = radius
        self.color = color
        self.owner = owner
        self.ricochet_bounces = max(0, int(ricochet_bounces))
        self.hit_targets = set()

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
        self.vx = 0.0
        self.vy = 0.0
        self.attract = 520.0
        self.max_speed = 540.0
        self.drag = 0.9
        self.pickup_range = 260.0
        self.magnet_locked = False
        self.magnet_time = 0.0
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

    def update(self, dt, player_pos=None):
        self.time_left -= dt
        if player_pos is None:
            return
        dx = player_pos[0] - self.x
        dy = player_pos[1] - self.y
        dist = math.hypot(dx, dy)
        if not self.magnet_locked and dist <= self.pickup_range:
            self.magnet_locked = True
            self.magnet_time = 0.0
        if not self.magnet_locked and dist > self.pickup_range:
            self.vx *= 0.82
            self.vy *= 0.82
            return
        if self.magnet_locked:
            self.magnet_time += dt
        ramp_force = 1.0 + min(7.0, self.magnet_time * 2.1)
        ramp_speed = 1.0 + min(6.0, self.magnet_time * 1.7)
        drag = min(0.98, self.drag + 0.06) if self.magnet_locked else self.drag
        dist = dist or 1.0
        ax = dx / dist * (self.attract * ramp_force)
        ay = dy / dist * (self.attract * ramp_force)
        self.vx += ax * dt
        self.vy += ay * dt
        self.vx *= drag
        self.vy *= drag
        speed = math.hypot(self.vx, self.vy)
        max_speed = self.max_speed * ramp_speed
        if speed > max_speed:
            scale = max_speed / speed
            self.vx *= scale
            self.vy *= scale
        self.x += self.vx * dt
        self.y += self.vy * dt

class ExpGem:
    _sprite_base = None
    _sprite_missing = False

    def __init__(self, x, y, amount=1):
        self.x = x
        self.y = y
        self.amount = amount
        self.radius = 6
        self.collect_radius = 42
        self.vx = 0.0
        self.vy = 0.0
        self.attract = 340.0
        self.max_speed = 420.0
        self.drag = 0.92
        self.pickup_range = 220.0
        self.magnet_locked = False
        self.magnet_time = 0.0
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
        if not self.magnet_locked and dist <= self.pickup_range:
            self.magnet_locked = True
            self.magnet_time = 0.0
        if not self.magnet_locked and dist > self.pickup_range:
            self.vx = 0.0
            self.vy = 0.0
            return
        if self.magnet_locked:
            self.magnet_time += dt
        ramp_force = 1.0 + min(8.0, self.magnet_time * 2.4)
        ramp_speed = 1.0 + min(7.0, self.magnet_time * 1.9)
        drag = min(0.985, self.drag + 0.05) if self.magnet_locked else self.drag
        dist = dist or 1.0
        ax = dx / dist * (self.attract * ramp_force)
        ay = dy / dist * (self.attract * ramp_force)
        self.vx += ax * dt
        self.vy += ay * dt
        self.vx *= drag
        self.vy *= drag
        speed = math.hypot(self.vx, self.vy)
        max_speed = self.max_speed * ramp_speed
        if speed > max_speed:
            scale = max_speed / speed
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
    STYLE = {
        "basic": {
            "shape": "circle",
            "radius": 14,
            "primary": (55, 160, 255),
            "secondary": (110, 220, 255),
            "core": (220, 245, 255),
        },
        "fast": {
            "shape": "arrow",
            "radius": 12,
            "primary": (255, 210, 65),
            "secondary": (255, 242, 135),
            "core": (255, 250, 215),
        },
        "tank": {
            "shape": "square",
            "radius": 22,
            "primary": (90, 245, 130),
            "secondary": (155, 255, 190),
            "core": (220, 255, 235),
        },
        "shooter": {
            "shape": "star7",
            "radius": 17,
            "primary": (255, 85, 85),
            "secondary": (255, 145, 130),
            "core": (255, 225, 215),
        },
    }

    def __init__(self, x, y, kind, wave):
        self.x = x
        self.y = y
        self.kind = kind
        base_speed = 70 + wave * 3
        self.speed = base_speed
        self.radius = 14
        self.max_hp = 20
        self.shoot_cooldown = 0.0
        self.rotation = 0.0
        self.facing_angle = 0.0
        self.beam_timer = 0.0
        self.beam_charge = 0.0
        self.beam_active = 0.0
        self.beam_angle = 0.0
        self.beam_length = WIDTH
        self.beam_width = 14
        self.neon_phase = random.uniform(0.0, math.tau)
        self.neon_flicker = random.uniform(2.3, 3.6)
        
        if kind == "fast":
            self.speed *= 3.0
            self.max_hp = 20 + wave * 8
        elif kind == "tank":
            self.speed *= 0.65
            self.max_hp = 75 + wave * 24
            self.beam_timer = 2.0
        elif kind == "shooter":
            self.speed *= 0.9
            self.max_hp = 30 + wave * 16
            self.shoot_cooldown = random.uniform(0.2, 0.8)
        else:
            self.max_hp = 25 + wave * 12

        style = Enemy.STYLE.get(kind, Enemy.STYLE["basic"])
        self.shape = style["shape"]
        self.neon_primary = style["primary"]
        self.neon_secondary = style["secondary"]
        self.neon_core = style["core"]
        self.radius = style["radius"]

        self.hp = self.max_hp
        self.burn_timer = 0.0
        self.burn_dps = 0.0
        self.burn_source = "fire_orb_burn"
        self.fire_orb_hit_cd = 0.0
        self.ally_hit_cd = 0.0
        self.is_ally = False
        self.ally_time = 0.0
        self.ally_source = "bio_minions"
        self.ally_power = 1.0
        self.base_neon_primary = self.neon_primary
        self.base_neon_secondary = self.neon_secondary
        self.base_neon_core = self.neon_core

    @staticmethod
    def _mix_color(color_a, color_b, t):
        t = clamp(t, 0.0, 1.0)
        return (
            int(color_a[0] + (color_b[0] - color_a[0]) * t),
            int(color_a[1] + (color_b[1] - color_a[1]) * t),
            int(color_a[2] + (color_b[2] - color_a[2]) * t),
        )

    @staticmethod
    def _regular_polygon(center, radius, sides, angle_offset=0.0):
        cx, cy = center
        points = []
        for i in range(sides):
            angle = angle_offset + i * (math.tau / sides)
            points.append((int(cx + math.cos(angle) * radius), int(cy + math.sin(angle) * radius)))
        return points

    @staticmethod
    def _star_polygon(center, outer_radius, inner_radius, branches, angle_offset=0.0):
        cx, cy = center
        points = []
        total = branches * 2
        for i in range(total):
            radius = outer_radius if i % 2 == 0 else inner_radius
            angle = angle_offset + i * (math.tau / total)
            points.append((int(cx + math.cos(angle) * radius), int(cy + math.sin(angle) * radius)))
        return points

    @staticmethod
    def _arrow_polygon(center, radius, angle):
        cx, cy = center
        points = []
        template = [
            (1.0, 0.0),
            (0.2, 0.56),
            (0.2, 0.22),
            (-0.9, 0.22),
            (-0.9, -0.22),
            (0.2, -0.22),
            (0.2, -0.56),
        ]
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        for tx, ty in template:
            px = tx * radius
            py = ty * radius
            rx = px * cos_a - py * sin_a
            ry = px * sin_a + py * cos_a
            points.append((int(cx + rx), int(cy + ry)))
        return points

    def _shape_angle(self, now):
        if self.shape == "arrow":
            return self.facing_angle
        if self.shape == "square":
            return self.facing_angle + math.pi / 4
        if self.shape == "star7":
            return now * 1.9 + self.neon_phase
        return now * 0.5 + self.neon_phase * 0.5

    def _draw_shape(self, surface, center, radius, color, width, angle):
        radius = max(2, int(radius))
        width = max(0, int(width))
        if self.shape == "circle":
            pygame.draw.circle(surface, color, center, radius, width)
            return
        if self.shape == "square":
            points = self._regular_polygon(center, radius, 4, angle)
            pygame.draw.polygon(surface, color, points, width)
            return
        if self.shape == "star7":
            points = self._star_polygon(center, radius, radius * 0.45, 7, angle - math.pi / 2)
            pygame.draw.polygon(surface, color, points, width)
            return
        if self.shape == "arrow":
            points = self._arrow_polygon(center, radius, angle)
            pygame.draw.polygon(surface, color, points, width)
            return
        pygame.draw.circle(surface, color, center, radius, width)

    def _draw_neon_body(self, screen):
        now = pygame.time.get_ticks() * 0.001
        pulse = 0.5 + 0.5 * math.sin(now * self.neon_flicker + self.neon_phase)
        twinkle = 0.5 + 0.5 * math.sin(now * (self.neon_flicker * 1.55) + self.neon_phase * 1.2)
        glow_color = self._mix_color(self.neon_primary, self.neon_secondary, pulse)
        rim_color = self._mix_color(glow_color, (255, 255, 255), 0.3 + twinkle * 0.2)
        inner_color = self._mix_color(BG_COLOR, glow_color, 0.08 + pulse * 0.08)
        angle = self._shape_angle(now)

        base_r = int(self.radius)
        tube_width = max(3, int(base_r * 0.3))
        pad = int(base_r * 1.8) + 20
        size = base_r * 2 + pad * 2
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        center = (size // 2, size // 2)

        self._draw_shape(
            surf,
            center,
            base_r - max(1, tube_width // 2),
            (*inner_color, 160),
            0,
            angle,
        )

        for spread, alpha in ((10, 24), (7, 42), (4, 68)):
            glow_radius = base_r + spread * (0.72 + twinkle * 0.22)
            glow_width = tube_width + spread
            self._draw_shape(
                surf,
                center,
                glow_radius,
                (*glow_color, int(alpha + pulse * 20)),
                glow_width,
                angle,
            )

        self._draw_shape(surf, center, base_r, (*glow_color, 235), tube_width, angle)
        self._draw_shape(surf, center, base_r - 1, (*rim_color, 205), max(1, tube_width // 3), angle)
        self._draw_shape(
            surf,
            center,
            max(2, base_r - tube_width - 1),
            (*self._mix_color(inner_color, self.neon_core, 0.2), 88),
            1,
            angle,
        )

        rect = surf.get_rect(center=(int(self.x), int(self.y)))
        screen.blit(surf, rect.topleft)
    
    def set_ally(self, duration=None, source="bio_minions", power=1.0):
        self.is_ally = True
        if self.ally_time < 0:
            pass
        elif duration is None or duration <= 0:
            self.ally_time = -1.0
        else:
            self.ally_time = max(self.ally_time, duration)
        self.ally_source = source
        self.ally_power = max(self.ally_power, power)
        self.neon_primary = (110, 220, 255)
        self.neon_secondary = (195, 242, 255)
        self.neon_core = (255, 255, 255)
        self.beam_charge = 0.0
        self.beam_active = 0.0
        self.beam_timer = min(self.beam_timer, 0.5) if self.kind == "tank" else self.beam_timer
        self.shoot_cooldown = min(self.shoot_cooldown, 0.2) if self.kind == "shooter" else self.shoot_cooldown

    def clear_ally_state(self):
        self.is_ally = False
        self.ally_time = 0.0
        self.ally_source = "bio_minions"
        self.ally_power = 1.0
        self.neon_primary = self.base_neon_primary
        self.neon_secondary = self.base_neon_secondary
        self.neon_core = self.base_neon_core

    def update(self, dt, player_pos, projectiles, wave, ally_target_pos=None):
        target_pos = player_pos
        if self.is_ally and ally_target_pos is not None:
            target_pos = ally_target_pos
        dx = target_pos[0] - self.x
        dy = target_pos[1] - self.y
        dist = math.hypot(dx, dy) or 1
        vx = dx / dist * self.speed
        vy = dy / dist * self.speed
        self.x += vx * dt
        self.y += vy * dt
        self.facing_angle = math.atan2(dy, dx)
        self.rotation = math.degrees(self.facing_angle)

        if self.burn_timer > 0:
            self.burn_timer -= dt
            self.hp -= self.burn_dps * dt
        self.fire_orb_hit_cd = max(0.0, self.fire_orb_hit_cd - dt)
        self.ally_hit_cd = max(0.0, self.ally_hit_cd - dt)
        if self.is_ally:
            if self.ally_time > 0:
                self.ally_time = max(0.0, self.ally_time - dt)
                if self.ally_time <= 0:
                    self.clear_ally_state()

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
                owner = "enemy"
                proj_damage = 14 + wave * 0.7
                proj_color = RED
                if self.is_ally:
                    owner = f"ally:{self.ally_source}"
                    proj_damage *= self.ally_power
                    proj_color = (120, 220, 255)
                proj = Projectile(
                    self.x,
                    self.y,
                    sx * (220 + wave * 6),
                    sy * (220 + wave * 6),
                    damage=proj_damage,
                    color=proj_color,
                    radius=4,
                    owner=owner,
                )
                projectiles.append(proj)

    def draw(self, screen):
        self._draw_neon_body(screen)
        if self.kind == "tank":
            if self.beam_charge > 0:
                self._draw_beam(screen, (165, 255, 195), 5)
            if self.beam_active > 0:
                if self.is_ally:
                    self._draw_beam(screen, (120, 220, 255), 7)
                else:
                    self._draw_beam(screen, (100, 255, 140), 7)
        if self.burn_timer > 0:
            burn_color = self._mix_color((255, 120, 60), self.neon_secondary, 0.35)
            pygame.draw.circle(screen, burn_color, (int(self.x), int(self.y)), self.radius + 4, 2)
        hp_ratio = clamp(self.hp / self.max_hp, 0, 1)
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
        glow = self._mix_color(color, (255, 255, 255), 0.35)
        pygame.draw.line(screen, self._mix_color(color, BG_COLOR, 0.5), (self.x, self.y), (ex, ey), width + 6)
        pygame.draw.line(screen, color, (self.x, self.y), (ex, ey), width)
        pygame.draw.line(screen, glow, (self.x, self.y), (ex, ey), max(1, width // 2))

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

    def beam_hits_entity(self, target_pos, radius):
        if self.beam_active <= 0:
            return False
        dx = target_pos[0] - self.x
        dy = target_pos[1] - self.y
        dir_x = math.cos(self.beam_angle)
        dir_y = math.sin(self.beam_angle)
        proj = dx * dir_x + dy * dir_y
        if proj < 0 or proj > self.beam_length:
            return False
        perp = abs(dx * dir_y - dy * dir_x)
        return perp <= self.beam_width + radius


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
                (185, 110, 255, alpha),
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
                (150, 80, 255, alpha),
                (surf.get_width() // 2, surf.get_height() // 2),
                int(self.radius * 1.1),
            )
            screen.blit(surf, (int(self.x - self.radius - 4), int(self.y - self.radius - 4)))


class Boss:
    def __init__(self, wave):
        self.x = WIDTH / 2
        self.y = HEIGHT * 0.18
        self.max_hp = 1200 + wave * 4500
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
        self.burn_source = "fire_orb_burn"
        self.fire_orb_hit_cd = 0.0
        self.neon_phase = random.uniform(0.0, math.tau)

    def phase(self):
        ratio = max(0.0, min(1.0, self.hp / self.max_hp))
        return int((1.0 - ratio) * 4)

    def update(self, dt, player_pos, projectiles, zones, wave, projectile_damage, zone_damage):
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
                    damage=projectile_damage,
                    color=(185, 110, 255),
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
                zones.append(BossZone(zx, zy, radius, zone_damage))
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

    @staticmethod
    def _draw_shape(surface, shape, center, radius, color, width, angle=0.0):
        radius = max(2, int(radius))
        width = max(0, int(width))
        if shape == "circle":
            pygame.draw.circle(surface, color, center, radius, width)
            return
        if shape == "square":
            points = Enemy._regular_polygon(center, radius, 4, angle)
            pygame.draw.polygon(surface, color, points, width)
            return
        if shape == "star7":
            points = Enemy._star_polygon(center, radius, radius * 0.45, 7, angle - math.pi / 2)
            pygame.draw.polygon(surface, color, points, width)
            return
        if shape == "arrow":
            points = Enemy._arrow_polygon(center, radius, angle)
            pygame.draw.polygon(surface, color, points, width)
            return
        pygame.draw.circle(surface, color, center, radius, width)

    @staticmethod
    def _draw_neon_tube(surface, shape, center, radius, color, thickness, angle=0.0, glow_scale=1.0):
        inner_dark = Enemy._mix_color(BG_COLOR, color, 0.11)
        highlight = Enemy._mix_color(color, (255, 255, 255), 0.5)
        Boss._draw_shape(surface, shape, center, radius - max(1, thickness // 2), (*inner_dark, 150), 0, angle)
        for spread, alpha in ((10, 22), (7, 40), (4, 62)):
            Boss._draw_shape(
                surface,
                shape,
                center,
                radius + spread * 0.65,
                (*color, int(alpha * glow_scale)),
                thickness + spread,
                angle,
            )
        Boss._draw_shape(surface, shape, center, radius, (*color, 235), thickness, angle)
        Boss._draw_shape(surface, shape, center, radius - 1, (*highlight, 188), max(1, thickness // 3), angle)

    def draw(self, screen):
        now = pygame.time.get_ticks() * 0.001
        phase = self.phase()
        pulse = 0.5 + 0.5 * math.sin(now * 2.2 + self.neon_phase)
        spin = now * (0.55 + phase * 0.08)
        violet_main = Enemy._mix_color((170, 90, 255), (205, 120, 255), pulse)
        violet_soft = Enemy._mix_color((120, 65, 220), (165, 95, 245), pulse)
        violet_hot = Enemy._mix_color((220, 175, 255), (250, 220, 255), 0.35 + pulse * 0.25)

        size = int(self.radius * 6.0)
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        center = (size // 2, size // 2)

        Boss._draw_neon_tube(
            surf,
            "square",
            center,
            self.radius + 18,
            violet_soft,
            thickness=6,
            angle=spin * 0.55 + math.pi / 4,
            glow_scale=1.0,
        )
        Boss._draw_neon_tube(
            surf,
            "circle",
            center,
            self.radius + 7,
            violet_main,
            thickness=6,
            angle=0.0,
            glow_scale=0.95,
        )
        Boss._draw_neon_tube(
            surf,
            "star7",
            center,
            self.radius - 2,
            violet_main,
            thickness=5,
            angle=-spin * 1.1,
            glow_scale=1.05,
        )
        Boss._draw_neon_tube(
            surf,
            "circle",
            center,
            self.radius * 0.52,
            violet_hot,
            thickness=4,
            angle=0.0,
            glow_scale=0.9,
        )

        shard_dist = self.radius + 26
        shard_r = self.radius * 0.34
        for i in range(4):
            ang = spin * 1.7 + i * (math.tau / 4)
            shard_center = (
                int(center[0] + math.cos(ang) * shard_dist),
                int(center[1] + math.sin(ang) * shard_dist),
            )
            Boss._draw_neon_tube(
                surf,
                "arrow",
                shard_center,
                shard_r,
                violet_soft,
                thickness=3,
                angle=ang,
                glow_scale=0.9,
            )

        pygame.draw.circle(surf, (255, 245, 255, 210), center, 5)
        rect = surf.get_rect(center=(int(self.x), int(self.y)))
        screen.blit(surf, rect.topleft)

        if self.burn_timer > 0:
            pygame.draw.circle(
                screen,
                (255, 120, 60),
                (int(self.x), int(self.y)),
                int(self.radius + 12),
                3,
            )
        if self.state == "laser":
            laser_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            for i in range(6):
                ang = self.laser_angle + i * (math.tau / 6)
                ex = self.x + math.cos(ang) * WIDTH
                ey = self.y + math.sin(ang) * WIDTH
                width = 8 + phase * 2.5
                beam_color = Enemy._mix_color(violet_main, violet_hot, 0.25 + (i % 2) * 0.35)
                beam_core = Enemy._mix_color(beam_color, (255, 255, 255), 0.55)
                pygame.draw.line(
                    laser_surf,
                    (*beam_color, 58),
                    (self.x, self.y),
                    (ex, ey),
                    int(width + 10),
                )
                pygame.draw.line(
                    laser_surf,
                    (*beam_color, 135),
                    (self.x, self.y),
                    (ex, ey),
                    int(width + 4),
                )
                pygame.draw.line(
                    laser_surf,
                    (*beam_core, 230),
                    (self.x, self.y),
                    (ex, ey),
                    int(max(2, width)),
                )
            screen.blit(laser_surf, (0, 0))


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
        self.even_spread_flip = False
        self.ricochet_level = 0
        self.focus_combo_level = 0
        self.focus_combo_timer = 0.0
        self.shield = 0.0
        self.shield_regen_level = 0
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
        self.laser_orb_damage = 10
        self.laser_orb_cooldown = 3.4
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
        self.ultimate_regen_time = 60.0
        self.ultimate_beam_time = 0.0
        self.ultimate_cooldown = 0.0
        self.ultimate_cooldown_max = 10.0
        self.vector_overdrive_time = 0.0
        self.shockwave_cooldown = 7.0
        self.shockwave_timer = 100.0
        self.shockwave_radius = 240
        self.shockwave_damage = 0.9
        self.shockwave_charging = False
        self.shockwave_charge_time = 0.0
        self.boss_kills = 0
        self.rocket_level = 0
        self.rocket_count = 0
        self.rocket_cooldown = 5.0
        self.rocket_timer = 0.0
        self.rocket_frag = False
        self.rocket_frag_level = 0
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

    def update(self, dt, keys, move_input=None):
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
        if move_input is not None:
            mvx, mvy = move_input
            vx += mvx
            vy += mvy

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
        self.vector_overdrive_time = max(0.0, self.vector_overdrive_time - dt)
        self.hurt_timer = max(0.0, self.hurt_timer - dt)
        self.shield_hit_timer = max(0.0, self.shield_hit_timer - dt)
        self.hurt_fx_timer = max(0.0, self.hurt_fx_timer - dt)
        if self.focus_combo_level > 0:
            self.focus_combo_timer += dt
        heal_mult = 5.0 if self.heal_boost > 0 else 1.0
        self.hp = min(self.max_hp, self.hp + self.max_hp * 0.01 * heal_mult * dt)
        if self.shield_regen_level > 0:
            shield_regen_rate = self.shield_regen_level * 0.5
            self.shield = min(6.0, self.shield + shield_regen_rate * dt)
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

    def projectile_bounces(self):
        if self.ricochet_level <= 0:
            return 0
        return min(4, 1 + (self.ricochet_level - 1) // 2)

    def reset_focus_combo(self):
        self.focus_combo_timer = 0.0

    def fire(self, target_pos, projectiles):
        if not self.can_fire():
            return
        overdrive_on = self.vector_overdrive_time > 0
        self.fire_timer = self.fire_rate * (0.35 if self.haste > 0 else 1.0)
        if overdrive_on:
            self.fire_timer *= 0.62
        angle = math.atan2(target_pos[1] - self.y, target_pos[0] - self.x)

        pickup_bonus = 1.8 if self.multishot > 0 else 0
        if overdrive_on:
            pickup_bonus += 2
        shots = int(clamp(self.bullets_per_shot + int(pickup_bonus * self.bullets_per_shot), 1, 10))
        max_spread = 0.35 + (shots / 80) * 0.95
        if shots == 1:
            offsets = [0.0]
        elif shots % 2 == 0:
            # Even shot count: force exactly one center bullet, then spread others around it.
            half = shots // 2
            if self.even_spread_flip:
                left_count = half
                right_count = half - 1
            else:
                left_count = half - 1
                right_count = half
            offsets = [0.0]
            if left_count > 0:
                for i in range(1, left_count + 1):
                    offsets.append(-max_spread * i / left_count)
            if right_count > 0:
                for i in range(1, right_count + 1):
                    offsets.append(max_spread * i / right_count)
            self.even_spread_flip = not self.even_spread_flip
        else:
            step = (2 * max_spread) / (shots - 1)
            offsets = [(-max_spread + i * step) for i in range(shots)]

        dmg_mult = 1.4 if self.haste > 0 else 1.0
        if overdrive_on:
            dmg_mult *= 1.55
        base_radius = 7 if self.haste > 0 else 4
        if overdrive_on:
            base_radius += 1
        projectile_speed = self.projectile_speed * (1.3 if overdrive_on else 1.0)
        projectile_color = (125, 240, 255) if overdrive_on else YELLOW

        for offset in offsets:
            proj_radius = base_radius
            damage = self.damage * dmg_mult
            ax = math.cos(angle + offset)
            ay = math.sin(angle + offset)
            projectiles.append(
                Projectile(
                    self.x,
                    self.y,
                    ax * projectile_speed,
                    ay * projectile_speed,
                    damage,
                    color=projectile_color,
                    radius=proj_radius,
                    owner="player",
                    ricochet_bounces=self.projectile_bounces(),
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
        if self.vector_overdrive_time > 0:
            ratio = clamp(self.vector_overdrive_time / 8.0, 0.0, 1.0)
            t = pygame.time.get_ticks() * 0.004
            aura_r = int(self.radius + 18 + math.sin(t * 1.6) * 5)
            aura = pygame.Surface((aura_r * 2 + 16, aura_r * 2 + 16), pygame.SRCALPHA)
            center = (aura.get_width() // 2, aura.get_height() // 2)
            pygame.draw.circle(aura, (95, 220, 255, int(55 * ratio + 20)), center, aura_r + 8, 6)
            pygame.draw.circle(aura, (170, 242, 255, int(95 * ratio + 30)), center, aura_r, 2)
            screen.blit(aura, (int(self.x - center[0]), int(self.y - center[1])))
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


class SpatialLaser:
    def __init__(self, start_pos, end_pos, width=60, damage=1.0, duration=0.18):
        self.sx, self.sy = start_pos
        self.ex, self.ey = end_pos
        self.width = width
        self.damage = damage
        self.time_left = duration
        self.duration = duration

    def update(self, dt):
        self.time_left -= dt

    def draw(self, screen):
        if self.time_left <= 0:
            return
        alpha = int(240 * (self.time_left / self.duration))
        surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pygame.draw.line(surf, (100, 200, 255, alpha), (self.sx, self.sy), (self.ex, self.ey), int(self.width * 1.2))
        pygame.draw.line(surf, (180, 230, 255, alpha), (self.sx, self.sy), (self.ex, self.ey), int(self.width * 0.8))
        pygame.draw.line(surf, (220, 245, 255, alpha), (self.sx, self.sy), (self.ex, self.ey), int(self.width * 0.4))
        screen.blit(surf, (0, 0))


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
        self.spin = random.uniform(0.0, math.tau)

    def update(self, dt):
        self.time_left -= dt
        self.tick_timer -= dt
        self.spin = (self.spin + dt * 2.4) % math.tau

    def should_tick(self):
        if self.tick_timer <= 0:
            self.tick_timer += self.tick_interval
            return True
        return False

    def draw(self, screen):
        if self.time_left <= 0:
            return
        ratio = clamp(self.time_left / max(0.001, self.duration), 0.0, 1.0)
        pulse = 0.97 + 0.03 * math.sin(pygame.time.get_ticks() * 0.006)
        r = int(self.radius * pulse)
        alpha_outer = int(60 + 35 * ratio)
        alpha_inner = int(130 + 80 * ratio)
        
        surf = pygame.Surface((r * 2 + 40, r * 2 + 40), pygame.SRCALPHA)
        center = (surf.get_width() // 2, surf.get_height() // 2)
        
        pygame.draw.circle(surf, (155, 110, 255, alpha_outer), center, r + 10, 7)
        pygame.draw.circle(surf, (215, 180, 255, alpha_inner), center, r, 2)
        
        for i in range(6):
            ang = self.spin * 1.5 + i * (math.tau / 6)
            px = center[0] + math.cos(ang) * (r - 10)
            py = center[1] + math.sin(ang) * (r - 10)
            pygame.draw.circle(surf, (238, 215, 255, 180), (int(px), int(py)), 3)
        
        screen.blit(surf, (int(self.x - center[0]), int(self.y - center[1])))


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


class UltimateConstellation:
    def __init__(
        self,
        node_count=4,
        duration=10.0,
        tick_interval=0.1,
        margin=120,
        preferred_points=None,
    ):
        self.node_count = max(4, int(node_count))
        self.duration = duration
        self.time_left = duration
        self.tick_interval = tick_interval
        self.tick_timer = 0.0
        self.margin = margin
        self.beam_width = 8.0
        self.node_move_speed = 72.0
        self.preferred_points = list(preferred_points) if preferred_points else []
        self.nodes = self._generate_nodes()
        self.edges = self._build_edges()

    def _generate_nodes(self):
        nodes = []
        min_dist = max(90, int(min(WIDTH, HEIGHT) * 0.20 - self.node_count * 5))
        min_dist = min(min_dist, 220)
        preferred = list(self.preferred_points)
        random.shuffle(preferred)
        preferred_min_dist = max(72, int(min_dist * 0.62))
        for px, py in preferred:
            if len(nodes) >= self.node_count:
                break
            x = clamp(px, self.margin, WIDTH - self.margin)
            y = clamp(py, self.margin, HEIGHT - self.margin)
            if not nodes:
                nodes.append((x, y))
                continue
            nearest = min(distance((x, y), n) for n in nodes)
            if nearest >= preferred_min_dist:
                nodes.append((x, y))

        while len(nodes) < self.node_count:
            best = None
            best_score = -1.0
            placed = False
            for _ in range(180):
                x = random.uniform(self.margin, WIDTH - self.margin)
                y = random.uniform(self.margin, HEIGHT - self.margin)
                if not nodes:
                    nodes.append((x, y))
                    placed = True
                    break
                nearest = min(distance((x, y), n) for n in nodes)
                if nearest >= min_dist:
                    nodes.append((x, y))
                    placed = True
                    break
                if nearest > best_score:
                    best_score = nearest
                    best = (x, y)
            if not placed:
                if best is not None:
                    nodes.append(best)
                else:
                    nodes.append(
                        (
                            random.uniform(self.margin, WIDTH - self.margin),
                            random.uniform(self.margin, HEIGHT - self.margin),
                        )
                    )
        cx = sum(x for x, _ in nodes) / len(nodes)
        cy = sum(y for _, y in nodes) / len(nodes)
        nodes.sort(key=lambda p: math.atan2(p[1] - cy, p[0] - cx))
        return nodes

    def _build_edges(self):
        n = len(self.nodes)
        edge_set = set()

        def add_edge(i, j):
            if i == j:
                return
            a, b = sorted((i, j))
            edge_set.add((a, b))

        for i in range(n):
            add_edge(i, (i + 1) % n)

        for i in range(0, n, 2):
            add_edge(i, (i + 2) % n)

        if n >= 7:
            for i in range(1, n, 3):
                add_edge(i, (i + 3) % n)

        return list(edge_set)

    def segments(self):
        for i, j in self.edges:
            yield self.nodes[i], self.nodes[j]

    def center(self):
        cx = sum(x for x, _ in self.nodes) / len(self.nodes)
        cy = sum(y for _, y in self.nodes) / len(self.nodes)
        return cx, cy

    def _extract_target_pos(self, target):
        if hasattr(target, "x") and hasattr(target, "y"):
            return float(target.x), float(target.y)
        if isinstance(target, (tuple, list)) and len(target) >= 2:
            return float(target[0]), float(target[1])
        return None

    def _assign_unique_targets(self, targets):
        if not targets or not self.nodes:
            return {}
        valid_targets = []
        for target in targets:
            pos = self._extract_target_pos(target)
            if pos is not None:
                valid_targets.append(pos)
        if not valid_targets:
            return {}

        pairs = []
        for node_idx, (nx, ny) in enumerate(self.nodes):
            for target_idx, (tx, ty) in enumerate(valid_targets):
                d2 = (tx - nx) * (tx - nx) + (ty - ny) * (ty - ny)
                pairs.append((d2, node_idx, target_idx))
        pairs.sort(key=lambda p: p[0])

        assigned_nodes = set()
        assigned_targets = set()
        assignment = {}
        limit = min(len(self.nodes), len(valid_targets))
        for _, node_idx, target_idx in pairs:
            if node_idx in assigned_nodes or target_idx in assigned_targets:
                continue
            assignment[node_idx] = valid_targets[target_idx]
            assigned_nodes.add(node_idx)
            assigned_targets.add(target_idx)
            if len(assignment) >= limit:
                break
        return assignment

    def _move_nodes_toward_targets(self, dt, targets):
        assignment = self._assign_unique_targets(targets)
        if not assignment:
            return
        max_step = self.node_move_speed * dt
        for node_idx, (tx, ty) in assignment.items():
            nx, ny = self.nodes[node_idx]
            dx = tx - nx
            dy = ty - ny
            dist = math.hypot(dx, dy)
            if dist <= 1e-5:
                continue
            step = min(max_step, dist)
            nx += (dx / dist) * step
            ny += (dy / dist) * step
            nx = clamp(nx, self.margin, WIDTH - self.margin)
            ny = clamp(ny, self.margin, HEIGHT - self.margin)
            self.nodes[node_idx] = (nx, ny)

    def update(self, dt, targets=None):
        self.time_left -= dt
        self.tick_timer -= dt
        if targets:
            self._move_nodes_toward_targets(dt, targets)

    def should_tick(self):
        if self.tick_timer <= 0:
            self.tick_timer += self.tick_interval
            return True
        return False

    def draw(self, screen):
        if self.time_left <= 0:
            return
        ratio = clamp(self.time_left / max(0.001, self.duration), 0.0, 1.0)
        t = pygame.time.get_ticks() * 0.001
        surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        glow_alpha = int(50 + 40 * ratio)
        beam_alpha = int(135 + 80 * ratio)
        core_alpha = int(190 + 65 * ratio)
        pulse = 0.88 + 0.12 * math.sin(t * 4.0)

        for (sx, sy), (ex, ey) in self.segments():
            pygame.draw.line(
                surf,
                (70, 200, 255, glow_alpha),
                (sx, sy),
                (ex, ey),
                int((self.beam_width + 8) * pulse),
            )
            pygame.draw.line(
                surf,
                (95, 225, 255, beam_alpha),
                (sx, sy),
                (ex, ey),
                int((self.beam_width + 2) * pulse),
            )
            pygame.draw.line(
                surf,
                (230, 248, 255, core_alpha),
                (sx, sy),
                (ex, ey),
                max(2, int(self.beam_width * 0.45)),
            )

        for idx, (x, y) in enumerate(self.nodes):
            twinkle = 0.5 + 0.5 * math.sin(t * 5.0 + idx * 0.9)
            beacon_phase = t * (2.0 + idx * 0.07)
            r = 6 + int(2 * twinkle)

            
            pygame.draw.circle(surf, (90, 220, 255, 75), (int(x), int(y)), r + 11)
            pygame.draw.circle(surf, (165, 236, 255, 52), (int(x), int(y)), r + 16, 3)

            outer = Enemy._regular_polygon((x, y), r + 9, 4, beacon_phase + math.pi / 4)
            inner = Enemy._regular_polygon((x, y), r + 4, 4, -beacon_phase * 1.2 + math.pi / 4)
            pygame.draw.polygon(surf, (110, 220, 255, 150), outer, 2)
            pygame.draw.polygon(surf, (215, 245, 255, 190), inner, 2)

            top = (int(x), int(y - (r + 6)))
            left = (int(x - max(4, r * 0.55)), int(y + max(3, r * 0.35)))
            right = (int(x + max(4, r * 0.55)), int(y + max(3, r * 0.35)))
            pygame.draw.polygon(surf, (14, 32, 55, 200), [top, right, left])
            pygame.draw.polygon(surf, (95, 195, 245, 185), [top, right, left], 2)

            pygame.draw.circle(surf, (180, 242, 255, 235), (int(x), int(y)), r)
            pygame.draw.circle(surf, (255, 255, 255, 235), (int(x), int(y)), max(2, r // 2))
            pygame.draw.line(
                surf,
                (205, 245, 255, 180),
                (int(x), int(y - r - 6)),
                (int(x), int(y + r + 4)),
                2,
            )

        screen.blit(surf, (0, 0))


class UltimatePrismaticBlade:
    def __init__(
        self,
        x,
        y,
        start_angle=0.0,
        duration=5.2,
        tick_interval=0.12,
        blade_count=3,
        reach=None,
        beam_width=30,
        sweep_speed=2.9,
    ):
        self.x = x
        self.y = y
        self.start_angle = start_angle
        self.duration = duration
        self.time_left = duration
        self.tick_interval = tick_interval
        self.tick_timer = 0.0
        self.blade_count = max(3, int(blade_count))
        self.reach = reach if reach is not None else math.hypot(WIDTH, HEIGHT) * 0.58
        self.beam_width = beam_width
        self.sweep_speed = sweep_speed
        self.inner_radius = max(108.0, min(180.0, self.reach * 0.14))
        self.total_sword_length = WIDTH * 0.5
        self.hilt_ratio = 0.22
        self.player_clearance = 120.0

    def update(self, dt, anchor_pos=None):
        self.time_left -= dt
        self.tick_timer -= dt
        if anchor_pos is not None:
            self.x, self.y = anchor_pos

    def should_tick(self):
        if self.tick_timer <= 0:
            self.tick_timer += self.tick_interval
            return True
        return False

    def segments(self):
        elapsed = self.duration - self.time_left
        hilt_len = self.total_sword_length * self.hilt_ratio
        blade_len = self.total_sword_length * (1.0 - self.hilt_ratio)
        for i in range(self.blade_count):
            base = self.start_angle + i * (math.tau / self.blade_count)
            jitter = math.sin(elapsed * 2.2 + i * 0.7) * 0.22
            ang = base + elapsed * self.sweep_speed + jitter
            inner = self.inner_radius + 6.0 * math.sin(elapsed * 2.6 + i * 0.9)
            inner = max(inner, hilt_len + self.player_clearance)
            sx = self.x + math.cos(ang) * inner
            sy = self.y + math.sin(ang) * inner
            ex = sx + math.cos(ang) * blade_len
            ey = sy + math.sin(ang) * blade_len
            yield (sx, sy), (ex, ey)

    def draw(self, screen):
        if self.time_left <= 0:
            return
        ratio = clamp(self.time_left / max(0.001, self.duration), 0.0, 1.0)
        surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

        for (sx, sy), (ex, ey) in self.segments():
            dx = ex - sx
            dy = ey - sy
            seg_len = math.hypot(dx, dy)
            if seg_len <= 1e-5:
                continue
            ux = dx / seg_len
            uy = dy / seg_len
            px = -uy
            py = ux

            sheath_off = self.beam_width * 0.72
            sheath_len = min(seg_len * 0.55, 420.0)
            sh_sx = sx + px * sheath_off
            sh_sy = sy + py * sheath_off
            sh_ex = sh_sx + ux * sheath_len
            sh_ey = sh_sy + uy * sheath_len
            pygame.draw.line(
                surf,
                (120, 55, 180, int(110 + 55 * ratio)),
                (int(sh_sx), int(sh_sy)),
                (int(sh_ex), int(sh_ey)),
                max(6, int(self.beam_width * 0.38)),
            )
            pygame.draw.line(
                surf,
                (220, 180, 255, int(120 + 75 * ratio)),
                (int(sh_sx), int(sh_sy)),
                (int(sh_ex), int(sh_ey)),
                2,
            )

            angle = math.atan2(uy, ux)
            draw_sword(surf, sx, sy, angle, self.total_sword_length, self.beam_width, ratio, self.hilt_ratio)

        screen.blit(surf, (0, 0))


class BladeSkillSlash:
    def __init__(self, x, y, angle, speed, max_distance, length, width, damage):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = speed
        self.max_distance = max_distance
        self.length = length
        self.width = width
        self.damage = damage
        self.traveled = 0.0
        self.time_left = 2.5
        self.hit_enemies = set()
        self.hit_boss = False
        self.hilt_ratio = 0.22

    def update(self, dt):
        vx = math.cos(self.angle) * self.speed
        vy = math.sin(self.angle) * self.speed
        self.x += vx * dt
        self.y += vy * dt
        self.traveled += self.speed * dt
        self.time_left -= dt

    def expired(self):
        return self.time_left <= 0 or self.traveled >= self.max_distance

    def segment(self):
        ux = math.cos(self.angle)
        uy = math.sin(self.angle)
        hilt_len = self.length * self.hilt_ratio
        blade_len = self.length * (1.0 - self.hilt_ratio)
        sx = self.x - ux * hilt_len
        sy = self.y - uy * hilt_len
        ex = self.x + ux * blade_len
        ey = self.y + uy * blade_len
        return sx, sy, ex, ey

    def hits_entity(self, tx, ty, radius):
        sx, sy, ex, ey = self.segment()
        dist = point_segment_distance(tx, ty, sx, sy, ex, ey)
        return dist <= radius + self.width * 0.48

    def draw(self, screen):
        ratio = clamp(self.time_left / 0.85, 0.0, 1.0)
        
        surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        
        ux = math.cos(self.angle)
        uy = math.sin(self.angle)
        hilt_len = self.length * self.hilt_ratio
        guard_x = self.x - ux * hilt_len
        guard_y = self.y - uy * hilt_len
        
        draw_sword(surf, guard_x, guard_y, self.angle, self.length, self.width, ratio, self.hilt_ratio)

        screen.blit(surf, (0, 0))


class UltimateVectorOverdrive:
    def __init__(self, x, y, duration=8.0, tick_interval=0.24, max_targets=5):
        self.x = x
        self.y = y
        self.duration = duration
        self.time_left = duration
        self.tick_interval = tick_interval
        self.tick_timer = 0.0
        self.max_targets = max_targets
        self.arcs = []

    def update(self, dt, anchor_pos=None):
        self.time_left -= dt
        self.tick_timer -= dt
        if anchor_pos is not None:
            self.x, self.y = anchor_pos
        for arc in list(self.arcs):
            arc["time_left"] -= dt
            if arc["time_left"] <= 0:
                self.arcs.remove(arc)

    def should_tick(self):
        if self.tick_timer <= 0:
            self.tick_timer += self.tick_interval
            return True
        return False

    def set_chain(self, points, duration=0.14):
        if len(points) < 2:
            return
        segments = []
        for i in range(len(points) - 1):
            segments.append((points[i], points[i + 1]))
        self.arcs.append({"segments": segments, "time_left": duration, "duration": duration})

    def draw(self, screen):
        if self.time_left <= 0:
            return
        ratio = clamp(self.time_left / max(0.001, self.duration), 0.0, 1.0)
        t = pygame.time.get_ticks() * 0.001
        pulse = 0.82 + 0.18 * math.sin(t * 8.0)
        ring_r = int(62 + 12 * pulse)
        aura = pygame.Surface((ring_r * 2 + 50, ring_r * 2 + 50), pygame.SRCALPHA)
        center = (aura.get_width() // 2, aura.get_height() // 2)
        pygame.draw.circle(aura, (90, 220, 255, int(40 + 25 * ratio)), center, ring_r + 12, 8)
        pygame.draw.circle(aura, (170, 244, 255, int(120 + 70 * ratio)), center, ring_r, 3)
        pygame.draw.circle(aura, (240, 252, 255, int(180 + 60 * ratio)), center, int(ring_r * 0.55), 2)
        screen.blit(aura, (int(self.x - center[0]), int(self.y - center[1])))

        for arc in self.arcs:
            arc_ratio = clamp(arc["time_left"] / max(0.001, arc["duration"]), 0.0, 1.0)
            surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            for a, b in arc["segments"]:
                pygame.draw.line(
                    surf,
                    (100, 220, 255, int(70 * arc_ratio)),
                    a,
                    b,
                    9,
                )
                pygame.draw.line(
                    surf,
                    (170, 244, 255, int(180 * arc_ratio + 30)),
                    a,
                    b,
                    4,
                )
                pygame.draw.line(
                    surf,
                    (255, 255, 255, int(220 * arc_ratio + 20)),
                    a,
                    b,
                    2,
                )
            screen.blit(surf, (0, 0))


class UltimateSpectralSwarm:
    def __init__(self, x, y, duration=8.0, spawn_interval=0.1):
        self.x = x
        self.y = y
        self.duration = duration
        self.time_left = duration
        self.spawn_interval = spawn_interval
        self.spawn_timer = 0.0
        self.spin = random.uniform(0.0, math.tau)

    def update(self, dt, anchor_pos=None):
        self.time_left -= dt
        self.spawn_timer -= dt
        self.spin = (self.spin + dt * 2.4) % math.tau
        if anchor_pos is not None:
            self.x, self.y = anchor_pos

    def consume_spawn_count(self):
        count = 0
        while self.spawn_timer <= 0 and self.time_left > 0:
            self.spawn_timer += self.spawn_interval
            count += 1
        return count

    def emit_point(self):
        ang = self.spin + random.uniform(-0.65, 0.65)
        r = random.uniform(28, 62)
        return self.x + math.cos(ang) * r, self.y + math.sin(ang) * r

    def draw(self, screen):
        if self.time_left <= 0:
            return
        ratio = clamp(self.time_left / max(0.001, self.duration), 0.0, 1.0)
        r = int(68 + 8 * math.sin(pygame.time.get_ticks() * 0.008))
        surf = pygame.Surface((r * 2 + 40, r * 2 + 40), pygame.SRCALPHA)
        center = (surf.get_width() // 2, surf.get_height() // 2)
        pygame.draw.circle(surf, (155, 110, 255, int(45 + 25 * ratio)), center, r + 10, 7)
        pygame.draw.circle(surf, (215, 180, 255, int(110 + 70 * ratio)), center, r, 2)
        for i in range(6):
            ang = self.spin * 1.5 + i * (math.tau / 6)
            px = center[0] + math.cos(ang) * (r - 10)
            py = center[1] + math.sin(ang) * (r - 10)
            pygame.draw.circle(surf, (238, 215, 255, 180), (int(px), int(py)), 3)
        screen.blit(surf, (int(self.x - center[0]), int(self.y - center[1])))


class UltimateSpectralShard:
    def __init__(self, x, y, angle, speed, damage, lifetime=3.4):
        self.x = x
        self.y = y
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.speed = speed
        self.turn_rate = 6.4
        self.damage = damage
        self.radius = 6
        self.time_left = lifetime
        self.target = None

    def _pick_target(self, targets):
        if not targets:
            self.target = None
            return
        self.target = min(targets, key=lambda e: (e.x - self.x) ** 2 + (e.y - self.y) ** 2)

    def update(self, dt, targets):
        self.time_left -= dt
        if self.target is None or self.target.hp <= 0 or self.target not in targets:
            self._pick_target(targets)
        if self.target is not None:
            dx = self.target.x - self.x
            dy = self.target.y - self.y
            dist = math.hypot(dx, dy) or 1.0
            desired_vx = (dx / dist) * self.speed
            desired_vy = (dy / dist) * self.speed
            mix = clamp(self.turn_rate * dt, 0.0, 1.0)
            self.vx = self.vx + (desired_vx - self.vx) * mix
            self.vy = self.vy + (desired_vy - self.vy) * mix
        self.x += self.vx * dt
        self.y += self.vy * dt

    def offscreen(self):
        return self.x < -50 or self.x > WIDTH + 50 or self.y < -50 or self.y > HEIGHT + 50

    def draw(self, screen):
        angle = math.atan2(self.vy, self.vx)
        tail_x = self.x - math.cos(angle) * 14
        tail_y = self.y - math.sin(angle) * 14
        min_x = int(min(tail_x, self.x) - 16)
        min_y = int(min(tail_y, self.y) - 16)
        max_x = int(max(tail_x, self.x) + 16)
        max_y = int(max(tail_y, self.y) + 16)
        w = max(8, max_x - min_x)
        h = max(8, max_y - min_y)
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        a = (tail_x - min_x, tail_y - min_y)
        b = (self.x - min_x, self.y - min_y)
        pygame.draw.line(surf, (190, 145, 255, 120), a, b, 6)
        pygame.draw.line(surf, (245, 228, 255, 220), a, b, 2)
        pygame.draw.circle(surf, (205, 165, 255, 190), (int(b[0]), int(b[1])), self.radius + 3)
        pygame.draw.circle(surf, (255, 245, 255, 240), (int(b[0]), int(b[1])), self.radius)
        screen.blit(surf, (min_x, min_y))


class UltimateQueenHive:
    def __init__(
        self,
        x,
        y,
        duration=9.0,
        tick_interval=0.16,
        max_targets=6,
        range_radius=430,
        jump_range=320,
    ):
        self.x = x
        self.y = y
        self.duration = duration
        self.time_left = duration
        self.tick_interval = tick_interval
        self.tick_timer = 0.0
        self.max_targets = max_targets
        self.range_radius = range_radius
        self.jump_range = jump_range
        self.links = []
        self.spin = random.uniform(0.0, math.tau)
        self.move_speed = 220.0
        self.target = None
        self.retarget_timer = 0.0
        self.hover_distance = 110.0
        self.facing_angle = random.uniform(0.0, math.tau)
        self.visual_radius = 34

    def update(self, dt, targets=None):
        if targets is None:
            targets = []
        old_x, old_y = self.x, self.y
        self.time_left -= dt
        self.tick_timer -= dt
        self.retarget_timer -= dt
        self.spin = (self.spin + dt * 1.35) % math.tau
        for link in list(self.links):
            link["time_left"] -= dt
            if link["time_left"] <= 0:
                self.links.remove(link)

        living_targets = [target for target in targets if target.hp > 0]
        if living_targets:
            if (
                self.target is None
                or self.target.hp <= 0
                or self.target not in living_targets
                or self.retarget_timer <= 0
            ):
                self.target = min(
                    living_targets,
                    key=lambda e: (e.x - self.x) ** 2 + (e.y - self.y) ** 2,
                )
                self.retarget_timer = 0.18

            dx = self.target.x - self.x
            dy = self.target.y - self.y
            dist = math.hypot(dx, dy) or 1.0

            if dist > self.hover_distance:
                step = min(dist - self.hover_distance, self.move_speed * dt)
                self.x += (dx / dist) * step
                self.y += (dy / dist) * step
            else:
                strafe_speed = self.move_speed * 0.3
                ang = math.atan2(dy, dx) + math.pi / 2
                self.x += math.cos(ang) * strafe_speed * dt
                self.y += math.sin(ang) * strafe_speed * dt
        else:
            self.target = None
            self.retarget_timer = 0.0

        self.x = clamp(self.x, 40, WIDTH - 40)
        self.y = clamp(self.y, 40, HEIGHT - 40)

        move_dx = self.x - old_x
        move_dy = self.y - old_y
        move_dist = math.hypot(move_dx, move_dy)
        if move_dist > 1e-4:
            desired = math.atan2(move_dy, move_dx)
            delta = (desired - self.facing_angle + math.pi) % math.tau - math.pi
            turn = clamp(dt * 8.0, 0.0, 1.0)
            self.facing_angle = (self.facing_angle + delta * turn) % math.tau

    def should_tick(self):
        if self.tick_timer <= 0:
            self.tick_timer += self.tick_interval
            return True
        return False

    def set_chain(self, points, duration=0.14):
        if len(points) < 2:
            return
        segments = []
        for i in range(len(points) - 1):
            segments.append((points[i], points[i + 1]))
        self.links.append({"segments": segments, "time_left": duration, "duration": duration})

    def draw(self, screen):
        if self.time_left <= 0:
            return
        ratio = clamp(self.time_left / max(0.001, self.duration), 0.0, 1.0)
        beast_r = self.visual_radius
        surf = pygame.Surface((beast_r * 2 + 80, beast_r * 2 + 80), pygame.SRCALPHA)
        center = (surf.get_width() // 2, surf.get_height() // 2)
        cx, cy = center

        facing = self.facing_angle
        fx, fy = math.cos(facing), math.sin(facing)
        px, py = -fy, fx

        for spread, alpha, width in ((18, 26, 10), (12, 44, 7), (6, 70, 4)):
            rr = beast_r + spread
            pygame.draw.circle(
                surf,
                (128, 205, 255, int(alpha + ratio * 18)),
                center,
                rr,
                width,
            )

        nose = (cx + fx * beast_r * 1.35, cy + fy * beast_r * 1.35)
        shoulder_l = (cx + fx * beast_r * 0.28 + px * beast_r * 0.98, cy + fy * beast_r * 0.28 + py * beast_r * 0.98)
        shoulder_r = (cx + fx * beast_r * 0.28 - px * beast_r * 0.98, cy + fy * beast_r * 0.28 - py * beast_r * 0.98)
        hip_l = (cx - fx * beast_r * 0.48 + px * beast_r * 0.72, cy - fy * beast_r * 0.48 + py * beast_r * 0.72)
        hip_r = (cx - fx * beast_r * 0.48 - px * beast_r * 0.72, cy - fy * beast_r * 0.48 - py * beast_r * 0.72)
        tail = (cx - fx * beast_r * 1.2, cy - fy * beast_r * 1.2)

        body_pts = [
            (int(nose[0]), int(nose[1])),
            (int(shoulder_l[0]), int(shoulder_l[1])),
            (int(hip_l[0]), int(hip_l[1])),
            (int(tail[0]), int(tail[1])),
            (int(hip_r[0]), int(hip_r[1])),
            (int(shoulder_r[0]), int(shoulder_r[1])),
        ]
        pygame.draw.polygon(surf, (92, 200, 255, int(150 + 70 * ratio)), body_pts)
        pygame.draw.polygon(surf, (220, 246, 255, int(190 + 55 * ratio)), body_pts, 2)

        wing_len = beast_r * 1.05
        wing_left_tip = (
            shoulder_l[0] + px * wing_len + fx * beast_r * 0.22,
            shoulder_l[1] + py * wing_len + fy * beast_r * 0.22,
        )
        wing_right_tip = (
            shoulder_r[0] - px * wing_len + fx * beast_r * 0.22,
            shoulder_r[1] - py * wing_len + fy * beast_r * 0.22,
        )
        left_wing = [
            (int(shoulder_l[0]), int(shoulder_l[1])),
            (int(wing_left_tip[0]), int(wing_left_tip[1])),
            (int(hip_l[0]), int(hip_l[1])),
        ]
        right_wing = [
            (int(shoulder_r[0]), int(shoulder_r[1])),
            (int(wing_right_tip[0]), int(wing_right_tip[1])),
            (int(hip_r[0]), int(hip_r[1])),
        ]
        pygame.draw.polygon(surf, (120, 220, 255, int(140 + 70 * ratio)), left_wing)
        pygame.draw.polygon(surf, (120, 220, 255, int(140 + 70 * ratio)), right_wing)
        pygame.draw.polygon(surf, (235, 250, 255, int(190 + 45 * ratio)), left_wing, 2)
        pygame.draw.polygon(surf, (235, 250, 255, int(190 + 45 * ratio)), right_wing, 2)

        eye_x = cx + fx * beast_r * 0.28
        eye_y = cy + fy * beast_r * 0.28
        eye_r = max(4, int(beast_r * 0.18))
        pygame.draw.circle(surf, (18, 35, 56, 210), (int(eye_x), int(eye_y)), eye_r + 4)
        pygame.draw.circle(surf, (110, 228, 255, int(175 + 50 * ratio)), (int(eye_x), int(eye_y)), eye_r + 1)
        pygame.draw.circle(surf, (255, 255, 255, 235), (int(eye_x), int(eye_y)), max(2, eye_r // 2))

        pygame.draw.line(
            surf,
            (180, 236, 255, int(140 + 60 * ratio)),
            (int(nose[0]), int(nose[1])),
            (int(tail[0]), int(tail[1])),
            2,
        )

        screen.blit(surf, (int(self.x - center[0]), int(self.y - center[1])))

        for link in self.links:
            link_ratio = clamp(link["time_left"] / max(0.001, link["duration"]), 0.0, 1.0)
            beam = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            for a, b in link["segments"]:
                pygame.draw.line(beam, (105, 210, 255, int(66 * link_ratio)), a, b, 10)
                pygame.draw.line(beam, (180, 242, 255, int(180 * link_ratio + 25)), a, b, 4)
                pygame.draw.line(beam, (255, 255, 255, int(225 * link_ratio + 15)), a, b, 2)
            screen.blit(beam, (0, 0))


class BeeHive:
    def __init__(self, x, y, duration=15.0, spawn_interval=1.0, source="bee_swarm"):
        self.x = x
        self.y = y
        self.duration = duration
        self.time_left = duration
        self.spawn_interval = spawn_interval
        self.spawn_timer = 0.0
        self.source = source
        self.spin = random.uniform(0.0, math.tau)

    def update(self, dt):
        self.time_left -= dt
        self.spawn_timer -= dt
        self.spin = (self.spin + dt * 1.2) % math.tau

    def consume_spawn_count(self):
        count = 0
        while self.spawn_timer <= 0 and self.time_left > 0:
            self.spawn_timer += self.spawn_interval
            count += 1
        return count

    def draw(self, screen):
        if self.time_left <= 0:
            return
        ratio = clamp(self.time_left / max(0.001, self.duration), 0.0, 1.0)
        r = 34
        surf = pygame.Surface((r * 2 + 70, r * 2 + 70), pygame.SRCALPHA)
        center = (surf.get_width() // 2, surf.get_height() // 2)
        cx, cy = center

        pygame.draw.circle(surf, (255, 210, 70, int(40 + 26 * ratio)), center, r + 14, 8)
        pygame.draw.circle(surf, (255, 235, 155, int(95 + 48 * ratio)), center, r + 2, 3)
        pygame.draw.circle(surf, (36, 30, 18, 220), center, r - 8)
        pygame.draw.circle(surf, (255, 220, 95, 210), center, r - 3, 2)

        nodes = 6
        for i in range(nodes):
            ang = self.spin + i * (math.tau / nodes)
            px = cx + math.cos(ang) * 19
            py = cy + math.sin(ang) * 19
            pygame.draw.circle(surf, (240, 170, 45, 200), (int(px), int(py)), 7)
            pygame.draw.circle(surf, (255, 232, 165, 225), (int(px), int(py)), 7, 1)

        entrance = pygame.Rect(cx - 8, cy + 5, 16, 10)
        pygame.draw.ellipse(surf, (18, 16, 14, 235), entrance)
        screen.blit(surf, (int(self.x - center[0]), int(self.y - center[1])))


class BeeMinion:
    def __init__(self, x, y, speed, damage, lifetime=7.0, source="bee_swarm", target=None):
        self.x = x
        self.y = y
        self.speed = speed
        self.damage = damage
        self.source = source
        self.radius = 6
        self.time_left = lifetime
        self.turn_rate = 8.8
        ang = random.uniform(0.0, math.tau)
        self.vx = math.cos(ang) * speed
        self.vy = math.sin(ang) * speed
        self.target = target
        self.wing_phase = random.uniform(0.0, math.tau)

    def _pick_target(self, targets):
        if not targets:
            self.target = None
            return
        self.target = min(targets, key=lambda e: (e.x - self.x) ** 2 + (e.y - self.y) ** 2)

    def update(self, dt, targets):
        self.time_left -= dt
        self.wing_phase = (self.wing_phase + dt * 26.0) % math.tau
        if self.target is None or self.target.hp <= 0 or self.target not in targets:
            self._pick_target(targets)
        if self.target is not None:
            dx = self.target.x - self.x
            dy = self.target.y - self.y
            dist = math.hypot(dx, dy) or 1.0
            desired_vx = (dx / dist) * self.speed
            desired_vy = (dy / dist) * self.speed
            mix = clamp(self.turn_rate * dt, 0.0, 1.0)
            self.vx += (desired_vx - self.vx) * mix
            self.vy += (desired_vy - self.vy) * mix
        self.x += self.vx * dt
        self.y += self.vy * dt

    def offscreen(self):
        return self.x < -80 or self.x > WIDTH + 80 or self.y < -80 or self.y > HEIGHT + 80

    def draw(self, screen):
        ang = math.atan2(self.vy, self.vx)
        fx, fy = math.cos(ang), math.sin(ang)
        px, py = -fy, fx

        body_len = 12
        body_w = 6
        nose = (self.x + fx * body_len * 0.55, self.y + fy * body_len * 0.55)
        tail = (self.x - fx * body_len * 0.7, self.y - fy * body_len * 0.7)
        body_pts = [
            (int(nose[0] + px * body_w), int(nose[1] + py * body_w)),
            (int(tail[0] + px * body_w * 0.8), int(tail[1] + py * body_w * 0.8)),
            (int(tail[0] - px * body_w * 0.8), int(tail[1] - py * body_w * 0.8)),
            (int(nose[0] - px * body_w), int(nose[1] - py * body_w)),
        ]
        pygame.draw.polygon(screen, (245, 190, 42), body_pts)
        pygame.draw.polygon(screen, (255, 235, 160), body_pts, 1)

        for stripe_t in (0.15, 0.42):
            sx = self.x + fx * (body_len * (0.35 - stripe_t))
            sy = self.y + fy * (body_len * (0.35 - stripe_t))
            pygame.draw.line(
                screen,
                (28, 24, 18),
                (int(sx + px * body_w * 0.9), int(sy + py * body_w * 0.9)),
                (int(sx - px * body_w * 0.9), int(sy - py * body_w * 0.9)),
                2,
            )

        wing_spread = 5.0 + 2.6 * abs(math.sin(self.wing_phase))
        wing_l = [
            (int(self.x - fx * 1 + px * 2), int(self.y - fy * 1 + py * 2)),
            (int(self.x - fx * 5 + px * (2 + wing_spread)), int(self.y - fy * 5 + py * (2 + wing_spread))),
            (int(self.x + fx * 1 + px * 2), int(self.y + fy * 1 + py * 2)),
        ]
        wing_r = [
            (int(self.x - fx * 1 - px * 2), int(self.y - fy * 1 - py * 2)),
            (int(self.x - fx * 5 - px * (2 + wing_spread)), int(self.y - fy * 5 - py * (2 + wing_spread))),
            (int(self.x + fx * 1 - px * 2), int(self.y + fy * 1 - py * 2)),
        ]
        pygame.draw.polygon(screen, (220, 246, 255, 120), wing_l)
        pygame.draw.polygon(screen, (220, 246, 255, 120), wing_r)
        pygame.draw.polygon(screen, (255, 255, 255, 175), wing_l, 1)
        pygame.draw.polygon(screen, (255, 255, 255, 175), wing_r, 1)


class UltimateSingularity:
    def __init__(
        self,
        x,
        y,
        radius=300,
        duration=6.0,
        tick_interval=0.18,
        pull_strength=520.0,
        orbit_radius=190.0,
        orbit_speed=1.9,
        start_angle=0.0,
    ):
        self.x = x
        self.y = y
        self.radius = radius
        self.duration = duration
        self.time_left = duration
        self.tick_interval = tick_interval
        self.tick_timer = 0.0
        self.pull_strength = pull_strength
        self.core_radius = max(14, int(radius * 0.12))
        self.explosion_radius = int(radius * 1.05)
        self.orbit_radius = orbit_radius
        self.orbit_speed = orbit_speed
        self.orbit_angle = start_angle
        self.exiting = False
        self.finished = False
        self.exit_vx = 0.0
        self.exit_vy = 0.0
        self.exit_speed = 620.0
        self.anchor_x = x
        self.anchor_y = y

    def update(self, dt, anchor_pos=None):
        if self.finished:
            return

        if not self.exiting:
            self.time_left -= dt
            self.tick_timer -= dt
            if anchor_pos is not None:
                self.orbit_angle = (self.orbit_angle + self.orbit_speed * dt) % math.tau
                ax, ay = anchor_pos
                self.anchor_x, self.anchor_y = ax, ay
                self.x = ax + math.cos(self.orbit_angle) * self.orbit_radius
                self.y = ay + math.sin(self.orbit_angle) * self.orbit_radius
                self.x = clamp(self.x, 30, WIDTH - 30)
                self.y = clamp(self.y, 30, HEIGHT - 30)

            if self.time_left <= 0:
                self.time_left = 0.0
                self.exiting = True
                tan_x = -math.sin(self.orbit_angle)
                tan_y = math.cos(self.orbit_angle)
                dx = self.x - self.anchor_x
                dy = self.y - self.anchor_y
                dist = math.hypot(dx, dy) or 1.0
                out_x = dx / dist
                out_y = dy / dist
                dir_x = tan_x * 0.82 + out_x * 0.36
                dir_y = tan_y * 0.82 + out_y * 0.36
                norm = math.hypot(dir_x, dir_y) or 1.0
                dir_x /= norm
                dir_y /= norm
                self.exit_vx = dir_x * self.exit_speed
                self.exit_vy = dir_y * self.exit_speed
        else:
            self.x += self.exit_vx * dt
            self.y += self.exit_vy * dt
            boost = 1.0 + dt * 0.9
            self.exit_vx *= boost
            self.exit_vy *= boost
            margin = 280
            if (
                self.x < -margin
                or self.x > WIDTH + margin
                or self.y < -margin
                or self.y > HEIGHT + margin
            ):
                self.finished = True

    def should_tick(self):
        if self.exiting or self.finished:
            return False
        if self.tick_timer <= 0:
            self.tick_timer += self.tick_interval
            return True
        return False

    def pull_entity(self, entity, dt, weight=1.0):
        if self.exiting or self.finished:
            return
        dx = self.x - entity.x
        dy = self.y - entity.y
        dist = math.hypot(dx, dy)
        if dist <= 1e-5 or dist > self.radius:
            return
        t = 1.0 - dist / self.radius
        force = self.pull_strength * (0.35 + t * 1.0) * weight
        entity.x += (dx / dist) * force * dt
        entity.y += (dy / dist) * force * dt

    def draw(self, screen):
        if self.finished:
            return
        now = pygame.time.get_ticks() * 0.001
        visual_scale = 1.34
        growth_t = 1.0 if self.exiting else clamp(1.0 - (self.time_left / self.duration), 0.0, 1.0)
        growth_ease = growth_t * growth_t * (3.0 - 2.0 * growth_t)
        growth_mult = (1.0 / 3.0) + (1.3 - (1.0 / 3.0)) * growth_ease

        disk_rx = int(
            self.radius
            * visual_scale
            * growth_mult
            * (0.62 + 0.07 * math.sin(now * 0.9 + growth_t * 2.3))
        )
        disk_ry = max(26, int(disk_rx * (0.33 + 0.05 * math.sin(now * 1.4 + 0.8))))
        core_r = int(
            self.core_radius
            * 1.38
            * growth_mult
            * (1.0 + 0.08 * math.sin(now * 4.2))
        )
        size = int(max(self.radius * 2 + 180, disk_rx * 2 + 280))
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        center = (size // 2, size // 2)
        cx, cy = center

        disk_cy = cy + int(self.radius * 0.02 * growth_mult)

        for spread, alpha in ((44, 20), (32, 30), (22, 42), (12, 56), (4, 74)):
            rx = disk_rx + spread
            ry = disk_ry + int(spread * 0.36)
            rect = pygame.Rect(cx - rx, disk_cy - ry, rx * 2, ry * 2)
            color = (
                95 + spread * 2,
                65 + spread,
                165 + min(80, spread * 3),
                int(alpha + 10),
            )
            pygame.draw.ellipse(surf, color, rect, max(2, 10 - spread // 4))

        filament_count = 30
        for i in range(filament_count):
            frac = i / max(1, filament_count - 1)
            rx = int(disk_rx * (0.52 + 0.45 * frac))
            ry = max(5, int(disk_ry * (0.62 + 0.38 * frac)))
            rect = pygame.Rect(cx - rx, disk_cy - ry, rx * 2, ry * 2)
            start = now * (1.7 + 0.35 * frac) + i * 0.44
            sweep = 0.85 + 0.55 * (0.5 + 0.5 * math.sin(now * 1.9 + i * 0.8))
            color_a = (
                int(170 + 60 * (1.0 - frac)),
                int(85 + 55 * frac),
                int(240 - 28 * frac),
                int((120 - 44 * frac) + 24),
            )
            color_b = (
                int(215 + 28 * (1.0 - frac)),
                int(155 + 28 * frac),
                255,
                int((78 - 34 * frac) + 14),
            )
            width = max(1, int(4 - frac * 2.0))
            pygame.draw.arc(surf, color_a, rect, start, start + sweep, width + 1)
            pygame.draw.arc(surf, color_b, rect, start + math.pi, start + math.pi + sweep * 0.75, width)

        photon_rx = max(core_r + 11, int(disk_rx * 0.34))
        photon_ry = max(7, int(photon_rx * 0.40))
        for spread, alpha, width in ((7, 56, 6), (3, 105, 4), (0, 190, 2)):
            rect = pygame.Rect(
                cx - (photon_rx + spread),
                disk_cy - (photon_ry + spread // 2),
                (photon_rx + spread) * 2,
                (photon_ry + spread // 2) * 2,
            )
            pygame.draw.ellipse(
                surf,
                (245, 195, 255, int(alpha + 12)),
                rect,
                width,
            )

        pygame.draw.circle(surf, (14, 8, 22, 245), (cx, cy), core_r + 4)
        pygame.draw.circle(surf, (0, 0, 0, 255), (cx, cy), core_r)
        pygame.draw.circle(surf, (175, 120, 235, 171), (cx, cy), core_r + 2, 1)

        lens_rx = photon_rx + 18
        lens_ry = photon_ry + 10
        lens_rect = pygame.Rect(cx - lens_rx, disk_cy - lens_ry, lens_rx * 2, lens_ry * 2)
        pygame.draw.arc(
            surf,
            (255, 240, 255, 205),
            lens_rect,
            math.pi * 1.08,
            math.pi * 1.92,
            3,
        )

        screen.blit(surf, (int(self.x - center[0]), int(self.y - center[1])))


class Shockwave:
    def __init__(self, x, y, radius, duration=0.42):
        self.x = x
        self.y = y
        self.radius = radius
        self.duration = duration
        self.time_left = duration
        self.spin = random.uniform(0.0, math.tau)

    def update(self, dt):
        self.time_left -= dt

    def draw(self, screen):
        if self.time_left <= 0:
            return
        progress = clamp(1.0 - (self.time_left / max(0.001, self.duration)), 0.0, 1.0)
        eased = 1.0 - (1.0 - progress) ** 2
        fade = 1.0 - progress
        ring_r = max(2, int(self.radius * eased))
        size = ring_r * 2 + 120
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        center = (size // 2, size // 2)

        for extra, alpha, width in ((34, 38, 11), (22, 70, 8), (10, 110, 5)):
            rr = ring_r + extra
            pygame.draw.circle(
                surf,
                (80, 210, 255, int(alpha * fade + 10)),
                center,
                rr,
                width,
            )

        ring_width = max(3, int(10 - progress * 6))
        pygame.draw.circle(
            surf,
            (145, 232, 255, int(225 * fade + 20)),
            center,
            ring_r,
            ring_width,
        )
        pygame.draw.circle(
            surf,
            (255, 255, 255, int(235 * fade + 20)),
            center,
            max(2, ring_r - 3),
            2,
        )

        inner_r = max(8, int(self.radius * (0.08 + 0.2 * (1.0 - progress))))
        pygame.draw.circle(surf, (36, 80, 120, int(95 * fade + 16)), center, inner_r)
        pygame.draw.circle(
            surf,
            (210, 246, 255, int(198 * fade + 18)),
            center,
            max(2, inner_r // 2),
        )

        spoke_count = 14
        spoke_start = max(6, int(ring_r * 0.18))
        for i in range(spoke_count):
            ang = self.spin + progress * 7.0 + i * (math.tau / spoke_count)
            sx = center[0] + math.cos(ang) * spoke_start
            sy = center[1] + math.sin(ang) * spoke_start
            end_r = max(
                spoke_start + 8,
                int(ring_r * (0.7 + 0.18 * math.sin(progress * 11.0 + i * 0.9))),
            )
            ex = center[0] + math.cos(ang) * end_r
            ey = center[1] + math.sin(ang) * end_r
            pygame.draw.line(
                surf,
                (120, 230, 255, int(90 * fade + 20)),
                (int(sx), int(sy)),
                (int(ex), int(ey)),
                2,
            )

        if progress < 0.45:
            flare_ratio = (0.45 - progress) / 0.45
            flare_r = max(ring_r + 18, int(self.radius * (0.25 + 0.55 * progress)))
            pygame.draw.circle(
                surf,
                (95, 220, 255, int(40 * flare_ratio + 10)),
                center,
                flare_r,
            )

        screen.blit(surf, (int(self.x - center[0]), int(self.y - center[1])))


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
        self.orbit_phase = random.uniform(0.0, math.tau)
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
        retreating = False
        if self.target is None or self.target not in targets or self.target.hp <= 0:
            if targets:
                self.target = min(
                    targets,
                    key=lambda e: (e.x - self.x) ** 2 + (e.y - self.y) ** 2,
                )
            else:
                self.target = None

        if self.target is not None:
            target_dx = self.x - self.target.x
            target_dy = self.y - self.target.y
            target_dist = math.hypot(target_dx, target_dy)
            keep_dist = max(120.0, self.target.radius + self.radius + 34.0)
            orbit_angle = pygame.time.get_ticks() * 0.0018 + self.orbit_phase
            desired_x = self.target.x + math.cos(orbit_angle) * keep_dist
            desired_y = self.target.y + math.sin(orbit_angle) * keep_dist
            if target_dist < keep_dist * 0.78:
                retreating = True
                if target_dist <= 0.1:
                    away_x, away_y = vec_from_angle(self.orbit_phase)
                else:
                    away_x = target_dx / target_dist
                    away_y = target_dy / target_dist
                desired_x = self.target.x + away_x * keep_dist
                desired_y = self.target.y + away_y * keep_dist
            margin = self.radius + 20
            self.target_x = clamp(desired_x, margin, WIDTH - margin)
            self.target_y = clamp(desired_y, margin, HEIGHT - margin)
        else:
            if math.hypot(self.target_x - self.x, self.target_y - self.y) < 12:
                self._pick_new_target()

        dx = self.target_x - self.x
        dy = self.target_y - self.y
        dist = math.hypot(dx, dy)
        if dist <= 0.1:
            return
        move_speed = self.speed * (1.35 if retreating else 1.0)
        vx = dx / dist * move_speed
        vy = dy / dist * move_speed
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


@dataclass(frozen=True)
class ClassChoice:
    key: str
    label: str
    ultimate_key: str
    ultimate_label: str
    desc: str


UPGRADE_POOL = [
    UpgradeChoice("speed", "Vitesse", "Bonus de vitesse"),
    UpgradeChoice("proj_speed", "Proj Speed", "Projectiles plus rapide"),
    UpgradeChoice("damage", "Degats", "Degats augmentes"),
    UpgradeChoice("max_hp", "PV Max", "Augmente la vie max"),
    UpgradeChoice("fire_rate", "Cadence", "Augmente la cadence de tir"),
    UpgradeChoice("bullets", "Multi-tir", "Plus de projectiles par tir"),
    UpgradeChoice("ricochet", "Ricochet", "Les tirs rebondissent sur d'autres cibles"),
    UpgradeChoice("focus_combo", "Combo concentration", "Sans degats recus, tes degats montent"),
    UpgradeChoice("fire_orb", "Orbe de feu", "Ajoute une boule de feu qui orbite"),
    UpgradeChoice("shield_regen", "Bouclier", "Regenere automatiquement le bouclier"),
    UpgradeChoice("rockets", "Lance roquette", "Lance des roquettes"),
]

EPIC_UPGRADES = [
    UpgradeChoice("laser_orb", "Orbe laser", "Une orbe tire des lasers"),
    UpgradeChoice("electroelf", "Electroelf", "Familier qui lance des eclairs"),
    UpgradeChoice("fire_ring","EVO: Cercle de feu+","Debloque le cercle de feu",
    ),
    UpgradeChoice("rocket_frag", "EVO: Rockets fragmentation+", "Les roquettes explosent en eclats"),
]

DAMAGE_SOURCE_ORDER = [
    "base_shot",
    "fire_orb_impact",
    "fire_orb_burn",
    "fire_ring_burn",
    "laser_orb",
    "electroelf",
    "rockets",
    "rocket_fragments",
    "blade_skill",
    "shockwave",
    "bee_swarm",
    "bio_minions",
    "ultimate_constellation",
    "ultimate_prismatic_blade",
    "ultimate_vector_overdrive",
    "ultimate_spectral_swarm",
    "ultimate_queen_hive",
    "ultimate_singularity",
    "ultimate_zone",
    "other",
]

DAMAGE_SOURCE_META = {
    "base_shot": {"label": "Tir principal", "upgrade_key": "damage"},
    "fire_orb_impact": {"label": "Orbe de feu (impact)", "upgrade_key": "fire_orb"},
    "fire_orb_burn": {"label": "Orbe de feu (brulure)", "upgrade_key": "fire_orb"},
    "fire_ring_burn": {"label": "Cercle de feu (brulure)", "upgrade_key": "fire_ring"},
    "laser_orb": {"label": "Orbe laser", "upgrade_key": "laser_orb"},
    "electroelf": {"label": "Electroelf", "upgrade_key": "electroelf"},
    "rockets": {"label": "Lance roquette", "upgrade_key": "rockets"},
    "rocket_fragments": {"label": "Fragments roquette", "upgrade_key": "rocket_frag"},
    "blade_skill": {"label": "Lame geante", "upgrade_key": None},
    "shockwave": {"label": "Onde de choc", "upgrade_key": None},
    "bee_swarm": {"label": "Essaim d'abeilles", "upgrade_key": None},
    "bio_minions": {"label": "Invocations chimiques", "upgrade_key": None},
    "ultimate_constellation": {"label": "Ulti: Constellation Laser", "upgrade_key": None},
    "ultimate_prismatic_blade": {"label": "Ulti: Lame Prismatique", "upgrade_key": None},
    "ultimate_vector_overdrive": {"label": "Ulti: Transmutation Hostile", "upgrade_key": None},
    "ultimate_spectral_swarm": {"label": "Ulti: Essaim Spectral", "upgrade_key": None},
    "ultimate_queen_hive": {"label": "Ulti: Ruche Royale", "upgrade_key": None},
    "ultimate_singularity": {"label": "Ulti: Singularite ", "upgrade_key": None},
    "ultimate_zone": {"label": "Zone ultime", "upgrade_key": None},
    "other": {"label": "Autres sources", "upgrade_key": None},
}

PLAYER_DAMAGE_SOURCE_ORDER = [
    "enemy_projectile",
    "enemy_contact",
    "tank_beam",
    "boss_contact",
    "boss_laser",
    "boss_zone",
    "other",
]

PLAYER_DAMAGE_SOURCE_META = {
    "enemy_projectile": {"label": "Projectile ennemi"},
    "enemy_contact": {"label": "Contact ennemi"},
    "tank_beam": {"label": "Laser tank"},
    "boss_contact": {"label": "Contact boss"},
    "boss_laser": {"label": "Laser boss"},
    "boss_zone": {"label": "Zone boss"},
    "other": {"label": "Autres sources"},
}

TEMP_PICKUP_POOL = ["shield", "haste", "multishot", "heal"]

CLASS_POOL = [
    ClassChoice(
        "laser_master",
        "Maitre des Lasers",
        "constellation_laser",
        "Constellation Laser",
        "Balises reliees par des lasers.",
    ),
    ClassChoice(
        "blade_master",
        "Maitre de la lame",
        "prismatic_blade",
        "Lame Prismatique",
        "Trois slashes traversent le terrain.",
    ),
    ClassChoice(
        "mad_biochemist",
        "Biochimiste fou",
        "vector_overdrive",
        "Transmutation Hostile",
        "Retourne les ennemis proches contre leurs allies.",
    ),
    ClassChoice(
        "shard_master",
        "Maitre des eclats",
        "spectral_swarm",
        "Essaim Spectral",
        "Nuage d'eclats qui traquent les cibles.",
    ),
    ClassChoice(
        "bee_master",
        "Maitre des abeilles",
        "queen_hive",
        "Ruche Royale",
        "E libere un essaim, l'ulti pose une ruche durable.",
    ),
    ClassChoice(
        "spatial_master",
        "Maitre spatial",
        "singularity",
        "Singularite",
        "Trou noir qui attire puis explose.",
    ),
]

#############################
# --- Boucle principale --- #
#############################
class Game:
    def __init__(self):
        global WIDTH, HEIGHT
        pygame.init()
        pygame.display.set_caption("Tank Survivor")
        self.screen = pygame.display.set_mode((0, 0), pygame.NOFRAME)
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
        self.blade_skill_slashes = []
        self.explosions = []
        self.lightning_effects = []
        self.ultimate_beams = []
        self.spatial_lasers = []
        self.ultimate_pulses = []
        self.ultimate_zones = []
        self.ultimate_constellations = []
        self.ultimate_singularities = []
        self.ultimate_prismatic_blades = []
        self.ultimate_vector_overdrives = []
        self.ultimate_spectral_swarms = []
        self.ultimate_spectral_shards = []
        self.ultimate_queen_hives = []
        self.bee_hives = []
        self.bee_minions = []
        self.shockwaves = []
        self.boss = None
        self.boss_zones = []
        self.pickups = []
        self.gems = []
        self.damage_numbers = []
        self.pulse_effects = []
        self.wave = 1
        self.state = "class_select"
        self.score = 0
        self.upgrade_choices = []
        self.ui_buttons = []
        self.class_choices = []
        self.selected_class: Optional[ClassChoice] = None
        self.selected_ultimate_key = "singularity"
        self.ultimate_boss_boost = 0
        self.ui_icons = self.load_ui_icons()
        self.upgrade_icons = self.load_upgrade_icons()
        self.reset_game()
        self.cheats_enabled = False
        self.cheat_buttons = []
        self.pending_upgrades = 0
        self.pending_wave_spawns = 0
        self.wave_total = 0
        self.wave_killed = 0
        self.wave_spawn_remaining = 0
        self.wave_spawn_interval = 0.0
        self.wave_spawn_timer = 0.0
        self.boss_spawn_interval = 1.0
        self.boss_spawn_timer = 0.0
        self.gem_rush_timer = 0.0
        self.boss_death_timer = 0.0
        self.gamepad = None
        self.gamepad_name = ""
        self.gamepad_deadzone = 0.22
        self.gamepad_aim_deadzone = 0.20
        self.gamepad_axis_centers = []
        self.gamepad_aim_axes = (2, 3)
        self.pad_btn_ulti = 3
        self.pad_btn_shockwave = 2
        self.pad_btn_pause = {6, 7}
        self.pad_btn_confirm = {0, 1}
        self.menu_selected_index = 0
        self.menu_nav_hold = (0, 0)
        self.menu_nav_repeat_timer = 0.0
        self.base_fire_enabled = True
        self.state = "start_menu"
        self.build_start_menu_buttons()
        self.refresh_gamepad()

    def refresh_gamepad(self):
        if not pygame.joystick.get_init():
            pygame.joystick.init()
        self.gamepad = None
        if pygame.joystick.get_count() <= 0:
            self.gamepad_name = ""
            self.gamepad_axis_centers = []
            return
        js = pygame.joystick.Joystick(0)
        if not js.get_init():
            js.init()
        self.gamepad = js
        self.gamepad_name = js.get_name().lower()
        button_count = js.get_numbuttons()
        hat_count = js.get_numhats()
        self.pad_btn_ulti = 3
        self.pad_btn_shockwave = 2
        self.pad_btn_pause = {6, 7}
        self.pad_btn_confirm = {0, 1}
        is_switch_profile = ("switch" in self.gamepad_name) or ("nintendo" in self.gamepad_name)
        is_8bitdo = "8bitdo" in self.gamepad_name
        # 8BitDo can expose multiple layouts depending on hardware mode.
        # In Switch mode with pygame 2.x it commonly looks like:
        # 16 buttons, 0 hats, dpad as buttons 11..14.
        if is_8bitdo and not is_switch_profile and button_count >= 16 and hat_count == 0:
            is_switch_profile = True
        if is_switch_profile:
            self.pad_btn_ulti = 2
            self.pad_btn_shockwave = 3
            # Nintendo Switch Pro Controller (pygame 2.x):
            # '+' is button 6, '-' is button 4.
            self.pad_btn_pause = {6, 4}
            self.pad_btn_confirm = {1, 0}
        self.calibrate_gamepad_axes()

    def calibrate_gamepad_axes(self):
        if self.gamepad is None:
            self.gamepad_axis_centers = []
            self.gamepad_aim_axes = (2, 3)
            return
        axis_count = self.gamepad.get_numaxes()
        self.gamepad_axis_centers = [self._gamepad_axis(i) for i in range(axis_count)]
        candidates = []
        for a, b in ((2, 3), (3, 4), (2, 4), (4, 5), (2, 5)):
            if a < axis_count and b < axis_count:
                candidates.append((a, b))
        if not candidates:
            if axis_count >= 4:
                candidates = [(2, 3)]
            elif axis_count >= 2:
                candidates = [(0, 1)]
            else:
                candidates = [(0, 0)]

        def pair_score(pair):
            a, b = pair
            ca = self.gamepad_axis_centers[a]
            cb = self.gamepad_axis_centers[b]
            return abs(ca) + abs(cb) + abs(abs(ca) - abs(cb)) * 0.35

        self.gamepad_aim_axes = min(candidates, key=pair_score)

    @staticmethod
    def _axis_normalized(value, deadzone):
        mag = abs(value)
        if mag <= deadzone:
            return 0.0
        scaled = (mag - deadzone) / max(1e-6, (1.0 - deadzone))
        return math.copysign(clamp(scaled, 0.0, 1.0), value)

    def _gamepad_axis(self, idx):
        if self.gamepad is None:
            return 0.0
        if idx < 0 or idx >= self.gamepad.get_numaxes():
            return 0.0
        return float(self.gamepad.get_axis(idx))

    def _gamepad_button(self, idx):
        if self.gamepad is None:
            return False
        if idx < 0 or idx >= self.gamepad.get_numbuttons():
            return False
        return bool(self.gamepad.get_button(idx))

    def _gamepad_button_any(self, indices):
        return any(self._gamepad_button(idx) for idx in indices)

    def get_gamepad_input(self):
        result = {
            "connected": False,
            "move": (0.0, 0.0),
            "aim": (0.0, 0.0),
            "aim_active": False,
            "menu_dir": (0, 0),
            "confirm_pressed": False,
            "ulti_pressed": False,
            "shockwave_pressed": False,
            "pause_pressed": False,
        }
        if self.gamepad is None:
            return result

        result["connected"] = True
        lx = self._axis_normalized(self._gamepad_axis(0), self.gamepad_deadzone)
        ly = self._axis_normalized(self._gamepad_axis(1), self.gamepad_deadzone)

        dpx = 0
        dpy = 0
        if self.gamepad.get_numhats() > 0:
            hx, hy = self.gamepad.get_hat(0)
            dpx += hx
            dpy += -hy
        if self._gamepad_button(14):
            dpx += 1
        if self._gamepad_button(13):
            dpx -= 1
        if self._gamepad_button(12):
            dpy += 1
        if self._gamepad_button(11):
            dpy -= 1

        mvx = lx + dpx
        mvy = ly + dpy
        mv_len = math.hypot(mvx, mvy)
        if mv_len > 1.0:
            mvx /= mv_len
            mvy /= mv_len
        result["move"] = (mvx, mvy)

        aim_ax, aim_ay = self.gamepad_aim_axes
        rx = self._gamepad_axis(aim_ax)
        ry = self._gamepad_axis(aim_ay)
        rx = self._axis_normalized(rx, self.gamepad_aim_deadzone)
        ry = self._axis_normalized(ry, self.gamepad_aim_deadzone)
        result["aim"] = (rx, ry)
        result["aim_active"] = (rx * rx + ry * ry) > 0.01

        menu_x = dpx
        menu_y = dpy
        if menu_x == 0 and abs(lx) > 0.55:
            menu_x = -1 if lx < 0 else 1
        if menu_y == 0 and abs(ly) > 0.55:
            menu_y = -1 if ly < 0 else 1
        if abs(menu_x) >= abs(menu_y):
            menu_y = 0
        else:
            menu_x = 0
        result["menu_dir"] = (int(menu_x), int(menu_y))

        result["confirm_pressed"] = self._gamepad_button_any(self.pad_btn_confirm)
        result["ulti_pressed"] = self._gamepad_button(self.pad_btn_ulti)
        result["shockwave_pressed"] = self._gamepad_button(self.pad_btn_shockwave)
        result["pause_pressed"] = self._gamepad_button_any(self.pad_btn_pause)
        return result

    def move_menu_selection(self, direction):
        if not self.ui_buttons:
            self.menu_selected_index = 0
            return
        if self.menu_selected_index < 0 or self.menu_selected_index >= len(self.ui_buttons):
            self.menu_selected_index = 0
            return
        dx_dir, dy_dir = direction
        current_rect = self.ui_buttons[self.menu_selected_index]["rect"]
        cx = current_rect.centerx
        cy = current_rect.centery
        best_idx = None
        best_score = None
        for idx, btn in enumerate(self.ui_buttons):
            if idx == self.menu_selected_index:
                continue
            rect = btn["rect"]
            dx = rect.centerx - cx
            dy = rect.centery - cy
            if dx_dir < 0 and dx >= -1:
                continue
            if dx_dir > 0 and dx <= 1:
                continue
            if dy_dir < 0 and dy >= -1:
                continue
            if dy_dir > 0 and dy <= 1:
                continue
            primary = abs(dx) if dx_dir != 0 else abs(dy)
            secondary = abs(dy) if dx_dir != 0 else abs(dx)
            score = primary * 3.0 + secondary
            if best_score is None or score < best_score:
                best_score = score
                best_idx = idx
        if best_idx is not None:
            self.menu_selected_index = best_idx
            return
        if dx_dir < 0 or dy_dir < 0:
            self.menu_selected_index = (self.menu_selected_index - 1) % len(self.ui_buttons)
        elif dx_dir > 0 or dy_dir > 0:
            self.menu_selected_index = (self.menu_selected_index + 1) % len(self.ui_buttons)

    def update_menu_navigation(self, dt, pad_input):
        if self.gamepad is None:
            self.menu_nav_hold = (0, 0)
            self.menu_nav_repeat_timer = 0.0
            return
        if self.state not in ("start_menu", "class_select", "upgrade", "game_over", "pause"):
            self.menu_nav_hold = (0, 0)
            self.menu_nav_repeat_timer = 0.0
            return
        if not self.ui_buttons:
            return
        if self.menu_selected_index >= len(self.ui_buttons):
            self.menu_selected_index = 0
        direction = pad_input["menu_dir"]
        if direction == (0, 0):
            self.menu_nav_hold = (0, 0)
            self.menu_nav_repeat_timer = 0.0
            return
        if direction != self.menu_nav_hold:
            self.menu_nav_hold = direction
            self.move_menu_selection(direction)
            self.menu_nav_repeat_timer = 0.22
            return
        self.menu_nav_repeat_timer -= dt
        while self.menu_nav_repeat_timer <= 0:
            self.move_menu_selection(direction)
            self.menu_nav_repeat_timer += 0.10

    def activate_selected_menu_button(self):
        if not self.ui_buttons:
            return False
        if self.menu_selected_index < 0 or self.menu_selected_index >= len(self.ui_buttons):
            self.menu_selected_index = 0
        btn = self.ui_buttons[self.menu_selected_index]
        if self.state == "start_menu":
            if btn["action"] == "play":
                self.open_class_select()
            else:
                return "quit"
            return True
        if self.state == "class_select":
            self.select_class(btn["class_choice"])
            return True
        if self.state == "upgrade":
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
            return True
        if self.state == "game_over":
            if btn["action"] == "replay":
                self.reset_game()
            else:
                return "quit"
            return True
        if self.state == "pause":
            if btn["action"] == "resume":
                self.state = "playing"
            elif btn["action"] == "replay":
                self.reset_game()
            else:
                return "quit"
            return True
        return False

    def toggle_pause(self):
        if self.state == "playing":
            self.state = "pause"
            self.build_pause_buttons()
            return True
        if self.state == "pause":
            self.state = "playing"
            return True
        return False

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
            return max(0, int(self.player.bullets_per_shot - 1))
        if key == "ricochet":
            return self.player.ricochet_level
        if key == "focus_combo":
            return self.player.focus_combo_level
        if key == "fire_orb":
            return self.player.fire_orb_level
        if key == "laser_orb":
            return self.player.laser_orb_level
        if key == "electroelf":
            return self.player.electroelf_level
        if key == "rockets":
            return self.player.rocket_level
        if key == "rocket_frag":
            return self.player.rocket_frag_level
        if key == "fire_ring":
            return self.player.fire_ring_level
        return 0

    def upgrade_max_level(self, key):
        if key == "fire_rate":
            return int(round((0.9 - 0.08) / 0.02))
        if key == "bullets":
            return 9
        if key == "ricochet":
            return 8
        if key == "focus_combo":
            return 8
        if key == "fire_orb":
            return 14
        if key == "laser_orb":
            return 10
        if key == "electroelf":
            return 5
        if key == "rockets":
            return 10
        if key == "shield_regen":
            return 10
        if key == "rocket_frag":
            return 10
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

    def reset_damage_stats(self):
        self.damage_total = 0.0
        self.damage_source_totals = {}
        self.player_damage_total = 0.0
        self.player_damage_source_totals = {}
        self.combat_time = 0.0

    def normalize_damage_source(self, source):
        if source in DAMAGE_SOURCE_META:
            return source
        return "other"

    def normalize_player_damage_source(self, source):
        if source in PLAYER_DAMAGE_SOURCE_META:
            return source
        return "other"

    def record_damage_stat(self, source, amount):
        if amount <= 0:
            return
        key = self.normalize_damage_source(source)
        self.damage_total += amount
        self.damage_source_totals[key] = self.damage_source_totals.get(key, 0.0) + amount

    def record_player_damage_stat(self, source, amount):
        if amount <= 0:
            return
        key = self.normalize_player_damage_source(source)
        self.player_damage_total += amount
        self.player_damage_source_totals[key] = self.player_damage_source_totals.get(key, 0.0) + amount

    def upgrade_label_from_key(self, key):
        for choice in list(UPGRADE_POOL) + EPIC_UPGRADES:
            if choice.key == key:
                return choice.label
        return key

    def damage_source_label(self, source):
        info = DAMAGE_SOURCE_META.get(source)
        if info is None:
            return DAMAGE_SOURCE_META["other"]["label"]
        return info["label"]

    def damage_source_upgrade_note(self, source):
        info = DAMAGE_SOURCE_META.get(source)
        if info is None:
            return "Upgrade: inconnu"
        if source in ("bio_minions", "bee_swarm"):
            return "Classe: competence E"
        upgrade_key = info.get("upgrade_key")
        if upgrade_key is None:
            return "Classe: ultime"
        level = self.upgrade_level(upgrade_key)
        max_level = self.upgrade_max_level(upgrade_key)
        label = self.upgrade_label_from_key(upgrade_key)
        if max_level is None:
            return f"Upgrade: {label} niv {level}"
        return f"Upgrade: {label} {level}/{max_level}"

    def player_damage_source_label(self, source):
        info = PLAYER_DAMAGE_SOURCE_META.get(source)
        if info is None:
            return PLAYER_DAMAGE_SOURCE_META["other"]["label"]
        return info["label"]

    @staticmethod
    def format_time_short(seconds):
        total = max(0, int(seconds))
        minutes = total // 60
        secs = total % 60
        return f"{minutes:02d}:{secs:02d}"

    @staticmethod
    def build_star_bar(value, thresholds):
        filled = 0
        for threshold in thresholds:
            if value >= threshold:
                filled += 1
        return int(clamp(filled, 0, 5))

    @staticmethod
    def star_points(center, outer_radius, inner_radius, branches=5, angle_offset=-math.pi / 2):
        cx, cy = center
        points = []
        total = branches * 2
        for i in range(total):
            radius = outer_radius if i % 2 == 0 else inner_radius
            angle = angle_offset + i * (math.tau / total)
            points.append((cx + math.cos(angle) * radius, cy + math.sin(angle) * radius))
        return points

    def draw_stat_rating(self, x, y, filled, total=5):
        badge_w = 124
        badge_h = 18
        badge = pygame.Surface((badge_w, badge_h), pygame.SRCALPHA)
        pygame.draw.rect(badge, (16, 30, 46, 210), badge.get_rect(), border_radius=9)
        pygame.draw.rect(badge, (85, 165, 220, 150), badge.get_rect(), 1, border_radius=9)
        glow_w = int((badge_w - 8) * (filled / max(1, total)))
        if glow_w > 0:
            glow = pygame.Surface((glow_w, badge_h - 6), pygame.SRCALPHA)
            pygame.draw.rect(glow, (120, 215, 255, 42), glow.get_rect(), border_radius=7)
            badge.blit(glow, (4, 3))

        slot_step = 24
        for i in range(total):
            center = (14 + i * slot_step, badge_h // 2)
            points = self.star_points(center, 7, 3.4)
            is_filled = i < filled
            if is_filled:
                pygame.draw.circle(badge, (255, 220, 140, 34), center, 10)
                pygame.draw.circle(badge, (255, 245, 210, 18), center, 7)
                pygame.draw.polygon(badge, (255, 232, 150), points)
                pygame.draw.polygon(badge, (255, 250, 225), points, 1)
            else:
                pygame.draw.polygon(badge, (68, 88, 108), points)
                pygame.draw.polygon(badge, (120, 144, 168), points, 1)

        self.screen.blit(badge, (x, y))

    def build_damage_stats_lines(self):
        total_damage = self.damage_total
        dps = total_damage / max(1.0, self.combat_time)
        level_progress = max(0, self.wave - 1)
        summary_lines = [
            ("Degats totaux", f"{int(total_damage)}", self.build_star_bar(total_damage, [1200, 6500, 22000, 58000, 130000])),
            ("DPS moyen", f"{dps:.1f}", self.build_star_bar(dps, [30, 90, 180, 320, 520])),
            ("Temps de combat", self.format_time_short(self.combat_time), self.build_star_bar(self.combat_time, [45, 120, 240, 420, 660])),
            ("Progression vagues", f"{level_progress}", self.build_star_bar(level_progress, [2, 5, 9, 14, 20])),
        ]

        detail_lines = []
        entries = []
        for key in DAMAGE_SOURCE_ORDER:
            value = self.damage_source_totals.get(key, 0.0)
            if value > 0:
                entries.append((key, value))
        entries.sort(key=lambda item: item[1], reverse=True)
        for source, value in entries:
            ratio = (value / total_damage * 100.0) if total_damage > 0 else 0.0
            label = self.damage_source_label(source)
            note = self.damage_source_upgrade_note(source)
            detail_lines.append((f"{label}: {int(value)} ({ratio:.1f}%) - {note}", ratio))
        if not detail_lines:
            detail_lines.append(("Aucun degat inflige pour le moment.", 0.0))
        return summary_lines, detail_lines

    def build_player_damage_stats_lines(self):
        total_damage = self.player_damage_total
        summary_lines = [
            ("Degats recus", f"{int(total_damage)}", self.build_star_bar(total_damage, [40, 90, 160, 260, 380])),
        ]

        detail_lines = []
        entries = []
        for key in PLAYER_DAMAGE_SOURCE_ORDER:
            value = self.player_damage_source_totals.get(key, 0.0)
            if value > 0:
                entries.append((key, value))
        entries.sort(key=lambda item: item[1], reverse=True)
        for source, value in entries:
            ratio = (value / total_damage * 100.0) if total_damage > 0 else 0.0
            detail_lines.append((f"{self.player_damage_source_label(source)}: {int(value)} ({ratio:.1f}%)", ratio))
        if not detail_lines:
            detail_lines.append(("Aucun degat recu pour le moment.", 0.0))
        return summary_lines, detail_lines

    def get_damage_stats_rect(self, anchor_rect, title, top_margin=0, bottom_margin=0, side="right", player_stats=False):
        if player_stats:
            summary_lines, detail_lines = self.build_player_damage_stats_lines()
        else:
            summary_lines, detail_lines = self.build_damage_stats_lines()
        all_widths = [self.big_font.size(title)[0]]
        if player_stats:
            all_widths.extend(self.font.size(f"{label}: {value}")[0] for label, value, _ in summary_lines)
        else:
            all_widths.extend(self.font.size(f"{label}: {value}")[0] + 150 for label, value, _ in summary_lines)
        all_widths.extend(self.font.size(text)[0] for text, _ in detail_lines)

        content_w = max(all_widths) if all_widths else 280
        panel_w = int(clamp(content_w + 40, 320, min(760, WIDTH - 40)))

        base_h = 56 + len(summary_lines) * 24 + 20
        detail_h = len(detail_lines) * 24 + 24
        panel_h = base_h + detail_h
        panel_h = max(220, int(panel_h))

        if side == "left":
            x = anchor_rect.x - panel_w - 24
            if x < 20:
                panel_w = max(280, anchor_rect.x - 44)
                x = max(20, anchor_rect.x - panel_w - 24)
        else:
            x = anchor_rect.right + 24
            if x + panel_w > WIDTH - 20:
                panel_w = max(280, WIDTH - x - 20)
            if x + panel_w > WIDTH - 20:
                x = max(20, WIDTH - panel_w - 20)

        y = max(top_margin, anchor_rect.y)
        if y + panel_h > HEIGHT - bottom_margin:
            y = max(top_margin, HEIGHT - bottom_margin - panel_h)

        return pygame.Rect(int(x), int(y), int(panel_w), int(panel_h))

    def draw_damage_stats_panel(self, rect, title, player_stats=False):
        panel = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(panel, (8, 16, 28, 238), panel.get_rect(), border_radius=14)
        pygame.draw.rect(panel, (95, 190, 245, 220), panel.get_rect(), 2, border_radius=14)
        pygame.draw.rect(panel, (170, 238, 255, 140), panel.get_rect().inflate(-10, -10), 1, border_radius=12)
        self.screen.blit(panel, rect.topleft)

        title_surf = self.big_font.render(title, True, (225, 245, 255))
        self.screen.blit(title_surf, (rect.x + 18, rect.y + 14))

        if player_stats:
            summary_lines, detail_lines = self.build_player_damage_stats_lines()
        else:
            summary_lines, detail_lines = self.build_damage_stats_lines()

        summary_y = rect.y + 56
        for label, value, stars in summary_lines:
            line = self.font.render(f"{label}: {value}", True, (200, 228, 248))
            self.screen.blit(line, (rect.x + 20, summary_y))
            if not player_stats:
                self.draw_stat_rating(rect.right - 164, summary_y + 1, stars)
            summary_y += 28

        line_y = summary_y + 4
        separator = pygame.Surface((rect.width - 40, 2), pygame.SRCALPHA)
        separator.fill((95, 190, 245, 120))
        self.screen.blit(separator, (rect.x + 20, line_y))

        start_y = line_y + 16
        for row, ratio in detail_lines:
            color = (220, 242, 255) if ratio >= 10 else (185, 215, 238)
            text_surf = self.font.render(row, True, color)
            self.screen.blit(text_surf, (rect.x + 20, start_y))
            start_y += 24

    def reset_game(self):
        self.player = Player()
        self.enemies.clear()
        self.projectiles.clear()
        self.rockets.clear()
        self.blade_skill_slashes.clear()
        self.explosions.clear()
        self.lightning_effects.clear()
        self.ultimate_beams.clear()
        self.spatial_lasers.clear()
        self.ultimate_pulses.clear()
        self.ultimate_zones.clear()
        self.ultimate_constellations.clear()
        self.ultimate_singularities.clear()
        self.ultimate_prismatic_blades.clear()
        self.ultimate_vector_overdrives.clear()
        self.ultimate_spectral_swarms.clear()
        self.ultimate_spectral_shards.clear()
        self.ultimate_queen_hives.clear()
        self.bee_hives.clear()
        self.bee_minions.clear()
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
        self.wave_spawn_remaining = 0
        self.wave_spawn_interval = 0.0
        self.wave_spawn_timer = 0.0
        self.boss_spawn_timer = 0.0
        self.gem_rush_timer = 0.0
        self.boss_death_timer = 0.0
        self.selected_class = None
        self.selected_ultimate_key = "singularity"
        self.ultimate_boss_boost = 0
        self.base_fire_enabled = True
        self.reset_damage_stats()
        self.spawn_wave(self.wave)
        self.prepare_class_choices()
        self.state = "class_select"

    def open_class_select(self):
        self.prepare_class_choices()
        self.state = "class_select"

    def prepare_class_choices(self):
        count = min(3, len(CLASS_POOL))
        self.class_choices = random.sample(CLASS_POOL, k=count)
        self.build_class_select_buttons()

    def build_class_select_buttons(self):
        self.ui_buttons = []
        self.menu_selected_index = 0
        panel_w = int(WIDTH * 0.90)
        panel_h = int(HEIGHT * 0.76)
        panel_x = (WIDTH - panel_w) / 2
        panel_y = (HEIGHT - panel_h) / 2
        gap = 22
        count = max(1, len(self.class_choices))
        card_w = (panel_w - gap * (count + 1)) / count
        card_h = panel_h - 80
        card_y = panel_y + 56
        for i, class_choice in enumerate(self.class_choices):
            card_x = panel_x + gap + i * (card_w + gap)
            rect = pygame.Rect(card_x, card_y, card_w, card_h)
            self.ui_buttons.append({"rect": rect, "class_choice": class_choice})

    def select_class(self, class_choice):
        self.selected_class = class_choice
        self.selected_ultimate_key = class_choice.ultimate_key
        self.state = "playing"
        self.ui_buttons = []

    def active_ultimate_key(self):
        implemented = {
            "singularity",
            "constellation_laser",
            "prismatic_blade",
            "vector_overdrive",
            "spectral_swarm",
            "queen_hive",
        }
        if self.selected_ultimate_key in implemented:
            return self.selected_ultimate_key
        return "singularity"


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
            "ricochet": "ricochet.png",
            "focus_combo": "focus_combo.png",
            "fire_orb": "fireball.png",
            "rockets": "rocket.png",
            "rocket_frag": "rocket.png",
            "fire_ring": "fire_ring.png",
            "laser_orb":"laser_orb.png",
            "electroelf":"electroelf.png",
            "shield_regen":"shield.png",
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

    def spawn_random_wave_enemy(self, wave):
        x, y = random_spawn_point()
        kind = random.choices(
            ["basic", "fast", "tank", "shooter"],
            weights=[70, 10, 10, 10],
        )[0]
        self.enemies.append(Enemy(x, y, kind, wave))


    def spawn_wave(self, wave):
        self.enemies.clear()
        self.boss = None
        self.boss_zones.clear()
        self.boss_spawn_timer = 0.0
        total = 18 + int(wave * 3.0)
        self.wave_total = total
        self.wave_killed = 0
        initial_count = max(1, int(total * 0.5))
        delayed_count = max(0, total - initial_count)
        for _ in range(initial_count):
            self.spawn_random_wave_enemy(wave)
        self.wave_spawn_remaining = delayed_count
        if delayed_count > 0:
            self.wave_spawn_interval = 10.0 / delayed_count
            self.wave_spawn_timer = self.wave_spawn_interval
        else:
            self.wave_spawn_interval = 0.0
            self.wave_spawn_timer = 0.0
        if wave % 5 == 0:
            self.boss = Boss(wave)
            self.boss_spawn_timer = self.boss_spawn_interval

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
            self.player.ultimate_cooldown_max = max(0.5, self.player.ultimate_cooldown_max - 0.1)
        elif key == "bullets":
            self.player.bullets_per_shot = min(10, self.player.bullets_per_shot + 1)
        elif key == "ricochet":
            self.player.ricochet_level = min(8, self.player.ricochet_level + 1)
        elif key == "focus_combo":
            self.player.focus_combo_level = min(8, self.player.focus_combo_level + 1)
        elif key == "shield_regen":
            self.player.shield_regen_level = min(10, self.player.shield_regen_level + 1)
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
            self.player.laser_orb_cooldown = max(1.0, self.player.laser_orb_cooldown - 0.05)
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
        elif key == "rocket_frag":
            if not self.player.rocket_frag:
                self.player.rocket_frag = True
                self.player.rocket_frag_level = 0
            else:
                if self.player.rocket_frag_level >= 10:
                    return
                self.player.rocket_frag_level += 1

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
        rockets_max = self.upgrade_max_level("rockets")
        if rockets_max is not None:
            if (self.player.rocket_level >= rockets_max and not self.player.rocket_frag) or self.player.rocket_frag:
                pool.append(EPIC_UPGRADES[3])
        pool = [u for u in pool if not self.upgrade_is_maxed(u.key)]
        if not pool:
            return False
        self.upgrade_choices = random.sample(pool, k=min(3, len(pool)))
        self.build_upgrade_buttons()
        return True

    def build_upgrade_buttons(self):
        self.ui_buttons = []
        self.menu_selected_index = 0
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

    def start_menu_panel_rect(self):
        panel_w = int(clamp(WIDTH * 0.56, 560, 980))
        panel_h = int(clamp(HEIGHT * 0.56, 380, 640))
        panel_x = (WIDTH - panel_w) / 2
        panel_y = (HEIGHT - panel_h) / 2 + int(HEIGHT * 0.08)
        return pygame.Rect(panel_x, panel_y, panel_w, panel_h)

    def build_start_menu_buttons(self):
        self.ui_buttons = []
        self.menu_selected_index = 0
        panel = self.start_menu_panel_rect()
        play_w = int(panel.width * 0.58)
        play_h = int(clamp(panel.height * 0.16, 62, 90))
        quit_w = int(panel.width * 0.40)
        quit_h = int(clamp(panel.height * 0.12, 48, 70))
        gap = 30
        play_x = panel.centerx - play_w / 2
        play_y = panel.y + int(panel.height * 0.33)
        quit_x = panel.centerx - quit_w / 2
        quit_y = play_y + play_h + gap
        self.ui_buttons.append({"rect": pygame.Rect(play_x, play_y, play_w, play_h), "action": "play"})
        self.ui_buttons.append({"rect": pygame.Rect(quit_x, quit_y, quit_w, quit_h), "action": "quit"})

    def build_game_over_buttons(self):
        self.ui_buttons = []
        self.menu_selected_index = 0
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
        self.menu_selected_index = 0
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
        test_label = self.font.render("Test", True, (255, 255, 255))
        text_h = test_label.get_height()
        h = text_h + 12
        
        max_text_width = 0
        for up in upgrades:
            label_text = self.upgrade_label_with_level(up)
            label_surf = self.font.render(label_text, True, (255, 255, 255))
            max_text_width = max(max_text_width, label_surf.get_width())
        level_label_surf = self.font.render("Niveau +1", True, (255, 255, 255))
        max_text_width = max(max_text_width, level_label_surf.get_width())
        
        ult_label_surf = self.font.render("ULT Max", True, (255, 255, 255))
        max_text_width = max(max_text_width, ult_label_surf.get_width())
        w = max_text_width + 20
        padding = 8
        total_h = (len(upgrades) + 2) * (h + padding) - padding
        x = WIDTH - w - 20
        y = HEIGHT - total_h - 20
        y = clamp(y, 10, HEIGHT - total_h - 10)
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
        self.player.boss_kills += 1
        self.wave_spawn_remaining = 0
        self.wave_spawn_interval = 0.0
        self.wave_spawn_timer = 0.0
        self.boss_spawn_timer = 0.0
        self.boss_zones.clear()
        for enemy in list(self.enemies):
            self.explosions.append(Explosion(enemy.x, enemy.y, 40, duration=0.3))
        self.enemies.clear()
        self.explosions.append(Explosion(bx, by, 90, duration=0.45))
        gem_count = self.wave * self.wave + 30
        self.spawn_gems(bx, by, count=gem_count, amount=1, spread=60)
        self.ultimate_boss_boost += 1
        self.wave_killed = self.wave_total
        self.boss_death_timer = 0.8
        self.state = "boss_death"

    def boss_projectile_damage(self):
        return 14 + self.wave * 1.6

    def boss_zone_damage(self):
        return 18 + self.wave * 1.8

    def boss_laser_damage(self):
        return 24 + self.wave * 2.0

    def boss_contact_damage(self):
        return 14 + self.wave * 1.4

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

    def damage_player(self, amount, source="other"):
        hp_before = self.player.hp
        shield_before = self.player.shield
        result = self.player.take_damage(amount)
        if result in ("shield", "hp"):
            self.player.reset_focus_combo()
        hp_loss = max(0.0, hp_before - self.player.hp)
        shield_loss = max(0.0, shield_before - self.player.shield)
        self.record_player_damage_stat(source, hp_loss + shield_loss)
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

    def damage_enemy(self, enemy, amount, source="other"):
        amount = self.apply_player_damage_multiplier(amount, source)
        if enemy not in self.enemies or amount <= 0 or enemy.hp <= 0:
            return
        dealt = min(amount, enemy.hp)
        enemy.hp -= amount
        self.record_damage_stat(source, dealt)
        self.spawn_damage_number(enemy.x, enemy.y, amount)
        self.spawn_pulse(enemy.x, enemy.y, color=(255, 150, 95), start_radius=8, end_radius=24, duration=0.11, width=2, fill_alpha=24)
        if enemy.hp <= 0 and enemy in self.enemies:
            self.enemies.remove(enemy)
            self.on_enemy_killed(enemy)

    def damage_ally(self, ally, amount):
        if ally not in self.enemies or not ally.is_ally or amount <= 0 or ally.hp <= 0:
            return
        ally.hp -= amount
        if ally.hp <= 0 and ally in self.enemies:
            self.enemies.remove(ally)

    def damage_boss(self, amount, source="other"):
        amount = self.apply_player_damage_multiplier(amount, source)
        if self.boss is None or amount <= 0 or self.boss.hp <= 0:
            return
        dealt = min(amount, self.boss.hp)
        self.boss.hp -= amount
        self.record_damage_stat(source, dealt)
        self.spawn_damage_number(self.boss.x, self.boss.y, amount, color=(255, 175, 90))
        if self.boss.hp <= 0:
            self.on_boss_killed()

    def fire_spatial_laser(self):
        target_pos = None
        nearest_dist = float('inf')
        
        for enemy in self.enemies:
            if enemy.is_ally:
                continue
            dist = distance((enemy.x, enemy.y), (self.player.x, self.player.y))
            if dist < nearest_dist:
                nearest_dist = dist
                target_pos = (enemy.x, enemy.y)
        
        if self.boss is not None:
            dist = distance((self.boss.x, self.boss.y), (self.player.x, self.player.y))
            if dist < nearest_dist:
                target_pos = (self.boss.x, self.boss.y)
        
        if target_pos is None:
            target_pos = (self.player.x + 400, self.player.y)
        
        width = self.spatial_laser_width()
        damage = self.spatial_laser_damage()
        
        laser = SpatialLaser(
            (self.player.x, self.player.y),
            target_pos,
            width=width,
            damage=damage,
            duration=0.18
        )
        self.spatial_lasers.append(laser)
        
        for enemy in list(self.enemies):
            if enemy.is_ally:
                continue
            dist_to_line = point_segment_distance(
                enemy.x, enemy.y,
                self.player.x, self.player.y,
                target_pos[0], target_pos[1]
            )
            if dist_to_line <= width * 0.6:
                self.damage_enemy(enemy, damage, source="spatial_laser")
        
        if self.boss is not None:
            dist_to_line = point_segment_distance(
                self.boss.x, self.boss.y,
                self.player.x, self.player.y,
                target_pos[0], target_pos[1]
            )
            if dist_to_line <= width * 0.6:
                self.damage_boss(damage, source="spatial_laser")
        
        self.pulse_effects.append(
            PulseEffect(
                self.player.x,
                self.player.y,
                color=(100, 200, 255),
                start_radius=20,
                end_radius=140,
                duration=0.2,
                width=5,
                fill_alpha=80,
            )
        )
        
        self.player.shockwave_charging = False
        self.player.shockwave_charge_time = 0.0
        self.player.shockwave_timer = 0.0

    def ultimate_cadence_multiplier(self):
        return clamp(0.9 / max(0.08, self.player.fire_rate), 1.0, 2.0)

    def ultimate_boss_level(self):
        return max(0, int(self.ultimate_boss_boost))

    def ultimate_damage_scale(self, per_level=0.14, cap=5.0):
        return min(cap, 1.0 + self.ultimate_boss_level() * per_level)

    def concentration_bonus_ratio(self):
        level = self.player.focus_combo_level
        if level <= 0:
            return 0.0
        gain_per_second = 0.01 + level * 0.003
        max_bonus = 0.12 + level * 0.06
        return min(max_bonus, self.player.focus_combo_timer * gain_per_second)

    def concentration_damage_multiplier(self):
        return 1.0 + self.concentration_bonus_ratio()

    def apply_player_damage_multiplier(self, amount, source):
        if amount <= 0:
            return 0.0
        if self.player.focus_combo_level <= 0:
            return amount
        return amount * self.concentration_damage_multiplier()

    def player_projectile_damage_value(self):
        dmg_mult = 1.4 if self.player.haste > 0 else 1.0
        if self.player.vector_overdrive_time > 0:
            dmg_mult *= 1.55
        return self.player.damage * dmg_mult

    def upgrade_force_value(self):
        return max(0.0, float(self.player.damage))

    def fire_orb_impact_damage_value(self):
        base = 4.0 + self.player.fire_orb_level * 1.5
        return base + 0.55 * self.upgrade_force_value()

    def fire_orb_burn_enemy_dps_value(self, enemy):
        base = 4.0 + enemy.max_hp * 0.05
        return base + 0.20 * self.upgrade_force_value()

    def fire_orb_burn_boss_dps_value(self):
        if self.boss is None:
            return 0.0
        base = 6.0 + self.boss.max_hp * 0.012
        return base + 0.16 * self.upgrade_force_value()

    def fire_ring_burn_dps_value(self):
        base = self.player.fire_ring_burn_dps
        return base + 0.24 * self.upgrade_force_value()

    def laser_orb_damage_value(self):
        base = self.player.laser_orb_damage
        return base + 0.42 * self.upgrade_force_value()

    def electroelf_damage_value(self):
        base = self.player.electroelf_damage
        return base + 0.95 * self.upgrade_force_value()

    def rocket_damage_value(self):
        base = 35.0 + self.player.rocket_level * 2.0
        return base + 0.60 * self.upgrade_force_value()

    def rocket_fragment_count(self):
        if not self.player.rocket_frag:
            return 0
        return 4 + min(8, self.player.rocket_frag_level)

    def rocket_fragment_damage_ratio(self):
        if not self.player.rocket_frag:
            return 0.0
        return 0.26 + min(0.28, self.player.rocket_frag_level * 0.028)

    def rocket_fragment_speed(self):
        return 320.0 + min(280.0, self.player.rocket_frag_level * 28.0)

    def ricochet_damage_decay(self):
        if self.player.ricochet_level <= 0:
            return 1.0
        return clamp(0.74 + self.player.ricochet_level * 0.025, 0.72, 0.92)

    def ricochet_range_value(self):
        return 180.0 + self.player.ricochet_level * 50.0

    def shockwave_damage_value(self):
        base = self.wave * 4.0
        return base + self.player.shockwave_damage * self.upgrade_force_value()

    def shockwave_radius_value(self):
        base_radius = float(self.player.shockwave_radius)
        target_radius = WIDTH * 0.5
        t = clamp(self.ultimate_boss_level() / 20.0, 0.0, 1.0)
        return int(base_radius + (target_radius - base_radius) * t)

    def constellation_node_count(self):
        bullets_level = self.upgrade_level("bullets")
        return int(clamp(4 + bullets_level // 3 + self.ultimate_boss_level(), 4, 20))

    def constellation_tick_interval(self):
        cadence_level = self.upgrade_level("fire_rate")
        return max(0.035, 0.1 - cadence_level * 0.0015 - self.ultimate_boss_level() * 0.0025)

    def constellation_duration(self):
        speed_level = self.upgrade_level("speed")
        bullets_level = self.upgrade_level("bullets")
        bonus = min(2.0, bullets_level * 0.05 + speed_level * 0.02)
        bonus += min(3.0, self.ultimate_boss_level() * 0.18)
        return 10.0 + bonus

    def prismatic_blade_duration(self):
        return 5.2 + min(2.4, self.ultimate_boss_level() * 0.24)

    def prismatic_blade_tick_interval(self):
        return max(0.055, 0.12 - self.ultimate_boss_level() * 0.004)

    def prismatic_blade_count(self):
        return int(min(6, 3 + self.ultimate_boss_level() // 3))

    def prismatic_blade_width(self):
        return int(min(56, 30 + self.ultimate_boss_level() * 1.5))

    def blade_skill_damage_value(self):
        base = self.player_projectile_damage_value() * 1.85 + self.wave * 3.2
        return base * self.ultimate_damage_scale(0.08, cap=3.2)

    def blade_skill_speed(self):
        return min(1700.0, 760.0 + self.ultimate_boss_level() * 28.0)


    def blade_skill_width(self):
        return int(min(60.0, 30.0 + self.ultimate_boss_level() * 2.0))

    def blade_skill_length(self):
        return int(min(1000.0, 700.0 + self.ultimate_boss_level() * 12.0))

    def blade_skill_cluster_radius(self):
        return min(320.0, 160.0 + self.ultimate_boss_level() * 8.0)

    def vector_overdrive_duration(self):
        return 8.0 + min(4.0, self.ultimate_boss_level() * 0.4)

    def vector_overdrive_tick_interval(self):
        return max(0.1, 0.24 - self.ultimate_boss_level() * 0.005)

    def vector_overdrive_max_targets(self):
        return int(min(14, 5 + self.ultimate_boss_level() // 2))

    def vector_overdrive_range(self):
        return min(760.0, 430.0 + self.ultimate_boss_level() * 20.0)

    def biochemist_transmute_radius(self):
        return min(840.0, 440.0 + self.ultimate_boss_level() * 32.0)

    def biochemist_transmute_duration(self):
        return 2.0

    def biochemist_ally_power(self):
        return min(2.6, 1.0 + self.ultimate_boss_level() * 0.12)

    def biochemist_summon_duration(self):
        return 8.0 + min(4.0, self.ultimate_boss_level() * 0.3)

    def biochemist_summon_count(self):
        return 5

    def biochemist_contact_damage(self, enemy):
        base = 10.0 + enemy.max_hp * 0.07 + self.wave * 0.7
        return base * self.biochemist_ally_power()

    def bee_hive_duration(self):
        return 30.0

    def bee_hive_spawn_interval(self):
        return 1.0

    def bee_swarm_damage(self):
        base = 4.0 + self.wave * 0.18
        return base * (1.0 + self.ultimate_boss_level() * 0.2)

    def bee_swarm_speed(self):
        return min(620.0, 340.0 + self.ultimate_boss_level() * 24.0)

    def bee_swarm_lifetime(self):
        return 6.5 + min(3.0, self.ultimate_boss_level() * 0.35)

    def bee_contact_damage(self, enemy):
        base = self.bee_swarm_damage()
        return (base + enemy.max_hp * 0.012) * 2.0

    def bee_boss_contact_damage(self):
        base = self.bee_swarm_damage()
        return base * 2.0

    def queen_hive_bee_count(self):
        return int(min(90, 30 + self.ultimate_boss_level() * 5))

    def queen_hive_cast_range(self):
        return 360.0 + min(220.0, self.ultimate_boss_level() * 18.0)

    def spectral_swarm_duration(self):
        return 8.0 + min(4.0, self.ultimate_boss_level() * 0.35)

    def spectral_swarm_spawn_interval(self):
        return max(0.045, 0.1 - self.ultimate_boss_level() * 0.003)

    def spectral_swarm_shard_lifetime(self):
        return 3.4 + min(2.0, self.ultimate_boss_level() * 0.18)

    def spectral_swarm_shard_speed_bonus(self):
        return min(180.0, self.ultimate_boss_level() * 12.0)

    def singularity_duration(self):
        return 6.0 + min(4.0, self.ultimate_boss_level() * 0.35)

    def singularity_radius(self):
        return int(min(520.0, 300.0 + self.ultimate_boss_level() * 14.0))

    def singularity_tick_interval(self):
        return max(0.08, 0.18 - self.ultimate_boss_level() * 0.0035)

    def singularity_pull_strength(self):
        return min(1100.0, 520.0 + self.ultimate_boss_level() * 40.0)

    def singularity_orbit_radius(self):
        return min(320.0, 190.0 + self.ultimate_boss_level() * 8.0)

    def singularity_orbit_speed(self):
        return min(3.0, 1.9 + self.ultimate_boss_level() * 0.04)

    def spatial_laser_width(self):
        return 60 + self.player.boss_kills * 8

    def spatial_laser_damage(self):
        return self.shockwave_damage_value() * 3.0 * self.ultimate_damage_scale(0.1, cap=3.0)

    def shockwave_cooldown_value(self):
        active_key = self.active_ultimate_key()
        if active_key == "constellation_laser":
            boss_progress = clamp(self.ultimate_boss_level() / 20.0, 0.0, 1.0)
            return 7.0 - 2.0 * boss_progress
        if active_key == "spectral_swarm":
            return 15.0
        if active_key == "queen_hive":
            return 10.0
        return self.player.shockwave_cooldown

    def try_activate_ultimate(self):
        if self.player.ultimate_charge < self.player.ultimate_max:
            return False
        if self.player.ultimate_beam_time > 0:
            return False
        if self.player.ultimate_cooldown > 0:
            return False
        active_key = self.active_ultimate_key()
        target_pos = pygame.mouse.get_pos()
        if active_key == "constellation_laser":
            self._activate_constellation_laser_ultimate()
            return True
        if active_key == "prismatic_blade":
            self._activate_prismatic_blade_ultimate(target_pos)
            return True
        if active_key == "vector_overdrive":
            self._activate_vector_overdrive_ultimate()
            return True
        if active_key == "spectral_swarm":
            self._activate_spectral_swarm_ultimate()
            return True
        if active_key == "queen_hive":
            self._activate_queen_hive_ultimate(target_pos)
            return True
        if active_key == "singularity":
            self._activate_singularity_ultimate(target_pos)
            return True
        return False

    def _clear_ultimate_effects(self):
        self.player.vector_overdrive_time = 0.0
        self.ultimate_beams.clear()
        self.spatial_lasers.clear()
        self.ultimate_zones.clear()
        self.ultimate_constellations.clear()
        self.ultimate_singularities.clear()
        self.ultimate_prismatic_blades.clear()
        self.ultimate_vector_overdrives.clear()
        self.ultimate_spectral_swarms.clear()
        self.ultimate_spectral_shards.clear()
        self.ultimate_queen_hives.clear()

    def _activate_constellation_laser_ultimate(self):
        self.player.ultimate_charge = 0
        self.player.ultimate_beam_time = self.constellation_duration()
        self.player.ultimate_cooldown = 0.0
        self._clear_ultimate_effects()
        preferred_points = [(enemy.x, enemy.y) for enemy in self.enemies if enemy.hp > 0 and not enemy.is_ally]
        if self.boss is not None and self.boss.hp > 0:
            preferred_points.append((self.boss.x, self.boss.y))
        constellation = UltimateConstellation(
            node_count=self.constellation_node_count(),
            duration=self.player.ultimate_beam_time,
            tick_interval=self.constellation_tick_interval(),
            margin=120,
            preferred_points=preferred_points,
        )
        constellation.beam_width = min(20, 8 + self.ultimate_boss_level() * 0.35)
        constellation.node_move_speed = min(220.0, 72.0 + self.ultimate_boss_level() * 8.0)
        self.ultimate_constellations.append(constellation)
        self.ultimate_pulses.append(UltimatePulse(self.player.x, self.player.y, 120, duration=0.28))
        cx, cy = constellation.center()
        self.ultimate_pulses.append(UltimatePulse(cx, cy, 180, duration=0.35))

    def _activate_prismatic_blade_ultimate(self, target_pos):
        sx, sy = self.player.x, self.player.y
        angle = math.atan2(target_pos[1] - sy, target_pos[0] - sx)
        self.player.ultimate_charge = 0
        self.player.ultimate_beam_time = self.prismatic_blade_duration()
        self.player.ultimate_cooldown = 0.0
        self._clear_ultimate_effects()
        blade = UltimatePrismaticBlade(
            sx,
            sy,
            start_angle=angle,
            duration=self.player.ultimate_beam_time,
            tick_interval=self.prismatic_blade_tick_interval(),
            blade_count=self.prismatic_blade_count(),
            beam_width=self.prismatic_blade_width(),
        )
        blade.total_sword_length = min(WIDTH * 0.74, WIDTH * 0.5 + self.ultimate_boss_level() * 36.0)
        self.ultimate_prismatic_blades.append(blade)
        self.ultimate_pulses.append(UltimatePulse(sx, sy, 130, duration=0.26))

    def _activate_vector_overdrive_ultimate(self):
        self.player.ultimate_charge = 0
        self.player.ultimate_beam_time = self.biochemist_transmute_duration()
        self.player.ultimate_cooldown = 0.0
        self._clear_ultimate_effects()
        radius = self.biochemist_transmute_radius()
        converted = 0
        for enemy in self.enemies:
            if enemy.hp <= 0 or enemy.is_ally:
                continue
            if distance((enemy.x, enemy.y), (self.player.x, self.player.y)) <= radius:
                enemy.set_ally(
                    None,
                    source="ultimate_vector_overdrive",
                    power=self.biochemist_ally_power(),
                )
                converted += 1
        self.ultimate_pulses.append(UltimatePulse(self.player.x, self.player.y, 145, duration=0.28))
        self.pulse_effects.append(
            PulseEffect(
                self.player.x,
                self.player.y,
                color=(120, 220, 255),
                start_radius=32,
                end_radius=int(radius),
                duration=0.32,
                width=6,
                fill_alpha=44,
            )
        )
        if converted <= 0:
            self.player.ultimate_charge = int(min(self.player.ultimate_max * 0.35, self.player.ultimate_max))

    def _activate_spectral_swarm_ultimate(self):
        self.player.ultimate_charge = 0
        self.player.ultimate_beam_time = self.spectral_swarm_duration()
        self.player.ultimate_cooldown = 0.0
        self._clear_ultimate_effects()
        swarm = UltimateSpectralSwarm(
            self.player.x,
            self.player.y,
            duration=self.player.ultimate_beam_time,
            spawn_interval=self.spectral_swarm_spawn_interval(),
        )
        self.ultimate_spectral_swarms.append(swarm)
        self.ultimate_pulses.append(UltimatePulse(self.player.x, self.player.y, 140, duration=0.28))

    def _activate_queen_hive_ultimate(self, target_pos):
        tx, ty = self.player.x, self.player.y
        self.player.ultimate_charge = 0
        self.player.ultimate_beam_time = 0.0
        self.player.ultimate_cooldown = 20.0
        self._clear_ultimate_effects()
        self.spawn_bee_hive(tx, ty, source="ultimate_queen_hive", move_existing=True)
        self.ultimate_pulses.append(UltimatePulse(tx, ty, 190, duration=0.28))
        self.pulse_effects.append(
            PulseEffect(
                tx,
                ty,
                color=(255, 210, 90),
                start_radius=26,
                end_radius=210,
                duration=0.3,
                width=7,
                fill_alpha=70,
            )
        )

    def _activate_singularity_ultimate(self, target_pos):
        tx, ty = target_pos
        tx = clamp(tx, 40, WIDTH - 40)
        ty = clamp(ty, 40, HEIGHT - 40)
        px, py = self.player.x, self.player.y
        ang = math.atan2(ty - py, tx - px)
        orbit_radius = self.singularity_orbit_radius()
        sx = px + math.cos(ang) * orbit_radius
        sy = py + math.sin(ang) * orbit_radius
        self.player.ultimate_charge = 0
        self.player.ultimate_beam_time = self.singularity_duration()
        self.player.ultimate_cooldown = 0.0
        self._clear_ultimate_effects()
        singularity = UltimateSingularity(
            sx,
            sy,
            radius=self.singularity_radius(),
            duration=self.player.ultimate_beam_time,
            tick_interval=self.singularity_tick_interval(),
            pull_strength=self.singularity_pull_strength(),
            orbit_radius=orbit_radius,
            orbit_speed=self.singularity_orbit_speed(),
            start_angle=ang,
        )
        self.ultimate_singularities.append(singularity)
        self.ultimate_pulses.append(UltimatePulse(self.player.x, self.player.y, 120, duration=0.3))
        self.ultimate_pulses.append(UltimatePulse(sx, sy, 170, duration=0.35))

    def try_activate_shockwave(self):
        cooldown = self.shockwave_cooldown_value()
        active_key = self.active_ultimate_key()
        
        if active_key == "constellation_laser":
            if not self.player.shockwave_charging:
                if self.player.shockwave_timer < cooldown:
                    return False
                self.player.shockwave_charging = True
                self.player.shockwave_charge_time = 0.0
            return True
        
        if self.player.shockwave_timer < cooldown:
            return False
        self.player.shockwave_timer = 0.0
        if active_key == "vector_overdrive":
            for _ in range(self.biochemist_summon_count()):
                self.spawn_biochemist_ally(source="bio_minions")
            self.pulse_effects.append(
                PulseEffect(
                    self.player.x,
                    self.player.y,
                    color=(120, 220, 255),
                    start_radius=22,
                    end_radius=120,
                    duration=0.22,
                    width=5,
                    fill_alpha=36,
                )
            )
            return True
        if active_key == "prismatic_blade":
            tx, ty = self.blade_skill_target_pos()
            ang = math.atan2(ty - self.player.y, tx - self.player.x)
            self.blade_skill_slashes.append(
                BladeSkillSlash(
                    self.player.x,
                    self.player.y,
                    ang,
                    speed=self.blade_skill_speed(),
                    max_distance= 3000,
                    length=self.blade_skill_length(),
                    width=self.blade_skill_width(),
                    damage=self.blade_skill_damage_value(),
                )
            )
            self.pulse_effects.append(
                PulseEffect(
                    self.player.x,
                    self.player.y,
                    color=(120, 220, 255),
                    start_radius=18,
                    end_radius=150,
                    duration=0.18,
                    width=5,
                    fill_alpha=34,
                )
            )
            return True
        if active_key == "spectral_swarm":
            zone_radius = int(self.shockwave_radius_value() * 1.5)
            zone = UltimateZone(
                self.player.x,
                self.player.y,
                radius=zone_radius,
                duration=7.0,
                tick_interval=1.0 / 3.0,
            )
            self.ultimate_zones.append(zone)
            self.pulse_effects.append(
                PulseEffect(
                    self.player.x,
                    self.player.y,
                    color=(155, 110, 255),
                    start_radius=18,
                    end_radius=int(max(50, zone_radius * 0.55)),
                    duration=0.25,
                    width=6,
                    fill_alpha=85,
                )
            )
            self.pulse_effects.append(
                PulseEffect(
                    self.player.x,
                    self.player.y,
                    color=(200, 150, 255),
                    start_radius=10,
                    end_radius=int(max(30, zone_radius * 0.35)),
                    duration=0.15,
                    width=3,
                    fill_alpha=100,
                )
            )
            return True
        if active_key == "queen_hive":
            targets = [enemy for enemy in self.enemies if not enemy.is_ally and enemy.hp > 0]
            if self.boss is not None:
                targets.append(self.boss)
            targets.sort(key=lambda e: (e.x - self.player.x) ** 2 + (e.y - self.player.y) ** 2)
            bee_count = self.queen_hive_bee_count()
            for i in range(bee_count):
                target = targets[i % len(targets)] if targets else None
                self.spawn_hive_bee(self.player.x, self.player.y, source="bee_swarm", target=target)
            self.pulse_effects.append(
                PulseEffect(
                    self.player.x,
                    self.player.y,
                    color=(255, 210, 90),
                    start_radius=22,
                    end_radius=170,
                    duration=0.24,
                    width=5,
                    fill_alpha=54,
                )
            )
            return True
        radius = self.shockwave_radius_value()
        damage = self.shockwave_damage_value()
        self.shockwaves.append(Shockwave(self.player.x, self.player.y, radius))
        self.pulse_effects.append(
            PulseEffect(
                self.player.x,
                self.player.y,
                color=(120, 225, 255),
                start_radius=18,
                end_radius=int(max(46, radius * 0.55)),
                duration=0.18,
                width=6,
                fill_alpha=95,
            )
        )
        self.pulse_effects.append(
            PulseEffect(
                self.player.x,
                self.player.y,
                color=(130, 235, 255),
                start_radius=24,
                end_radius=int(max(72, radius * 0.82)),
                duration=0.3,
                width=7,
                fill_alpha=62,
            )
        )
        self.pulse_effects.append(
            PulseEffect(
                self.player.x,
                self.player.y,
                color=(230, 248, 255),
                start_radius=12,
                end_radius=int(max(32, radius * 0.38)),
                duration=0.12,
                width=3,
                fill_alpha=120,
            )
        )
        for enemy in list(self.enemies):
            if enemy.is_ally:
                continue
            dist = distance((enemy.x, enemy.y), (self.player.x, self.player.y))
            if dist <= radius:
                self.damage_enemy(enemy, damage, source="shockwave")
        if self.boss is not None:
            dist = distance((self.boss.x, self.boss.y), (self.player.x, self.player.y))
            if dist <= radius:
                self.damage_boss(damage, source="shockwave")
        return True

    def handle_collisions(self):
        for proj in list(self.projectiles):
            if proj.owner.startswith("player"):
                for enemy in list(self.enemies):
                    if enemy.is_ally:
                        continue
                    if distance((proj.x, proj.y), (enemy.x, enemy.y)) < proj.radius + enemy.radius:
                        source = "base_shot"
                        if proj.owner.startswith("player:"):
                            source = proj.owner.split(":", 1)[1]
                        self.damage_enemy(enemy, proj.damage, source=source)
                        if proj in self.projectiles and not self.try_ricochet_projectile(proj, enemy):
                            self.projectiles.remove(proj)
                        break
                if proj in self.projectiles and self.boss is not None:
                    if distance((proj.x, proj.y), (self.boss.x, self.boss.y)) < proj.radius + self.boss.radius:
                        source = "base_shot"
                        if proj.owner.startswith("player:"):
                            source = proj.owner.split(":", 1)[1]
                        self.damage_boss(proj.damage, source=source)
                        if not self.try_ricochet_projectile(proj, self.boss):
                            self.projectiles.remove(proj)
            elif proj.owner.startswith("ally:"):
                ally_source = proj.owner.split(":", 1)[1]
                for enemy in list(self.enemies):
                    if enemy.is_ally:
                        continue
                    if distance((proj.x, proj.y), (enemy.x, enemy.y)) < proj.radius + enemy.radius:
                        self.damage_enemy(enemy, proj.damage, source=ally_source)
                        if proj in self.projectiles:
                            self.projectiles.remove(proj)
                        break
                if proj in self.projectiles and self.boss is not None:
                    if distance((proj.x, proj.y), (self.boss.x, self.boss.y)) < proj.radius + self.boss.radius:
                        self.damage_boss(proj.damage, source=ally_source)
                        self.projectiles.remove(proj)
            else:
                ally_hit = None
                for ally in self.enemies:
                    if not ally.is_ally or ally.hp <= 0:
                        continue
                    if distance((proj.x, proj.y), (ally.x, ally.y)) < proj.radius + ally.radius:
                        ally_hit = ally
                        break
                if ally_hit is not None:
                    self.damage_ally(ally_hit, max(8, proj.damage))
                    if proj in self.projectiles:
                        self.projectiles.remove(proj)
                elif distance((proj.x, proj.y), (self.player.x, self.player.y)) < proj.radius + self.player.radius:
                    self.damage_player(max(8, proj.damage), source="enemy_projectile")
                    if proj in self.projectiles:
                        self.projectiles.remove(proj)

        for enemy in list(self.enemies):
            if enemy.is_ally:
                continue
            target_entity, target_is_player = self.get_nearest_target_for_hostile(enemy)
            contact_damage = max(7, int(self.player.max_hp * 0.075))
            if target_is_player:
                if distance((enemy.x, enemy.y), (self.player.x, self.player.y)) < enemy.radius + self.player.radius:
                    self.damage_player(contact_damage, source="enemy_contact")
            else:
                if distance((enemy.x, enemy.y), (target_entity.x, target_entity.y)) < enemy.radius + target_entity.radius:
                    self.damage_ally(target_entity, contact_damage)

        if self.boss is not None:
            if distance((self.boss.x, self.boss.y), (self.player.x, self.player.y)) < self.boss.radius + self.player.radius:
                self.damage_player(self.boss_contact_damage(), source="boss_contact")

        for ally in self.enemies:
            if not ally.is_ally or ally.ally_hit_cd > 0:
                continue
            for enemy in self.enemies:
                if enemy is ally or enemy.is_ally:
                    continue
                if distance((ally.x, ally.y), (enemy.x, enemy.y)) < ally.radius + enemy.radius:
                    self.damage_enemy(enemy, self.biochemist_contact_damage(ally), source=ally.ally_source)
                    ally.ally_hit_cd = 0.45
                    break
            if ally.ally_hit_cd <= 0 and self.boss is not None:
                if distance((ally.x, ally.y), (self.boss.x, self.boss.y)) < ally.radius + self.boss.radius:
                    self.damage_boss(self.biochemist_contact_damage(ally) * 0.8, source=ally.ally_source)
                    ally.ally_hit_cd = 0.45

        for orb in self.player.fire_orbiters:
            for enemy in self.enemies:
                if enemy.is_ally:
                    continue
                if distance((orb.x, orb.y), (enemy.x, enemy.y)) < orb.size + enemy.radius:
                    if enemy.fire_orb_hit_cd <= 0:
                        orb_impact_damage = self.fire_orb_impact_damage_value()
                        self.damage_enemy(enemy, orb_impact_damage, source="fire_orb_impact")
                        enemy.fire_orb_hit_cd = 0.35
                    enemy.burn_timer = max(enemy.burn_timer, 3.0)
                    orb_burn_dps = self.fire_orb_burn_enemy_dps_value(enemy)
                    if orb_burn_dps >= enemy.burn_dps:
                        enemy.burn_source = "fire_orb_burn"
                    enemy.burn_dps = max(enemy.burn_dps, orb_burn_dps)
            if self.boss is not None:
                if distance((orb.x, orb.y), (self.boss.x, self.boss.y)) < orb.size + self.boss.radius:
                    if self.boss.fire_orb_hit_cd <= 0:
                        orb_impact_damage = self.fire_orb_impact_damage_value()
                        self.damage_boss(orb_impact_damage, source="fire_orb_impact")
                        self.boss.fire_orb_hit_cd = 0.35
                    self.boss.burn_timer = max(self.boss.burn_timer, 3.0)
                    orb_burn_dps = self.fire_orb_burn_boss_dps_value()
                    if orb_burn_dps >= self.boss.burn_dps:
                        self.boss.burn_source = "fire_orb_burn"
                    self.boss.burn_dps = max(self.boss.burn_dps, orb_burn_dps)

        if self.player.fire_ring:
            ring_radius = self.player.fire_ring_radius
            ring_thickness = 10
            for enemy in self.enemies:
                if enemy.is_ally:
                    continue
                dist = distance((enemy.x, enemy.y), (self.player.x, self.player.y))
                if ring_radius - ring_thickness <= dist <= ring_radius + ring_thickness:
                    enemy.burn_timer = max(enemy.burn_timer, 4.0)
                    ring_burn = self.fire_ring_burn_dps_value()
                    if ring_burn >= enemy.burn_dps:
                        enemy.burn_source = "fire_ring_burn"
                    enemy.burn_dps = max(enemy.burn_dps, ring_burn)
            if self.boss is not None:
                dist = distance((self.boss.x, self.boss.y), (self.player.x, self.player.y))
                if ring_radius - ring_thickness <= dist <= ring_radius + ring_thickness:
                    self.boss.burn_timer = max(self.boss.burn_timer, 4.0)
                    ring_burn = self.fire_ring_burn_dps_value()
                    if ring_burn >= self.boss.burn_dps:
                        self.boss.burn_source = "fire_ring_burn"
                    self.boss.burn_dps = max(self.boss.burn_dps, ring_burn)

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
        candidates = [enemy for enemy in self.enemies if not enemy.is_ally and enemy.hp > 0]
        if self.boss is not None:
            candidates.append(self.boss)
        if not candidates:
            return None
        return min(candidates, key=lambda e: (e.x - px) ** 2 + (e.y - py) ** 2)

    def blade_skill_target_pos(self):
        if self.boss is not None and self.boss.hp > 0:
            return self.boss.x, self.boss.y

        hostiles = [enemy for enemy in self.enemies if not enemy.is_ally and enemy.hp > 0]
        if not hostiles:
            return pygame.mouse.get_pos()

        cluster_r2 = self.blade_skill_cluster_radius() ** 2
        px, py = self.player.x, self.player.y
        best_target = hostiles[0]
        best_count = -1
        best_dist2 = float("inf")
        for anchor in hostiles:
            count = 0
            for enemy in hostiles:
                dx = enemy.x - anchor.x
                dy = enemy.y - anchor.y
                if dx * dx + dy * dy <= cluster_r2:
                    count += 1
            dist2 = (anchor.x - px) ** 2 + (anchor.y - py) ** 2
            if count > best_count or (count == best_count and dist2 < best_dist2):
                best_count = count
                best_dist2 = dist2
                best_target = anchor
        return best_target.x, best_target.y

    def get_nearest_hostile_for_ally(self, ally):
        candidates = [enemy for enemy in self.enemies if enemy is not ally and not enemy.is_ally and enemy.hp > 0]
        if self.boss is not None and self.boss.hp > 0:
            candidates.append(self.boss)
        if not candidates:
            return None
        return min(candidates, key=lambda e: (e.x - ally.x) ** 2 + (e.y - ally.y) ** 2)

    def get_nearest_target_for_hostile(self, hostile):
        nearest_is_player = True
        nearest_target = self.player
        nearest_d2 = (self.player.x - hostile.x) ** 2 + (self.player.y - hostile.y) ** 2
        for ally in self.enemies:
            if ally is hostile or not ally.is_ally or ally.hp <= 0:
                continue
            d2 = (ally.x - hostile.x) ** 2 + (ally.y - hostile.y) ** 2
            if d2 < nearest_d2:
                nearest_d2 = d2
                nearest_is_player = False
                nearest_target = ally
        return nearest_target, nearest_is_player

    def spawn_biochemist_ally(self, kind=None, source="bio_minions", duration=None):
        if kind is None:
            kind = random.choice(["basic", "fast", "tank", "shooter"])
        angle = random.uniform(0.0, math.tau)
        radius = random.uniform(70.0, 130.0)
        x = clamp(self.player.x + math.cos(angle) * radius, 40, WIDTH - 40)
        y = clamp(self.player.y + math.sin(angle) * radius, 40, HEIGHT - 40)
        ally = Enemy(x, y, kind, self.wave)
        ally.set_ally(
            duration,
            source=source,
            power=self.biochemist_ally_power(),
        )
        self.enemies.append(ally)
        return ally

    def spawn_bee_hive(self, x=None, y=None, source="bee_swarm", move_existing=False):
        if x is None or y is None:
            x, y = self.player.x, self.player.y
        spawn_interval = self.bee_hive_spawn_interval()
        if source == "ultimate_queen_hive":
            spawn_interval *= 0.5
        if move_existing and self.bee_hives:
            hive = self.bee_hives[0]
            hive.x = x
            hive.y = y
            hive.duration = self.bee_hive_duration()
            hive.time_left = hive.duration
            hive.spawn_interval = spawn_interval
            hive.spawn_timer = 0.0
            hive.source = source
            return hive
        hive = BeeHive(
            x,
            y,
            duration=self.bee_hive_duration(),
            spawn_interval=spawn_interval,
            source=source,
        )
        self.bee_hives.append(hive)
        return hive

    def spawn_hive_bee(self, x, y, source="bee_swarm", target=None):
        ang = random.uniform(0.0, math.tau)
        r = random.uniform(8.0, 26.0)
        bx = clamp(x + math.cos(ang) * r, 30, WIDTH - 30)
        by = clamp(y + math.sin(ang) * r, 30, HEIGHT - 30)
        bee = BeeMinion(
            bx,
            by,
            speed=self.bee_swarm_speed(),
            damage=self.bee_swarm_damage(),
            lifetime=self.bee_swarm_lifetime(),
            source=source,
            target=target,
        )
        self.bee_minions.append(bee)
        return bee

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
            rocket_radius = 24 if self.player.rocket_frag else 12
            rocket = Rocket(
                self.player.x,
                self.player.y,
                vx * 320,
                vy * 320,
                damage=self.rocket_damage_value(),
                target=target,
                get_target=self.get_nearest_enemy,
                explosion_radius=70,
                radius=rocket_radius,
            )
            self.rockets.append(rocket)

    def spawn_rocket_fragments(self, x, y, base_damage):
        count = self.rocket_fragment_count()
        if count <= 0:
            return
        angle0 = random.uniform(0.0, math.tau)
        ratio = self.rocket_fragment_damage_ratio()
        base_speed = self.rocket_fragment_speed()
        for i in range(count):
            ang = angle0 + i * (math.tau / count) + random.uniform(-0.08, 0.08)
            speed = base_speed * random.uniform(0.9, 1.1)
            proj = Projectile(
                x,
                y,
                math.cos(ang) * speed,
                math.sin(ang) * speed,
                damage=base_damage * ratio,
                color=(255, 195, 120),
                radius=5,
                owner="player:rocket_fragments",
                ricochet_bounces=self.player.projectile_bounces(),
            )
            self.projectiles.append(proj)

    def find_ricochet_target(self, proj):
        max_range = self.ricochet_range_value()
        max_range2 = max_range * max_range
        candidates = [enemy for enemy in self.enemies if (not enemy.is_ally) and enemy.hp > 0]
        if self.boss is not None and self.boss.hp > 0:
            candidates.append(self.boss)
        if not candidates:
            return None
        next_target = None
        next_d2 = None
        for target in candidates:
            if id(target) in proj.hit_targets:
                continue
            d2 = (target.x - proj.x) ** 2 + (target.y - proj.y) ** 2
            if d2 > max_range2:
                continue
            if next_d2 is None or d2 < next_d2:
                next_d2 = d2
                next_target = target
        return next_target

    def try_ricochet_projectile(self, proj, hit_target):
        if not proj.owner.startswith("player"):
            return False
        if proj.ricochet_bounces <= 0:
            return False
        proj.hit_targets.add(id(hit_target))
        new_target = self.find_ricochet_target(proj)
        if new_target is None:
            return False
        dx = new_target.x - proj.x
        dy = new_target.y - proj.y
        dist = math.hypot(dx, dy) or 1.0
        speed = max(220.0, math.hypot(proj.vx, proj.vy))
        proj.vx = dx / dist * speed
        proj.vy = dy / dist * speed
        proj.damage *= self.ricochet_damage_decay()
        proj.ricochet_bounces -= 1
        return True

    def update(self, dt):
        self.combat_time += dt
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
        pad_input = self.get_gamepad_input()
        self.player.update(dt, keys, move_input=pad_input["move"])
        if self.player.ultimate_charge < self.player.ultimate_max:
            regen_rate = self.player.ultimate_max / max(1.0, self.player.ultimate_regen_time)
            self.player.ultimate_charge = min(
                self.player.ultimate_max,
                self.player.ultimate_charge + regen_rate * dt,
            )
        if self.state == "playing" and self.wave_spawn_remaining > 0:
            self.wave_spawn_timer -= dt
            while self.wave_spawn_remaining > 0 and self.wave_spawn_timer <= 0:
                self.spawn_random_wave_enemy(self.wave)
                self.wave_spawn_remaining -= 1
                self.wave_spawn_timer += self.wave_spawn_interval
        if self.state == "playing" and self.boss is not None and self.boss.hp > 0:
            self.boss_spawn_timer -= dt
            while self.boss_spawn_timer <= 0:
                self.spawn_random_wave_enemy(self.wave)
                self.boss_spawn_timer += self.boss_spawn_interval
        if self.player.rocket_count > 0:
            self.player.rocket_timer += dt
            while self.player.rocket_timer >= self.player.rocket_cooldown:
                self.player.rocket_timer -= self.player.rocket_cooldown
                self.fire_rockets()
        
        if self.player.shockwave_charging:
            self.player.shockwave_charge_time += dt
            if self.player.shockwave_charge_time >= 0.5:
                self.fire_spatial_laser()
                self.player.shockwave_charging = False
                self.player.shockwave_charge_time = 0.0
        
        cooldown = self.shockwave_cooldown_value()
        if self.player.shockwave_timer < cooldown:
            self.player.shockwave_timer = min(
                cooldown, self.player.shockwave_timer + dt
            )
        manual_fire = pygame.mouse.get_pressed(num_buttons=3)[0] or keys[pygame.K_SPACE]
        target_pos = pygame.mouse.get_pos()
        if pad_input["aim_active"]:
            ax, ay = pad_input["aim"]
            target_pos = (self.player.x + ax * 1200, self.player.y + ay * 1200)
            manual_fire = False
        elif not manual_fire:
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
                candidates = [enemy for enemy in self.enemies if not enemy.is_ally and enemy.hp > 0]
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
                    laser_orb_damage = self.laser_orb_damage_value()
                    for enemy in list(self.enemies):
                        if enemy.is_ally:
                            continue
                        dist = point_segment_distance(enemy.x, enemy.y, sx, sy, ex, ey)
                        if dist <= enemy.radius + beam_width:
                            self.damage_enemy(enemy, laser_orb_damage, source="laser_orb")
                    if self.boss is not None:
                        dist = point_segment_distance(self.boss.x, self.boss.y, sx, sy, ex, ey)
                        if dist <= self.boss.radius + beam_width:
                            self.damage_boss(laser_orb_damage, source="laser_orb")
        if self.player.electroelf_level > 0:
            if self.player.electroelf is None:
                self.player.electroelf = ElectroElf()
            targets = [enemy for enemy in self.enemies if not enemy.is_ally and enemy.hp > 0]
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
                        damage=self.electroelf_damage_value(),
                        target=target,
                        charge_time=0.45,
                        duration=0.28,
                    )
                    self.lightning_effects.append(strike)
        if self.base_fire_enabled:
            if manual_fire:
                self.player.fire(pygame.mouse.get_pos(), self.projectiles)
            else:
                if self.get_nearest_enemy():
                    self.player.fire(target_pos, self.projectiles)

        for enemy in self.enemies:
            hp_before = enemy.hp
            move_target = (self.player.x, self.player.y)
            ally_target = None
            if enemy.is_ally:
                target = self.get_nearest_hostile_for_ally(enemy)
                if target is not None:
                    ally_target = (target.x, target.y)
                else:
                    ally_target = (self.player.x, self.player.y)
            else:
                nearest_target, _ = self.get_nearest_target_for_hostile(enemy)
                move_target = (nearest_target.x, nearest_target.y)
            enemy.update(dt, move_target, self.projectiles, self.wave, ally_target_pos=ally_target)
            burn_damage = max(0.0, hp_before - enemy.hp)
            if burn_damage > 0:
                self.record_damage_stat(getattr(enemy, "burn_source", "fire_orb_burn"), burn_damage)
            if enemy.is_ally and enemy.kind == "tank" and enemy.beam_active > 0:
                for hostile in self.enemies:
                    if hostile is enemy or hostile.is_ally:
                        continue
                    if enemy.beam_hits_entity((hostile.x, hostile.y), hostile.radius):
                        self.damage_enemy(hostile, (22 + self.wave * 0.4) * enemy.ally_power, source=enemy.ally_source)
                if self.boss is not None and enemy.beam_hits_entity((self.boss.x, self.boss.y), self.boss.radius):
                    self.damage_boss((22 + self.wave * 0.4) * enemy.ally_power, source=enemy.ally_source)
            if (not enemy.is_ally) and enemy.kind == "tank" and enemy.beam_active > 0:
                beam_damage = 22 + self.wave * 0.4
                if enemy.beam_hits_player((self.player.x, self.player.y)):
                    self.damage_player(beam_damage, source="tank_beam")
                for ally in list(self.enemies):
                    if ally is enemy or not ally.is_ally or ally.hp <= 0:
                        continue
                    if enemy.beam_hits_entity((ally.x, ally.y), ally.radius):
                        self.damage_ally(ally, beam_damage)

        for enemy in list(self.enemies):
            if enemy.hp <= 0:
                self.enemies.remove(enemy)
                self.on_enemy_killed(enemy)

        if self.boss is not None:
            boss_hp_before = self.boss.hp
            self.boss.update(
                dt,
                (self.player.x, self.player.y),
                self.projectiles,
                self.boss_zones,
                self.wave,
                self.boss_projectile_damage(),
                self.boss_zone_damage(),
            )
            boss_burn_damage = max(0.0, boss_hp_before - self.boss.hp)
            if boss_burn_damage > 0:
                self.record_damage_stat(getattr(self.boss, "burn_source", "fire_orb_burn"), boss_burn_damage)
            if self.boss.laser_hits_player((self.player.x, self.player.y)) and self.boss.can_laser_damage():
                self.damage_player(self.boss_laser_damage(), source="boss_laser")
            if self.boss is not None and self.boss.hp <= 0:
                self.on_boss_killed()

        for pickup in list(self.pickups):
            pickup.update(dt, (self.player.x, self.player.y))
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

        for slash in list(self.blade_skill_slashes):
            slash.update(dt)
            for enemy in list(self.enemies):
                if enemy.is_ally or enemy.hp <= 0 or enemy in slash.hit_enemies:
                    continue
                if slash.hits_entity(enemy.x, enemy.y, enemy.radius):
                    slash.hit_enemies.add(enemy)
                    self.damage_enemy(enemy, slash.damage, source="blade_skill")
            if self.boss is not None and self.boss.hp > 0 and not slash.hit_boss:
                if slash.hits_entity(self.boss.x, self.boss.y, self.boss.radius):
                    slash.hit_boss = True
                    self.damage_boss(slash.damage * 0.78, source="blade_skill")
            if slash.expired():
                self.blade_skill_slashes.remove(slash)

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
                if enemy.is_ally:
                    continue
                if distance((rocket.x, rocket.y), (enemy.x, enemy.y)) < rocket.radius + enemy.radius:
                    hit = enemy
                    break
            hit_boss = False
            if self.boss is not None:
                if distance((rocket.x, rocket.y), (self.boss.x, self.boss.y)) < rocket.radius + self.boss.radius:
                    hit_boss = True
            if hit or hit_boss:
                for enemy in list(self.enemies):
                    if enemy.is_ally:
                        continue
                    if distance((rocket.x, rocket.y), (enemy.x, enemy.y)) <= rocket.explosion_radius:
                        self.damage_enemy(enemy, rocket.damage, source="rockets")
                if self.boss is not None:
                    if distance((rocket.x, rocket.y), (self.boss.x, self.boss.y)) <= rocket.explosion_radius:
                        self.damage_boss(rocket.damage, source="rockets")
                self.explosions.append(
                    Explosion(rocket.x, rocket.y, rocket.explosion_radius, duration=0.25)
                )
                if self.player.rocket_frag:
                    self.spawn_rocket_fragments(rocket.x, rocket.y, rocket.damage)
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

        for laser in list(self.spatial_lasers):
            laser.update(dt)
            if laser.time_left <= 0:
                self.spatial_lasers.remove(laser)

        for pulse in list(self.ultimate_pulses):
            pulse.update(dt)
            if pulse.time_left <= 0:
                self.ultimate_pulses.remove(pulse)

        for hive in list(self.bee_hives):
            hive.update(dt)
            spawn_count = hive.consume_spawn_count()
            for _ in range(spawn_count):
                self.spawn_hive_bee(hive.x, hive.y, source=hive.source)
            if hive.time_left <= 0:
                self.bee_hives.remove(hive)

        for bee in list(self.bee_minions):
            targets = [enemy for enemy in self.enemies if not enemy.is_ally and enemy.hp > 0]
            if self.boss is not None:
                targets.append(self.boss)
            bee.update(dt, targets)
            hit = False
            for enemy in list(self.enemies):
                if enemy.is_ally:
                    continue
                if distance((bee.x, bee.y), (enemy.x, enemy.y)) <= bee.radius + enemy.radius:
                    self.damage_enemy(enemy, self.bee_contact_damage(enemy), source=bee.source)
                    hit = True
                    break
            if not hit and self.boss is not None:
                if distance((bee.x, bee.y), (self.boss.x, self.boss.y)) <= bee.radius + self.boss.radius:
                    self.damage_boss(self.bee_boss_contact_damage() * 0.1, source=bee.source)
                    hit = True
            if hit:
                self.spawn_pulse(
                    bee.x,
                    bee.y,
                    color=(255, 210, 90),
                    start_radius=4,
                    end_radius=16,
                    duration=0.1,
                    width=2,
                    fill_alpha=26,
                )
                self.bee_minions.remove(bee)
                continue
            if bee.time_left <= 0 or bee.offscreen():
                self.bee_minions.remove(bee)

        for zone in list(self.ultimate_zones):
            zone.update(dt)
            if zone.should_tick():
                damage = self.player.damage * 0.6
                for enemy in list(self.enemies):
                    if enemy.is_ally:
                        continue
                    if distance((enemy.x, enemy.y), (zone.x, zone.y)) <= zone.radius:
                        self.damage_enemy(enemy, damage, source="ultimate_zone")
                if self.boss is not None:
                    if distance((self.boss.x, self.boss.y), (zone.x, zone.y)) <= zone.radius:
                        self.damage_boss(damage, source="ultimate_zone")
            if zone.time_left <= 0:
                self.ultimate_zones.remove(zone)

        for constellation in list(self.ultimate_constellations):
            constellation_targets = [enemy for enemy in self.enemies if not enemy.is_ally and enemy.hp > 0]
            if self.boss is not None:
                constellation_targets.append(self.boss)
            constellation.update(dt, constellation_targets)
            if constellation.should_tick():
                tick_damage = (
                    self.player.damage
                    * 0.35
                    * self.ultimate_cadence_multiplier()
                    * self.ultimate_damage_scale(0.16, cap=5.8)
                )
                beam_hit_radius = constellation.beam_width * (
                    0.5 + min(0.26, self.ultimate_boss_level() * 0.02)
                )
                hit_enemies = set()
                boss_hit = False
                for (sx, sy), (ex, ey) in constellation.segments():
                    for enemy in self.enemies:
                        if enemy.is_ally:
                            continue
                        if enemy in hit_enemies:
                            continue
                        dist = point_segment_distance(enemy.x, enemy.y, sx, sy, ex, ey)
                        if dist <= enemy.radius + beam_hit_radius:
                            hit_enemies.add(enemy)
                    if self.boss is not None and not boss_hit:
                        dist = point_segment_distance(self.boss.x, self.boss.y, sx, sy, ex, ey)
                        if dist <= self.boss.radius + beam_hit_radius:
                            boss_hit = True

                for enemy in list(hit_enemies):
                    self.damage_enemy(enemy, tick_damage, source="ultimate_constellation")
                if boss_hit:
                    self.damage_boss(tick_damage * 0.85, source="ultimate_constellation")

            if constellation.time_left <= 0:
                cx, cy = constellation.center()
                self.ultimate_pulses.append(UltimatePulse(cx, cy, 180, duration=0.28))
                self.ultimate_constellations.remove(constellation)

        for singularity in list(self.ultimate_singularities):
            singularity.update(dt, (self.player.x, self.player.y))
            if singularity.finished:
                self.ultimate_singularities.remove(singularity)
                continue
            if singularity.exiting:
                continue

            for enemy in self.enemies:
                if enemy.is_ally:
                    continue
                singularity.pull_entity(enemy, dt, weight=1.0)
            if self.boss is not None:
                singularity.pull_entity(self.boss, dt, weight=0.25)

            if singularity.should_tick():
                tick_damage = (
                    self.player.damage * 0.55 + self.wave * 1.8
                ) * self.ultimate_damage_scale(0.16, cap=5.5)
                center_bonus = 1.35 + min(0.5, self.ultimate_boss_level() * 0.02)
                for enemy in list(self.enemies):
                    if enemy.is_ally:
                        continue
                    d = distance((enemy.x, enemy.y), (singularity.x, singularity.y))
                    if d <= singularity.radius:
                        damage = tick_damage * (center_bonus if d <= singularity.core_radius * 2 else 1.0)
                        self.damage_enemy(enemy, damage, source="ultimate_singularity")
                if self.boss is not None:
                    d = distance((self.boss.x, self.boss.y), (singularity.x, singularity.y))
                    if d <= singularity.radius:
                        damage = tick_damage * 0.8
                        if d <= singularity.core_radius * 2:
                            damage *= center_bonus
                        self.damage_boss(damage, source="ultimate_singularity")


        for blade in list(self.ultimate_prismatic_blades):
            blade.update(dt, (self.player.x, self.player.y))
            if blade.should_tick():
                touch_damage = self.player_projectile_damage_value() * (
                    4.0 + min(10.0, self.ultimate_boss_level() * 0.9)
                )
                hit_radius = blade.beam_width * (1.35 + min(0.55, self.ultimate_boss_level() * 0.02)) + 18.0
                hit_enemies = set()
                boss_hit = False
                for (sx, sy), (ex, ey) in blade.segments():
                    for enemy in self.enemies:
                        if enemy.is_ally:
                            continue
                        if enemy in hit_enemies:
                            continue
                        dist = point_segment_distance(enemy.x, enemy.y, sx, sy, ex, ey)
                        if dist <= enemy.radius + hit_radius:
                            hit_enemies.add(enemy)
                    if self.boss is not None and not boss_hit:
                        dist = point_segment_distance(self.boss.x, self.boss.y, sx, sy, ex, ey)
                        if dist <= self.boss.radius + hit_radius:
                            boss_hit = True
                for enemy in list(hit_enemies):
                    self.damage_enemy(enemy, touch_damage, source="ultimate_prismatic_blade")
                if boss_hit:
                    self.damage_boss(touch_damage, source="ultimate_prismatic_blade")
            if blade.time_left <= 0:
                self.ultimate_pulses.append(UltimatePulse(blade.x, blade.y, 180, duration=0.24))
                self.ultimate_prismatic_blades.remove(blade)

        for overdrive in list(self.ultimate_vector_overdrives):
            overdrive.update(dt, (self.player.x, self.player.y))
            if overdrive.should_tick():
                targets = [enemy for enemy in self.enemies if not enemy.is_ally and enemy.hp > 0]
                if self.boss is not None:
                    targets.append(self.boss)
                targets.sort(key=lambda e: (e.x - self.player.x) ** 2 + (e.y - self.player.y) ** 2)
                chained = []
                for target in targets:
                    if len(chained) >= overdrive.max_targets:
                        break
                    if distance((target.x, target.y), (self.player.x, self.player.y)) <= self.vector_overdrive_range():
                        chained.append(target)
                if chained:
                    chain_points = [(self.player.x, self.player.y)]
                    base_damage = (
                        self.player.damage * 0.8 + self.wave * 0.8
                    ) * self.ultimate_damage_scale(0.13, cap=4.8)
                    chain_decay = min(0.97, 0.88 + self.ultimate_boss_level() * 0.006)
                    for i, target in enumerate(chained):
                        chain_points.append((target.x, target.y))
                        dmg = base_damage * (chain_decay ** i)
                        if self.boss is not None and target is self.boss:
                            self.damage_boss(dmg * 0.75, source="ultimate_vector_overdrive")
                        else:
                            self.damage_enemy(target, dmg, source="ultimate_vector_overdrive")
                    overdrive.set_chain(chain_points)
            if overdrive.time_left <= 0:
                self.player.vector_overdrive_time = 0.0
                self.ultimate_pulses.append(UltimatePulse(self.player.x, self.player.y, 150, duration=0.24))
                self.ultimate_vector_overdrives.remove(overdrive)

        for swarm in list(self.ultimate_spectral_swarms):
            swarm.update(dt, (self.player.x, self.player.y))
            spawn_count = swarm.consume_spawn_count()
            for _ in range(spawn_count):
                ex, ey = swarm.emit_point()
                angle = random.uniform(0.0, math.tau)
                speed_bonus = self.spectral_swarm_shard_speed_bonus()
                speed = random.uniform(420.0 + speed_bonus, 540.0 + speed_bonus)
                damage = (
                    self.player.damage * 1.22 + self.wave * 0.35
                ) * self.ultimate_damage_scale(0.14, cap=5.0)
                shard = UltimateSpectralShard(
                    ex,
                    ey,
                    angle,
                    speed,
                    damage,
                    lifetime=self.spectral_swarm_shard_lifetime(),
                )
                shard.turn_rate = min(12.0, shard.turn_rate + self.ultimate_boss_level() * 0.25)
                self.ultimate_spectral_shards.append(shard)
            if swarm.time_left <= 0:
                self.ultimate_pulses.append(UltimatePulse(self.player.x, self.player.y, 140, duration=0.22))
                self.ultimate_spectral_swarms.remove(swarm)

        for shard in list(self.ultimate_spectral_shards):
            targets = [enemy for enemy in self.enemies if not enemy.is_ally and enemy.hp > 0]
            if self.boss is not None:
                targets.append(self.boss)
            shard.update(dt, targets)
            hit = False
            for enemy in list(self.enemies):
                if enemy.is_ally:
                    continue
                if distance((shard.x, shard.y), (enemy.x, enemy.y)) <= shard.radius + enemy.radius:
                    self.damage_enemy(enemy, shard.damage, source="ultimate_spectral_swarm")
                    hit = True
                    break
            if not hit and self.boss is not None:
                if distance((shard.x, shard.y), (self.boss.x, self.boss.y)) <= shard.radius + self.boss.radius:
                    self.damage_boss(shard.damage * 0.78, source="ultimate_spectral_swarm")
                    hit = True
            if hit:
                self.spawn_pulse(
                    shard.x,
                    shard.y,
                    color=(195, 160, 255),
                    start_radius=8,
                    end_radius=26,
                    duration=0.11,
                    width=2,
                    fill_alpha=22,
                )
                self.ultimate_spectral_shards.remove(shard)
                continue
            if shard.time_left <= 0 or shard.offscreen():
                self.ultimate_spectral_shards.remove(shard)

        for prism in list(self.ultimate_queen_hives):
            candidates = [enemy for enemy in self.enemies if not enemy.is_ally and enemy.hp > 0]
            if self.boss is not None:
                candidates.append(self.boss)
            prism.update(dt, candidates)
            if prism.should_tick():
                if candidates:
                    candidates.sort(key=lambda e: (e.x - prism.x) ** 2 + (e.y - prism.y) ** 2)
                    first = candidates[0]
                    if distance((first.x, first.y), (prism.x, prism.y)) <= prism.range_radius:
                        chain = [first]
                        visited = {first}
                        while len(chain) < prism.max_targets:
                            current = chain[-1]
                            next_target = None
                            next_dist = None
                            for candidate in candidates:
                                if candidate in visited or candidate.hp <= 0:
                                    continue
                                d = distance((candidate.x, candidate.y), (current.x, current.y))
                                if d <= prism.jump_range and (next_dist is None or d < next_dist):
                                    next_dist = d
                                    next_target = candidate
                            if next_target is None:
                                break
                            chain.append(next_target)
                            visited.add(next_target)

                        points = [(prism.x, prism.y)]
                        base_damage = (
                            self.player.damage * 1.45 + self.wave * 0.9
                        ) * self.ultimate_damage_scale(0.14, cap=5.2)
                        chain_decay = min(0.95, 0.84 + self.ultimate_boss_level() * 0.005)
                        for i, target in enumerate(chain):
                            points.append((target.x, target.y))
                            dmg = base_damage * (chain_decay ** i)
                            if self.boss is not None and target is self.boss:
                                self.damage_boss(dmg * 0.76, source="ultimate_queen_hive")
                            else:
                                self.damage_enemy(target, dmg, source="ultimate_queen_hive")
                        prism.set_chain(points)

            if prism.time_left <= 0:
                self.ultimate_pulses.append(UltimatePulse(prism.x, prism.y, 180, duration=0.26))
                self.ultimate_queen_hives.remove(prism)

        for zone in list(self.boss_zones):
            zone.update(dt)
            if zone.should_damage:
                zone.should_damage = False
                if distance((zone.x, zone.y), (self.player.x, self.player.y)) <= zone.radius + self.player.radius:
                    self.damage_player(zone.damage, source="boss_zone")
            if zone.time_left <= 0:
                self.boss_zones.remove(zone)

        for strike in list(self.lightning_effects):
            strike.update(dt)
            if strike.should_damage:
                strike.should_damage = False
                for enemy in list(self.enemies):
                    if enemy.is_ally:
                        continue
                    if distance((enemy.x, enemy.y), (strike.ex, strike.ey)) <= strike.radius:
                        self.damage_enemy(enemy, strike.damage, source="electroelf")
                if self.boss is not None:
                    if distance((self.boss.x, self.boss.y), (strike.ex, strike.ey)) <= strike.radius:
                        self.damage_boss(strike.damage, source="electroelf")
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

        if (
            self.state == "playing"
            and not any((not enemy.is_ally) and enemy.hp > 0 for enemy in self.enemies)
            and self.boss is None
            and self.wave_spawn_remaining <= 0
        ):
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
        accent = (110, 220, 255)
        panel_bg = (9, 16, 28, 224)
        panel_border = (70, 155, 220, 220)
        panel_inner = (160, 238, 255, 145)
        text_main = (225, 242, 255)
        text_soft = (180, 214, 238)
        bar_back = (12, 22, 38)

        def draw_panel(rect, accent_lines=True):
            glow = pygame.Surface((rect.width + 18, rect.height + 18), pygame.SRCALPHA)
            pygame.draw.rect(glow, (*accent, 30), glow.get_rect(), 8, border_radius=14)
            pygame.draw.rect(glow, (*accent, 18), glow.get_rect().inflate(-6, -6), 5, border_radius=12)
            self.screen.blit(glow, (rect.x - 9, rect.y - 9))

            panel = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            pygame.draw.rect(panel, panel_bg, panel.get_rect(), border_radius=10)
            pygame.draw.rect(panel, panel_border, panel.get_rect(), 2, border_radius=10)
            if accent_lines:
                inner = panel.get_rect().inflate(-8, -8)
                pygame.draw.rect(panel, panel_inner, inner, 1, border_radius=8)
            self.screen.blit(panel, rect.topleft)

        def draw_bar(x, y, w, h, ratio, fill, back=None):
            ratio = clamp(ratio, 0.0, 1.0)
            bg = bar_back if back is None else back
            pygame.draw.rect(self.screen, bg, (x, y, w, h), border_radius=5)
            if ratio > 0:
                fill_w = max(2, int(w * ratio))
                pygame.draw.rect(self.screen, fill, (x, y, fill_w, h), border_radius=5)
                shine = pygame.Surface((fill_w, h), pygame.SRCALPHA)
                pygame.draw.rect(shine, (255, 255, 255, 44), shine.get_rect(), border_radius=5)
                self.screen.blit(shine, (x, y))
            pygame.draw.rect(self.screen, (80, 150, 215), (x, y, w, h), 1, border_radius=5)

        def draw_white_text(text, x, y):
            shadow = self.font.render(text, True, (10, 14, 24))
            label = self.font.render(text, True, WHITE)
            self.screen.blit(shadow, (x + 1, y + 1))
            self.screen.blit(label, (x, y))

        def draw_tag(text, center_x, y, color=(120, 220, 255), ready=False):
            ticks = pygame.time.get_ticks() * 0.001
            pulse = 0.5 + 0.5 * math.sin(ticks * 7.4)
            label = self.font.render(text, True, (232, 247, 255))
            pad_x = 11
            pad_y = 3
            rect = pygame.Rect(0, 0, label.get_width() + pad_x * 2, label.get_height() + pad_y * 2)
            rect.centerx = int(center_x)
            rect.y = int(y)

            glow = pygame.Surface((rect.width + 20, rect.height + 16), pygame.SRCALPHA)
            glow_alpha = 24 + int(18 * pulse)
            if ready:
                glow_alpha += 28
            pygame.draw.rect(
                glow,
                (color[0], color[1], color[2], glow_alpha),
                glow.get_rect(),
                border_radius=12,
            )
            pygame.draw.rect(
                glow,
                (color[0], color[1], color[2], max(8, glow_alpha // 2)),
                glow.get_rect().inflate(-6, -4),
                border_radius=10,
            )
            self.screen.blit(glow, (rect.x - 10, rect.y - 8))

            body = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            body_color = (8, 14, 26, 230) if not ready else (10, 18, 30, 240)
            border_alpha = 170 if not ready else 220
            pygame.draw.rect(body, body_color, body.get_rect(), border_radius=10)
            pygame.draw.rect(
                body,
                (color[0], color[1], color[2], border_alpha),
                body.get_rect(),
                2,
                border_radius=10,
            )
            highlight = pygame.Rect(3, 2, body.get_width() - 6, max(3, body.get_height() // 3))
            pygame.draw.rect(body, (255, 255, 255, 28), highlight, border_radius=8)
            self.screen.blit(body, rect.topleft)

            shadow = self.font.render(text, True, (10, 14, 24))
            self.screen.blit(
                shadow,
                (rect.centerx - shadow.get_width() / 2 + 1, rect.y + pad_y + 1),
            )
            self.screen.blit(label, (rect.centerx - label.get_width() / 2, rect.y + pad_y))

        margin = 16
        top_y = 12

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
        draw_bar(bar_x, hp_y, main_bar_w, 14, hp_ratio, (230, 90, 90), back=(30, 36, 46))
        draw_bar(bar_x, fire_y, main_bar_w, 10, fire_ratio, (240, 210, 90), back=(30, 36, 46))
        pv_to_draw = max(0,int(self.player.hp))
        draw_white_text(f"PV {pv_to_draw}", bar_x + 6, hp_y - 4)

        mini_w = 96
        mini_x = left_rect.right - mini_w - 12
        shield_ratio = clamp(self.player.shield / 6.0, 0, 1)
        rocket_ratio = 0.0
        if self.player.rocket_count > 0:
            rocket_ratio = clamp(self.player.rocket_timer / self.player.rocket_cooldown, 0, 1)
        draw_bar(mini_x, hp_y + 2, mini_w, 10, shield_ratio, PURPLE, back=(30, 36, 46))
        draw_bar(mini_x, fire_y, mini_w, 10, rocket_ratio, (255, 150, 60), back=(30, 36, 46))
        draw_white_text("SHD", mini_x + 4, hp_y - 6)
        draw_white_text("RKT", mini_x + 4, fire_y - 6)

    
        wave_w = 560
        wave_h = 40
        wave_x = WIDTH / 2 - wave_w / 2
        wave_rect = pygame.Rect(wave_x, top_y, wave_w, wave_h)
        draw_panel(wave_rect)
        if self.boss is not None and self.boss.max_hp > 0:
            wave_ratio = clamp(self.boss.hp / self.boss.max_hp, 0, 1)
            wave_label = "BOSS"
            wave_fill = (195, 145, 255)
        elif self.wave_total > 0:
            wave_ratio = clamp(self.wave_killed / self.wave_total, 0, 1)
            wave_label = f"Vague {self.wave}"
            wave_fill = (120, 220, 255)
        else:
            wave_ratio = 0.0
            wave_label = f"Vague {self.wave}"
            wave_fill = (120, 220, 255)
        wave_label_w = 134
        wave_bar_h = 12
        wave_bar_x = wave_rect.x + wave_label_w
        wave_bar_w = wave_rect.right - wave_bar_x - 14
        wave_bar_y = wave_rect.y + (wave_h - wave_bar_h) / 2
        wave_shadow = self.font.render(wave_label, True, (10, 14, 24))
        wave_text = self.font.render(wave_label, True, wave_fill)
        wave_label_y = wave_rect.y + wave_h / 2 - wave_text.get_height() / 2
        self.screen.blit(wave_shadow, (wave_rect.x + 14 + 1, wave_label_y + 1))
        self.screen.blit(wave_text, (wave_rect.x + 14, wave_label_y))
        draw_bar(wave_bar_x, wave_bar_y, wave_bar_w, wave_bar_h, wave_ratio, wave_fill)


        score_w = 210
        score_h = 58
        score_rect = pygame.Rect(WIDTH - score_w - margin, top_y, score_w, score_h)
        draw_panel(score_rect)
        score_kicker = self.font.render("SCORE", True, (120, 220, 255))
        score_kicker_shadow = self.font.render("SCORE", True, (10, 14, 24))
        score_value = self.big_font.render(str(self.score), True, (228, 244, 255))
        score_value_shadow = self.big_font.render(str(self.score), True, (10, 14, 24))
        self.screen.blit(score_kicker_shadow, (score_rect.x + 14 + 1, score_rect.y + 8 + 1))
        self.screen.blit(score_kicker, (score_rect.x + 14, score_rect.y + 8))
        self.screen.blit(
            score_value_shadow,
            (score_rect.right - score_value.get_width() - 14 + 1, score_rect.y + 20 + 1),
        )
        self.screen.blit(
            score_value,
            (score_rect.right - score_value.get_width() - 14, score_rect.y + 20),
        )
        score_line = pygame.Surface((score_rect.width - 28, 2), pygame.SRCALPHA)
        score_line.fill((95, 190, 245, 90))
        self.screen.blit(score_line, (score_rect.x + 14, score_rect.y + 24))

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
                    "color": (120, 230, 255),
                    "fallback": WHITE,
                }
            )
        if self.player.haste > 0:
            buffs.append(
                {
                    "key": "haste",
                    "time": self.player.haste,
                    "max_time": 6.0,
                    "color": (170, 240, 255),
                    "fallback": GREEN,
                }
            )
        if self.player.heal_boost > 0:
            buffs.append(
                {
                    "key": "heal",
                    "time": self.player.heal_boost,
                    "max_time": 5.0,
                    "color": (135, 230, 255),
                    "fallback": GREEN,
                }
            )
        if buffs:
            buffs.sort(key=lambda b: b["time"], reverse=True)
            buff_h = 20 + row_h * len(buffs)
            buff_rect = pygame.Rect(buff_x, buff_y, buff_w, buff_h)
            draw_panel(buff_rect, accent_lines=False)
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
                )
                icon = self.ui_icons.get(buff["key"])
                if icon:
                    self.screen.blit(icon, (buff_rect.x + 6, row_y - 6))
                else:
                    pygame.draw.circle(
                        self.screen, buff["fallback"], (buff_rect.x + 14, row_y + 4), 5
                    )
                row_y += row_h

        xp_w = 360
        xp_h = 34
        xp_rect = pygame.Rect(margin, HEIGHT - xp_h - 14, xp_w, xp_h)
        draw_panel(xp_rect)
        xp_ratio = clamp(self.player.xp / max(1, self.player.next_xp), 0, 1)
        lvl_label = f"Niv : {self.player.level}"
        lvl_shadow = self.font.render(lvl_label, True, (10, 14, 24))
        lvl_text = self.font.render(lvl_label, True, (120, 220, 255))
        lvl_slot_w = max(98, lvl_text.get_width() + 4)
        xp_bar_x = xp_rect.x + 12
        xp_bar_y = xp_rect.y + 12
        xp_bar_w = xp_w - 24 - lvl_slot_w - 10
        draw_bar(xp_bar_x, xp_bar_y, xp_bar_w, 10, xp_ratio, (120, 225, 255))
        lvl_x = xp_bar_x + xp_bar_w + 10
        lvl_y = xp_rect.y + xp_h / 2 - lvl_text.get_height() / 2
        self.screen.blit(lvl_shadow, (lvl_x + 1, lvl_y + 1))
        self.screen.blit(lvl_text, (lvl_x, lvl_y))

        ult_w = 340
        ult_h = 34
        ult_rect = pygame.Rect(WIDTH - ult_w - margin, HEIGHT - ult_h - 14, ult_w, ult_h)
        draw_panel(ult_rect)
        ult_ratio = clamp(self.player.ultimate_charge / max(1, self.player.ultimate_max), 0, 1)
        ult_color = (170, 240, 255) if ult_ratio >= 1 else (95, 145, 175)
        ult_label = "ULT (A)"
        ult_label_x = ult_rect.x + 10
        ult_label_color = (170, 240, 255) if ult_ratio >= 1 else (106, 170, 205)
        ult_label_shadow = self.font.render(ult_label, True, (10, 14, 24))
        ult_label_text = self.font.render(ult_label, True, ult_label_color)
        ult_label_y = ult_rect.y + ult_h / 2 - ult_label_text.get_height() / 2
        self.screen.blit(ult_label_shadow, (ult_label_x + 1, ult_label_y + 1))
        self.screen.blit(ult_label_text, (ult_label_x, ult_label_y))
        ult_label_w = 86
        cd_slot_w = 56
        cd_slot_x = ult_rect.x + ult_label_w
        cd_slot_rect = pygame.Rect(cd_slot_x, ult_rect.y + 6, cd_slot_w, ult_h - 12)
        pygame.draw.rect(self.screen, (12, 22, 38), cd_slot_rect, border_radius=6)
        pygame.draw.rect(self.screen, (70, 150, 210), cd_slot_rect, 1, border_radius=6)
        # Cooldown "reel": temps restant pendant l'effet actif + cooldown post-effet.
        ult_cooldown_left = max(0.0, self.player.ultimate_beam_time + self.player.ultimate_cooldown)
        cd_text = self.font.render(f"{ult_cooldown_left:0.1f}s", True, text_soft)
        self.screen.blit(
            cd_text,
            (
                cd_slot_rect.centerx - cd_text.get_width() / 2,
                cd_slot_rect.centery - cd_text.get_height() / 2,
            ),
        )

        ult_bar_x = cd_slot_rect.right + 8
        ult_bar_w = ult_rect.right - ult_bar_x - 10
        draw_bar(ult_bar_x, ult_rect.y + 12, ult_bar_w, 10, ult_ratio, ult_color)

        shock_w = 240
        shock_h = 28
        shock_rect = pygame.Rect(
            WIDTH - shock_w - margin, ult_rect.y - shock_h - 18, shock_w, shock_h
        )
        draw_panel(shock_rect, accent_lines=False)
        cooldown = self.shockwave_cooldown_value()
        shock_ratio = clamp(
            self.player.shockwave_timer / max(0.01, cooldown), 0, 1
        )
        active_key = self.active_ultimate_key()
        if active_key == "vector_overdrive":
            shock_label = "INVOC (E)"
        elif active_key == "prismatic_blade":
            shock_label = "LAME (E)"
        elif active_key == "spectral_swarm":
            shock_label = "ZONE (E)"
        elif active_key == "queen_hive":
            shock_label = "ESSAIM (E)"
        elif active_key == "constellation_laser":
            shock_label = "LASER (E)"
        else:
            shock_label = "ONDE (E)"
        shock_label_x = shock_rect.x + 10
        shock_label_shadow = self.font.render(shock_label, True, (10, 14, 24))
        shock_label_text = self.font.render(shock_label, True, (120, 220, 255))
        shock_label_y = shock_rect.y + shock_h / 2 - shock_label_text.get_height() / 2
        self.screen.blit(shock_label_shadow, (shock_label_x + 1, shock_label_y + 1))
        self.screen.blit(shock_label_text, (shock_label_x, shock_label_y))
        shock_label_w = shock_label_text.get_width() + 20
        
        if active_key == "constellation_laser" and self.player.shockwave_charging:
            charge_ratio = clamp(self.player.shockwave_charge_time / 0.5, 0.0, 1.0)
            bar_color = (100, 200, 255)
        else:
            charge_ratio = shock_ratio
            bar_color = (120, 220, 255)
        
        draw_bar(
            shock_rect.x + shock_label_w,
            shock_rect.y + 10,
            shock_w - shock_label_w - 10,
            8,
            charge_ratio,
            bar_color,
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
            color = (22, 36, 56) if hovered else (14, 24, 40)
            glow = pygame.Surface((rect.width + 10, rect.height + 10), pygame.SRCALPHA)
            pygame.draw.rect(glow, (115, 225, 255, 36), glow.get_rect(), 4, border_radius=8)
            self.screen.blit(glow, (rect.x - 5, rect.y - 5))
            pygame.draw.rect(self.screen, color, rect, border_radius=6)
            pygame.draw.rect(self.screen, (95, 195, 245), rect, 2, border_radius=6)
            label = self.font.render(btn["label"], True, (220, 242, 255))
            text_x = rect.x + (rect.width - label.get_width()) // 2
            text_y = rect.y + (rect.height - label.get_height()) // 2
            self.screen.blit(label, (text_x, text_y))

    def draw_upgrade_screen(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((4, 10, 18, 228))
        self.screen.blit(overlay, (0, 0))
        panel_w = int(WIDTH * 0.8)
        panel_h = int(HEIGHT * 0.8)
        panel_x = (WIDTH - panel_w) / 2
        panel_y = (HEIGHT - panel_h) / 2
        panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
        glow = pygame.Surface((panel_rect.width + 28, panel_rect.height + 28), pygame.SRCALPHA)
        pygame.draw.rect(glow, (115, 225, 255, 28), glow.get_rect(), 10, border_radius=18)
        self.screen.blit(glow, (panel_rect.x - 14, panel_rect.y - 14))
        pygame.draw.rect(self.screen, (10, 18, 30), panel_rect, border_radius=14)
        pygame.draw.rect(self.screen, (85, 185, 240), panel_rect, 2, border_radius=14)
        inner = panel_rect.inflate(-16, -16)
        pygame.draw.rect(self.screen, (170, 238, 255), inner, 1, border_radius=12)

        title = self.big_font.render("Choisis un upgrade", True, (215, 240, 255))
        self.screen.blit(
            title, (panel_x + panel_w / 2 - title.get_width() / 2, panel_y - 36)
        )

        mouse_pos = pygame.mouse.get_pos()
        epic_keys = {u.key for u in EPIC_UPGRADES}
        for idx, btn in enumerate(self.ui_buttons):
            rect = btn["rect"]
            choice = btn["choice"]
            hovered = rect.collidepoint(mouse_pos) or (self.gamepad is not None and idx == self.menu_selected_index)
            is_epic = choice.key in epic_keys
            if is_epic:
                color = (40, 34, 72) if hovered else (28, 24, 56)
                border = (190, 140, 255)
            else:
                color = (20, 34, 54) if hovered else (14, 24, 42)
                border = (95, 190, 245)
            glow = pygame.Surface((rect.width + 12, rect.height + 12), pygame.SRCALPHA)
            pygame.draw.rect(glow, (115, 225, 255, 22), glow.get_rect(), 4, border_radius=10)
            self.screen.blit(glow, (rect.x - 6, rect.y - 6))
            pygame.draw.rect(self.screen, color, rect, border_radius=10)
            pygame.draw.rect(self.screen, border, rect, 2, border_radius=8)
            label = self.big_font.render(choice.label, True, (228, 244, 255))
            desc = self.font.render(choice.desc, True, (184, 214, 236))
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
                pygame.draw.rect(self.screen, (14, 20, 32), img_area, border_radius=8)
                pygame.draw.rect(self.screen, (70, 130, 180), img_area, 2, border_radius=8)

            desc_y = rect.y + name_h + img_h + 6
            self.screen.blit(desc, (rect.x + 16, desc_y))

    def draw_class_select_screen(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((4, 10, 18, 232))
        self.screen.blit(overlay, (0, 0))

        panel_w = int(WIDTH * 0.90)
        panel_h = int(HEIGHT * 0.76)
        panel_x = (WIDTH - panel_w) / 2
        panel_y = (HEIGHT - panel_h) / 2
        panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)

        glow = pygame.Surface((panel_rect.width + 28, panel_rect.height + 28), pygame.SRCALPHA)
        pygame.draw.rect(glow, (115, 225, 255, 30), glow.get_rect(), 10, border_radius=18)
        self.screen.blit(glow, (panel_rect.x - 14, panel_rect.y - 14))
        pygame.draw.rect(self.screen, (10, 18, 30), panel_rect, border_radius=14)
        pygame.draw.rect(self.screen, (95, 190, 245), panel_rect, 2, border_radius=14)
        inner = panel_rect.inflate(-16, -16)
        pygame.draw.rect(self.screen, (170, 238, 255), inner, 1, border_radius=12)

        title = self.big_font.render("Choisis ta classe", True, (220, 242, 255))
        self.screen.blit(title, (panel_rect.centerx - title.get_width() / 2, panel_rect.y + 16))

        def draw_wrapped_text(text, x, y, max_width, color, max_lines=2, line_spacing=3):
            words = text.split()
            lines = []
            current = ""
            for word in words:
                candidate = word if not current else f"{current} {word}"
                if self.font.size(candidate)[0] <= max_width:
                    current = candidate
                    continue
                if current:
                    lines.append(current)
                current = word
            if current:
                lines.append(current)

            if len(lines) > max_lines:
                lines = lines[:max_lines]
                last = lines[-1]
                while last and self.font.size(last + "...")[0] > max_width:
                    last = last[:-1]
                lines[-1] = (last.rstrip() + "...") if last else "..."

            line_h = self.font.get_height()
            for idx, line in enumerate(lines):
                surf = self.font.render(line, True, color)
                self.screen.blit(surf, (x, y + idx * (line_h + line_spacing)))
            if not lines:
                return 0
            return len(lines) * line_h + (len(lines) - 1) * line_spacing

        def draw_class_preview(img_rect, class_choice):
            preview = pygame.Surface((img_rect.width, img_rect.height), pygame.SRCALPHA)
            local_rect = preview.get_rect()
            pygame.draw.rect(preview, (10, 18, 34, 220), local_rect, border_radius=8)
            pygame.draw.rect(preview, (70, 130, 190, 170), local_rect, 1, border_radius=8)
            t = pygame.time.get_ticks() * 0.001
            cx, cy = local_rect.center
            span = min(img_rect.width, img_rect.height)

            grid_alpha = int(26 + 10 * (0.5 + 0.5 * math.sin(t * 1.8)))
            for y in range(12, local_rect.height, 18):
                pygame.draw.line(
                    preview,
                    (90, 170, 235, grid_alpha),
                    (10, y),
                    (local_rect.width - 10, y),
                    1,
                )

            def draw_target_dot(x, y, r=4):
                pygame.draw.circle(preview, (95, 215, 255, 90), (int(x), int(y)), r + 4)
                pygame.draw.circle(preview, (195, 242, 255, 220), (int(x), int(y)), r)
                pygame.draw.circle(preview, (255, 255, 255, 210), (int(x), int(y)), max(1, r // 2))

            if class_choice.ultimate_key == "constellation_laser":
                node_count = 6
                base_r = span * 0.34
                nodes = []
                for i in range(node_count):
                    ang = t * 0.85 + i * (math.tau / node_count)
                    rr = base_r * (0.84 + 0.16 * math.sin(t * 1.9 + i * 0.8))
                    nodes.append((cx + math.cos(ang) * rr, cy + math.sin(ang) * rr))

                target_points = []
                for i in range(4):
                    ang = -t * 0.55 + i * (math.tau / 4) + 0.3
                    rr = base_r * 0.62
                    tx = cx + math.cos(ang) * rr
                    ty = cy + math.sin(ang) * rr
                    target_points.append((tx, ty))
                    draw_target_dot(tx, ty, 3)

                links = []
                for i in range(node_count):
                    links.append((nodes[i], nodes[(i + 1) % node_count]))
                    links.append((nodes[i], nodes[(i + 2) % node_count]))

                for tx, ty in target_points:
                    nearest = sorted(nodes, key=lambda p: (p[0] - tx) ** 2 + (p[1] - ty) ** 2)[:2]
                    for n in nearest:
                        links.append((n, (tx, ty)))

                beam_w = max(2, int(span * 0.028))
                for a, b in links:
                    pygame.draw.line(preview, (70, 200, 255, 50), a, b, beam_w + 7)
                    pygame.draw.line(preview, (95, 225, 255, 130), a, b, beam_w + 2)
                    pygame.draw.line(preview, (230, 248, 255, 230), a, b, max(2, beam_w // 2))

                for i, (x, y) in enumerate(nodes):
                    twinkle = 0.5 + 0.5 * math.sin(t * 5.2 + i * 0.9)
                    beacon_phase = t * (2.0 + i * 0.07)
                    r = 4 + int(2.2 * twinkle)
                    pygame.draw.circle(preview, (90, 220, 255, 75), (int(x), int(y)), r + 10)
                    pygame.draw.circle(preview, (165, 236, 255, 52), (int(x), int(y)), r + 15, 2)
                    outer = Enemy._regular_polygon((x, y), r + 8, 4, beacon_phase + math.pi / 4)
                    inner = Enemy._regular_polygon((x, y), r + 4, 4, -beacon_phase * 1.2 + math.pi / 4)
                    pygame.draw.polygon(preview, (110, 220, 255, 150), outer, 2)
                    pygame.draw.polygon(preview, (215, 245, 255, 190), inner, 2)
                    top = (int(x), int(y - (r + 5)))
                    left = (int(x - max(3, r * 0.5)), int(y + max(3, r * 0.35)))
                    right = (int(x + max(3, r * 0.5)), int(y + max(3, r * 0.35)))
                    pygame.draw.polygon(preview, (14, 32, 55, 200), [top, right, left])
                    pygame.draw.polygon(preview, (95, 195, 245, 185), [top, right, left], 1)
                    pygame.draw.circle(preview, (180, 242, 255, 235), (int(x), int(y)), r)
                    pygame.draw.circle(preview, (255, 255, 255, 220), (int(x), int(y)), max(2, r // 2))
                    pygame.draw.line(
                        preview,
                        (205, 245, 255, 180),
                        (int(x), int(y - r - 5)),
                        (int(x), int(y + r + 3)),
                        1,
                    )
            elif class_choice.ultimate_key == "prismatic_blade":
                inner_radius = span * 0.18
                sword_len = span * 0.74
                sword_w = max(14, int(span * 0.12))
                for i in range(3):
                    ang = t * 2.9 + i * (math.tau / 3) + 0.2 * math.sin(t * 2.4 + i)
                    sx = cx + math.cos(ang) * inner_radius
                    sy = cy + math.sin(ang) * inner_radius
                    draw_sword(
                        preview,
                        sx,
                        sy,
                        ang,
                        sword_len,
                        sword_w,
                        0.92,
                        hilt_ratio=0.22,
                    )
            elif class_choice.ultimate_key == "vector_overdrive":
                r = span * 0.26
                pulse = 0.9 + 0.1 * math.sin(t * 6.5)
                rr = int(r * pulse)
                pygame.draw.circle(preview, (90, 220, 255, 40), (cx, cy), rr + 34, 10)
                pygame.draw.circle(preview, (170, 244, 255, 155), (cx, cy), rr + 6, 3)
                pygame.draw.circle(preview, (240, 252, 255, 120), (cx, cy), max(14, rr // 3), 2)

                hostile_pts = []
                ally_pts = []
                for i in range(5):
                    ang = t * 0.7 + i * (math.tau / 5)
                    hx = cx + math.cos(ang) * rr * 1.35
                    hy = cy + math.sin(ang) * rr * 1.05
                    hostile_pts.append((hx, hy))
                    draw_target_dot(hx, hy, 3)
                    poly = Enemy._regular_polygon((hx, hy), 10, 4, ang + math.pi / 4)
                    pygame.draw.polygon(preview, (255, 110, 110, 120), poly, 2)

                    ax = cx + math.cos(ang + 0.38) * rr * 0.72
                    ay = cy + math.sin(ang + 0.38) * rr * 0.58
                    ally_pts.append((ax, ay))
                    star = Enemy._star_polygon((ax, ay), 10, 5, 5, -math.pi / 2)
                    pygame.draw.polygon(preview, (120, 220, 255, 165), star)
                    pygame.draw.polygon(preview, (235, 248, 255, 220), star, 1)

                for (hx, hy), (ax, ay) in zip(hostile_pts, ally_pts):
                    pygame.draw.line(preview, (120, 220, 255, 70), (hx, hy), (ax, ay), 8)
                    pygame.draw.line(preview, (190, 242, 255, 200), (hx, hy), (ax, ay), 3)
                    pygame.draw.line(preview, (255, 255, 255, 210), (hx, hy), (ax, ay), 1)
            elif class_choice.ultimate_key == "spectral_swarm":
                hub_r = int(span * 0.28 + 6 * math.sin(t * 5.8))
                pygame.draw.circle(preview, (155, 110, 255, 62), (cx, cy), hub_r + 10, 7)
                pygame.draw.circle(preview, (215, 180, 255, 165), (cx, cy), hub_r, 2)
                for i in range(6):
                    ang = t * 3.0 + i * (math.tau / 6)
                    px = cx + math.cos(ang) * (hub_r - 8)
                    py = cy + math.sin(ang) * (hub_r - 8)
                    pygame.draw.circle(preview, (238, 215, 255, 180), (int(px), int(py)), 3)

                for i in range(10):
                    ang = t * 2.2 + i * (math.tau / 10)
                    sx = cx + math.cos(ang) * (hub_r * 0.55)
                    sy = cy + math.sin(ang) * (hub_r * 0.55)
                    ex = sx + math.cos(ang + 0.2 * math.sin(t * 2.8 + i)) * 22
                    ey = sy + math.sin(ang + 0.2 * math.sin(t * 2.8 + i)) * 22
                    pygame.draw.line(preview, (190, 145, 255, 120), (sx, sy), (ex, ey), 5)
                    pygame.draw.line(preview, (245, 228, 255, 220), (sx, sy), (ex, ey), 2)
                    pygame.draw.circle(preview, (205, 165, 255, 190), (int(ex), int(ey)), 6)
                    pygame.draw.circle(preview, (255, 245, 255, 240), (int(ex), int(ey)), 3)
            elif class_choice.ultimate_key == "queen_hive":
                hive_r = max(18, int(span * 0.12))
                hive_y = cy + int(math.sin(t * 0.9) * 3)
                pygame.draw.circle(preview, (255, 210, 70, 70), (cx, hive_y), hive_r + 14, 7)
                pygame.draw.circle(preview, (36, 30, 18, 220), (cx, hive_y), hive_r)
                pygame.draw.circle(preview, (255, 225, 120, 225), (cx, hive_y), hive_r, 2)
                for i in range(6):
                    ang = t * 1.2 + i * (math.tau / 6)
                    px = cx + math.cos(ang) * (hive_r * 0.7)
                    py = hive_y + math.sin(ang) * (hive_r * 0.7)
                    pygame.draw.circle(preview, (240, 170, 45, 200), (int(px), int(py)), 5)
                    pygame.draw.circle(preview, (255, 232, 165, 220), (int(px), int(py)), 5, 1)

                for i in range(12):
                    ang = t * 2.8 + i * (math.tau / 12)
                    r = hive_r + 22 + 10 * math.sin(t * 1.8 + i)
                    bx = cx + math.cos(ang) * r
                    by = hive_y + math.sin(ang) * r * 0.65
                    vx = math.cos(ang + 0.8)
                    vy = math.sin(ang + 0.8)
                    fx, fy = vx, vy
                    nx, ny = -fy, fx
                    body_len = 10
                    body_w = 4
                    nose = (bx + fx * body_len * 0.55, by + fy * body_len * 0.55)
                    tail = (bx - fx * body_len * 0.65, by - fy * body_len * 0.65)
                    body_pts = [
                        (int(nose[0] + nx * body_w), int(nose[1] + ny * body_w)),
                        (int(tail[0] + nx * body_w * 0.8), int(tail[1] + ny * body_w * 0.8)),
                        (int(tail[0] - nx * body_w * 0.8), int(tail[1] - ny * body_w * 0.8)),
                        (int(nose[0] - nx * body_w), int(nose[1] - ny * body_w)),
                    ]
                    pygame.draw.polygon(preview, (245, 190, 42, 215), body_pts)
                    pygame.draw.line(
                        preview,
                        (26, 22, 16, 220),
                        (int(bx + nx * body_w), int(by + ny * body_w)),
                        (int(bx - nx * body_w), int(by - ny * body_w)),
                        2,
                    )
                    wing_l = [
                        (int(bx - fx * 1 + nx * 2), int(by - fy * 1 + ny * 2)),
                        (int(bx - fx * 4 + nx * 7), int(by - fy * 4 + ny * 7)),
                        (int(bx + fx * 1 + nx * 2), int(by + fy * 1 + ny * 2)),
                    ]
                    wing_r = [
                        (int(bx - fx * 1 - nx * 2), int(by - fy * 1 - ny * 2)),
                        (int(bx - fx * 4 - nx * 7), int(by - fy * 4 - ny * 7)),
                        (int(bx + fx * 1 - nx * 2), int(by + fy * 1 - ny * 2)),
                    ]
                    pygame.draw.polygon(preview, (220, 246, 255, 115), wing_l)
                    pygame.draw.polygon(preview, (220, 246, 255, 115), wing_r)
            elif class_choice.ultimate_key == "singularity":
                growth_t = 0.5 + 0.5 * math.sin(t * 0.65 - math.pi / 2)
                growth_ease = growth_t * growth_t * (3.0 - 2.0 * growth_t)
                growth_mult = (1.0 / 3.0) + (1.3 - (1.0 / 3.0)) * growth_ease
                preview_scale = 4.0

                disk_rx = max(
                    16,
                    int(span * 0.22 * growth_mult * (0.95 + 0.05 * math.sin(t * 1.2)) * preview_scale),
                )
                disk_ry = max(7, int(disk_rx * 0.34))
                core_r = max(4, int(span * 0.045 * growth_mult * preview_scale))
                disk_cy = cy

                for spread, alpha in ((14, 24), (10, 34), (6, 48), (2, 68)):
                    rx = disk_rx + spread
                    ry = disk_ry + int(spread * 0.38)
                    rect = pygame.Rect(cx - rx, disk_cy - ry, rx * 2, ry * 2)
                    col = (150 + spread * 3, 90 + spread * 2, 220 + min(25, spread * 2), alpha)
                    pygame.draw.ellipse(preview, col, rect, max(1, 6 - spread // 3))

                filament_count = 14
                for i in range(filament_count):
                    frac = i / max(1, filament_count - 1)
                    rx = int(disk_rx * (0.56 + 0.4 * frac))
                    ry = max(4, int(disk_ry * (0.6 + 0.4 * frac)))
                    rect = pygame.Rect(cx - rx, disk_cy - ry, rx * 2, ry * 2)
                    start = t * (1.6 + 0.3 * frac) + i * 0.45
                    sweep = 0.9
                    col = (205, 145, 255, int(110 - 45 * frac))
                    pygame.draw.arc(preview, col, rect, start, start + sweep, 2)

                photon_rx = max(core_r + 5, int(disk_rx * 0.36))
                photon_ry = max(5, int(photon_rx * 0.40))
                for spread, alpha, width in ((4, 70, 4), (2, 120, 3), (0, 180, 2)):
                    rect = pygame.Rect(
                        cx - (photon_rx + spread),
                        disk_cy - (photon_ry + spread // 2),
                        (photon_rx + spread) * 2,
                        (photon_ry + spread // 2) * 2,
                    )
                    pygame.draw.ellipse(preview, (245, 195, 255, alpha), rect, width)

                pygame.draw.circle(preview, (14, 8, 22, 240), (cx, cy), core_r + 3)
                pygame.draw.circle(preview, (0, 0, 0, 255), (cx, cy), core_r)
                pygame.draw.circle(preview, (175, 120, 235, 160), (cx, cy), core_r + 1, 1)
                lens_rect = pygame.Rect(
                    cx - (photon_rx + 10),
                    disk_cy - (photon_ry + 6),
                    (photon_rx + 10) * 2,
                    (photon_ry + 6) * 2,
                )
                pygame.draw.arc(preview, (255, 240, 255, 185), lens_rect, math.pi * 1.08, math.pi * 1.92, 2)

            else:
                pulse = 0.5 + 0.5 * math.sin(t * 2.4)
                r = int(min(img_rect.width, img_rect.height) * (0.22 + pulse * 0.05))
                center = local_rect.center
                pygame.draw.circle(preview, (65, 190, 255, 45), center, r + 16, 8)
                pygame.draw.circle(preview, (95, 220, 255, 115), center, r + 8, 4)
                pygame.draw.circle(preview, (190, 245, 255, 215), center, r, 2)
                pygame.draw.circle(preview, (210, 250, 255, 140), center, max(3, r // 3))

            self.screen.blit(preview, img_rect.topleft)

        mouse_pos = pygame.mouse.get_pos()
        for idx, btn in enumerate(self.ui_buttons):
            rect = btn["rect"]
            class_choice = btn["class_choice"]
            hovered = rect.collidepoint(mouse_pos) or (self.gamepad is not None and idx == self.menu_selected_index)
            color = (24, 38, 60) if hovered else (14, 24, 42)
            border = (120, 215, 255) if hovered else (90, 175, 230)
            card_glow = pygame.Surface((rect.width + 12, rect.height + 12), pygame.SRCALPHA)
            pygame.draw.rect(card_glow, (115, 225, 255, 24), card_glow.get_rect(), 5, border_radius=10)
            self.screen.blit(card_glow, (rect.x - 6, rect.y - 6))
            pygame.draw.rect(self.screen, color, rect, border_radius=10)
            pygame.draw.rect(self.screen, border, rect, 2, border_radius=10)

            label = self.big_font.render(class_choice.label, True, (228, 244, 255))
            self.screen.blit(label, (rect.x + 14, rect.y + 14))

            ulti = self.font.render(
                f"Ulti: {class_choice.ultimate_label}",
                True,
                (190, 222, 242),
            )
            self.screen.blit(ulti, (rect.x + 14, rect.y + 54))

            content_top = rect.y + 82
            desc_line_h = self.font.get_height()
            desc_max_h = desc_line_h * 2 + 3
            hint_h = self.font.get_height()
            bottom_padding = 14
            preview_h = rect.height - (content_top - rect.y) - desc_max_h - hint_h - bottom_padding - 12
            preview_h = int(clamp(preview_h, 210, 494))
            img_rect = pygame.Rect(rect.x + 14, content_top, rect.width - 28, preview_h)
            draw_class_preview(img_rect, class_choice)

            desc_y = img_rect.bottom + 8
            draw_wrapped_text(
                class_choice.desc,
                rect.x + 14,
                desc_y,
                rect.width - 28,
                (170, 202, 226),
                max_lines=2,
            )

            hint = self.font.render("Clique pour commencer la partie", True, (145, 190, 220))
            hint_y = rect.bottom - hint.get_height() - 10
            self.screen.blit(hint, (rect.x + 14, hint_y))

    def draw_start_screen(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((3, 8, 14, 244))
        self.screen.blit(overlay, (0, 0))
        t = pygame.time.get_ticks() * 0.001
        for i, (cx, cy, r, col) in enumerate(
            (
                (WIDTH * 0.18, HEIGHT * 0.22, WIDTH * 0.24, (70, 160, 230)),
                (WIDTH * 0.82, HEIGHT * 0.78, WIDTH * 0.28, (55, 125, 195)),
                (WIDTH * 0.66, HEIGHT * 0.18, WIDTH * 0.18, (95, 205, 255)),
            )
        ):
            pulse = 0.85 + 0.15 * math.sin(t * (1.2 + i * 0.32))
            rr = int(r * pulse)
            orb = pygame.Surface((rr * 2 + 8, rr * 2 + 8), pygame.SRCALPHA)
            pygame.draw.circle(orb, (*col, 22), (rr + 4, rr + 4), rr)
            self.screen.blit(orb, (int(cx - rr - 4), int(cy - rr - 4)))

        main_title_font = pygame.font.Font(self.font_path, int(clamp(WIDTH * 0.12, 80, 140)))
        main_title = "TANK SURVIVOR"
        title_y = int(HEIGHT * 0.08)
        
        title_base = main_title_font.render(main_title, True, (240, 252, 255))
        glow_surf = pygame.Surface((title_base.get_width() + 40, title_base.get_height() + 40), pygame.SRCALPHA)
        
        glow_color = (100, 200, 255)
        for offset in range(16, 0, -2):
            alpha = int(40 * (1 - offset/16))
            glow_text = main_title_font.render(main_title, True, (*glow_color, alpha))
            glow_surf.blit(glow_text, (offset // 2 + 20, 20))
        
        title_final = main_title_font.render(main_title, True, (240, 252, 255))
        glow_surf.blit(title_final, (20, 20))
        
        glow_rect = glow_surf.get_rect(center=(WIDTH // 2, title_y + 20))
        self.screen.blit(glow_surf, glow_rect.topleft)
        
        play_font = pygame.font.Font(self.font_path, int(clamp(WIDTH * 0.035, 30, 50)))
        quit_font = pygame.font.Font(self.font_path, int(clamp(WIDTH * 0.025,  20, 35)))

        mouse_pos = pygame.mouse.get_pos()
        for idx, btn in enumerate(self.ui_buttons):
            rect = btn["rect"]
            action = btn["action"]
            hovered = rect.collidepoint(mouse_pos) or (self.gamepad is not None and idx == self.menu_selected_index)
            is_play = action == "play"
            if is_play:
                color = (24, 66, 98) if hovered else (16, 48, 78)
                color_inner = (34, 96, 132) if hovered else (24, 74, 110)
                border = (156, 236, 255) if hovered else (122, 214, 248)
                text_color = (238, 250, 255)
                label = play_font.render("Play", True, text_color)
            else:
                color = (16, 40, 64) if hovered else (12, 30, 52)
                color_inner = (24, 58, 88) if hovered else (18, 46, 74)
                border = (128, 206, 242) if hovered else (100, 176, 220)
                text_color = (216, 240, 255)
                label = quit_font.render("Quitter", True, text_color)

            glow = pygame.Surface((rect.width + 18, rect.height + 18), pygame.SRCALPHA)
            pygame.draw.rect(glow, (*border, 36), glow.get_rect(), 8, border_radius=16)
            pygame.draw.rect(glow, (*border, 22), glow.get_rect().inflate(-8, -8), 5, border_radius=13)
            self.screen.blit(glow, (rect.x - 9, rect.y - 9))

            pygame.draw.rect(self.screen, color, rect, border_radius=14)
            inner_rect = rect.inflate(-8, -8)
            pygame.draw.rect(self.screen, color_inner, inner_rect, border_radius=10)
            pygame.draw.rect(self.screen, border, rect, 2, border_radius=14)
            self.screen.blit(
                label, (rect.x + rect.width / 2 - label.get_width() / 2, rect.y + rect.height / 2 - label.get_height() / 2)
            )

    def draw_game_over(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((4, 10, 18, 232))
        self.screen.blit(overlay, (0, 0))
        panel_w = 520
        panel_h = 240
        panel_rect = pygame.Rect(WIDTH / 2 - panel_w / 2, 120, panel_w, panel_h)
        glow = pygame.Surface((panel_rect.width + 26, panel_rect.height + 26), pygame.SRCALPHA)
        pygame.draw.rect(glow, (115, 225, 255, 30), glow.get_rect(), 8, border_radius=18)
        self.screen.blit(glow, (panel_rect.x - 13, panel_rect.y - 13))
        pygame.draw.rect(self.screen, (10, 18, 30), panel_rect, border_radius=14)
        pygame.draw.rect(self.screen, (95, 190, 245), panel_rect, 2, border_radius=14)
        inner = panel_rect.inflate(-16, -16)
        pygame.draw.rect(self.screen, (170, 238, 255), inner, 1, border_radius=12)

        title = self.big_font.render("Game Over", True, (220, 242, 255))
        self.screen.blit(title, (panel_rect.centerx - title.get_width() / 2, panel_rect.y + 26))
        score = self.font.render(f"Score: {self.score}  |  Vague: {self.wave}", True, (194, 220, 242))
        self.screen.blit(score, (panel_rect.centerx - score.get_width() / 2, panel_rect.y + 76))
        hint = self.font.render("Choisis un bouton pour continuer", True, (168, 200, 225))
        self.screen.blit(hint, (panel_rect.centerx - hint.get_width() / 2, panel_rect.y + 110))

        left_stats_rect = self.get_damage_stats_rect(
            panel_rect,
            "Degats recus",
            top_margin=40,
            bottom_margin=40,
            side="left",
            player_stats=True,
        )
        self.draw_damage_stats_panel(left_stats_rect, "Degats recus", player_stats=True)

        stats_rect = self.get_damage_stats_rect(panel_rect, "Bilan des degats", top_margin=40, bottom_margin=40)
        self.draw_damage_stats_panel(stats_rect, "Bilan des degats")

        mouse_pos = pygame.mouse.get_pos()
        for idx, btn in enumerate(self.ui_buttons):
            rect = btn["rect"]
            action = btn["action"]
            hovered = rect.collidepoint(mouse_pos) or (self.gamepad is not None and idx == self.menu_selected_index)
            color = (22, 36, 56) if hovered else (14, 24, 40)
            pygame.draw.rect(self.screen, color, rect, border_radius=10)
            pygame.draw.rect(self.screen, (95, 195, 245), rect, 2, border_radius=10)
            text = "Rejouer" if action == "replay" else "Quitter"
            label = self.big_font.render(text, True, (220, 242, 255))
            self.screen.blit(
                label, (rect.x + rect.width / 2 - label.get_width() / 2, rect.y + 14)
            )

    def draw_pause(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((4, 10, 18, 224))
        self.screen.blit(overlay, (0, 0))
        panel_w = 520
        panel_h = 220
        panel_rect = pygame.Rect(WIDTH / 2 - panel_w / 2, HEIGHT / 2 - panel_h / 2, panel_w, panel_h)
        glow = pygame.Surface((panel_rect.width + 26, panel_rect.height + 26), pygame.SRCALPHA)
        pygame.draw.rect(glow, (115, 225, 255, 30), glow.get_rect(), 8, border_radius=18)
        self.screen.blit(glow, (panel_rect.x - 13, panel_rect.y - 13))
        pygame.draw.rect(self.screen, (10, 18, 30), panel_rect, border_radius=14)
        pygame.draw.rect(self.screen, (95, 190, 245), panel_rect, 2, border_radius=14)
        inner = panel_rect.inflate(-16, -16)
        pygame.draw.rect(self.screen, (170, 238, 255), inner, 1, border_radius=12)

        title = self.big_font.render("Pause", True, (220, 242, 255))
        self.screen.blit(title, (panel_rect.centerx - title.get_width() / 2, panel_rect.y + 26))

        left_stats_rect = self.get_damage_stats_rect(
            panel_rect,
            "Degats recus",
            top_margin=40,
            bottom_margin=40,
            side="left",
            player_stats=True,
        )
        self.draw_damage_stats_panel(left_stats_rect, "Degats recus", player_stats=True)

        stats_rect = self.get_damage_stats_rect(panel_rect, "Stats de degats", top_margin=40, bottom_margin=40)
        self.draw_damage_stats_panel(stats_rect, "Stats de degats")

        mouse_pos = pygame.mouse.get_pos()
        for idx, btn in enumerate(self.ui_buttons):
            rect = btn["rect"]
            action = btn["action"]
            hovered = rect.collidepoint(mouse_pos) or (self.gamepad is not None and idx == self.menu_selected_index)
            color = (22, 36, 56) if hovered else (14, 24, 40)
            pygame.draw.rect(self.screen, color, rect, border_radius=10)
            pygame.draw.rect(self.screen, (95, 195, 245), rect, 2, border_radius=10)
            text = "Reprendre" if action == "resume" else ("Rejouer" if action == "replay" else "Quitter")
            label = self.big_font.render(text, True, (220, 242, 255))
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
        for hive in self.bee_hives:
            hive.draw(self.screen)
        for bee in self.bee_minions:
            bee.draw(self.screen)
        for proj in self.projectiles:
            proj.draw(self.screen)
        for slash in self.blade_skill_slashes:
            slash.draw(self.screen)
        for rocket in self.rockets:
            rocket.draw(self.screen)
        for explosion in self.explosions:
            explosion.draw(self.screen)
        for shock in self.shockwaves:
            shock.draw(self.screen)
        for pulse in self.ultimate_pulses:
            pulse.draw(self.screen)
        for constellation in self.ultimate_constellations:
            constellation.draw(self.screen)
        for singularity in self.ultimate_singularities:
            singularity.draw(self.screen)
        for blade in self.ultimate_prismatic_blades:
            blade.draw(self.screen)
        for overdrive in self.ultimate_vector_overdrives:
            overdrive.draw(self.screen)
        for prism in self.ultimate_queen_hives:
            prism.draw(self.screen)
        for swarm in self.ultimate_spectral_swarms:
            swarm.draw(self.screen)
        for shard in self.ultimate_spectral_shards:
            shard.draw(self.screen)
        for zone in self.ultimate_zones:
            zone.draw(self.screen)
        for beam in self.ultimate_beams:
            beam.draw(self.screen)
        for laser in self.spatial_lasers:
            laser.draw(self.screen)
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
        if self.state == "start_menu":
            self.draw_start_screen()
        if self.state == "upgrade":
            self.draw_upgrade_screen()
        if self.state == "class_select":
            self.draw_class_select_screen()
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
                if event.type in (pygame.JOYDEVICEADDED, pygame.JOYDEVICEREMOVED):
                    self.refresh_gamepad()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_o:
                    self.cheats_enabled = not self.cheats_enabled
                    self.cheat_buttons = []
                if event.type == pygame.KEYDOWN and self.state in ("start_menu", "class_select", "upgrade", "game_over", "pause"):
                    if event.key in (pygame.K_LEFT, pygame.K_q, pygame.K_a):
                        self.move_menu_selection((-1, 0))
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        self.move_menu_selection((1, 0))
                    elif event.key in (pygame.K_UP, pygame.K_z, pygame.K_w):
                        self.move_menu_selection((0, -1))
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        self.move_menu_selection((0, 1))
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                        action_result = self.activate_selected_menu_button()
                        if action_result == "quit":
                            running = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    if self.state == "start_menu":
                        running = False
                    else:
                        self.toggle_pause()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_a:
                    if self.state == "playing":
                        self.try_activate_ultimate()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                    if self.state == "playing":
                        self.try_activate_shockwave()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                    self.base_fire_enabled = not self.base_fire_enabled
                if event.type == pygame.JOYBUTTONDOWN and self.gamepad is not None:
                    if event.button in self.pad_btn_pause:
                        self.toggle_pause()
                    if self.state == "playing":
                        if event.button == self.pad_btn_ulti:
                            self.try_activate_ultimate()
                        if event.button == self.pad_btn_shockwave:
                            self.try_activate_shockwave()
                    if self.state in ("start_menu", "class_select", "upgrade", "game_over", "pause"):
                        if event.button in self.pad_btn_confirm:
                            action_result = self.activate_selected_menu_button()
                            if action_result == "quit":
                                running = False
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.state == "start_menu":
                        for btn in self.ui_buttons:
                            if btn["rect"].collidepoint(event.pos):
                                if btn["action"] == "play":
                                    self.open_class_select()
                                else:
                                    running = False
                                break
                    elif self.state == "class_select":
                        for btn in self.ui_buttons:
                            if btn["rect"].collidepoint(event.pos):
                                self.select_class(btn["class_choice"])
                                break
                    elif self.state == "upgrade":
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

            if self.gamepad is not None:
                self.update_menu_navigation(dt, self.get_gamepad_input())
            else:
                self.menu_nav_hold = (0, 0)
                self.menu_nav_repeat_timer = 0.0
            if self.state in ("playing", "wave_clear", "boss_death"):
                self.update(dt)

            if self.player.hp <= 0 and self.state != "game_over":
                self.state = "game_over"
                self.build_game_over_buttons()

            self.draw()
            pygame.display.flip()

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    Game().run()
