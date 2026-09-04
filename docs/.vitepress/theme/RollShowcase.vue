<script setup lang="ts">
import { computed } from 'vue'
import { useData, withBase } from 'vitepress'
import result from './roll-case.json'

const { lang } = useData()
const copy = computed(() => lang.value.startsWith('zh') ? {
  video: 'MicroDuck 在 Isaac 仿真中连续前滚翻，50 秒完整演示，无解说音轨',
  fallback: '浏览器无法播放时，可使用下方链接打开视频。',
  title: '先看终点：一圈接着一圈，连续翻起来。',
  caption: '50 秒完整回放 · Isaac 平地仿真 · 1080p / 25 fps · 点击播放，无解说音轨',
  results: '本段视频的回放结果',
  turns: '连续前滚翻', resets: '中途重置', gap: '最长翻转间隔',
  turnUnit: ' 圈', resetUnit: ' 次', timeUnit: ' 秒',
  open: '单独打开完整视频 ↗'
} : {
  video: 'MicroDuck performing continuous forward rolls in Isaac simulation: full 50-second replay, without narration',
  fallback: 'If your browser cannot play the video, open it using the link below.',
  title: 'The goal: one forward roll after another.',
  caption: 'Full 50-second replay · Isaac flat-ground simulation · 1080p / 25 fps · Press play; no narration',
  results: 'Results from this video run',
  turns: 'Consecutive rolls', resets: 'Resets', gap: 'Longest turn gap',
  turnUnit: ' turns', resetUnit: '', timeUnit: ' s',
  open: 'Open the full video ↗'
})
</script>

<template>
  <figure class="roll-showcase">
    <video
      controls
      playsinline
      preload="metadata"
      width="1920"
      height="1080"
      :poster="withBase('/media/continuous-roll/poster.jpg')"
      :aria-label="copy.video"
    >
      <source :src="withBase('/media/continuous-roll/continuous-forward-roll.mp4')" type="video/mp4" />
      {{ copy.fallback }}
    </video>
    <figcaption>
      <strong>{{ copy.title }}</strong>
      <span>{{ copy.caption }}</span>
    </figcaption>
    <dl class="roll-stats" :aria-label="copy.results">
      <div><dt>{{ copy.turns }}</dt><dd>{{ result.video.consecutive_turns }}<small>{{ copy.turnUnit }}</small></dd></div>
      <div><dt>{{ copy.resets }}</dt><dd>{{ result.video.resets }}<small>{{ copy.resetUnit }}</small></dd></div>
      <div><dt>{{ copy.gap }}</dt><dd>{{ result.video.maximum_full_turn_gap_seconds.toFixed(2) }}<small>{{ copy.timeUnit }}</small></dd></div>
    </dl>
    <a class="roll-video-link" :href="withBase('/media/continuous-roll/continuous-forward-roll.mp4')">{{ copy.open }}</a>
  </figure>
</template>

<style scoped>
.roll-showcase { margin: 24px 0; overflow: hidden; border: 1px solid var(--vp-c-divider); border-radius: 16px; background: var(--vp-c-bg-soft); }
video { display: block; width: 100%; height: auto; aspect-ratio: 16 / 9; background: #252832; }
figcaption { display: grid; gap: 6px; padding: 18px 20px 12px; line-height: 1.6; }
figcaption span { color: var(--vp-c-text-2); font-size: 13px; }
.roll-stats { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); margin: 0; padding: 4px 20px 12px; gap: 12px; }
dt { min-height: 2.8em; color: var(--vp-c-text-2); font-size: 12px; }
dd { margin: 4px 0 0; font-size: 25px; font-weight: 700; line-height: 1.3; font-variant-numeric: tabular-nums; }
small { font-size: 12px; font-weight: 400; }
.roll-video-link { display: inline-block; margin: 0 20px 18px; font-size: 13px; }
@media (max-width: 420px) { figcaption { padding: 14px 14px 10px; } .roll-stats { padding: 4px 14px 12px; gap: 6px; } dd { font-size: 22px; } .roll-video-link { margin-left: 14px; } }
</style>
