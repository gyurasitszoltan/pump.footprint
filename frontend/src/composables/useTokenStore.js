import { reactive, ref, computed } from 'vue'

const tokens = reactive(new Map())
const selectedMint = ref(null)
const footprint = reactive({
  mint: null,
  mc_levels: [],
  cells: {},
  ohlc: {},
  stats: {},
  poc: {},
  rsi14: null,
  current_bucket: 0,
  max_abs_delta: 1,
  size_bins: [1, 2],
})

export function useTokenStore() {
  function handleMessage(data) {
    const handlers = {
      token_list: handleTokenList,
      token_added: handleTokenAdded,
      token_removed: handleTokenRemoved,
      token_summary_update: handleSummaryUpdate,
      token_liked: handleTokenLiked,
      footprint_snapshot: handleFootprintSnapshot,
      footprint_update: handleFootprintUpdate,
    }
    const handler = handlers[data.type]
    if (handler) handler(data)
  }

  function handleTokenList(data) {
    tokens.clear()
    for (const t of data.tokens) {
      tokens.set(t.mint, t)
    }
    // If selected token was removed
    if (selectedMint.value && !tokens.has(selectedMint.value)) {
      selectedMint.value = null
      clearFootprint()
    }
  }

  function handleTokenAdded(data) {
    tokens.set(data.token.mint, data.token)
    sendTokenNotification(data.token)
  }

  function sendTokenNotification(token) {
    if (!('Notification' in window)) return
    const title = `🚀 ${token.symbol || token.mint.slice(0, 6)}`
    const options = { body: token.name || '', tag: token.mint, renotify: false }
    if (Notification.permission === 'granted') {
      new Notification(title, options)
    } else if (Notification.permission === 'default') {
      Notification.requestPermission().then(perm => {
        if (perm === 'granted') new Notification(title, options)
      })
    }
  }

  function handleTokenRemoved(data) {
    tokens.delete(data.mint)
    if (selectedMint.value === data.mint) {
      selectedMint.value = null
      clearFootprint()
    }
  }

  function handleSummaryUpdate(data) {
    const existing = tokens.get(data.mint)
    if (existing) {
      Object.assign(existing, data)
    }
  }

  function handleTokenLiked(data) {
    const existing = tokens.get(data.mint)
    if (existing) {
      existing.liked = data.liked
    }
  }

  function handleFootprintSnapshot(data) {
    footprint.mint = data.mint
    footprint.mc_levels = data.mc_levels
    footprint.cells = data.cells
    footprint.ohlc = data.ohlc
    footprint.stats = data.stats
    footprint.poc = data.poc
    footprint.rsi14 = data.rsi14
    footprint.current_bucket = data.current_bucket
    footprint.max_abs_delta = data.max_abs_delta
    footprint.size_bins = data.size_bins || [1, 2]
  }

  function handleFootprintUpdate(data) {
    if (data.mint !== footprint.mint) return

    const key = `${data.bucket}:${data.mc_level}`
    footprint.cells[key] = data.cell
    footprint.ohlc[String(data.bucket)] = data.ohlc
    footprint.stats[String(data.bucket)] = data.stats
    if (data.poc !== null && data.poc !== undefined) {
      footprint.poc[String(data.bucket)] = data.poc
    }
    footprint.current_bucket = data.bucket
    footprint.max_abs_delta = data.max_abs_delta

    if (data.mc_levels_expanded) {
      footprint.mc_levels = data.mc_levels_expanded
    }

    // Merge imbalance updates
    if (data.imbalance_updates) {
      for (const imb of data.imbalance_updates) {
        const imbKey = `${imb.bucket}:${imb.mc_level}`
        const cell = footprint.cells[imbKey]
        if (cell) {
          cell.buy_imb = imb.buy_imb
          cell.sell_imb = imb.sell_imb
        }
      }
    }
  }

  function clearFootprint() {
    footprint.mint = null
    footprint.mc_levels = []
    footprint.cells = {}
    footprint.ohlc = {}
    footprint.stats = {}
    footprint.poc = {}
    footprint.rsi14 = null
    footprint.current_bucket = 0
    footprint.max_abs_delta = 1
    footprint.size_bins = [1, 2]
  }

  function selectToken(mint) {
    selectedMint.value = mint
  }

  const tokenList = computed(() => Array.from(tokens.values()).reverse())

  return {
    tokens,
    tokenList,
    selectedMint,
    footprint,
    handleMessage,
    selectToken,
  }
}
