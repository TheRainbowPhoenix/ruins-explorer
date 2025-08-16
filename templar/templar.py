from gint import *
from templar_data import *
from templar_rooms import bounce, room_level1, room_levels
import time

# 320x224 is 20x14, add one because the outer border uses half on each side
WW, WH = 21, 15
# Viewports
MAP_X, MAP_Y = -8, -8
HUD_X, HUD_Y, HUD_W, HUD_H = 320, 0, 76, 224

STANCE_IDLE, STANCE_RUNNING, STANCE_JUMPING, STANCE_HURT, STANCE_VICTORY = 0, 1, 2, 3, 4
FACING_LEFT, FACING_RIGHT = 0, 1
PH_GROUNDED, PH_LWALL, PH_RWALL, PH_HEADBANG, PH_TOOFAST, PH_FAILED, PH_DEATH = 1, 2, 4, 8, 16, 32, 64

SOLID_STD, SOLID_PLANK, SOLID_INTERACTIBLE, SOLID_DEATH, SOLID_NOT, SOLID_FLAG = 0, 1, 2, 3, 4, 5

class vec2:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def __add__(u, v):
        return vec2(u.x + v.x, u.y + v.y)
    def __sub__(u, v):
        return vec2(u.x - v.x, u.y - vy)
    def __mul__(u, v):
        if isinstance(v, vec2):
            return u.x * v.x + u.y * v.y
        else:
            return vec2(u.x * v, u.y * v)

class rect:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def left(self):
        return self.x
    def right(self):
        return self.x + self.w
    def top(self):
        return self.y
    def bottom(self):
        return self.y + self.h

    def intersects(r1, r2):
        return r1.right() > r2.left() and r1.left() < r2.right() \
           and r1.bottom() > r2.top() and r1.top() < r2.bottom()

class playerT:
    def initialize(self, pos):
        self.pos = pos
        self.speed = vec2(0, 0)
        # Stance and direction faced
        self.stance = -1
        self.facing = FACING_RIGHT
        # True if grounded, otherwise airborne
        self._grounded = True
        # Number of jump frames still available
        self.jump_frames = 0
        # Number of non-control frames due to animation
        self.noncontrol_frames = 0
        # Animation
        self.anim = animstateT()

    def grounded(self):
        return self._grounded
    def airborne(self):
        return not self._grounded

def tile_solid(room, tileID):
    return tileID != 0xff and room.tileset.solid[tileID] == SOLID_STD

class roomT:
    def __init__(self, w, h, spawn_x, spawn_y, hitboxes, intboxes, tileset, flag_sequence):
        self.w = w
        self.h = h
        self.tiles = None
        self.tilecollisions = None
        self.spawn_x = spawn_x
        self.spawn_y = spawn_y
        # TODO: room hitboxes/intboxes are obsolete?
        self._hitboxes = hitboxes
        self._intboxes = intboxes
        self.tileset = tileset
        self.flag_sequence = flag_sequence

    def hitboxes(self):
        return self._hitboxes
    def intboxes(self):
        return self._intboxes

    def alignToTiles(self, wr):
        x1 = max(int(wr.x) >> 4, 0)
        x2 = min(int(wr.x + wr.w - 1) >> 4, self.w - 1)
        y1 = max(int(wr.y) >> 4, 0)
        y2 = min(int(wr.y + wr.h - 1) >> 4, self.h - 1)
        return x1, y1, x2, y2

    def hitboxesNear(self, wr):
        x1, y1, x2, y2 = self.alignToTiles(wr)
        tb = self.tileset.tileboxes
        for y in range(y1, y2+1):
            for x in range(x1, x2+1):
                i = self.w * y + x
                t = self.tiles[i]
                if t != 0xff and tb[4*t+2]:
                    yield rect(16*x + tb[4*t], 16*y + tb[4*t+1], tb[4*t+2],
                        tb[4*t+3]), self.tilecollisions[i], self.tileset.solid[t]

    def hitboxesAll(self):
        i = 0
        tb = self.tileset.tileboxes
        for y in range(self.h):
            for x in range(self.w):
                t = self.tiles[i]
                if t != 0xff and tb[4*t+2]:
                    yield rect(16*x + tb[4*t], 16*y + tb[4*t+1], tb[4*t+2],
                        tb[4*t+3]), self.tilecollisions[i], self.tileset.solid[t]
                i += 1

    def computeTileCollisions(self):
        w, h = self.w, self.h
        i = 0
        self.tilecollisions = bytearray(w * h)
        for y in range(h):
            for x in range(w):
                t = self.tiles[i]
                solid = SOLID_NOT if t == 0xff else self.tileset.solid[t]

                if solid == SOLID_NOT:
                    pass
                elif solid == SOLID_PLANK:
                    # Planks can only have GROUNDED sides
                    if y > 0 and not tile_solid(self, self.tiles[i - w]):
                        self.tilecollisions[i] = PH_GROUNDED
                else:
                    sides = 0
                    if y > 0 and not tile_solid(self, self.tiles[i - w]):
                        sides |= PH_GROUNDED
                    if y < h - 1 and not tile_solid(self, self.tiles[i + w]):
                        sides |= PH_HEADBANG
                    if x > 0 and not tile_solid(self, self.tiles[i - 1]):
                        sides |= PH_RWALL
                    if x < w - 1 and not tile_solid(self, self.tiles[i + 1]):
                        sides |= PH_LWALL
                    self.tilecollisions[i] = sides
                i += 1

class inputT:
    def __init__(self):
        self.dx = 0
        self.dy = 0
        self.jump_down = False
        self.jump_buffer = 0
        self.interact = False

class gameT:
    def __init__(self):
        self.room = None
        self.dirty_tiles = None
        self.player = None
        self.intcard_time = 0
        self.toofast_frames = 0
        self.physics_failed_frames = 0

    def startLevel(self, room, player):
        self.room = room
        self.dirty_tiles = bytearray(room.w * room.h)
        self.player = player
        self.reset_timer = -1
        self.end_timer = -1
        self.deaths = 0
        self.entities = []
        self.flags = dict()
        self.flags_taken = 0
        self.flag_cursor = 0
        self.time = 0

        for i in range(room.w * room.h):
            self.dirty_tiles[i] = 1

    def markTilesDirty(self, wr):
        x1, y1, x2, y2 = self.room.alignToTiles(wr)
        # print(wr.x, wr.y, "*", wr.w, wr.h, "->", x1, y1, "--", x2, y2)
        for y in range(y1, y2+1):
            for x in range(x1, x2+1):
                self.dirty_tiles[y * self.room.w + x] = 1

    def showFlag(self, x, y):
        self.flags[(x, y)] = False
        self.dirty_tiles[y * self.room.w + x] = 1

    def takeFlag(self, x, y):
        xy = (x, y)
        if xy not in self.flags:
            return
        if not self.flags[xy]:
            self.flags[xy] = True
            n = sum(c for a, b, c in self.room.flag_sequence if a == x and b == y)
            self.showNextFlags(n)
            self.flags_taken += 1

    def showNextFlags(self, n):
        n = min(n, len(self.room.flag_sequence) - self.flag_cursor)
        for i in range(n):
            x, y, _ = self.room.flag_sequence[self.flag_cursor]
            self.showFlag(x, y)
            self.flag_cursor += 1

class animframeT:
    def __init__(self, img, imgH, x, y, w, h, cx, cy, duration):
        self.img = img
        self.imgH = imgH
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.cx = cx
        self.cy = cy
        self.duration = duration

class animstateT:
    def __init__(self):
        self.frames = None
        self.index = -1
        self.elapsed = 0

    def set(self, frames):
        self.frames = frames
        self.index = 0
        self.elapsed = 0

    def update(self, dt):
        if self.index < 0:
            return

        self.elapsed += dt
        if self.elapsed * 1000 < self.frames[self.index].duration:
            return False

        self.elapsed = 0
        self.index = (self.index + 1) % len(self.frames)
        return self.index == 0

class tilesetT:
    def __init__(self, img, tileboxes, solid):
        self.img = img
        self.tileboxes = tileboxes
        self.solid = solid

def physics_player_hitbox(pos):
    return rect(pos.x-5, pos.y - 14, 11, 14)

def physics_acceptable(room, pos):
    new_player_hb = physics_player_hitbox(pos)
    for hb, _, solid in room.hitboxesNear(new_player_hb):
        if solid == SOLID_STD and new_player_hb.intersects(hb):
            return False
    return True

def physics_interaction(room, pos):
    return -1
    # player_hb = physics_player_hitbox(pos)
    # for i, hb in enumerate(room.hitboxesNear(player_hb)):
    #     if player_hb.intersects(hb):
    #         return i
    # return -1

debug_resolution = rect(0, 0, 0, 0)

def physics_displace(room, pos, diff):
    pr = physics_player_hitbox(pos + diff)
    resolution = vec2(0, 0)
    flags = 0
    global debug_resolution

    # Check how each intersecting hitbox wants to resolve any collision. For
    # this we track *flags* (resolution directions for all hitboxes) and
    # *resolution* (the actual movement for resolving).
    for i, (r, rf, solid) in enumerate(room.hitboxesNear(pr)):
        if not pr.intersects(r):
            continue

        # Cause death
        if solid == SOLID_DEATH:
            return pos + diff, PH_DEATH
        # Don't interact at all
        if solid == SOLID_NOT or solid == SOLID_FLAG:
            continue
        # Planks only interact if we're going through with downwards speed
        if (solid == SOLID_PLANK) and (diff.y < 0 or pos.y > r.top() + 1):
            continue

        # Find how far we are clipping into each edge. left/top are positive,
        # right/bottom are negative, all are 0 if not clipping.
        leftOverlap   = max(r.right()  - pr.left(),   0)
        rightOverlap  = min(r.left()   - pr.right(),  0)
        topOverlap    = max(r.bottom() - pr.top(),    0)
        bottomOverlap = min(r.top()    - pr.bottom(), 0)

        # Now determine in which direction to push back. This is the direction
        # with the smallest overlap among directions that have collisions and
        # an overlap.
        smallestOverlap = 9999999
        # Resolution x, y, and direction flag
        xo, yo, fo = 0, 0, 0

        if (rf & PH_LWALL) and 0 < leftOverlap < smallestOverlap:
            xo = leftOverlap
            yo = 0
            fo = PH_LWALL
            smallestOverlap = leftOverlap
        if (rf & PH_RWALL) and 0 < -rightOverlap < smallestOverlap:
            xo = rightOverlap
            yo = 0
            fo = PH_RWALL
            smallestOverlap = -rightOverlap
        if (rf & PH_HEADBANG) and 0 < topOverlap < smallestOverlap:
            xo = 0
            yo = topOverlap
            fo = PH_HEADBANG
            smallestOverlap = topOverlap
        if (rf & PH_GROUNDED) and 0 < -bottomOverlap < smallestOverlap:
            xo = 0
            yo = bottomOverlap
            fo = PH_GROUNDED
            smallestOverlap = -bottomOverlap

        # Apply resolution for that axis. We don't have to worry about
        # overriding other hitboxes, because either they agree on the direction
        # (in which case max is correct) or we'll drop the axis later.
        if abs(xo) > abs(resolution.x):
            resolution.x = xo
        if abs(yo) > abs(resolution.y):
            resolution.y = yo
        flags |= fo

    debug_resolution = physics_player_hitbox(pos + diff + resolution)

    # If we're clipping super far, just refuse the movement entirely. This
    # shouldn't happen at low speeds. Abort and stay inbounds.
    if max(resolution.x, resolution.y) >= 15:
        return pos, PH_TOOFAST

    # Otherwise, clamp the offending directions and try to reposition. Don't
    # resolve if we have opposite resolution directions *on the same axis* from
    # from different hitboxes.
    adjusted = pos + diff
    if (PH_LWALL | PH_RWALL) & ~flags:
        adjusted.x += resolution.x
    if (PH_HEADBANG | PH_GROUNDED) & ~flags:
        adjusted.y += resolution.y

    if physics_acceptable(room, adjusted):
        return adjusted, flags
    else:
        return pos, flags | PH_FAILED

def player_set_stance(player, stance):
    if player.stance == stance:
        return

    player.stance = stance
    if stance == STANCE_IDLE:
        player.anim.set(sprites["Idle"])
    elif stance == STANCE_RUNNING:
        player.anim.set(sprites["Running"])
    elif stance == STANCE_JUMPING:
        player.anim.set(sprites["Jumping"])
    elif stance == STANCE_HURT:
        player.anim.set(sprites["Hurt"])
    elif stance == STANCE_VICTORY:
        player.anim.set(sprites["Victory"])

def player_set_facing(player, facing):
    player.facing = facing

def game_update(game, dt, input):
    if game.end_timer < 0:
        game.time += dt
    if game.intcard_time > 0:
        game.intcard_time = max(game.intcard_time - dt, 0)
        return 0, False

    player = game.player
    player.anim.update(dt)

    newentities = []
    for pos, e in game.entities:
        if not e.update(dt):
            newentities.append((pos, e))
    game.entities = newentities

    if game.end_timer > 0:
        game.end_timer -= dt
        if game.end_timer <= 0:
            return 0, "END"
        return 0, False

    if game.reset_timer > 0:
        game.reset_timer -= dt
        if game.reset_timer <= 0:
            game.reset_timer = -1
            game.player.pos.x = game.room.spawn_x
            game.player.pos.y = game.room.spawn_y
            game.player.speed.x = 0
            game.player.speed.y = 0
            game.deaths += 1
        return 0, False

    if player.noncontrol_frames > 0:
        # TODO: Reset input to 0
        player.noncontrol_frames -= 1
        # HACK: Reset stance at end of interaction
        if not player.noncontrol_frames:
            player_set_stance(player, STANCE_IDLE)

    has_jb = input.jump_buffer > 0
    if input.jump_buffer:
        input.jump_buffer -= 1
        # Normal jump
        if player.grounded():
            player.speed.y = -140
            player.jump_frames = 5
            input.jump_buffer = 0

    player.speed.x *= 0.95
    if input.dx > 0:
        player.speed.x = max(player.speed.x, 64)
    elif input.dx < 0:
        player.speed.x = min(player.speed.x, -64)
    else:
        player.speed.x = int(player.speed.x * 0.5)
    if player.airborne():
        player.speed.y += 9.81 * dt * 30

    if player.jump_frames > 0:
        # jump impulsion overrides gravity?
        if not input.jump_down:
            player.speed.y = max(player.speed.y, -20)
        player.jump_frames -= 1

    if player.grounded():
        if player.speed.x:
            player_set_stance(player, STANCE_RUNNING)
        else:
            player_set_stance(player, STANCE_IDLE)
    else:
        player_set_stance(player, STANCE_JUMPING)

    if player.speed.x > 0:
        player_set_facing(player, FACING_RIGHT)
    elif player.speed.x < 0:
        player_set_facing(player, FACING_LEFT)

    player.pos, flags = \
        physics_displace(game.room, player.pos, player.speed * dt)
    death = (flags & PH_DEATH) != 0

    player._grounded = (flags & PH_GROUNDED) != 0

    # Ground bounce
    if has_jb and flags == PH_GROUNDED and abs(player.speed.x) > 0 and player.speed.y > 80:
        player.speed.y = -player.speed.y
        player.speed.x *= 1.5
        player.speed.y = max(-200, min(player.speed.y * 1.2, -100))
        input.jump_buffer = 0
        vfx = animstateT()
        vfx.set(bounce[None])
        game.entities.append((player.pos, vfx))
    # Left wall bounce
    elif has_jb and flags == PH_LWALL and player.speed.x < -60 and player.speed.y < 0:
        player.speed.x = -player.speed.x
        player.speed.y = max(-200, min(player.speed.y * 1.3, -100))
        player.speed.x = max(player.speed.x * 1.2, 128)
        input.jump_buffer = 0
        vfx = animstateT()
        vfx.set(bounce[None])
        game.entities.append((player.pos, vfx))
    # Right wall bounce
    elif has_jb and flags == PH_RWALL and player.speed.x > 60 and player.speed.y < 0:
        player.speed.x = -player.speed.x
        player.speed.y = max(-200, min(player.speed.y * 1.3, -100))
        player.speed.x = min(player.speed.x * 1.2, -128)
        input.jump_buffer = 0
        vfx = animstateT()
        vfx.set(bounce[None])
        game.entities.append((player.pos, vfx))
    else:
        if flags & (PH_LWALL | PH_RWALL | PH_TOOFAST | PH_FAILED):
            player.speed.x = 0
        if flags & (PH_HEADBANG | PH_TOOFAST | PH_FAILED):
            player.speed.y = max(player.speed.y, 0)
        if flags & PH_GROUNDED:
            player.speed.y = 20  # HACK: non-zero to keep hitting the ground
    game.toofast_frames += (flags & PH_TOOFAST) != 0
    game.physics_failed_frames += (flags & PH_FAILED) != 0

    # Pick up flags
    pr = physics_player_hitbox(player.pos)
    for r, _, solid in game.room.hitboxesNear(pr):
        if solid == SOLID_FLAG and pr.intersects(r):
            # HACK: Backwards world to tile grid conversion
            x, y = int(r.x) >> 4, int(r.y) >> 4
            game.takeFlag(x, y)

    # if input.interact:
    #     iid = physics_interaction(game.room, player.pos)
    #     if iid >= 0:
    #         pass # TODO: interactions
    #         player.speed.x = 0
    #         player.speed.y = 0
    #         # TODO: Set interaction stance
    #         player.noncontrol_frames = 20
    #         game.intcard_time = 8.0

    return flags, death

def world2screen(pos):
    return vec2(MAP_X + int(pos.x), MAP_Y + int(pos.y))
def world2screen_rect(r):
    return rect(MAP_X + int(r.x), MAP_Y + int(r.y), int(r.w), int(r.h))
def screen2world_rect(r):
    return rect(r.x - MAP_X, r.y - MAP_Y, r.w, r.h)

def draw_rect(game, r, color):
    game.markTilesDirty(r)
    r = world2screen_rect(r)
    drect(r.x, r.y, r.x+r.w-1, r.y+r.h-1, color)

def draw_outline(game, r, color):
    game.markTilesDirty(r)
    r = world2screen_rect(r)
    drect_border(r.x, r.y, r.x+r.w-1, r.y+r.h-1, C_NONE, 1, color)

def draw_flagged_outline(game, r, rb, color1, color2):
    game.markTilesDirty(r)
    r = world2screen_rect(r)
    dline(r.x, r.y, r.x+r.w-1, r.y,
        color2 if rb & PH_GROUNDED else color1)
    dline(r.x, r.y+r.h-1, r.x+r.w-1, r.y+r.h-1,
        color2 if rb & PH_HEADBANG else color1)
    dline(r.x, r.y, r.x, r.y+r.h-1,
        color2 if rb & PH_RWALL else color1)
    dline(r.x+r.w-1, r.y, r.x+r.w-1, r.y+r.h-1,
        color2 if rb & PH_LWALL else color1)

def draw_hud(game, input, flags, frame_time, debug):
    player = game.player
    x, y = HUD_X, HUD_Y
    drect(x, y, x+HUD_W-1, y+HUD_H-1, RGB24(0x332816))
    x += 2
    y += 4

    if debug > 0:
        dtext(x, y, C_WHITE, "======")

        inps = "[I]"
        if input.dx < 0:
            inps += " <"
        if input.dx > 0:
            inps += " >"
        if input.jump_down or input.jump_buffer:
            inps += " {}{}".format("J" if input.jump_down else "j", input.jump_buffer)
        if input.interact:
            inps += " i"
        dtext(x, y+15, C_WHITE, inps)

        dtext(x, y+30, C_WHITE, "airborne" if player.airborne() else "grounded")
        dtext(x, y+45, C_WHITE, "x={}".format(player.pos.x))
        dtext(x, y+60, C_WHITE, "y={}".format(player.pos.y))
        dtext(x, y+75, C_WHITE, "vx={}".format(player.speed.x))
        dtext(x, y+90, C_WHITE, "vy={}".format(player.speed.y))

        fl = "[F]"
        if flags & PH_LWALL:
            fl += " L"
        if flags & PH_RWALL:
            fl += " R"
        if flags & PH_GROUNDED:
            fl += " G"
        if flags & PH_HEADBANG:
            fl += " H"
        dtext(x, y+105, C_WHITE, fl)

        tff = game.toofast_frames
        phff = game.physics_failed_frames
        dtext(x, y+120, C_RED if tff or phff else C_WHITE, "PH: {} {}".format(tff, phff))
        dtext(x, y+135, C_WHITE, "ft: {} ms".format(frame_time))
    else:
        dtext(x, y, C_WHITE, "Flags: {}/{}".format(game.flags_taken,
            len(game.room.flag_sequence)))
        dtext(x, y+15, C_WHITE, "Deaths: {}".format(game.deaths))
        dtext(x, y+30, C_WHITE, "Time: {:.1f}".format(game.time))

def draw_player(game, p):
    flipped = (p.facing == FACING_LEFT)

    base = world2screen(p.pos)
    if p.anim.index >= 0:
        f = p.anim.frames[p.anim.index]
        img, cx = f.img, f.cx
        if flipped:
            img, cx = f.imgH, f.w - 1 - cx
        dsubimage(base.x - cx, base.y - f.cy, img, f.x, f.y, f.w, f.h)
        dirty_r = screen2world_rect(rect(base.x - cx, base.y - f.cy, f.w, f.h))
        game.markTilesDirty(dirty_r)
        # draw_outline(game, dirty_r, C_WHITE)

def draw_entity(game, pos, anim):
    base = world2screen(pos)
    if anim.index >= 0:
        f = anim.frames[anim.index]
        dsubimage(base.x - f.cx, base.y - f.cy, f.img, f.x, f.y, f.w, f.h)
        dirty_r = screen2world_rect(rect(base.x - f.cx, base.y - f.cy, f.w, f.h))
        game.markTilesDirty(dirty_r)

def draw_tile(x, y, tileset, tileID):
    img = tileset.img
    x = MAP_X + 16 * x
    y = MAP_Y + 16 * y
    w = img.width >> 4
    tx = tileID % w
    ty = tileID // w
    if 16 * ty < img.height:
        dsubimage(x, y, img, 176, 48, 16, 16)
        dsubimage(x, y, img, 16*(tileID % w), 16*(tileID // w), 16, 16)
    else:
        dsubimage(x, y, img, 176, 48, 16, 16)

def draw_room(game, room, dirty_tiles):
    i = 0
    for ty in range(room.h):
        for tx in range(room.w):
            t = room.tiles[i]
            # Flag that hasn't appeared or has been taken
            if t == 101 and game.flags.get((tx, ty), True):
                t = 0xff
            if dirty_tiles[i]:
                draw_tile(tx, ty, room.tileset, t)
            dirty_tiles[i] = 0
            i += 1

def gen_sample_room(room):
    for ty in range(room.h):
        for tx in range(room.w):
            if ty == 0 or ty == WH-1 or tx == 0 or tx == WW-1:
                tileID = 0xff
            elif ty == WH-2:
                tileID = 4
            else:
                tileID = (tx ^ ty) & 1
            room.tiles[ty * room.w + tx] = tileID

def RGB24(rgb):
    r, g, b = rgb >> 19, (rgb >> 10) & 0x3f, (rgb >> 3) & 0x1f
    return (r << 11) + (g << 5) + b

def main():
    debug_hitboxes = 0

    # Patch conversion type
    for _, frames in sprites.items():
        for i in range(len(frames)):
            frames[i] = animframeT(*frames[i])
    # Patch conversion type
    for _, frames in bounce.items():
        for i in range(len(frames)):
            frames[i] = animframeT(*frames[i])
    # Patch conversion type
    global tileset
    tileset = tilesetT(*tileset)

    flag_sequence = [
        (15, 13, 1),
        (19, 10, 2),
        (11,  6, 1),
        ( 5,  5, 1),
        (17,  2, 0),
        ( 1,  8, 0),
    ]
    room = roomT(WW, WH, 32, 224, [], [], tileset, flag_sequence)
    room.tiles = room_level1[2]
    room.computeTileCollisions()
    # room.tiles = bytearray(room.w * room.h)
    # gen_sample_room(room)

    player = playerT()
    player.initialize(vec2(room.spawn_x, room.spawn_y))
    player_set_stance(player, STANCE_IDLE)

    game = gameT()
    game.startLevel(room, player)
    game.showNextFlags(1)

    input = inputT()
    flags = 0
    frame_time = 0

    while True:
        frame_start = time.monotonic()
        draw_room(game, game.room, game.dirty_tiles)
        for pos, e in game.entities:
            draw_entity(game, pos, e)
        draw_player(game, player)
        draw_hud(game, input, flags, frame_time, debug_hitboxes)

        if debug_hitboxes == 2:
            for b, bf, _ in room.hitboxesAll():
                draw_flagged_outline(game, b, bf, 0xf800, 0xffff)
            for b in room.intboxes():
                draw_outline(game, b, 0xffe0)

        if debug_hitboxes >= 1:
            phb = physics_player_hitbox(player.pos)
            draw_outline(game, debug_resolution, C_RGB(0,15,0))
            draw_outline(game, phb, 0x07e0)
            draw_rect(game, rect(player.pos.x, player.pos.y, 1, 1), C_WHITE)

        dupdate()

        cleareventflips()
        clearevents()
        input.dx = keydown(KEY_RIGHT) - keydown(KEY_LEFT)
        input.jump_down = keydown(KEY_SHIFT) or keydown(KEY_UP)
        if keypressed(KEY_SHIFT) or keypressed(KEY_UP):
            input.jump_buffer = 3
        input.interact = keydown(KEY_ALPHA) or keydown(KEY_DOWN)

        if keypressed(KEY_OPTN):
            debug_hitboxes = (debug_hitboxes + 1) % 3

        # Simulate as if a fixed 20 FPS, which is the target framerate
        # 55 ms ≈ 7 RTC ticks, which is what we use to throttle
        flags, death = game_update(game, 0.055, input)
        if death == "END":
            break

        # Ignore death, would be epic.
        if game.flags_taken >= len(game.room.flag_sequence) and game.end_timer < 0:
            player_set_stance(game.player, STANCE_VICTORY)
            game.end_timer = 3

        # HACK: Avoid out-of-bounds
        if player.pos.x < 0 or player.pos.x > 16 * room.w or \
           player.pos.y < 0 or player.pos.y > 16 * room.h:
            death = True

        frame_time = int((time.monotonic() - frame_start) * 1e-6)

        if frame_time < 53:
            time.sleep_ms(53 - frame_time)

        if keydown(KEY_F6):
            time.sleep(0.5)
        if keydown(KEY_VARS) or death:
            player_set_stance(player, STANCE_HURT)
            game.reset_timer = 0.6
        if keypressed(KEY_POWER):
            game.showNextFlags(1)

# Polyfill

import time

# Polyfill for time.sleep_ms on platforms that don't have it
if not hasattr(time, 'sleep_ms'):
    def sleep_ms(ms: int) -> None:
        """Sleep for the given number of milliseconds."""
        time.sleep(ms / 1000.0)
    time.sleep_ms = sleep_ms

main()
