<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { Chart, ScatterController, LinearScale, PointElement, Tooltip, Legend } from 'chart.js'
import { fmtSol, fmtMcUsd, fmtMint } from '../utils/format.js'

Chart.register(ScatterController, LinearScale, PointElement, Tooltip, Legend)

const props = defineProps({
  mint: { type: String, required: true },
  bucketIdx: { type: Number, required: true },
})

const emit = defineEmits(['close'])

const loading = ref(true)
const error = ref(null)
const trades = ref([])
const chartCanvas = ref(null)
let chartInstance = null

function onKeydown(e) {
  if (e.key === 'Escape') emit('close')
}

function onBackdropClick(e) {
  if (e.target === e.currentTarget) emit('close')
}

onMounted(async () => {
  document.addEventListener('keydown', onKeydown)
  try {
    const res = await fetch(`/api/trades/${props.mint}/${props.bucketIdx}`)
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const data = await res.json()
    trades.value = data.trades.sort((a, b) => a.ts - b.ts)
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }

  await nextTick()
  if (trades.value.length > 0 && chartCanvas.value) {
    renderChart()
  }
})

onUnmounted(() => {
  document.removeEventListener('keydown', onKeydown)
  if (chartInstance) {
    chartInstance.destroy()
    chartInstance = null
  }
})

function renderChart() {
  const t = trades.value
  if (!t.length) return

  const minTs = t[0].ts
  const buys = []
  const sells = []

  for (const tr of t) {
    const point = {
      x: (tr.ts - minTs) / 1000,
      y: tr.mc,
      r: Math.max(3, Math.min(12, Math.sqrt(tr.sol) * 4)),
    }
    if (tr.side === 'buy') buys.push(point)
    else sells.push(point)
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
        tooltip: {
          callbacks: {
            label(ctx) {
              const d = ctx.raw
              return `${ctx.dataset.label} | ${d.y.toLocaleString()} USD | ${d.x.toFixed(2)}s`
            },
          },
        },
      },
      scales: {
        x: {
          title: { display: true, text: 'Time (s)', color: '#666', font: { size: 10 } },
          min: 0,
          max: 10,
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

function fmtTime(ts) {
  const d = new Date(ts)
  return d.toLocaleTimeString('hu-HU', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
    + '.' + String(d.getMilliseconds()).padStart(3, '0')
}
</script>

<template>
  <div
    class="fixed inset-0 z-50 flex items-center justify-center"
    style="background:rgba(0,0,0,0.75)"
    @click="onBackdropClick"
  >
    <div
      class="bg-[#111] border border-gray-700 rounded-lg shadow-2xl flex flex-col"
      style="width:850px;max-width:95vw;max-height:85vh;"
    >
      <!-- Header -->
      <div class="flex items-center justify-between px-4 py-2 border-b border-gray-800">
        <span class="text-gray-300 text-sm font-mono">
          Bucket {{ bucketIdx }} ({{ bucketIdx * 10 }}s - {{ bucketIdx * 10 + 10 }}s)
          &mdash; {{ trades.length }} trades
        </span>
        <button
          class="text-gray-500 hover:text-white text-lg px-2"
          @click="emit('close')"
        >&times;</button>
      </div>

      <!-- Content -->
      <div class="flex-1 overflow-auto p-4" style="min-height:0;">
        <div v-if="loading" class="text-gray-500 text-center py-8">Loading...</div>
        <div v-else-if="error" class="text-red-400 text-center py-8">{{ error }}</div>
        <template v-else>
          <!-- Chart -->
          <div v-if="trades.length > 0" style="height:220px;margin-bottom:12px;">
            <canvas ref="chartCanvas"></canvas>
          </div>
          <div v-else class="text-gray-600 text-center py-4 text-sm">No trades in this bucket</div>

          <!-- Trade table -->
          <table v-if="trades.length > 0" class="w-full text-[9px] font-mono border-collapse">
            <thead>
              <tr class="text-gray-500">
                <th class="text-left px-2 py-1 border-b border-gray-800">Time</th>
                <th class="text-center px-2 py-1 border-b border-gray-800">Side</th>
                <th class="text-right px-2 py-1 border-b border-gray-800">SOL</th>
                <th class="text-right px-2 py-1 border-b border-gray-800">MC</th>
                <th class="text-left px-2 py-1 border-b border-gray-800">Wallet</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(tr, i) in trades" :key="i" class="hover:bg-gray-900">
                <td class="text-gray-400 px-2 py-0.5">{{ fmtTime(tr.ts) }}</td>
                <td class="text-center px-2 py-0.5">
                  <span :class="tr.side === 'buy' ? 'text-green-400' : 'text-red-400'">
                    {{ tr.side }}
                  </span>
                </td>
                <td class="text-gray-300 text-right px-2 py-0.5">{{ fmtSol(tr.sol) }}</td>
                <td class="text-gray-300 text-right px-2 py-0.5">{{ fmtMcUsd(tr.mc) }}</td>
                <td class="text-gray-600 px-2 py-0.5">{{ fmtMint(tr.wallet) }}</td>
              </tr>
            </tbody>
          </table>
        </template>
      </div>
    </div>
  </div>
</template>
