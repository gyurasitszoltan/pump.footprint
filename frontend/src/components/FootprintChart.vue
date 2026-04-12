<script setup>
import { ref, watch, nextTick } from 'vue'
import FootprintGrid from './FootprintGrid.vue'
import BucketDetailModal from './BucketDetailModal.vue'

const props = defineProps({
  footprint: { type: Object, required: true },
})

const scrollContainer = ref(null)
let initialScrollDone = false

const showBucketModal = ref(false)
const selectedBucket = ref(0)
const selectedMcLevel = ref(null)

function onBucketClick(bucketIdx) {
  selectedBucket.value = bucketIdx
  selectedMcLevel.value = null
  showBucketModal.value = true
}

function onCellClick({ bucket, mcLevel }) {
  selectedBucket.value = bucket
  selectedMcLevel.value = mcLevel
  showBucketModal.value = true
}

watch(() => props.footprint.mint, () => {
  initialScrollDone = false
})

watch(() => props.footprint.current_bucket, async () => {
  if (initialScrollDone) return
  await nextTick()
  if (scrollContainer.value) {
    scrollContainer.value.scrollLeft = 0
    scrollContainer.value.scrollTop = scrollContainer.value.scrollHeight
    initialScrollDone = true
  }
})
</script>

<template>
  <div class="border border-gray-800 rounded">
    <div ref="scrollContainer" class="fp-scroll" style="max-height:70vh;">
      <FootprintGrid :footprint="footprint" @bucket-click="onBucketClick" @cell-click="onCellClick" />
    </div>
    <div class="text-gray-600 text-[9px] px-2 py-1 border-t border-gray-800">
      Green = buy &gt; sell | Red = sell &gt; buy | Cell: buy_sol | sell_sol | Bucket: 10s x $1,000 MC | SOL=$85
    </div>
  </div>
  <Teleport to="body">
    <BucketDetailModal
      v-if="showBucketModal"
      :mint="footprint.mint"
      :bucket-idx="selectedBucket"
      :mc-level="selectedMcLevel"
      @close="showBucketModal = false"
    />
  </Teleport>
</template>

<style scoped>
.fp-scroll {
  overflow: auto;
}
.fp-scroll::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}
.fp-scroll::-webkit-scrollbar-track {
  background: #0d0d0d;
}
.fp-scroll::-webkit-scrollbar-thumb {
  background: #333;
  border-radius: 4px;
}
.fp-scroll::-webkit-scrollbar-corner {
  background: #0d0d0d;
}
</style>
