/**
 * 主题相关组合式函数
 * 提供暗黑模式切换和主题管理
 */

import { ref, computed, onMounted, watch } from 'vue'
import { useAppStore } from '@/stores/app'

/**
 * 使用主题
 */
export function useTheme() {
    const appStore = useAppStore()

    const isDark = computed(() => appStore.theme === 'dark')

    // 初始化主题
    const initTheme = () => {
        const savedTheme = localStorage.getItem('weibo_theme') || 'light'
        applyTheme(savedTheme)
    }

    // 应用主题
    const applyTheme = (themeName) => {
        const html = document.documentElement

        if (themeName === 'dark') {
            html.classList.add('dark')
        } else {
            html.classList.remove('dark')
        }

        html.setAttribute('data-theme', themeName)
    }

    // 切换主题
    const toggleTheme = () => {
        const newTheme = isDark.value ? 'light' : 'dark'
        appStore.setTheme(newTheme)
        applyTheme(newTheme)
    }

    // 设置主题
    const setTheme = (themeName) => {
        appStore.setTheme(themeName)
        applyTheme(themeName)
    }

    // 监听主题变化
    watch(() => appStore.theme, (newTheme) => {
        applyTheme(newTheme)
    })

    // 初始化
    onMounted(() => {
        initTheme()
    })

    return {
        isDark,
        toggleTheme,
        setTheme,
        initTheme
    }
}

/**
 * 主题色配置
 */
export const themeColors = {
    light: {
        primary: '#0078D4',
        success: '#28a745',
        warning: '#ffc107',
        danger: '#dc3545',
        info: '#6c757d',
        background: '#f0f2f5',
        cardBg: '#ffffff',
        textPrimary: '#333333',
        textSecondary: '#666666',
        border: '#e8e8e8'
    },
    dark: {
        primary: '#3794ff',
        success: '#34d058',
        warning: '#ffcc00',
        danger: '#ea4a5a',
        info: '#8b949e',
        background: '#0d1117',
        cardBg: '#161b22',
        textPrimary: '#c9d1d9',
        textSecondary: '#8b949e',
        border: '#30363d'
    }
}

/**
 * 获取当前主题色
 */
export function getThemeColor(colorName) {
    const theme = localStorage.getItem('weibo_theme') || 'light'
    return themeColors[theme]?.[colorName] || themeColors.light[colorName]
}
