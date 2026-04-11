export function cellBgColor(delta, maxAbsDelta) {
  if (maxAbsDelta === 0 || isNaN(delta) || delta === 0) return 'transparent'
  const intensity = Math.min(Math.abs(delta) / maxAbsDelta, 1.0)
  const alpha = (0.20 + 0.70 * intensity).toFixed(2)
  return delta > 0
    ? `rgba(0,180,80,${alpha})`
    : `rgba(220,50,50,${alpha})`
}

export function deltaBgColor(delta, maxAbsDelta) {
  if (delta === 0 || maxAbsDelta === 0) return '#0d0d0d'
  const intensity = Math.min(Math.abs(delta) / maxAbsDelta, 1.0)
  const alpha = (0.25 + 0.65 * intensity).toFixed(2)
  return delta > 0
    ? `rgba(0,180,80,${alpha})`
    : `rgba(220,50,50,${alpha})`
}

export function volumeBgColor(vol, maxVol) {
  if (vol === 0 || maxVol === 0) return '#1a1a1a'
  const intensity = Math.min(vol / maxVol, 1.0)
  const alpha = (0.10 + 0.30 * intensity).toFixed(2)
  return `rgba(100,100,180,${alpha})`
}

export function rsiColor(rsi) {
  if (rsi === null || rsi === undefined) return '#666'
  if (rsi <= 30) return '#ef4444'
  if (rsi >= 70) return '#ef4444'
  return '#4ade80'
}

export function candleShadow(ohlc, mcLevel, mcLevelSize) {
  if (!ohlc) return ''
  const isBull = ohlc.c >= ohlc.o
  const color = isBull ? '#26a69a' : '#ef5350'
  const bodyLo = Math.min(ohlc.o, ohlc.c)
  const bodyHi = Math.max(ohlc.o, ohlc.c)
  const levelHi = mcLevel + mcLevelSize

  if (mcLevel < bodyHi && levelHi > bodyLo) {
    return `box-shadow:inset 5px 0 0 ${color};`
  } else if (mcLevel < ohlc.h && levelHi > ohlc.l) {
    return `box-shadow:inset 2px 0 0 ${color};`
  }
  return ''
}
