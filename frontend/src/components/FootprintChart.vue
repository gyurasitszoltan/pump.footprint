<script setup>
import { ref, watch, nextTick } from 'vue'
import FootprintGrid from './FootprintGrid.vue'
import StatsBar from './StatsBar.vue'

const props = defineProps({
  footprint: { type: Object, required: true },
})

const scrollContainer = ref(null)
let initialScrollDone = false

// Auto-scroll only on first snapshot (token switch)
watch(() => props.footprint.mint, async () => {
  initialScrollDone = false
})

watch(() => props.footprint.current_bucket, async () => {
  if (initialScrollDone) return
  await nextTick()
  if (scrollContainer.value) {
    scrollContainer.value.scrollLeft = scrollContainer.value.scrollWidth
    initialScrollDone = true
  }
})
</script>

<template>
  <div class="border border-gray-800 rounded">
    <div ref="scrollContainer" class="overflow-x-auto">
      <FootprintGrid :footprint="footprint" />
      <StatsBar :footprint="footprint" />
    </div>
    <div class="text-gray-600 text-[9px] px-2 py-1 border-t border-gray-800">
      Green = buy &gt; sell | Red = sell &gt; buy | Cell: buy_sol | sell_sol | Bucket: 10s x $1,000 MC | SOL=$85
    </div>
  </div>
</template>
