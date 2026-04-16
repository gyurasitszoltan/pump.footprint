<script setup>
import { ref } from 'vue'
import { useSettings } from '../composables/useSettings.js'

defineProps({ modelValue: Boolean })
const emit = defineEmits(['update:modelValue'])

const { settings, resetSettings, DEFAULT_SETTINGS } = useSettings()

const activeTab = ref('BAR STAT')
const tabs = ['BAR STAT']

function close() {
  emit('update:modelValue', false)
}

function onOverlayClick(e) {
  if (e.target === e.currentTarget) close()
}
</script>

<template>
  <Teleport to="body">
    <div
      v-if="modelValue"
      class="fixed inset-0 z-50 flex items-center justify-center"
      style="background: rgba(0,0,0,0.6)"
      @click="onOverlayClick"
    >
      <div
        style="background:#1a1a1a; border:1px solid #333; font-family:monospace; width:320px; max-height:80vh; display:flex; flex-direction:column; border-radius:4px;"
      >
        <!-- Header -->
        <div style="display:flex; align-items:center; justify-content:space-between; padding:8px 12px; border-bottom:1px solid #333;">
          <span style="color:#888; font-size:11px; font-weight:bold; letter-spacing:1px;">SETTINGS</span>
          <button
            @click="close"
            style="color:#555; background:none; border:none; cursor:pointer; font-size:14px; line-height:1; padding:0 2px;"
            title="Close"
          >✕</button>
        </div>

        <!-- Tabs -->
        <div style="display:flex; border-bottom:1px solid #333;">
          <button
            v-for="tab in tabs"
            :key="tab"
            @click="activeTab = tab"
            :style="{
              padding: '5px 12px',
              fontSize: '10px',
              fontFamily: 'monospace',
              letterSpacing: '0.5px',
              background: 'none',
              border: 'none',
              borderBottom: activeTab === tab ? '2px solid #555' : '2px solid transparent',
              color: activeTab === tab ? '#ccc' : '#555',
              cursor: 'pointer',
            }"
          >{{ tab }}</button>
        </div>

        <!-- Tab content -->
        <div style="flex:1; overflow-y:auto; padding:10px 12px;">
          <!-- BAR STAT tab -->
          <template v-if="activeTab === 'BAR STAT'">
            <div
              v-for="key in Object.keys(DEFAULT_SETTINGS.barStat.rows)"
              :key="key"
              style="display:flex; align-items:center; justify-content:space-between; padding:3px 0; border-bottom:1px solid #1f1f1f;"
            >
              <span style="color:#aaa; font-size:11px;">{{ key }}</span>
              <label style="position:relative; display:inline-block; width:28px; height:15px; cursor:pointer;">
                <input
                  type="checkbox"
                  v-model="settings.barStat.rows[key]"
                  style="opacity:0; width:0; height:0; position:absolute;"
                />
                <span
                  :style="{
                    position: 'absolute',
                    inset: 0,
                    borderRadius: '8px',
                    background: settings.barStat.rows[key] ? '#3a7a3a' : '#333',
                    transition: 'background 0.15s',
                  }"
                ></span>
                <span
                  :style="{
                    position: 'absolute',
                    top: '2px',
                    left: settings.barStat.rows[key] ? '15px' : '2px',
                    width: '11px',
                    height: '11px',
                    borderRadius: '50%',
                    background: settings.barStat.rows[key] ? '#7dff7d' : '#666',
                    transition: 'left 0.15s, background 0.15s',
                  }"
                ></span>
              </label>
            </div>
          </template>
        </div>

        <!-- Footer -->
        <div style="padding:6px 12px; border-top:1px solid #333; display:flex; justify-content:flex-end;">
          <button
            @click="resetSettings"
            style="font-family:monospace; font-size:10px; color:#555; background:none; border:1px solid #333; cursor:pointer; padding:3px 8px; border-radius:3px;"
          >RESET</button>
        </div>
      </div>
    </div>
  </Teleport>
</template>
