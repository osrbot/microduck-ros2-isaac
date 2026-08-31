# Contributing

Thank you for improving MicroDuck ROS 2 + Isaac Sim. Start with the bilingual
[contribution guide](https://osrbot.github.io/microduck-ros2-isaac/project/contributing)
or its [Chinese version](https://osrbot.github.io/microduck-ros2-isaac/zh/project/contributing).

At minimum, keep upstream inputs pinned, preserve the mixed-license attribution
boundary, do not commit local environments or fetched policies, and report what
was actually tested. Documentation changes must pass:

```bash
npm ci
npm audit --audit-level=high
npm run docs:build
```

Cross-layer code changes should run `./scripts/validate_all.sh` when the required
ROS, MuJoCo, and Isaac environments are available.
