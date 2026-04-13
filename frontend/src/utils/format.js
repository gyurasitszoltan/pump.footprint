export function fmtSol(v) {
  if (v === 0) return ''
  if (Math.abs(v) >= 1000) return `${(v / 1000).toFixed(1)}K`
  return v.toFixed(1)
}

export function fmtSolSigned(v) {
  if (v === 0) return ''
  const abs = Math.abs(v)
  const str = abs >= 1000 ? `${(abs / 1000).toFixed(1)}K` : abs.toFixed(1)
  return v < 0 ? `-${str}` : str
}

export function fmtMcUsd(v) {
  if (v >= 1_000_000) return `$${(v / 1_000_000).toFixed(1)}M`
  if (v >= 1000) return `$${(v / 1000).toFixed(1)}K`
  return `$${v.toFixed(0)}`
}

export function fmtMcSigned(v) {
  if (v === 0 || v == null) return ''
  const abs = Math.abs(v)
  let str
  if (abs >= 1_000_000) str = `${(abs / 1_000_000).toFixed(1)}M`
  else if (abs >= 1000) str = `${(abs / 1000).toFixed(1)}K`
  else str = abs.toFixed(0)
  return v < 0 ? `-${str}` : str
}

export function fmtMint(mint) {
  if (!mint || mint.length <= 10) return mint
  return `${mint.slice(0, 6)}...${mint.slice(-4)}`
}
