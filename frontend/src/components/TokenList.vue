<script setup>
import TokenRow from './TokenRow.vue'

defineProps({
  tokens: { type: Array, default: () => [] },
  selectedMint: { type: String, default: null },
})

const emit = defineEmits(['select'])
</script>

<template>
  <div class="border border-gray-800 rounded mb-2 overflow-y-auto" style="max-height:20vh;">
    <table class="w-full text-xs">
      <thead class="sticky top-0 z-10" style="background:#0d0d0d;">
        <tr class="text-gray-500 border-b border-gray-800">
          <th class="text-left px-2 py-1 font-normal">Token</th>
          <th class="text-left px-2 py-1 font-normal w-20">Pad</th>
          <th class="text-right px-2 py-1 font-normal w-14">Time</th>
          <th class="text-right px-2 py-1 font-normal w-14">Trades</th>
          <th class="text-right px-2 py-1 font-normal w-10">NW</th>
          <th class="text-right px-2 py-1 font-normal w-16">Vol</th>
          <th class="text-right px-2 py-1 font-normal w-16">Delta</th>
          <th class="text-right px-2 py-1 font-normal w-12">Buy%</th>
          <th class="text-right px-2 py-1 font-normal w-12">UW</th>
          <th class="text-right px-2 py-1 font-normal w-20">MCap</th>
          <th class="text-right px-2 py-1 font-normal w-14">RSI</th>
        </tr>
      </thead>
      <tbody>
        <TokenRow
          v-for="token in tokens"
          :key="token.mint"
          :token="token"
          :selected="token.mint === selectedMint"
          @select="emit('select', token.mint)"
        />
      </tbody>
    </table>
    <div v-if="tokens.length === 0" class="text-gray-600 text-xs text-center py-3">
      Waiting for token migrations...
    </div>
  </div>
</template>
