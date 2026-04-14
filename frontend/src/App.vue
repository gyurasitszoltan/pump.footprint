<script setup>
import { useWebSocket } from './composables/useWebSocket.js'
import { useTokenStore } from './composables/useTokenStore.js'
import TokenList from './components/TokenList.vue'
import FootprintChart from './components/FootprintChart.vue'

const store = useTokenStore()
const { connected, selectToken: wsSelectToken, unselectToken, deleteToken, likeToken } = useWebSocket(store.handleMessage)

function onSelectToken(mint) {
  store.selectToken(mint)
  wsSelectToken(mint)
}

function onDeleteToken(mint) {
  deleteToken(mint)
}

function onLikeToken(mint, liked) {
  likeToken(mint, liked)
}

function requestNotificationPermission() {
  if ('Notification' in window && Notification.permission === 'default') {
    Notification.requestPermission()
  }
}
</script>

<template>
  <div class="min-h-screen p-2">
    <div class="flex items-center gap-3 mb-2 px-2">
      <h1 class="text-sm font-bold text-gray-400">PUMP FOOTPRINT</h1>
      <span
        class="w-2 h-2 rounded-full cursor-pointer"
        :class="connected ? 'bg-green-500' : 'bg-red-500'"
        :title="connected ? 'Connected' : 'Disconnected'"
        @click="requestNotificationPermission"
      />
    </div>

    <TokenList
      :tokens="store.tokenList.value"
      :selected-mint="store.selectedMint.value"
      @select="onSelectToken"
      @delete="onDeleteToken"
      @like="onLikeToken"
    />

    <FootprintChart
      v-if="store.selectedMint.value"
      :footprint="store.footprint"
    />
    <div v-else class="text-gray-600 text-sm mt-8 text-center">
      Select a token to view footprint chart
    </div>
  </div>
</template>
