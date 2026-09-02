<script setup lang="ts">
import { computed } from 'vue'
import { useData } from 'vitepress'

const { lang } = useData()
const isChinese = computed(() => lang.value.startsWith('zh'))
</script>

<template>
  <section class="md-home-section md-duck-makers">
    <div v-if="isChinese" class="md-makers-shell">
      <div class="md-makers-copy">
        <div class="md-section-kicker">一只鸭，从脑洞到落地</div>
        <h2>这只鸭，是怎么孵出来的？</h2>
        <p class="md-makers-lead">Pollen Robotics × Hugging Face 把 MicroDuck 想出来，Seeed Studio 把它一只只造出来。</p>
      </div>
      <div class="md-makers-details">
        <div class="md-makers-grid" aria-label="MicroDuck 产品与制造分工">
          <div class="md-maker-card md-maker-pollen"><span>把鸭子想出来</span><strong>Pollen Robotics × Hugging Face</strong></div>
          <div class="md-maker-card md-maker-seeed"><span>把鸭子造出来</span><strong>Seeed Studio</strong><small>官方制造合作伙伴</small></div>
        </div>
        <div class="md-makers-actions">
          <a class="md-maker-buy" href="https://store.pollen-robotics.com/products/microduck" target="_blank" rel="noopener noreferrer">Buy MicroDuck</a>
          <a class="md-maker-link" href="https://www.seeedstudio.com/" target="_blank" rel="noopener noreferrer">Seeed Studio</a>
        </div>
      </div>
    </div>

    <div v-else class="md-makers-shell">
      <div class="md-makers-copy">
        <div class="md-section-kicker">FROM IDEA TO REAL DUCK</div>
        <h2>Who hatched this duck?</h2>
        <p class="md-makers-lead">Pollen Robotics × Hugging Face dreamed up MicroDuck. Seeed Studio builds it.</p>
      </div>
      <div class="md-makers-details">
        <div class="md-makers-grid" aria-label="Who created and builds MicroDuck">
          <div class="md-maker-card md-maker-pollen"><span>Dreamed up the duck</span><strong>Pollen Robotics × Hugging Face</strong></div>
          <div class="md-maker-card md-maker-seeed"><span>Built the duck</span><strong>Seeed Studio</strong><small>Official manufacturing partner</small></div>
        </div>
        <div class="md-makers-actions">
          <a class="md-maker-buy" href="https://store.pollen-robotics.com/products/microduck" target="_blank" rel="noopener noreferrer">Buy MicroDuck</a>
          <a class="md-maker-link" href="https://www.seeedstudio.com/" target="_blank" rel="noopener noreferrer">Seeed Studio</a>
        </div>
      </div>
    </div>
  </section>
</template>
