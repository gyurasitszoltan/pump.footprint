<script setup>
import { computed } from 'vue'
import FootprintCell from './FootprintCell.vue'
import { candleShadow, deltaBgColor, volumeBgColor } from '../utils/colors.js'
import { fmtSol, fmtSolSigned } from '../utils/format.js'

const MC_LEVEL_SIZE = 1000
const NUM_BUCKETS = 60
const CELL_W = 50
const CELL_H = 12

const props = defineProps({
  footprint: { type: Object, required: true },
})

const buckets = computed(() => Array.from({ length: NUM_BUCKETS }, (_, i) => i))

const mcLevels = computed(() => {
  const levels = props.footprint.mc_levels
  return levels && levels.length > 0 ? levels : []
})

function timeLabel(bucket) {
  return `${bucket * 10}s`
}

function mcLabel(level) {
  return `$${level.toLocaleString()}`
}

function getCell(bucket, level) {
  return props.footprint.cells[`${bucket}:${level}`] || null
}

function getOhlc(bucket) {
  return props.footprint.ohlc[String(bucket)] || null
}

function isPoc(bucket, level) {
  return props.footprint.poc[String(bucket)] === level
}

function isLastPrice(bucket, level) {
  if (bucket !== props.footprint.current_bucket) return false
  const ohlc = getOhlc(bucket)
  if (!ohlc) return false
  return Math.floor(ohlc.c / MC_LEVEL_SIZE) * MC_LEVEL_SIZE === level
}

function getCandleShadow(bucket, level) {
  return candleShadow(getOhlc(bucket), level, MC_LEVEL_SIZE)
}

// --- Stats ---
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

const maxAbsBucketDelta = computed(() => {
  let max = 0
  for (let b = 0; b < NUM_BUCKETS; b++) {
    const abs = Math.abs(getStat(b).delta)
    if (abs > max) max = abs
  }
  return max || 1
})

function fmtBuySell(stat) {
  if (stat.vol === 0) return ''
  return `${fmtSol(stat.buy || 0)}|${fmtSol(stat.sell || 0)}`
}

function fmtBuyPct(stat) {
  if (!stat.vol) return ''
  return `${Math.round(((stat.buy || 0) / stat.vol) * 100)}%`
}

const statRows = [
  { label: 'Volume', key: 'vol', format: (v, s) => fmtSol(v), bgFn: 'volume', textColor: '#aaa' },
  { label: 'B|S', key: '_buysell', format: (v, s) => fmtBuySell(s), bgFn: 'volume', textColor: '#aaa' },
  { label: 'Buy%', key: '_buypct', format: (v, s) => fmtBuyPct(s), bgFn: 'buypct', textColor: '#fff' },
  { label: 'Delta', key: 'delta', format: (v, s) => fmtSolSigned(v), bgFn: 'delta', textColor: '#fff' },
  { label: 'Trades', key: 'trades', format: (v, s) => v > 0 ? String(v) : '', bgFn: null, textColor: '#777' },
]

function statBg(row, stat) {
  if (row.bgFn === 'volume') return volumeBgColor(stat.vol, maxVol.value)
  if (row.bgFn === 'delta') return deltaBgColor(stat.delta, maxAbsBucketDelta.value)
  if (row.bgFn === 'buypct') {
    if (!stat.vol) return '#111'
    const pct = (stat.buy || 0) / stat.vol
    return deltaBgColor(pct - 0.5, 0.5)  // >50% green, <50% red
  }
  return '#111'
}

const SCROLLBAR_H = 8  // matches .fp-scroll::-webkit-scrollbar height

const stickyLeft = {
  position: 'sticky',
  left: 0,
  zIndex: 2,
  background: '#0d0d0d',
}

const stickyTopLeft = {
  position: 'sticky',
  left: 0,
  top: 0,
  zIndex: 4,
  background: '#0d0d0d',
}
</script>

<template>
  <table class="border-collapse" style="font-family:monospace;table-layout:fixed;background:#0d0d0d;">
    <!-- Header: sticky top -->
    <thead>
      <tr>
        <th
          class="text-gray-500 font-normal text-right border-r border-gray-800 whitespace-nowrap"
          :style="{ width: '52px', minWidth: '52px', fontSize: '8px', padding: '1px 4px', ...stickyTopLeft }"
        >MC\T</th>
        <th
          v-for="b in buckets"
          :key="b"
          class="text-gray-600 font-normal border-r whitespace-nowrap"
          :style="{
            width: CELL_W + 'px', minWidth: CELL_W + 'px', maxWidth: CELL_W + 'px',
            height: CELL_H + 'px', fontSize: '8px', padding: '1px 3px',
            textAlign: 'center', borderColor: '#1a1a1a',
            position: 'sticky', top: 0, zIndex: 3, background: '#0d0d0d',
          }"
        >{{ timeLabel(b) }}</th>
      </tr>
    </thead>

    <!-- Body: MC labels sticky left -->
    <tbody>
      <tr v-for="level in mcLevels" :key="level">
        <td
          class="text-gray-500 text-right whitespace-nowrap border-r border-gray-800"
          :style="{ fontSize: '8px', padding: '1px 4px', borderBottom: '1px solid #1a1a1a', ...stickyLeft }"
        >{{ mcLabel(level) }}</td>
        <td
          v-for="b in buckets"
          :key="b"
          :style="{
            width: CELL_W + 'px', minWidth: CELL_W + 'px', maxWidth: CELL_W + 'px',
            height: CELL_H + 'px', fontSize: '8px', padding: '0 2px',
            textAlign: 'center', whiteSpace: 'nowrap', overflow: 'hidden',
            borderBottom: isLastPrice(b, level) ? '1px solid #fff' : '1px solid #111',
            borderTop: '1px solid transparent',
            borderRight: isPoc(b, level) ? '2px solid #ffd700' : '1px solid #111',
          }"
        >
          <FootprintCell
            :cell="getCell(b, level)"
            :max-abs-delta="footprint.max_abs_delta"
            :candle-shadow="getCandleShadow(b, level)"
          />
        </td>
      </tr>
    </tbody>

    <!-- Stats: sticky bottom -->
    <tfoot>
      <tr>
        <td
          :colspan="NUM_BUCKETS + 1"
          :style="{ height: '3px', background: '#2a2a2a', padding: 0, position: 'sticky', bottom: `${statRows.length * 12 + SCROLLBAR_H}px`, zIndex: 1 }"
        />
      </tr>
      <tr v-for="(row, ri) in statRows" :key="row.label">
        <td
          class="text-gray-500 font-bold text-right whitespace-nowrap border-r border-gray-800"
          :style="{
            width: '52px', minWidth: '52px', fontSize: '8px', padding: '1px 4px',
            background: row.bgFn === null ? '#111' : '#1a1a1a',
            position: 'sticky', left: 0, bottom: `${(statRows.length - 1 - ri) * 12 + SCROLLBAR_H}px`, zIndex: 4,
          }"
        >{{ row.label }}</td>
        <td
          v-for="b in buckets"
          :key="b"
          :style="{
            width: CELL_W + 'px', minWidth: CELL_W + 'px', maxWidth: CELL_W + 'px',
            height: '12px', fontSize: '8px', padding: '0 2px',
            textAlign: 'center', whiteSpace: 'nowrap',
            background: statBg(row, getStat(b)),
            color: row.textColor,
            borderRight: '1px solid #111',
            position: 'sticky', bottom: `${(statRows.length - 1 - ri) * 12 + SCROLLBAR_H}px`, zIndex: 1,
          }"
        >{{ row.format(getStat(b)[row.key], getStat(b)) }}</td>
      </tr>
    </tfoot>
  </table>
</template>
