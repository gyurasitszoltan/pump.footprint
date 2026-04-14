import { ref, onUnmounted } from 'vue'

export function useWebSocket(onMessage) {
  const connected = ref(false)
  let ws = null
  let backoff = 1000
  let reconnectTimer = null

  function connect() {
    const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:'
    const url = `${protocol}//${location.host}/ws`

    ws = new WebSocket(url)
    ws.binaryType = 'arraybuffer'

    ws.onopen = () => {
      connected.value = true
      backoff = 1000
    }

    ws.onmessage = (event) => {
      try {
        const data = typeof event.data === 'string'
          ? JSON.parse(event.data)
          : JSON.parse(new TextDecoder().decode(event.data))
        onMessage(data)
      } catch (e) {
        console.error('WS parse error:', e)
      }
    }

    ws.onclose = () => {
      connected.value = false
      scheduleReconnect()
    }

    ws.onerror = () => {
      ws.close()
    }
  }

  function scheduleReconnect() {
    reconnectTimer = setTimeout(() => {
      backoff = Math.min(backoff * 2, 30000)
      connect()
    }, backoff)
  }

  function send(data) {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify(data))
    }
  }

  function selectToken(mint) {
    send({ type: 'select_token', mint })
  }

  function unselectToken() {
    send({ type: 'unselect_token' })
  }

  function deleteToken(mint) {
    send({ type: 'delete_token', mint })
  }

  function likeToken(mint, liked) {
    send({ type: 'like_token', mint, liked })
  }

  connect()

  onUnmounted(() => {
    clearTimeout(reconnectTimer)
    if (ws) ws.close()
  })

  return { connected, send, selectToken, unselectToken, deleteToken, likeToken }
}
