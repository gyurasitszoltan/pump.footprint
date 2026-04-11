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

export function fmtMint(mint) {
  if (!mint || mint.length <= 10) return mint
  return `${mint.slice(0, 6)}...${mint.slice(-4)}`
}
