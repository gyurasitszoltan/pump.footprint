<script setup>
import { computed } from 'vue'
import { deltaBgColor, volumeBgColor } from '../utils/colors.js'
import { fmtSol, fmtSolSigned, fmtMcUsd } from '../utils/format.js'

const NUM_BUCKETS = 60
const CELL_W = 50

const props = defineProps({
  footprint: { type: Object, required: true },
})

const buckets = computed(() => Array.from({ length: NUM_BUCKETS }, (_, i) => i))

function getStat(bucket) {
  return props.footprint.stats?.[String(bucket)] || {
    vol: 0, delta: 0, trades: 0,
    sol_in_pool: null, vol_exp: null, tps_exp: null, pool_exp: null,
    vwap: null,
  }
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

// Deviation color: ±10% none, ±20% light, ±30%+ strong (green=above, red=below)
function deviationBg(actual, expected) {
  if (!expected || actual == null) return null
  const ratio = (actual - expected) / expected
  const abs = Math.abs(ratio)
  if (abs < 0.10) return null
  const up = ratio > 0
  if (abs < 0.20) return up ? '#14532d' : '#450a0a'
  if (abs < 0.30) return up ? '#166534' : '#7f1d1d'
  return up ? '#15803d' : '#991b1b'
}

function fmtDevPct(actual, expected) {
  if (!expected || actual == null) return ''
  const pct = Math.round(((actual - expected) / expected) * 100)
  return pct >= 0 ? `+${pct}%` : `${pct}%`
}

const rows = [
  {
    label: 'Volume',
    getLeft:    s => fmtSol(s.vol),
    getRight:   s => fmtDevPct(s.vol, s.vol_exp),
    getRightBg: s => deviationBg(s.vol, s.vol_exp),
    bgFn: 'volume',
  },
  {
    label: 'Delta',
    getLeft:    s => fmtSolSigned(s.delta),
    getRight:   () => '',
    getRightBg: () => null,
    bgFn: 'delta',
  },
  {
    label: 'Trades',
    getLeft:    s => s.trades > 0 ? String(s.trades) : '',
    getRight:   s => fmtDevPct(s.trades, s.tps_exp),
    getRightBg: s => deviationBg(s.trades, s.tps_exp),
    bgFn: null,
  },
  {
    label: 'Pool',
    getLeft:    s => s.sol_in_pool ? fmtSol(s.sol_in_pool) : '',
    getRight:   s => fmtDevPct(s.sol_in_pool, s.pool_exp),
    getRightBg: s => deviationBg(s.sol_in_pool, s.pool_exp),
    bgFn: null,
  },
  {
    label: 'VWAP',
    getLeft:    s => s.vwap ? fmtMcUsd(s.vwap) : '',
    getRight:   (s, b) => vwapDevPct(b, s.vwap),
    getRightBg: (s, b) => vwapDevBg(b, s.vwap),
    bgFn: null,
  },
]

function vwapDevPct(bucket, vwap) {
  if (!vwap) return ''
  const closeMc = props.footprint.ohlc?.[String(bucket)]?.c
  if (!closeMc) return ''
  const pct = Math.round(((closeMc - vwap) / vwap) * 100)
  return pct >= 0 ? `+${pct}%` : `${pct}%`
}

function vwapDevBg(bucket, vwap) {
  if (!vwap) return null
  const closeMc = props.footprint.ohlc?.[String(bucket)]?.c
  if (!closeMc) return null
  const ratio = (closeMc - vwap) / vwap
  const abs = Math.abs(ratio)
  if (abs < 0.02) return null
  const up = ratio > 0
  if (abs < 0.08) return up ? '#14532d' : '#450a0a'
  if (abs < 0.20) return up ? '#166534' : '#7f1d1d'
  return up ? '#15803d' : '#991b1b'
}

function rowBg(row, stat) {
  if (row.bgFn === 'volume') return volumeBgColor(stat.vol, maxVol.value)
  if (row.bgFn === 'delta')  return deltaBgColor(stat.delta, maxAbsDelta.value)
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
            height: '12px', fontSize: '8px', padding: '0 1px',
            textAlign: 'center', whiteSpace: 'nowrap',
            background: rowBg(row, getStat(b)),
            borderRight: '1px solid #111',
          }"
        >
          <span style="color:#aaa">{{ row.getLeft(getStat(b)) }}</span>
          <template v-if="row.getRight(getStat(b), b)">
            <span style="color:#333">|</span>
            <span :style="{
              color: row.getRightBg(getStat(b), b) ? '#fff' : '#555',
              background: row.getRightBg(getStat(b), b) || 'transparent',
              padding: '0 1px',
            }">{{ row.getRight(getStat(b), b) }}</span>
          </template>
        </td>
      </tr>
    </tbody>
  </table>
</template>
