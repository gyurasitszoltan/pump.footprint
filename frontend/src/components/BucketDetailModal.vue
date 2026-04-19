<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { Chart, ScatterController, LinearScale, PointElement, Tooltip, Legend } from 'chart.js'
import zoomPlugin from 'chartjs-plugin-zoom'
import { fmtSol, fmtMcUsd, fmtMint } from '../utils/format.js'

Chart.register(ScatterController, LinearScale, PointElement, Tooltip, Legend, zoomPlugin)

const MC_LEVEL_SIZE = 1000

const props = defineProps({
  mint: { type: String, required: true },
  bucketIdx: { type: Number, required: true },
  mcLevel: { type: Number, default: null },
  multiView: { type: Boolean, default: false },
})

const emit = defineEmits(['close'])

const loading = ref(true)
const error = ref(null)
const trades = ref([])
const chartCanvas = ref(null)
let chartInstance = null
let tradeChartMap = {}
let buyRadii = []
let sellRadii = []

// multi-view state
const viewMode = ref('full') // 'full' | 'min1'..'min9'
const allTrades = ref([])
const allTradesLoading = ref(false)
const allTradesError = ref(null)
let allTradesFetched = false

function onKeydown(e) {
  if (e.key === 'Escape') emit('close')
}

function onBackdropClick(e) {
  if (e.target === e.currentTarget) emit('close')
}

onMounted(async () => {
  document.addEventListener('keydown', onKeydown)

  if (props.multiView) {
    await fetchAllTrades()
  } else {
    try {
      const res = await fetch(`/api/trades/${props.mint}/${props.bucketIdx}`)
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const data = await res.json()
      let filtered = data.trades
      if (props.mcLevel !== null) {
        filtered = filtered.filter(t => Math.floor(t.mc / MC_LEVEL_SIZE) * MC_LEVEL_SIZE === props.mcLevel)
      }
      trades.value = filtered.sort((a, b) => a.ts - b.ts)
    } catch (e) {
      error.value = e.message
    } finally {
      loading.value = false
    }

    await nextTick()
    if (trades.value.length > 0 && chartCanvas.value) {
      renderChart(trades.value, bucketChartConfig())
    }
  }
})

onUnmounted(() => {
  document.removeEventListener('keydown', onKeydown)
  destroyChart()
})

async function fetchAllTrades() {
  if (allTradesFetched) return
  allTradesLoading.value = true
  allTradesError.value = null
  try {
    const res = await fetch(`/api/trades/${props.mint}/all`)
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const data = await res.json()
    allTrades.value = data.trades.sort((a, b) => a.ts - b.ts)
    allTradesFetched = true
  } catch (e) {
    allTradesError.value = e.message
  } finally {
    allTradesLoading.value = false
    loading.value = false
  }
}

// filtered trades for the active view (multiView mode)
const viewTrades = computed(() => {
  if (!props.multiView) return trades.value
  if (viewMode.value === 'full') return allTrades.value
  const n = parseInt(viewMode.value.replace('min', ''))
  const startBucket = (n - 1) * 6
  const endBucket = n * 6
  return allTrades.value.filter(t => t.bucket >= startBucket && t.bucket < endBucket)
})

function minNChartConfig(n) {
  return {
    xMin: (n - 1) * 60,
    xMax: n * 60,
    xLabel: `Time (s) — minute ${n}`,
    xRef: allTrades.value.length > 0 ? allTrades.value[0].ts : 0,
  }
}

function fullChartConfig() {
  return {
    xMin: 0,
    xMax: 600,
    xLabel: 'Time (s)',
    xRef: allTrades.value.length > 0 ? allTrades.value[0].ts : 0,
  }
}

function bucketChartConfig() {
  const t = trades.value
  return {
    xMin: 0,
    xMax: 10,
    xLabel: 'Time (s) within bucket',
    xRef: t.length > 0 ? t[0].ts : 0,
  }
}

watch(viewTrades, async () => {
  if (!props.multiView) return
  await nextTick()
  if (chartCanvas.value) {
    const n = viewMode.value === 'full' ? null : parseInt(viewMode.value.replace('min', ''))
    const cfg = n === null ? fullChartConfig() : minNChartConfig(n)
    renderChart(viewTrades.value, cfg)
  }
}, { immediate: false })

watch(allTradesLoading, async (loading) => {
  if (!loading && props.multiView && chartCanvas.value) {
    await nextTick()
    const cfg = viewMode.value === 'full' ? fullChartConfig() : minNChartConfig(parseInt(viewMode.value.replace('min', '')))
    renderChart(viewTrades.value, cfg)
  }
})

async function setView(mode) {
  viewMode.value = mode
  if (!allTradesFetched) {
    await fetchAllTrades()
  }
}

function destroyChart() {
  if (chartInstance) {
    chartInstance.destroy()
    chartInstance = null
  }
}

function renderChart(t, { xMin, xMax, xLabel, xRef }) {
  destroyChart()
  if (!t.length || !chartCanvas.value) return

  const buys = []
  const sells = []
  buyRadii = []
  sellRadii = []
  tradeChartMap = {}
  let buyIdx = 0, sellIdx = 0

  for (let i = 0; i < t.length; i++) {
    const tr = t[i]
    const r = Math.max(3, Math.min(12, Math.sqrt(tr.sol) * 4))
    const point = { x: (tr.ts - xRef) / 1000, y: tr.mc, sol: tr.sol, r }
    if (tr.side === 'buy') {
      tradeChartMap[i] = { datasetIndex: 0, pointIndex: buyIdx++ }
      buys.push(point)
      buyRadii.push(r)
    } else {
      tradeChartMap[i] = { datasetIndex: 1, pointIndex: sellIdx++ }
      sells.push(point)
      sellRadii.push(r)
    }
  }

  chartInstance = new Chart(chartCanvas.value, {
    type: 'scatter',
    data: {
      datasets: [
        {
          label: 'Buy',
          data: buys,
          backgroundColor: 'rgba(74, 222, 128, 0.7)',
          borderColor: '#4ade80',
          borderWidth: 1,
          pointRadius: buys.map(p => p.r),
        },
        {
          label: 'Sell',
          data: sells,
          backgroundColor: 'rgba(248, 113, 113, 0.7)',
          borderColor: '#f87171',
          borderWidth: 1,
          pointRadius: sells.map(p => p.r),
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          labels: { color: '#888', font: { size: 10 } },
        },
        zoom: {
          zoom: {
            wheel: { enabled: true },
            pinch: { enabled: true },
            mode: 'x',
          },
          pan: {
            enabled: true,
            mode: 'x',
          },
        },
        tooltip: {
          callbacks: {
            label(ctx) {
              const d = ctx.raw
              return `${ctx.dataset.label} | ${d.sol.toFixed(2)} SOL | ${fmtMcUsd(d.y)} | ${d.x.toFixed(2)}s`
            },
          },
        },
      },
      scales: {
        x: {
          title: { display: true, text: xLabel, color: '#666', font: { size: 10 } },
          min: xMin,
          max: xMax,
          ticks: { color: '#666', font: { size: 9 } },
          grid: { color: '#222' },
        },
        y: {
          title: { display: true, text: 'Market Cap (USD)', color: '#666', font: { size: 10 } },
          ticks: {
            color: '#666',
            font: { size: 9 },
            callback(v) { return fmtMcUsd(v) },
          },
          grid: { color: '#222' },
        },
      },
    },
  })
}

const activeDisplayTrades = computed(() => props.multiView ? viewTrades.value : trades.value)

const walletColors = computed(() => {
  const counts = {}
  for (const tr of activeDisplayTrades.value) {
    counts[tr.wallet] = (counts[tr.wallet] || 0) + 1
  }
  const palette = [
    '#f97316','#a78bfa','#38bdf8','#fb7185','#34d399',
    '#fbbf24','#e879f9','#60a5fa','#f472b6','#4ade80',
    '#c084fc','#22d3ee','#f9a8d4','#86efac','#fde68a',
  ]
  let idx = 0
  const map = {}
  for (const [wallet, count] of Object.entries(counts)) {
    if (count > 1) {
      map[wallet] = palette[idx % palette.length]
      idx++
    }
  }
  return map
})

function onTradeHover(i) {
  if (!chartInstance || tradeChartMap[i] === undefined) return
  const { datasetIndex, pointIndex } = tradeChartMap[i]
  chartInstance.data.datasets[0].pointRadius = [...buyRadii]
  chartInstance.data.datasets[1].pointRadius = [...sellRadii]
  const baseR = datasetIndex === 0 ? buyRadii[pointIndex] : sellRadii[pointIndex]
  chartInstance.data.datasets[datasetIndex].pointRadius[pointIndex] = baseR * 2.5
  chartInstance.update('none')
}

function onTradeLeave() {
  if (!chartInstance) return
  chartInstance.data.datasets[0].pointRadius = [...buyRadii]
  chartInstance.data.datasets[1].pointRadius = [...sellRadii]
  chartInstance.update('none')
}

function fmtTime(ts) {
  const d = new Date(ts)
  return d.toLocaleTimeString('hu-HU', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
    + '.' + String(d.getMilliseconds()).padStart(3, '0')
}

const tabs = [
  { key: 'full', label: '600s' },
  { key: 'min1', label: "1m" },
  { key: 'min2', label: "2m" },
  { key: 'min3', label: "3m" },
  { key: 'min4', label: "4m" },
  { key: 'min5', label: "5m" },
  { key: 'min6', label: "6m" },
  { key: 'min7', label: "7m" },
  { key: 'min8', label: "8m" },
  { key: 'min9', label: "9m" },
]

const headerText = computed(() => {
  if (!props.multiView) {
    const base = `Bucket ${props.bucketIdx} (${props.bucketIdx * 10}s – ${props.bucketIdx * 10 + 10}s)`
    const lvl = props.mcLevel !== null ? ` — ${fmtMcUsd(props.mcLevel)} level` : ''
    return `${base}${lvl} — ${trades.value.length} trades`
  }
  if (viewMode.value === 'full') {
    return `Full 600s — ${allTrades.value.length} trades`
  }
  const n = parseInt(viewMode.value.replace('min', ''))
  return `Minute ${n} (${(n-1)*60}s – ${n*60}s) — ${viewTrades.value.length} trades`
})
</script>

<template>
  <div
    class="fixed inset-0 z-50 flex items-center justify-center"
    style="background:rgba(0,0,0,0.75)"
    @click="onBackdropClick"
  >
    <div
      class="bg-[#111] border border-gray-700 rounded-lg shadow-2xl flex flex-col"
      :style="multiView ? 'width:950px;max-width:95vw;max-height:90vh;' : 'width:850px;max-width:95vw;max-height:85vh;'"
    >
      <!-- Header -->
      <div class="flex items-center justify-between px-4 py-2 border-b border-gray-800">
        <span class="text-gray-300 text-sm font-mono">{{ headerText }}</span>
        <button
          class="text-gray-500 hover:text-white text-lg px-2"
          @click="emit('close')"
        >&times;</button>
      </div>

      <!-- Tab bar (csak multiView módban) -->
      <div v-if="multiView" class="flex gap-1 px-4 py-2 border-b border-gray-800 flex-wrap">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          @click="setView(tab.key)"
          :class="[
            'px-2 py-0.5 text-xs font-mono rounded border transition-colors',
            viewMode === tab.key
              ? 'bg-gray-700 border-gray-500 text-white'
              : 'bg-transparent border-gray-700 text-gray-500 hover:border-gray-500 hover:text-gray-300'
          ]"
        >{{ tab.label }}</button>
      </div>

      <!-- Content -->
      <div class="flex flex-col flex-1 p-4" style="min-height:0;">
        <div v-if="loading || allTradesLoading" class="text-gray-500 text-center py-8">Loading...</div>
        <div v-else-if="error || allTradesError" class="text-red-400 text-center py-8">{{ error || allTradesError }}</div>
        <template v-else>
          <!-- Chart -->
          <div v-if="activeDisplayTrades.length > 0" style="height:220px;margin-bottom:12px;flex-shrink:0;position:relative;">
            <button
              class="absolute top-0 right-0 z-10 text-[9px] font-mono px-1 py-0.5 text-gray-600 hover:text-gray-300 border border-gray-800 hover:border-gray-600 rounded transition-colors"
              style="background:#111"
              title="Reset zoom"
              @click="chartInstance && chartInstance.resetZoom()"
            >⟳</button>
            <canvas ref="chartCanvas"></canvas>
          </div>
          <div v-else class="text-gray-600 text-center py-4 text-sm">No trades in this view</div>

          <!-- Trade table -->
          <div v-if="activeDisplayTrades.length > 0" class="overflow-auto flex-1" style="min-height:0;">
            <table class="w-full text-[9px] font-mono border-collapse">
              <thead class="sticky top-0 bg-[#111]">
                <tr class="text-gray-500">
                  <th class="text-left px-2 py-1 border-b border-gray-800">Time</th>
                  <th class="text-center px-2 py-1 border-b border-gray-800">Side</th>
                  <th class="text-right px-2 py-1 border-b border-gray-800">SOL</th>
                  <th class="text-left px-2 py-1 border-b border-gray-800"></th>
                  <th class="text-right px-2 py-1 border-b border-gray-800">MC</th>
                  <th class="text-left px-2 py-1 border-b border-gray-800">Wallet</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="(tr, i) in activeDisplayTrades"
                  :key="i"
                  class="hover:bg-gray-900"
                  @mouseenter="onTradeHover(i)"
                  @mouseleave="onTradeLeave"
                >
                  <td class="text-gray-400 px-2 py-0.5">{{ fmtTime(tr.ts) }}</td>
                  <td class="text-center px-2 py-0.5">
                    <span :class="tr.side === 'buy' ? 'text-green-400' : 'text-red-400'">
                      {{ tr.side }}
                    </span>
                  </td>
                  <td class="text-gray-300 text-right px-2 py-0.5">{{ fmtSol(tr.sol) }}</td>
                  <td class="px-2 py-0.5" :class="tr.side === 'buy' ? 'text-green-600' : 'text-red-700'">{{ '#'.repeat(Math.min(15, Math.max(1, Math.floor(tr.sol)))) }}</td>
                  <td class="text-gray-300 text-right px-2 py-0.5">{{ fmtMcUsd(tr.mc) }}</td>
                  <td class="px-2 py-0.5" :style="walletColors[tr.wallet] ? { color: walletColors[tr.wallet] } : { color: '#4b5563' }">{{ fmtMint(tr.wallet) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>
