<script setup lang="ts">
import { computed } from 'vue'
import { useData } from 'vitepress'
import data from './roll-case.json'

const { lang } = useData()
const copy = computed(() => lang.value.startsWith('zh') ? {
  title: '诊断策略与选定策略的前 6 秒净翻转进度',
  description: '橙色虚线为未截断动作的原始 ONNX 回放，进度停在不足一圈；青色实线为第三轮选定策略的第 0 个环境，进度持续跨过整圈刻度。每五个控制步抽取一个样本。',
  angle: '净翻转角度 / 2π（圈）', time: '仿真时间（秒）',
  baseline: '橙色虚线：原始策略诊断', selected: '青色实线：第三轮选定策略',
  caption: '数据取自两段独立回放的第 0 个环境，每 0.1 秒抽样。纵轴是连续展开的净角度；整数刻度对应完整翻转进度。不同策略与配置的对比，用于理解现象。'
} : {
  title: 'Net rotation over the first 6 seconds: diagnostic and selected policies',
  description: 'The dashed orange line is the original ONNX replay without action clipping; it stays below one full turn. The solid teal line is environment 0 of the selected round 3 policy; it keeps crossing full-turn marks. One sample is shown every five control steps.',
  angle: 'Net angle / 2π (turns)', time: 'Simulation time (s)',
  baseline: 'Dashed orange: original ONNX', selected: 'Solid teal: selected round 3 policy',
  caption: 'Environment 0 from two separate replays, sampled every 0.1 seconds. The vertical axis is the unwrapped net angle; whole-number marks represent full-turn progress. The policies and settings differ, so this chart illustrates the behavior rather than isolating a single change.'
})

const path = (rows: number[][]) => rows.map(([t, phase], i) =>
  `${i ? 'L' : 'M'}${(48 + t / 6 * 484).toFixed(2)},${(226 - phase / 5 * 190).toFixed(2)}`
).join(' ')
</script>

<template>
  <figure class="roll-phase">
    <svg viewBox="0 0 560 282" role="img" aria-labelledby="roll-phase-title roll-phase-desc">
      <title id="roll-phase-title">{{ copy.title }}</title>
      <desc id="roll-phase-desc">{{ copy.description }}</desc>
      <g v-for="tick in [0, 1, 2, 3, 4, 5]" :key="tick">
        <line x1="48" x2="532" :y1="226 - tick * 38" :y2="226 - tick * 38" class="grid" />
        <text x="34" :y="230 - tick * 38" text-anchor="end">{{ tick }}</text>
      </g>
      <g v-for="tick in [0, 1, 2, 3, 4, 5, 6]" :key="`time-${tick}`">
        <text :x="48 + tick / 6 * 484" y="248" text-anchor="middle">{{ tick }}</text>
      </g>
      <text x="48" y="19">{{ copy.angle }}</text>
      <text x="532" y="274" text-anchor="end">{{ copy.time }}</text>
      <path :d="path(data.phaseFirstSixSeconds.baseline)" class="baseline" />
      <path :d="path(data.phaseFirstSixSeconds.selected)" class="selected" />
    </svg>
    <div class="legend"><span class="baseline-label">{{ copy.baseline }}</span><span class="selected-label">{{ copy.selected }}</span></div>
    <figcaption>{{ copy.caption }}</figcaption>
  </figure>
</template>

<style scoped>
.roll-phase { margin: 24px 0; padding: 16px; border: 1px solid var(--vp-c-divider); border-radius: 12px; background: var(--vp-c-bg-soft); }
svg { display: block; width: 100%; height: auto; overflow: visible; }
text { fill: var(--vp-c-text-2); font-size: 12px; }
.grid { stroke: var(--vp-c-divider); stroke-width: 1; }
path { fill: none; stroke-width: 2.5; stroke-linejoin: round; }
.baseline { stroke: #c96522; stroke-dasharray: 6 4; }
.selected { stroke: #07857b; }
.legend { display: flex; gap: 10px 20px; flex-wrap: wrap; font-size: 12px; }
.baseline-label { color: #b65617; }
.selected-label { color: #08766e; }
:global(.dark) .baseline-label { color: #efac73; }
:global(.dark) .selected-label { color: #61d5c7; }
figcaption { margin-top: 12px; font-size: 12px; line-height: 1.7; color: var(--vp-c-text-2); }
@media (max-width: 520px) { text { font-size: 22px; } path { stroke-width: 3.5; } }
</style>
