<script setup>
import { computed } from 'vue'
import { cellBgColor } from '../utils/colors.js'

const props = defineProps({
  cell: { type: Object, default: null },
  maxAbsDelta: { type: Number, default: 1 },
  candleShadow: { type: String, default: '' },
})

const bg = computed(() => {
  if (!props.cell) return '#0d0d0d'
  return cellBgColor(props.cell.delta, props.maxAbsDelta)
})

const buyStyle = computed(() => {
  if (!props.cell) return {}
  const imb = props.cell.buy_imb
  return {
    color: imb ? '#2dd4bf' : '#4ade80',
    fontWeight: imb ? 'bold' : 'normal',
  }
})

const sellStyle = computed(() => {
  if (!props.cell) return {}
  const imb = props.cell.sell_imb
  return {
    color: imb ? '#f472b6' : '#f87171',
    fontWeight: imb ? 'bold' : 'normal',
  }
})
</script>

<template>
  <div
    v-if="cell"
    class="w-full h-full flex items-center justify-center"
    :style="{ background: bg, [candleShadow ? 'boxShadow' : '']: candleShadow.replace('box-shadow:', '').replace(';', '') }"
  >
    <span :style="buyStyle">{{ cell.buy.toFixed(1) }}</span>
    <span style="color:#aaa;margin:0 1px;">|</span>
    <span :style="sellStyle">{{ cell.sell.toFixed(1) }}</span>
  </div>
  <div v-else class="w-full h-full" :style="{ background: '#0d0d0d', ...(candleShadow ? { boxShadow: candleShadow.replace('box-shadow:', '').replace(';', '') } : {}) }" />
</template>
