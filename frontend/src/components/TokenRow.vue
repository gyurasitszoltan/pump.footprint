<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { fmtMint, fmtMcUsd } from '../utils/format.js'
import { rsiColor } from '../utils/colors.js'

const props = defineProps({
  token: { type: Object, required: true },
  selected: { type: Boolean, default: false },
})

const emit = defineEmits(['select'])

const now = ref(Date.now())
let timer = null

onMounted(() => {
  timer = setInterval(() => { now.value = Date.now() }, 1000)
})
onUnmounted(() => clearInterval(timer))

const activeSec = computed(() => {
  return Math.floor((now.value - props.token.migrate_ts_ms) / 1000)
})

const isExpiring = computed(() => activeSec.value >= 540)

const copyIcon = ref('📋')
function copyMint() {
  navigator.clipboard.writeText(props.token.mint).then(() => {
    copyIcon.value = '✅'
    setTimeout(() => { copyIcon.value = '📋' }, 1200)
  })
}
</script>

<template>
  <tr
    class="cursor-pointer hover:bg-gray-800/50 transition-colors"
    :class="selected ? 'bg-blue-900/30' : ''"
    @click="emit('select')"
  >
    <td class="px-2 py-1">
      <div class="flex items-center gap-1.5">
        <a
          :href="`https://gmgn.ai/sol/token/${token.mint}`"
          target="_blank"
          class="text-blue-400 hover:text-blue-300"
          @click.stop
        >{{ fmtMint(token.mint) }}</a>
        <button
          class="text-[10px] opacity-60 hover:opacity-100"
          @click.stop="copyMint"
          title="Copy mint address"
        >{{ copyIcon }}</button>
        <span v-if="token.symbol" class="text-gray-500 ml-1">{{ token.symbol }}</span>
      </div>
    </td>
    <td
      class="text-right px-2 py-1 tabular-nums"
      :class="isExpiring ? 'text-red-400 bg-red-900/30 font-bold' : 'text-gray-400'"
    >{{ activeSec }}s</td>
    <td class="text-right px-2 py-1 text-gray-400 tabular-nums">{{ token.trades_10s }}</td>
    <td class="text-right px-2 py-1 text-gray-300 tabular-nums">{{ fmtMcUsd(token.mc_usd || 0) }}</td>
    <td
      class="text-right px-2 py-1 tabular-nums font-bold"
      :style="{ color: rsiColor(token.rsi14) }"
    >{{ token.rsi14 !== null && token.rsi14 !== undefined ? token.rsi14 : '—' }}</td>
  </tr>
</template>
