<script setup>
import { computed } from 'vue'
import FootprintCell from './FootprintCell.vue'
import { candleShadow } from '../utils/colors.js'

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

function getCandleShadow(bucket, level) {
  return candleShadow(getOhlc(bucket), level, MC_LEVEL_SIZE)
}
</script>

<template>
  <table class="border-collapse" style="font-family:monospace;table-layout:fixed;background:#0d0d0d;">
    <thead>
      <tr>
        <th
          class="text-gray-500 font-normal text-right border-r border-gray-800 whitespace-nowrap"
          style="width:52px;min-width:52px;font-size:8px;padding:1px 4px;"
        >MC\T</th>
        <th
          v-for="b in buckets"
          :key="b"
          class="text-gray-600 font-normal border-r whitespace-nowrap"
          :style="{
            width: CELL_W + 'px', minWidth: CELL_W + 'px', maxWidth: CELL_W + 'px',
            height: CELL_H + 'px', fontSize: '8px', padding: '1px 3px',
            textAlign: 'center', borderColor: '#1a1a1a'
          }"
        >{{ timeLabel(b) }}</th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="level in mcLevels" :key="level">
        <td
          class="text-gray-500 text-right whitespace-nowrap border-r border-gray-800"
          style="font-size:8px;padding:1px 4px;border-bottom:1px solid #1a1a1a;"
        >{{ mcLabel(level) }}</td>
        <td
          v-for="b in buckets"
          :key="b"
          :style="{
            width: CELL_W + 'px', minWidth: CELL_W + 'px', maxWidth: CELL_W + 'px',
            height: CELL_H + 'px', fontSize: '8px', padding: '0 2px',
            textAlign: 'center', whiteSpace: 'nowrap', overflow: 'hidden',
            borderBottom: isPoc(b, level) ? '1px solid #ffd700' : '1px solid #111',
            borderTop: isPoc(b, level) ? '1px solid #ffd700' : 'none',
            borderRight: '1px solid #111',
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
  </table>
</template>
