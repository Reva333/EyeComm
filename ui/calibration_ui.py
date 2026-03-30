from __future__ import annotations

import cv2
import os
import time
from dataclasses import dataclass

import numpy as np
import pygame

from config.settings import SCREEN_HEIGHT, SCREEN_WIDTH
from gaze.calibration import CalibrationProfile, CalibrationSample, build_profile

BG_GRAY = (112, 112, 112)
BG_HEAD = (96, 96, 96)
TEXT_DARK = (28, 28, 28)
TEXT_MUTED = (55, 55, 55)
TARGET_RED = (225, 20, 24)
TARGET_RED_DARK = (165, 15, 18)
TARGET_LINE = (15, 15, 15)

TARGET_RADIUS = 16
TARGET_RING = 28
TARGET_CROSS = 36
TARGET_DOT = 4
HEAD_GUIDE_W = 260
HEAD_GUIDE_H = 320
PREVIEW_W = 300
PREVIEW_H = 225

MOVE_DURATION = 1.4
HOLD_DURATION = 1.0
COLLECT_AFTER = 0.18

EYE_XS = (0.12, 0.38, 0.62, 0.88)
EYE_YS = (0.16, 0.38, 0.62, 0.84)
HEAD_POINTS = (
    (0.50, 0.08),
    (0.92, 0.50),
    (0.50, 0.92),
    (0.08, 0.50),
)


@dataclass(frozen=True)
class CalibrationStage:
    label: str
    title: str
    subtitle: str
    background: tuple[int, int, int]
    points: tuple[tuple[float, float], ...]
    sample_weight: float
    show_direction: bool = False


EYE_STAGE = CalibrationStage(
    label="Eye Tracking",
    title="Follow the target slowly with your eyes only.",
    subtitle="The target will stop for 1 second at each of 16 points.",
    background=BG_GRAY,
    points=tuple(
        (x, y)
        for row, y in enumerate(EYE_YS)
        for x in (EYE_XS if row % 2 == 0 else tuple(reversed(EYE_XS)))
    ),
    sample_weight=1.0,
)

HEAD_STAGE = CalibrationStage(
    label="Head Tracking",
    title="Follow the target with gentle head movement.",
    subtitle="The target now moves edge to edge and pauses for 1 second at each point.",
    background=BG_HEAD,
    points=HEAD_POINTS,
    sample_weight=0.9,
    show_direction=True,
)

STAGES = (EYE_STAGE, HEAD_STAGE)


class CalibrationUI:
    def __init__(self, shared_state):
        self.state = shared_state

    def run(self) -> CalibrationProfile | None:
        os.environ["SDL_VIDEO_WINDOW_POS"] = "0,0"
        pygame.init()
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.NOFRAME)
        pygame.display.set_caption("GazeControl Calibration")

        title_font = pygame.font.SysFont("Arial", 22)
        subtitle_font = pygame.font.SysFont("Arial", 18)
        meta_font = pygame.font.SysFont("Arial", 18)
        timer_font = pygame.font.SysFont("Arial", 26)
        arrow_font = pygame.font.SysFont("Arial", 72, bold=True)
        clock = pygame.time.Clock()

        while self.state.running:
            samples: list[CalibrationSample] = []
            current_target = (0.50, 0.50)
            if not self._run_positioning(
                screen,
                title_font,
                subtitle_font,
                meta_font,
                clock,
            ):
                pygame.quit()
                return None
            if not self._run_intro(
                screen,
                title_font,
                subtitle_font,
                timer_font,
                clock,
                current_target,
            ):
                pygame.quit()
                return None

            for stage in STAGES:
                for index, point in enumerate(stage.points):
                    move_start = time.time()
                    while self.state.running:
                        progress = (time.time() - move_start) / MOVE_DURATION
                        if progress >= 1.0:
                            break

                        if not self._handle_events():
                            pygame.quit()
                            return None

                        target = _interpolate(current_target, point, progress)
                        self._draw_frame(
                            screen=screen,
                            title_font=title_font,
                            subtitle_font=subtitle_font,
                            meta_font=meta_font,
                            timer_font=timer_font,
                            arrow_font=arrow_font,
                            stage=stage,
                            point_index=index,
                            target=target,
                            hold_remaining=None,
                        )
                        pygame.display.flip()
                        clock.tick(60)

                    current_target = point

                    hold_start = time.time()
                    last_timestamp = -1.0
                    while self.state.running:
                        hold_elapsed = time.time() - hold_start
                        if hold_elapsed >= HOLD_DURATION:
                            break

                        if not self._handle_events():
                            pygame.quit()
                            return None

                        measurement = self._snapshot_measurement()
                        if (
                            measurement is not None and
                            measurement.timestamp != last_timestamp and
                            hold_elapsed >= COLLECT_AFTER
                        ):
                            samples.append(
                                CalibrationSample(
                                    measurement=measurement,
                                    target_nx=point[0],
                                    target_ny=point[1],
                                    weight=stage.sample_weight,
                                )
                            )
                            last_timestamp = measurement.timestamp

                        self._draw_frame(
                            screen=screen,
                            title_font=title_font,
                            subtitle_font=subtitle_font,
                            meta_font=meta_font,
                            timer_font=timer_font,
                            arrow_font=arrow_font,
                            stage=stage,
                            point_index=index,
                            target=point,
                            hold_remaining=max(0.0, HOLD_DURATION - hold_elapsed),
                        )
                        pygame.display.flip()
                        clock.tick(60)

                if not self.state.running:
                    pygame.quit()
                    return None

            try:
                profile = build_profile(samples)
                pygame.quit()
                return profile
            except Exception:
                if not self._show_retry_screen(
                    screen,
                    title_font,
                    subtitle_font,
                    clock,
                ):
                    pygame.quit()
                    return None

        pygame.quit()
        return None

    def _run_intro(
        self,
        screen,
        title_font,
        subtitle_font,
        timer_font,
        clock,
        target,
    ) -> bool:
        intro_start = time.time()
        while self.state.running:
            elapsed = time.time() - intro_start
            if elapsed >= 3.0:
                return True

            if not self._handle_events():
                return False

            screen.fill(BG_GRAY)
            title = title_font.render(
                "Follow the target slowly. Keep still during eye tracking.",
                True,
                TEXT_DARK,
            )
            subtitle = subtitle_font.render(
                "Each point pauses for 1 second so the system can calibrate.",
                True,
                TEXT_MUTED,
            )
            countdown = timer_font.render(str(max(1, 3 - int(elapsed))), True, TEXT_DARK)
            screen.blit(title, ((SCREEN_WIDTH - title.get_width()) // 2, 96))
            screen.blit(subtitle, ((SCREEN_WIDTH - subtitle.get_width()) // 2, 128))
            self._draw_target(screen, target)
            screen.blit(
                countdown,
                ((SCREEN_WIDTH - countdown.get_width()) // 2, (SCREEN_HEIGHT // 2) + 62),
            )
            pygame.display.flip()
            clock.tick(60)

        return False

    def _run_positioning(
        self,
        screen,
        title_font,
        subtitle_font,
        meta_font,
        clock,
    ) -> bool:
        while self.state.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.state.running = False
                    return False
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_q, pygame.K_ESCAPE):
                        self.state.running = False
                        return False
                    if event.key == pygame.K_SPACE:
                        if self._snapshot_measurement() is not None:
                            return True

            measurement, frame = self._snapshot_frame()

            screen.fill(BG_GRAY)
            title = title_font.render(
                "Place your head inside the guide before tracking starts.",
                True,
                TEXT_DARK,
            )
            subtitle = subtitle_font.render(
                "Sit comfortably, face forward, then press SPACE to continue.",
                True,
                TEXT_MUTED,
            )
            status = meta_font.render(
                "Face detected" if measurement is not None else "Waiting for face detection...",
                True,
                TEXT_DARK if measurement is not None else TEXT_MUTED,
            )

            screen.blit(title, ((SCREEN_WIDTH - title.get_width()) // 2, 72))
            screen.blit(subtitle, ((SCREEN_WIDTH - subtitle.get_width()) // 2, 104))
            screen.blit(status, ((SCREEN_WIDTH - status.get_width()) // 2, 136))

            self._draw_head_guide(screen)
            self._draw_preview(screen, frame)

            pygame.display.flip()
            clock.tick(30)

        return False

    def _draw_frame(
        self,
        screen,
        title_font,
        subtitle_font,
        meta_font,
        timer_font,
        arrow_font,
        stage: CalibrationStage,
        point_index: int,
        target: tuple[float, float],
        hold_remaining: float | None,
    ):
        screen.fill(stage.background)

        title = title_font.render(stage.title, True, TEXT_DARK)
        subtitle = subtitle_font.render(stage.subtitle, True, TEXT_MUTED)
        progress_text = meta_font.render(
            f"{stage.label} {point_index + 1}/{len(stage.points)}",
            True,
            TEXT_MUTED,
        )

        screen.blit(title, ((SCREEN_WIDTH - title.get_width()) // 2, 88))
        screen.blit(subtitle, ((SCREEN_WIDTH - subtitle.get_width()) // 2, 120))
        screen.blit(progress_text, ((SCREEN_WIDTH - progress_text.get_width()) // 2, 152))

        if stage.show_direction:
            arrow = arrow_font.render(_arrow_for_point(target), True, TEXT_DARK)
            screen.blit(arrow, ((SCREEN_WIDTH - arrow.get_width()) // 2, 194))

        self._draw_target(screen, target)

        if hold_remaining is not None:
            hold_text = timer_font.render(
                f"{hold_remaining:0.1f}s",
                True,
                TEXT_DARK,
            )
            tx = int(target[0] * SCREEN_WIDTH)
            ty = int(target[1] * SCREEN_HEIGHT)
            screen.blit(
                hold_text,
                (tx - hold_text.get_width() // 2, ty + 62),
            )

    def _draw_target(self, screen, target: tuple[float, float]):
        tx = int(target[0] * SCREEN_WIDTH)
        ty = int(target[1] * SCREEN_HEIGHT)

        pygame.draw.circle(screen, TARGET_RED_DARK, (tx, ty), TARGET_RING + 2)
        pygame.draw.circle(screen, TARGET_RED, (tx, ty), TARGET_RING)
        pygame.draw.circle(screen, TARGET_RED_DARK, (tx, ty), TARGET_RADIUS)
        pygame.draw.circle(screen, TARGET_LINE, (tx, ty), TARGET_RING, 2)
        pygame.draw.circle(screen, TARGET_LINE, (tx, ty), TARGET_RADIUS, 2)
        pygame.draw.line(
            screen,
            TARGET_LINE,
            (tx - TARGET_CROSS, ty),
            (tx + TARGET_CROSS, ty),
            2,
        )
        pygame.draw.line(
            screen,
            TARGET_LINE,
            (tx, ty - TARGET_CROSS),
            (tx, ty + TARGET_CROSS),
            2,
        )
        pygame.draw.circle(screen, TARGET_LINE, (tx, ty), TARGET_DOT)

    def _show_retry_screen(self, screen, title_font, subtitle_font, clock) -> bool:
        while self.state.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.state.running = False
                    return False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        self.state.running = False
                        return False
                    if event.key == pygame.K_r:
                        return True

            screen.fill(BG_GRAY)
            title = title_font.render(
                "Calibration was unstable. Press R to retry or Q to quit.",
                True,
                TEXT_DARK,
            )
            subtitle = subtitle_font.render(
                "Keep your face visible and wait for each 3 second hold.",
                True,
                TEXT_MUTED,
            )
            screen.blit(title, ((SCREEN_WIDTH - title.get_width()) // 2, 110))
            screen.blit(subtitle, ((SCREEN_WIDTH - subtitle.get_width()) // 2, 142))
            self._draw_target(screen, (0.50, 0.50))
            pygame.display.flip()
            clock.tick(30)

        return False

    def _snapshot_measurement(self):
        with self.state.lock:
            return self.state.latest_measurement

    def _snapshot_frame(self):
        with self.state.lock:
            measurement = self.state.latest_measurement
            frame = None if self.state.frame is None else self.state.frame.copy()
        return measurement, frame

    def _handle_events(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.state.running = False
                return False
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_q, pygame.K_ESCAPE):
                self.state.running = False
                return False
        return True

    def _draw_head_guide(self, screen):
        cx = SCREEN_WIDTH // 2
        cy = SCREEN_HEIGHT // 2 + 24
        rect = pygame.Rect(0, 0, HEAD_GUIDE_W, HEAD_GUIDE_H)
        rect.center = (cx, cy)

        pygame.draw.ellipse(screen, (150, 150, 150), rect, 3)
        inner = rect.inflate(-48, -64)
        pygame.draw.ellipse(screen, (176, 176, 176), inner, 1)
        pygame.draw.line(screen, (140, 140, 140), (cx, rect.top + 10), (cx, rect.bottom - 10), 1)
        pygame.draw.line(screen, (140, 140, 140), (rect.left + 10, cy), (rect.right - 10, cy), 1)

    def _draw_preview(self, screen, frame):
        panel = pygame.Rect(0, 0, PREVIEW_W + 16, PREVIEW_H + 16)
        panel.topright = (SCREEN_WIDTH - 42, 54)
        pygame.draw.rect(screen, (92, 92, 92), panel, border_radius=16)

        preview_rect = pygame.Rect(0, 0, PREVIEW_W, PREVIEW_H)
        preview_rect.center = panel.center

        if frame is None:
            pygame.draw.rect(screen, (128, 128, 128), preview_rect, border_radius=12)
            return

        preview = cv2.resize(frame, (PREVIEW_W, PREVIEW_H))
        preview = cv2.cvtColor(preview, cv2.COLOR_BGR2RGB)
        surface = pygame.surfarray.make_surface(np.transpose(preview, (1, 0, 2)))
        screen.blit(surface, preview_rect.topleft)
        pygame.draw.rect(screen, (170, 170, 170), preview_rect, 1, border_radius=12)


def _interpolate(
    start: tuple[float, float],
    end: tuple[float, float],
    progress: float,
) -> tuple[float, float]:
    progress = max(0.0, min(progress, 1.0))
    smooth = progress * progress * (3.0 - 2.0 * progress)
    return (
        start[0] + (end[0] - start[0]) * smooth,
        start[1] + (end[1] - start[1]) * smooth,
    )


def _arrow_for_point(point: tuple[float, float]) -> str:
    x, y = point
    if y <= 0.2:
        return "^"
    if y >= 0.8:
        return "v"
    if x <= 0.2:
        return "<"
    return ">"
