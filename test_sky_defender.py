"""sky_defender 폭발 효과 테스트 (headless: SDL_VIDEODRIVER=dummy)

실행: python -m unittest test_sky_defender -v
"""
import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame  # noqa: E402

import sky_defender as sd  # noqa: E402


class ExplosionFramesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        pygame.init()
        pygame.display.set_mode((1, 1))
        cls.image = pygame.Surface((45, 45), pygame.SRCALPHA)
        cls.image.fill((255, 128, 0, 255))

    @classmethod
    def tearDownClass(cls) -> None:
        pygame.quit()

    def test_frame_count_and_growth(self) -> None:
        frames = sd.Explosion.build_frames(self.image, base_size=40, count=6,
                                           scale_range=(0.5, 1.5))
        self.assertEqual(len(frames), 6)
        self.assertEqual(frames[0].get_width(), 20)
        self.assertEqual(frames[-1].get_width(), 60)
        self.assertEqual(frames[0].get_alpha(), 255)
        self.assertEqual(frames[-1].get_alpha(), 0)

    def test_invalid_count_raises(self) -> None:
        with self.assertRaises(ValueError):
            sd.Explosion.build_frames(self.image, base_size=40, count=0)

    def test_empty_frames_raises(self) -> None:
        with self.assertRaises(ValueError):
            sd.Explosion([], (0, 0))

    def test_lifetime_and_center_fixed(self) -> None:
        frames = sd.Explosion.build_frames(self.image, base_size=40, count=4)
        group = pygame.sprite.Group()
        boom = sd.Explosion(frames, (100, 200), group)
        for _ in range(3):
            boom.update()
            self.assertTrue(boom.alive())
            self.assertEqual(boom.rect.center, (100, 200))
        boom.update()
        self.assertFalse(boom.alive())
        self.assertEqual(len(group), 0)


class GameExplosionTest(unittest.TestCase):
    def setUp(self) -> None:
        self.game = sd.Game()

    def tearDown(self) -> None:
        pygame.quit()

    def test_kill_spawns_explosion_at_enemy_center(self) -> None:
        enemy = sd.Enemy(self.game.enemy_img, self.game.enemy_mask,
                         self.game.all_sprites, self.game.enemies)
        enemy.rect.center = (300, 240)
        sd.Bullet(300, 250, self.game.all_sprites, self.game.bullets)

        self.game.check_collisions()

        self.assertEqual(self.game.score, sd.SCORE_PER_KILL)
        self.assertEqual(len(self.game.enemies), 0)
        self.assertEqual(len(self.game.effects), 1)
        boom = next(iter(self.game.effects))
        self.assertEqual(boom.rect.center, (300, 240))
        self.assertIn(boom, self.game.all_sprites)

    def test_explosion_not_counted_as_enemy(self) -> None:
        self.game.spawn_explosion((320, 470))   # 화면 하단 근처
        self.game.check_collisions()
        self.assertEqual(self.game.life, sd.START_LIFE)

    def test_reset_round_clears_effects(self) -> None:
        self.game.spawn_explosion((10, 10))
        self.game.reset_round()
        self.assertEqual(len(self.game.effects), 0)
        self.assertEqual(len(self.game.all_sprites), 1)   # player 만 남음

    def test_explosion_expires_via_group_update(self) -> None:
        self.game.spawn_explosion((10, 10))
        for _ in range(sd.EXPLOSION_FRAMES):
            self.game.effects.update()
        self.assertEqual(len(self.game.effects), 0)


if __name__ == "__main__":
    unittest.main()
