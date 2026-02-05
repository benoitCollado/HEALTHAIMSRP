<template>
  <div class="canvas" ref="wrap">
    <div class="controls">
      <router-link :to="prevLink">Prev</router-link>
      <router-link :to="nextLink">Next</router-link>
    </div>
    <div v-if="page" class="page-frame" :style="frameStyle">
      <div class="page-canvas">
        <div v-for="(a, idx) in page.areas" :key="idx"
             class="overlay-link"
             :style="areaStyle(a)">
          <a :href="a.href" @click.prevent="handleClick(a.href)" style="display:block;width:100%;height:100%"></a>
        </div>
        <div class="page-title" style="position:absolute;left:8px;top:8px;color:#fff;font-weight:bold">{{ page.title }}</div>
      </div>
    </div>
    <div v-else style="color:#333;">Page introuvable</div>
  </div>
</template>

<script lang="ts">
import { defineComponent, computed, ref, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import maquette from '../data/maquette.json'

export default defineComponent({
  setup() {
    const route = useRoute()
    const router = useRouter()
    const pages = (maquette as any).pages
    const originalW = (maquette as any).originalWidth
    const originalH = (maquette as any).originalHeight

    const wrap = ref<HTMLElement | null>(null)
    const scale = ref(1)

    const page = computed(() => pages.find((p: any) => p.id === (route.params.id || pages[0]?.id)))

    function recompute() {
      if (!wrap.value) return
      const rect = wrap.value.getBoundingClientRect()
      const W = rect.width - 40
      const H = rect.height - 40
      const s = Math.min(W / originalW, H / originalH)
      scale.value = s > 1 ? 1 : s
    }

    onMounted(() => {
      window.addEventListener('resize', recompute)
      recompute()
    })
    onBeforeUnmount(() => {
      window.removeEventListener('resize', recompute)
    })

    const frameStyle = computed(() => ({ width: Math.round(originalW * scale.value) + 'px', height: Math.round(originalH * scale.value) + 'px' }))

    function areaStyle(a: any) {
      const [x1,y1,x2,y2] = a.coords
      const left = x1 * scale.value
      const top = y1 * scale.value
      const width = (x2 - x1) * scale.value
      const height = (y2 - y1) * scale.value
      return { left: left + 'px', top: top + 'px', width: width + 'px', height: height + 'px' }
    }

    function handleClick(href: string) {
      const id = href.replace('#','')
      router.push({ path: '/' + id })
    }

    const index = computed(() => pages.findIndex((p: any) => p.id === page.value?.id))
    const prevLink = computed(() => '/' + (pages[(index.value - 1 + pages.length) % pages.length].id))
    const nextLink = computed(() => '/' + (pages[(index.value + 1) % pages.length].id))

    return { page, areaStyle, frameStyle, wrap, handleClick, prevLink, nextLink }
  }
})
</script>
