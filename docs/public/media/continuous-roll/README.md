# Continuous-roll tutorial media

Robot: Pollen Robotics MicroDuck, rendered from this project's upstream-derived
USD. Model source: <https://github.com/pollen-robotics/microduck_rl>, revision
`d424a0c899f6b33cbd3daeb279913134349c0b63`. See the repository's
`NOTICE-MICRODUCK.md` for attribution and the upstream “Creative Commons
BY-SA-NC” model terms (the upstream notice does not state a version).

Project session: `roll120-20260904-073725`, recorded 2026-09-04. Selected policy:
trial 3, checkpoint 600. These are flat-ground Isaac simulation recordings.

- `continuous-forward-roll.mp4`: complete 50-second recording, 1920 × 1080,
  25 fps, no audio. Re-encoded as H.264 / yuv420p, CRF 26, fast-start metadata.
  Frame order, playback speed, and duration are unchanged.
- `poster.jpg`: frame at 0.8 seconds, scaled to 1280 × 720.
- `first-rolls.mp4`: first 10 seconds of the first-round checkpoint-100 replay,
  after reset-height correction and arena enlargement; 1280 × 720, 25 fps,
  H.264, no audio. This excerpt illustrates the intermediate behavior, not
  the complete 30-second measurement.

Original 50-second recording SHA-256:
`cbb07968ca83f969d541393ca4edb6170175c60db735ffaa7a0dc19c81304f7c`.

Selected checkpoint SHA-256:
`fd2c5bbc9e2711376f407309a7f4725de853f71f56f6e5dae9e27a81a500ec66`.

The original recording and model remain in the project output archive. This
web-media directory does not contain model weights, machine paths, or raw logs.
