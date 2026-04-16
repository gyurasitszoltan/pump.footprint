import { reactive, watch } from 'vue'

const STORAGE_KEY = 'pf_settings'

const DEFAULT_SETTINGS = {
  barStat: {
    rows: {
      'Volume':    true,
      'B|S':       true,
      'Buy%':      true,
      'Delta':     true,
      'CVD':       true,
      'EMA±':      true,
      'Trades':    true,
      'N Wall':    true,
      'Pool':      true,
      'Size Bins': true,
      'RSI':       true,
    }
  }
}

function deepMerge(target, source) {
  const result = { ...target }
  for (const key of Object.keys(source)) {
    if (source[key] && typeof source[key] === 'object' && !Array.isArray(source[key])) {
      result[key] = deepMerge(target[key] ?? {}, source[key])
    } else {
      result[key] = source[key]
    }
  }
  return result
}

function loadSettings() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (raw) {
      const parsed = JSON.parse(raw)
      return deepMerge(DEFAULT_SETTINGS, parsed)
    }
  } catch {}
  return deepMerge({}, DEFAULT_SETTINGS)
}

// Singleton – module-scope reactive state
const settings = reactive(loadSettings())

watch(settings, () => {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(settings))
}, { deep: true })

export function useSettings() {
  function resetSettings() {
    const defaults = deepMerge({}, DEFAULT_SETTINGS)
    Object.assign(settings, defaults)
    settings.barStat.rows = { ...defaults.barStat.rows }
  }

  return { settings, resetSettings, DEFAULT_SETTINGS }
}
