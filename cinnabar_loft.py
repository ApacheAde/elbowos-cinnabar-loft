#!/usr/bin/env python3
"""CINNABAR LOFT — neon louver-ascent arcade for ElbowOS. Python 3 + pygame."""
import math, os, random, subprocess, sys

RECORD = "--record" in sys.argv or os.environ.get("ELBOWOS_RECORD") == "1"
PLAY = "--play" in sys.argv
if RECORD or not PLAY:
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

W, H, FPS, SECS = 1080, 1920, 30, 15
OUT = os.environ.get("ELBOWOS_MP4", "/home/workdir/artifacts/CINNABAR_LOFT_ElbowOS.mp4")
TITLE, HANDLE = "CINNABAR LOFT", "x.com/ElbowOS"

INK = (18, 6, 8)
WINE = (48, 10, 16)
RUST = (128, 28, 22)
CINN = (232, 58, 36)
EMBER = (255, 96, 42)
AMBER = (255, 168, 48)
GOLD = (255, 214, 92)
CREAM = (255, 236, 210)
LIME = (186, 255, 92)
TEAL = (48, 210, 196)
WHITE = (255, 248, 240)


class Game:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        flags = 0 if PLAY else pygame.HIDDEN
        try:
            self.screen = pygame.display.set_mode((W, H), flags)
        except pygame.error:
            os.environ["SDL_VIDEODRIVER"] = "dummy"
            pygame.display.quit()
            pygame.display.init()
            self.screen = pygame.display.set_mode((W, H))
        pygame.display.set_caption(TITLE)
        self.font_lg = pygame.font.SysFont("DejaVu Sans", 54, bold=True)
        self.font = pygame.font.SysFont("DejaVu Sans", 34, bold=True)
        self.font_sm = pygame.font.SysFont("DejaVu Sans", 24)
        self.clock = pygame.time.Clock()
        self.reset()

    def reset(self):
        self.t = self.score = self.combo = self.flash = self.banner = 0
        self.banner_txt = ""
        self.px, self.py = W * 0.5, 1480
        self.vx = 0
        self.heat = 3
        self.scroll = 0
        self.sparks, self.embers, self.motes = [], [], []
        self.louvers = []
        for i in range(8):
            self.louvers.append(self.make_louver(-220 - i * 260))
        for _ in range(70):
            self.motes.append([random.randrange(W), random.randrange(H),
                               random.uniform(1.2, 3.4), random.choice((RUST, AMBER, CINN))])

    def make_louver(self, y):
        gap = random.uniform(0.18, 0.55)
        span = random.uniform(0.22, 0.34)
        spd = random.choice((-1, 1)) * random.uniform(0.018, 0.038)
        return [y, gap, span, spd, False]

    def burst(self, x, y, col, n=12):
        for _ in range(n):
            a = random.uniform(0, 6.2832)
            sp = random.uniform(1.4, 9)
            self.sparks.append([x, y, math.cos(a) * sp, math.sin(a) * sp, 18, col])

    def autoplay(self):
        upcoming = [lv for lv in self.louvers if self.py - 420 < lv[0] < self.py + 40]
        target = W * 0.5
        if upcoming:
            lv = min(upcoming, key=lambda z: abs(z[0] - self.py))
            gap, span = lv[1], lv[2]
            target = (gap + span * 0.5) * W
        err = target - self.px
        self.vx += max(-1.8, min(1.8, err * 0.018))
        self.vx *= 0.86

    def tick(self):
        self.t += 1
        self.flash = max(0, self.flash - 1)
        self.banner = max(0, self.banner - 1)
        self.px = max(70, min(W - 70, self.px + self.vx))
        rise = 7.4 + min(4.0, self.combo * 0.12)
        self.scroll += rise
        self.py -= 0.35
        if self.py < 1180:
            self.py += 0.8
        for m in self.motes:
            m[1] += m[2] + rise * 0.25
            if m[1] > H:
                m[0], m[1] = random.randrange(W), -12
        for lv in self.louvers:
            lv[0] += rise
            lv[1] = (lv[1] + lv[3]) % 1.0
            if lv[0] > H + 80:
                lv[0] = min(z[0] for z in self.louvers) - 260
                lv[1] = random.uniform(0.12, 0.62)
                lv[2] = random.uniform(0.20, 0.32)
                lv[3] = random.choice((-1, 1)) * random.uniform(0.018, 0.04)
                lv[4] = False
            if not lv[4] and abs(lv[0] - self.py) < rise:
                gx0, gx1 = lv[1] * W, (lv[1] + lv[2]) * W
                if gx1 > W:
                    ok = self.px > gx0 or self.px < gx1 - W
                else:
                    ok = gx0 <= self.px <= gx1
                if ok:
                    lv[4] = True
                    self.combo += 1
                    self.score += 25 + self.combo * 5
                    self.burst(self.px, self.py, GOLD, 16)
                    if self.combo % 8 == 0:
                        self.banner, self.banner_txt = 26, "THERMAL +"
                        self.heat = min(5, self.heat + 1)
                else:
                    self.combo = 0
                    self.heat -= 1
                    self.flash = 10
                    self.burst(self.px, lv[0], CINN, 22)
                    if self.heat <= 0:
                        self.banner, self.banner_txt = 36, "REKINDLE"
                        self.heat = 3
                        self.px = W * 0.5
        if self.t % 3 == 0:
            self.embers.append([self.px + random.uniform(-10, 10), self.py + 18,
                                random.uniform(-0.6, 0.6), random.uniform(3, 7), 16])
        for e in self.embers:
            e[0] += e[2]
            e[1] += e[3]
            e[4] -= 1
        self.embers = [e for e in self.embers if e[4] > 0]
        for sp in self.sparks:
            sp[0] += sp[2]
            sp[1] += sp[3]
            sp[4] -= 1
        self.sparks = [s for s in self.sparks if s[4] > 0]

    def draw_moth(self, surf):
        x, y = int(self.px), int(self.py)
        flap = 18 + int(10 * math.sin(self.t * 0.45))
        pygame.draw.ellipse(surf, EMBER, (x - flap - 8, y - 10, flap + 6, 22))
        pygame.draw.ellipse(surf, AMBER, (x + 2, y - 10, flap + 6, 22))
        pygame.draw.ellipse(surf, GOLD, (x - 16, y - 22, 32, 40))
        pygame.draw.circle(surf, CREAM, (x, y - 8), 10)
        pygame.draw.circle(surf, INK, (x - 4, y - 10), 3)
        pygame.draw.circle(surf, INK, (x + 4, y - 10), 3)
        glow = 16 + int(6 * math.sin(self.t * 0.3))
        pygame.draw.circle(surf, LIME if self.combo > 4 else TEAL, (x, y), glow + 10, 3)

    def draw(self, surf):
        for i in range(28):
            t = i / 27
            pygame.draw.rect(surf, (int(18 + 30 * t), int(6 + 8 * t), int(8 + 6 * (1 - t))),
                             (0, int(i * H / 28), W, H // 28 + 2))
        for m in self.motes:
            pygame.draw.circle(surf, m[3], (int(m[0]), int(m[1])), 3)
        pygame.draw.rect(surf, WINE, (36, 150, 28, H - 280), border_radius=10)
        pygame.draw.rect(surf, WINE, (W - 64, 150, 28, H - 280), border_radius=10)
        for lv in self.louvers:
            y = int(lv[0])
            if y < 120 or y > H - 80:
                continue
            g0, g1 = lv[1] * W, (lv[1] + lv[2]) * W
            pygame.draw.rect(surf, RUST, (50, y - 16, W - 100, 32), border_radius=8)
            if g1 <= W:
                pygame.draw.rect(surf, INK, (int(g0), y - 18, int(g1 - g0), 36))
                pygame.draw.rect(surf, AMBER, (int(g0), y - 18, int(g1 - g0), 36), 3)
            else:
                pygame.draw.rect(surf, INK, (int(g0), y - 18, int(W - g0 - 50), 36))
                pygame.draw.rect(surf, INK, (50, y - 18, int(g1 - W), 36))
            pygame.draw.rect(surf, CINN, (50, y - 16, W - 100, 32), 2, border_radius=8)
        for e in self.embers:
            pygame.draw.circle(surf, EMBER, (int(e[0]), int(e[1])), max(2, e[4] // 4))
        self.draw_moth(surf)
        for sp in self.sparks:
            pygame.draw.circle(surf, sp[5], (int(sp[0]), int(sp[1])), max(2, sp[4] // 3))
        if self.flash:
            ov = pygame.Surface((W, H), pygame.SRCALPHA)
            ov.fill((255, 40, 30, 40))
            surf.blit(ov, (0, 0))
        title = self.font_lg.render(TITLE, True, GOLD)
        surf.blit(title, title.get_rect(center=(W // 2, 56)))
        sub = self.font_sm.render(HANDLE, True, TEAL)
        surf.blit(sub, sub.get_rect(center=(W // 2, 108)))
        if self.banner:
            lab = self.font.render(self.banner_txt, True, LIME)
            surf.blit(lab, lab.get_rect(center=(W // 2, 160)))
        sc = self.font.render(f"SCORE  {self.score}", True, WHITE)
        cb = self.font_sm.render(f"COMBO  x{self.combo}    HEAT  {self.heat}", True, AMBER)
        hint = self.font_sm.render("A / D  drift the moth    ride the louvers", True, CREAM)
        surf.blit(sc, sc.get_rect(center=(W // 2, H - 118)))
        surf.blit(cb, cb.get_rect(center=(W // 2, H - 72)))
        surf.blit(hint, hint.get_rect(center=(W // 2, H - 32)))

    def play_interactive(self):
        running = True
        while running:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT or (ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE):
                    running = False
            keys = pygame.key.get_pressed()
            ax = 0
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                ax -= 1.6
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                ax += 1.6
            self.vx = self.vx * 0.86 + ax
            self.tick()
            self.draw(self.screen)
            pygame.display.flip()
            self.clock.tick(FPS)
        pygame.quit()

    def record(self):
        frames = FPS * SECS
        cmd = [
            "ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
            "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
            "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-crf", "20", "-preset", "fast", "-movflags", "+faststart",
            OUT,
        ]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        canvas = pygame.Surface((W, H))
        try:
            for i in range(frames):
                self.autoplay()
                self.tick()
                self.draw(canvas)
                proc.stdin.write(pygame.image.tostring(canvas, "RGB"))
                if i % 30 == 0:
                    print(f"frame {i}/{frames}", flush=True)
        finally:
            proc.stdin.close()
            err = proc.stderr.read().decode("utf-8", "ignore")
            rc = proc.wait()
        if rc != 0:
            raise SystemExit(f"ffmpeg failed ({rc}):\n{err[-1200:]}")
        print("wrote", OUT)
        pygame.quit()


def main():
    g = Game()
    if PLAY and not RECORD:
        g.play_interactive()
    else:
        g.record()


if __name__ == "__main__":
    main()
