<script setup>
import { computed } from 'vue'
import FootprintCell from './FootprintCell.vue'
import { candleShadow, deltaBgColor, volumeBgColor } from '../utils/colors.js'
import { fmtSol, fmtSolSigned, fmtMcSigned } from '../utils/format.js'
import { useSettings } from '../composables/useSettings.js'

const MC_LEVEL_SIZE = 1000
const NUM_BUCKETS = 60
const CELL_W = 50
const CELL_H = 12

const props = defineProps({
  footprint: { type: Object, required: true },
})

const emit = defineEmits(['bucket-click', 'cell-click'])

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
  return props.footprint.stats[String(bucket)] || { vol: 0, delta: 0, trades: 0, sol_in_pool: null, vol_exp: null, tps_exp: null, pool_exp: null }
}

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

function fmtSplitDev(leftHtml, actual, expected) {
  const devStr = fmtDevPct(actual, expected)
  if (!devStr) return leftHtml
  const bg = deviationBg(actual, expected)
  const color = bg ? '#fff' : '#555'
  const bgStyle = bg ? `background:${bg};padding:0 1px` : 'padding:0 1px'
  return `${leftHtml}<span style="color:#333">|</span><span style="color:${color};${bgStyle}">${devStr}</span>`
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

const cvdMap = computed(() => {
  const map = {}
  let cum = 0
  let hadTrade = false
  for (let b = 0; b < NUM_BUCKETS; b++) {
    const s = getStat(b)
    if (s.trades > 0) {
      cum += s.delta
      hadTrade = true
    }
    map[b] = hadTrade && s.trades > 0 ? cum : null
  }
  return map
})

const maxAbsCvd = computed(() => {
  let max = 0
  for (let b = 0; b < NUM_BUCKETS; b++) {
    const v = cvdMap.value[b]
    if (v != null) {
      const abs = Math.abs(v)
      if (abs > max) max = abs
    }
  }
  return max || 1
})

const maxAbsEmaArea = computed(() => {
  let max = 0
  for (let b = 0; b < NUM_BUCKETS; b++) {
    const abs = Math.abs(getStat(b).ema_area || 0)
    if (abs > max) max = abs
  }
  return max || 1
})

const rsiDivergenceBuckets = computed(() => {
  const map = new Map()
  for (let b = 1; b < NUM_BUCKETS; b++) {
    const cur = getStat(b)
    const prev = getStat(b - 1)
    const curOhlc = getOhlc(b)
    const prevOhlc = getOhlc(b - 1)
    if (!curOhlc || !prevOhlc) continue

    const bullish =
      cur.rsi_min != null && prev.rsi_min != null &&
      prev.rsi_min < cur.rsi_min &&
      curOhlc.l < prevOhlc.l

    const bearish =
      cur.rsi_max != null && prev.rsi_max != null &&
      prev.rsi_max > cur.rsi_max &&
      curOhlc.h > prevOhlc.h

    if (bullish && bearish) map.set(b, 'both')
    else if (bullish) map.set(b, 'bullish')
    else if (bearish) map.set(b, 'bearish')
  }
  return map
})

function fmtCvd(bucket) {
  const v = cvdMap.value[bucket]
  return v ? fmtSolSigned(v) : ''
}

function fmtVwap(bucket) {
  const s = getStat(bucket)
  if (!s.vwap) return ''
  const ohlc = getOhlc(bucket)
  const ratio = ohlc?.c ? (ohlc.c - s.vwap) / s.vwap : null
  const near = ratio !== null && Math.abs(ratio) < 0.01
  const valColor = near ? '#1a1600' : '#aaa'
  const vwapStr = `<span style="color:${valColor}">${(s.vwap / 1000).toFixed(1)}</span>`
  if (!ohlc?.c) return vwapStr
  const pct = Math.round(ratio * 100)
  if (Math.abs(pct) < 2) return vwapStr
  const color = pct > 0 ? '#4ade80' : '#f87171'
  const sign = pct > 0 ? '+' : ''
  return `${vwapStr}<span style="color:#444">|</span><span style="color:${color}">${sign}${pct}</span>`
}

function fmtBuySell(stat) {
  if (stat.vol === 0) return ''
  return `<span style="color:#4ade80">${fmtSol(stat.buy || 0)}</span><span style="color:#666">|</span><span style="color:#f87171">${fmtSol(stat.sell || 0)}</span>`
}

function fmtBuyPct(stat) {
  if (!stat.vol) return ''
  return `${Math.round(((stat.buy || 0) / stat.vol) * 100)}%`
}

function fmtSizeBin(stat, binIdx) {
  const bins = stat.bins
  if (!bins || !bins[binIdx]) return ''
  const b = bins[binIdx]
  if (b.buy === 0 && b.sell === 0) return ''
  const buyStr = b.buy > 0 ? `<span style="color:#4ade80">${fmtSol(b.buy)}</span>` : '<span style="color:#555">0.0</span>'
  const sellStr = b.sell > 0 ? `<span style="color:#f87171">${fmtSol(b.sell)}</span>` : '<span style="color:#555">0.0</span>'
  return `${buyStr}<span style="color:#666">|</span>${sellStr}`
}

function fmtRsi(v, stat) {
  const mn = stat.rsi_min
  const mx = stat.rsi_max
  if (mn == null && mx == null) return ''
  const minVal = mn != null ? Math.round(mn) : '-'
  const maxVal = mx != null ? Math.round(mx) : '-'
  const minColor = mn != null && mn < 30 ? '#f87171' : '#777'
  const maxColor = mx != null && mx > 70 ? '#4ade80' : '#777'
  return `<span style="color:${minColor}">${minVal}</span><span style="color:#666">|</span><span style="color:${maxColor}">${maxVal}</span>`
}

function sizeBinLabel(bins, idx) {
  if (idx === 0) return `<${bins[0]}`
  if (idx === bins.length) return `>${bins[bins.length - 1]}`
  return `${bins[idx - 1]}-${bins[idx]}`
}

const statRows = computed(() => {
  const bins = props.footprint.size_bins || [1, 2]
  const numBins = bins.length + 1
  const rows = [
    { label: 'Volume', key: 'vol', format: (v, s) => fmtSplitDev(`<span style="color:#aaa">${fmtSol(v)}</span>`, v, s.vol_exp), bgFn: 'volume', textColor: '#aaa', html: true },
    { label: 'B|S', key: '_buysell', format: (v, s) => fmtBuySell(s), bgFn: 'volume', textColor: '#aaa', html: true },
    { label: 'Buy%', key: '_buypct', format: (v, s) => fmtBuyPct(s), bgFn: 'buypct', textColor: '#fff' },
    { label: 'Delta', key: 'delta', format: (v, s) => fmtSolSigned(v), bgFn: 'delta', textColor: '#fff' },
    { label: 'CVD', key: '_cvd', format: () => '', bgFn: 'cvd', textColor: '#fff' },
    { label: 'EMA±', key: 'ema_area', format: (v, s) => fmtMcSigned(s.ema_area), bgFn: 'ema_area', textColor: '#fff' },
    { label: 'Trades', key: 'trades', format: (v, s) => fmtSplitDev(`<span style="color:#777">${v > 0 ? String(v) : ''}</span>`, v, s.tps_exp), bgFn: null, textColor: '#777', html: true },
    { label: 'N Wall', key: 'neww', format: (v, s) => v > 0 ? String(v) : '', bgFn: null, textColor: '#777' },
    { label: 'Pool', key: 'sol_in_pool', format: (v, s) => fmtSplitDev(`<span style="color:#888">${v ? fmtSol(v) : ''}</span>`, v, s.pool_exp), bgFn: null, textColor: '#888', html: true },
  ]
  for (let i = 0; i < numBins; i++) {
    rows.push({
      label: sizeBinLabel(bins, i),
      key: `_bin${i}`,
      format: (v, s) => fmtSizeBin(s, i),
      bgFn: null,
      textColor: '#aaa',
      html: true,
    })
  }
  rows.push({
    label: 'RSI',
    key: '_rsi',
    format: (v, s) => fmtRsi(v, s),
    bgFn: 'rsi',
    textColor: '#aaa',
    html: true,
  })
  rows.push({
    label: 'VWAP',
    key: '_vwap',
    format: () => '',
    bgFn: null,
    textColor: '#aaa',
    html: true,
  })
  return rows
})

function statBg(row, stat) {
  if (row.bgFn === 'volume') return volumeBgColor(stat.vol, maxVol.value)
  if (row.bgFn === 'delta') return deltaBgColor(stat.delta, maxAbsBucketDelta.value)
  if (row.bgFn === 'buypct') {
    if (!stat.vol) return '#111'
    const pct = (stat.buy || 0) / stat.vol
    return deltaBgColor(pct - 0.5, 0.5)  // >50% green, <50% red
  }
  if (row.bgFn === 'rsi') {
    if (stat.rsi_min != null && stat.rsi_min < 30) return '#7f1d1d'
    if (stat.rsi_max != null && stat.rsi_max > 70) return '#14532d'
    return '#111'
  }
  if (row.bgFn === 'ema_area') {
    return deltaBgColor(stat.ema_area || 0, maxAbsEmaArea.value)
  }
  return '#111'
}

function vwapStatBg(bucket) {
  const s = getStat(bucket)
  if (!s.vwap) return '#111'
  const ohlc = getOhlc(bucket)
  if (!ohlc?.c) return '#111'
  const ratio = (ohlc.c - s.vwap) / s.vwap
  const abs = Math.abs(ratio)
  if (abs < 0.01) return '#b4a200'
  if (abs < 0.02) return '#111'
  const up = ratio > 0
  if (abs < 0.08) return up ? '#052e16' : '#1c0505'
  if (abs < 0.20) return up ? '#14532d' : '#450a0a'
  return up ? '#166534' : '#7f1d1d'
}

const SCROLLBAR_H = 8  // matches .fp-scroll::-webkit-scrollbar height

const { settings } = useSettings()

const visibleStatRows = computed(() => {
  const rowSettings = settings.barStat.rows
  return statRows.value.filter(row => {
    if (row.key?.startsWith('_bin')) return rowSettings['Size Bins'] !== false
    return rowSettings[row.label] !== false
  })
})

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
          class="text-gray-600 font-normal border-r whitespace-nowrap hover:text-white hover:bg-gray-800"
          :style="{
            width: CELL_W + 'px', minWidth: CELL_W + 'px', maxWidth: CELL_W + 'px',
            height: CELL_H + 'px', fontSize: '8px', padding: '1px 3px',
            textAlign: 'center', borderColor: '#1a1a1a',
            position: 'sticky', top: 0, zIndex: 3, background: '#0d0d0d',
            cursor: 'pointer',
          }"
          @click="emit('bucket-click', b)"
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
            cursor: 'pointer',
          }"
          @click="emit('cell-click', { bucket: b, mcLevel: level })"
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
          :style="{ height: '3px', background: '#2a2a2a', padding: 0, position: 'sticky', bottom: `${visibleStatRows.length * 12 + SCROLLBAR_H}px`, zIndex: 1 }"
        />
      </tr>
      <tr v-for="(row, ri) in visibleStatRows" :key="row.label">
        <td
          class="text-gray-500 font-bold text-right whitespace-nowrap border-r border-gray-800"
          :style="{
            width: '52px', minWidth: '52px', fontSize: '8px', padding: '1px 4px',
            background: row.bgFn === null ? '#111' : '#1a1a1a',
            position: 'sticky', left: 0, bottom: `${(visibleStatRows.length - 1 - ri) * 12 + SCROLLBAR_H}px`, zIndex: 4,
          }"
        >{{ row.label }}</td>
        <td
          v-for="b in buckets"
          :key="b"
          :style="{
            width: CELL_W + 'px', minWidth: CELL_W + 'px', maxWidth: CELL_W + 'px',
            height: '12px', fontSize: '8px', padding: '0 2px',
            textAlign: 'center', whiteSpace: 'nowrap',
            background: row.key === '_vwap' ? vwapStatBg(b) : row.bgFn === 'cvd' ? deltaBgColor(cvdMap[b], maxAbsCvd) : statBg(row, getStat(b)),
            color: row.textColor,
            borderBottom: '1px solid #111',
            boxShadow: row.key === '_rsi'
              ? (rsiDivergenceBuckets.get(b) === 'both'    ? 'inset 0 -1px 0 #facc15'
                : rsiDivergenceBuckets.get(b) === 'bullish' ? 'inset 0 -1px 0 #4ade80'
                : rsiDivergenceBuckets.get(b) === 'bearish' ? 'inset 0 -1px 0 #f87171'
                : 'none')
              : 'none',
            borderRight: '1px solid #111',
            position: 'sticky', bottom: `${(visibleStatRows.length - 1 - ri) * 12 + SCROLLBAR_H}px`, zIndex: 1,
          }"
          v-html="row.key === '_vwap' ? fmtVwap(b) : row.key === '_cvd' ? fmtCvd(b) : row.format(getStat(b)[row.key], getStat(b))"
        />
      </tr>
    </tfoot>
  </table>
</template>
