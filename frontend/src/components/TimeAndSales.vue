<script setup>
import { ref, computed } from 'vue'
import { fmtMcUsd } from '../utils/format.js'

const props = defineProps({
  trades: { type: Array, required: true },
})

const minSol = ref(0)

const filteredTrades = computed(() =>
  props.trades.filter(t => t.sol >= minSol.value)
)

function fmtTime(tsMs) {
  return new Date(tsMs).toLocaleTimeString('en-GB', {
    hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false,
  })
}
</script>

<template>
  <div class="ts-panel">
    <div class="ts-header">
      <span class="ts-col-time">Time</span>
      <span class="ts-col-mc">MC</span>
      <span class="ts-col-sol">SOL</span>
    </div>
    <div class="ts-body">
      <div
        v-for="(trade, idx) in filteredTrades"
        :key="idx"
        class="ts-row"
        :class="trade.side === 'buy' ? 'ts-buy' : 'ts-sell'"
      >
        <span class="ts-col-time">{{ fmtTime(trade.ts) }}</span>
        <span class="ts-col-mc">{{ fmtMcUsd(trade.mc) }}</span>
        <span class="ts-col-sol">{{ trade.sol.toFixed(2) }}</span>
      </div>
    </div>
    <div class="ts-filter">
      <span class="ts-filter-label">min {{ minSol }} SOL</span>
      <input
        v-model.number="minSol"
        type="range"
        min="0"
        max="10"
        step="1"
        class="ts-slider"
      />
    </div>
  </div>
</template>

<style scoped>
.ts-panel {
  width: 168px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  border: 1px solid #1f2937;
  border-radius: 4px;
  background: #0d0d0d;
  font-family: ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, monospace;
  font-size: 10px;
  overflow: hidden;
}
.ts-header {
  display: flex;
  padding: 3px 4px;
  border-bottom: 1px solid #1f2937;
  color: #6b7280;
  background: #0d0d0d;
}
.ts-body { overflow-y: auto; flex: 1; }
.ts-row  { display: flex; padding: 1px 4px; }
.ts-buy  { color: #4ade80; }
.ts-sell { color: #f87171; }
.ts-col-time { width: 56px; flex-shrink: 0; }
.ts-col-mc   { flex: 1; text-align: right; padding-right: 4px; }
.ts-col-sol  { width: 36px; flex-shrink: 0; text-align: right; }

.ts-filter {
  border-top: 1px solid #1f2937;
  padding: 4px 6px;
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.ts-filter-label {
  color: #6b7280;
  text-align: center;
}
.ts-slider {
  width: 100%;
  accent-color: #4b5563;
  cursor: pointer;
}
</style>
