<template>
  <div ref="chartRef" class="base-chart" :style="{ height: height, width: width }"></div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, nextTick, markRaw } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  options: {
    type: Object,
    required: true
  },
  height: {
    type: String,
    default: '300px'
  },
  width: {
    type: String,
    default: '100%'
  },
  theme: {
    type: String,
    default: 'light'
  },
  autoResize: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['click', 'legendselectchanged'])

const chartRef = ref(null)
let chartInstance = null

const initChart = () => {
  if (chartRef.value) {
    chartInstance = markRaw(echarts.init(chartRef.value, props.theme))
    chartInstance.setOption(props.options, true)
    
    chartInstance.on('click', (params) => {
      emit('click', params)
    })
    
    chartInstance.on('legendselectchanged', (params) => {
      emit('legendselectchanged', params)
    })
    
    if (props.autoResize) {
      window.addEventListener('resize', handleResize)
    }
  }
}

const handleResize = () => {
  chartInstance?.resize()
}

const updateOptions = (newOptions) => {
  chartInstance?.setOption(newOptions, { notMerge: false })
}

watch(() => props.options, (newOptions) => {
  nextTick(() => {
    updateOptions(newOptions)
  })
}, { deep: true })

watch(() => props.theme, (newTheme) => {
  chartInstance?.dispose()
  chartInstance = markRaw(echarts.init(chartRef.value, newTheme))
  chartInstance.setOption(props.options, true)
})

onMounted(() => {
  nextTick(() => {
    initChart()
  })
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  chartInstance?.dispose()
})

defineExpose({
  resize: handleResize,
  getInstance: () => chartInstance
})
</script>

<style lang="scss" scoped>
.base-chart {
  min-height: 200px;
}
</style>
