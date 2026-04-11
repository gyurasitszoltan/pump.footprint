<script setup>
import { computed } from 'vue'
import { deltaBgColor, volumeBgColor } from '../utils/colors.js'
import { fmtSol, fmtSolSigned } from '../utils/format.js'

const NUM_BUCKETS = 60
const CELL_W = 50

const props = defineProps({
  footprint: { type: Object, required: true },
})

const buckets = computed(() => Array.from({ length: NUM_BUCKETS }, (_, i) => i))

function getStat(bucket) {
  return props.footprint.stats[String(bucket)] || { vol: 0, delta: 0, trades: 0 }
}

const maxVol = computed(() => {
  let max = 0
  for (let b = 0; b < NUM_BUCKETS; b++) {
    const s = getStat(b)
    if (s.vol > max) max = s.vol
  }
  return max || 1
})

const maxAbsDelta = computed(() => {
  let max = 0
  for (let b = 0; b < NUM_BUCKETS; b++) {
    const s = getStat(b)
    const abs = Math.abs(s.delta)
    if (abs > max) max = abs
  }
  return max || 1
})

const rows = [
  { label: 'Volume', key: 'vol', format: fmtSol, bgFn: 'volume', textColor: '#aaa' },
  { label: 'Delta', key: 'delta', format: fmtSolSigned, bgFn: 'delta', textColor: '#fff' },
  { label: 'Trades', key: 'trades', format: v => v > 0 ? String(v) : '', bgFn: null, textColor: '#777' },
]

function rowBg(row, stat) {
  if (row.bgFn === 'volume') return volumeBgColor(stat.vol, maxVol.value)
  if (row.bgFn === 'delta') return deltaBgColor(stat.delta, maxAbsDelta.value)
  return '#111'
}
</script>

<template>
  <table class="border-collapse" style="font-family:monospace;table-layout:fixed;background:#0d0d0d;">
    <tbody>
      <!-- Separator -->
      <tr>
        <td :colspan="NUM_BUCKETS + 1" style="height:3px;background:#2a2a2a;padding:0;" />
      </tr>
      <tr v-for="row in rows" :key="row.label">
        <td
          class="text-gray-500 font-bold text-right whitespace-nowrap border-r border-gray-800"
          style="width:52px;min-width:52px;font-size:8px;padding:1px 4px;"
          :style="{ background: row.bgFn === null ? '#111' : '#1a1a1a' }"
        >{{ row.label }}</td>
        <td
          v-for="b in buckets"
          :key="b"
          :style="{
            width: CELL_W + 'px', minWidth: CELL_W + 'px', maxWidth: CELL_W + 'px',
            height: '12px', fontSize: '8px', padding: '0 2px',
            textAlign: 'center', whiteSpace: 'nowrap',
            background: rowBg(row, getStat(b)),
            color: row.textColor,
            borderRight: '1px solid #111',
          }"
        >{{ row.format(getStat(b)[row.key]) }}</td>
      </tr>
    </tbody>
  </table>
</template>
