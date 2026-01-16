/**
 * 错误页面通用交互脚本
 * 微博舆情分析可视化系统
 * 提供404页面和错误页面的交互效果
 */

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function () {
    initErrorPageEffects();
});

/**
 * 初始化错误页面所有交互效果
 */
function initErrorPageEffects() {
    initMouseParallax();
    initButtonRippleEffects();
    initCardTiltEffect();
    initScrollAnimations();
    addCustomStyles();
}

/**
 * 鼠标移动视差效果
 */
function initMouseParallax() {
    document.addEventListener('mousemove', function (e) {
        const mouseX = e.clientX / window.innerWidth;
        const mouseY = e.clientY / window.innerHeight;

        // 浮动元素视差效果
        const floatingElements = document.querySelectorAll('.floating-element, .particle');
        floatingElements.forEach((element, index) => {
            const speed = (index + 1) * 0.02;
            const x = (mouseX - 0.5) * speed * 100;
            const y = (mouseY - 0.5) * speed * 100;
            element.style.transform = `translate(${x}px, ${y}px)`;
        });
    });
}

/**
 * 按钮波纹点击效果
 */
function initButtonRippleEffects() {
    const buttons = document.querySelectorAll('.modern-button, .back-button, .action-button');

    buttons.forEach(button => {
        button.addEventListener('click', function (e) {
            createRippleEffect(e, this);
        });
    });
}

/**
 * 创建波纹效果
 * @param {Event} e - 点击事件
 * @param {Element} element - 被点击的元素
 */
function createRippleEffect(e, element) {
    const ripple = document.createElement('span');
    const rect = element.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    const x = e.clientX - rect.left - size / 2;
    const y = e.clientY - rect.top - size / 2;

    ripple.className = 'ripple-effect';
    ripple.style.cssText = `
        position: absolute;
        width: ${size}px;
        height: ${size}px;
        left: ${x}px;
        top: ${y}px;
        background: rgba(255, 255, 255, 0.3);
        border-radius: 50%;
        transform: scale(0);
        animation: ripple 0.6s linear;
        pointer-events: none;
        z-index: 1000;
    `;

    // 确保按钮具有相对定位
    if (getComputedStyle(element).position === 'static') {
        element.style.position = 'relative';
    }

    element.appendChild(ripple);

    // 移除波纹元素
    setTimeout(() => {
        if (ripple.parentNode) {
            ripple.parentNode.removeChild(ripple);
        }
    }, 600);
}

/**
 * 卡片倾斜效果（仅适用于错误页面）
 */
function initCardTiltEffect() {
    const card = document.querySelector('.error-card, .glass-card');
    if (!card) return;

    document.addEventListener('mousemove', function (e) {
        const mouseX = e.clientX / window.innerWidth;
        const mouseY = e.clientY / window.innerHeight;

        const tiltX = (mouseY - 0.5) * 5;
        const tiltY = (mouseX - 0.5) * -5;

        card.style.transform = `perspective(1000px) rotateX(${tiltX}deg) rotateY(${tiltY}deg)`;
    });

    // 鼠标离开时重置倾斜
    document.addEventListener('mouseleave', function () {
        card.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg)';
    });
}

/**
 * 滚动动画效果
 */
function initScrollAnimations() {
    // 为错误消息添加延迟动画
    const errorMessage = document.querySelector('.error-message');
    if (errorMessage && errorMessage.textContent.trim()) {
        errorMessage.style.animation = 'fadeInBounce 0.8s ease-out 0.5s both';
    }

    // 为按钮添加交错出现动画
    const buttons = document.querySelectorAll('.action-button, .back-button');
    buttons.forEach((button, index) => {
        button.style.animation = `fadeInUp 0.6s ease-out ${0.3 + index * 0.1}s both`;
    });
}

/**
 * 添加动态样式
 */
function addCustomStyles() {
    if (document.getElementById('error-page-dynamic-styles')) return;

    const style = document.createElement('style');
    style.id = 'error-page-dynamic-styles';
    style.textContent = `
        @keyframes ripple {
            to {
                transform: scale(4);
                opacity: 0;
            }
        }
        
        @keyframes fadeInBounce {
            0% {
                opacity: 0;
                transform: translateY(-20px);
            }
            60% {
                opacity: 1;
                transform: translateY(5px);
            }
            100% {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        /* 增强按钮悬停效果 */
        .modern-button:hover,
        .back-button:hover,
        .action-button:hover {
            animation: buttonPulse 0.3s ease-out;
        }
        
        @keyframes buttonPulse {
            0% {
                transform: translateY(-3px) scale(1);
            }
            50% {
                transform: translateY(-3px) scale(1.05);
            }
            100% {
                transform: translateY(-3px) scale(1);
            }
        }
        
        /* 页面加载动画 */
        .error-page-body {
            animation: pageLoad 1s ease-out;
        }
        
        @keyframes pageLoad {
            from {
                opacity: 0;
            }
            to {
                opacity: 1;
            }
        }
        
        /* 提升玻璃效果 */
        .glass-card:hover {
            backdrop-filter: blur(25px);
            border: 1px solid rgba(255, 255, 255, 0.3);
            transition: all 0.3s ease;
        }
        
        /* 图标旋转效果 */
        .error-icon:hover svg,
        .icon-container:hover svg {
            animation: iconSpin 1s ease-in-out;
        }
        
        @keyframes iconSpin {
            from {
                transform: rotate(0deg);
            }
            to {
                transform: rotate(360deg);
            }
        }
    `;

    document.head.appendChild(style);
}

/**
 * 主题切换功能（为将来扩展准备）
 */
function toggleTheme(theme = 'auto') {
    const body = document.body;

    switch (theme) {
        case 'dark':
            body.classList.add('theme-dark');
            body.classList.remove('theme-light');
            break;
        case 'light':
            body.classList.add('theme-light');
            body.classList.remove('theme-dark');
            break;
        default:
            // 自动检测系统主题
            if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
                body.classList.add('theme-dark');
                body.classList.remove('theme-light');
            } else {
                body.classList.add('theme-light');
                body.classList.remove('theme-dark');
            }
    }
}

/**
 * 错误信息展示增强
 */
function enhanceErrorDisplay() {
    const errorMessage = document.querySelector('.error-message');
    if (!errorMessage) return;

    const message = errorMessage.textContent.trim();
    if (message) {
        // 如果错误信息过长，添加展开/收起功能
        if (message.length > 100) {
            const shortMessage = message.substring(0, 100) + '...';
            const fullMessage = message;

            errorMessage.innerHTML = `
                <span class="message-text">${shortMessage}</span>
                <button class="expand-btn" onclick="toggleErrorMessage(this)">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                        <path d="M6 9L12 15L18 9" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                </button>
            `;

            errorMessage.setAttribute('data-full-message', fullMessage);
            errorMessage.setAttribute('data-short-message', shortMessage);
        }
    }
}

/**
 * 切换错误信息显示
 */
function toggleErrorMessage(button) {
    const errorMessage = button.closest('.error-message');
    const messageText = errorMessage.querySelector('.message-text');
    const fullMessage = errorMessage.getAttribute('data-full-message');
    const shortMessage = errorMessage.getAttribute('data-short-message');
    const isExpanded = errorMessage.classList.contains('expanded');

    if (isExpanded) {
        messageText.textContent = shortMessage;
        button.innerHTML = `
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                <path d="M6 9L12 15L18 9" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
        `;
        errorMessage.classList.remove('expanded');
    } else {
        messageText.textContent = fullMessage;
        button.innerHTML = `
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                <path d="M18 15L12 9L6 15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
        `;
        errorMessage.classList.add('expanded');
    }
}

/**
 * 性能优化：防抖函数
 */
function debounce(func, wait, immediate) {
    let timeout;
    return function executedFunction() {
        const context = this;
        const args = arguments;
        const later = function () {
            timeout = null;
            if (!immediate) func.apply(context, args);
        };
        const callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func.apply(context, args);
    };
}

// 优化鼠标移动事件性能
const optimizedMouseMove = debounce(function (e) {
    // 在这里可以添加更复杂的鼠标移动效果
}, 16); // 约60fps

// 监听窗口大小变化，调整响应式效果
window.addEventListener('resize', debounce(function () {
    // 重新计算和调整动画效果
    const floatingElements = document.querySelectorAll('.floating-element, .particle');
    floatingElements.forEach(element => {
        element.style.transform = 'translate(0, 0)';
    });
}, 250));

// 导出函数供外部使用
window.ErrorPageEffects = {
    init: initErrorPageEffects,
    toggleTheme: toggleTheme,
    enhanceErrorDisplay: enhanceErrorDisplay
};