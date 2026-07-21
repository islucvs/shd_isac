/**
 * UI Module
 * Handles UI utilities, toast notifications, modals, and common UI operations
 */

/**
 * Toast Notification System
 */
class ToastManager {
    constructor() {
        this.container = null;
        this.init();
    }
    
    init() {
        this.container = document.createElement('div');
        this.container.className = 'toast-container';
        document.body.appendChild(this.container);
    }
    
    show(message, type = 'info', title = '') {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        
        const toastTitle = title || this.getDefaultTitle(type);
        
        toast.innerHTML = `
            <div class="toast-title">${toastTitle}</div>
            <div class="toast-message">${message}</div>
        `;
        
        this.container.appendChild(toast);
        
        // Auto remove after 4 seconds
        setTimeout(() => {
            toast.classList.add('toast-exit');
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
            }, 300);
        }, 4000);
        
        return toast;
    }
    
    getDefaultTitle(type) {
        const titles = {
            info: 'ISAC NOTIFICATION',
            success: 'MISSION COMPLETE',
            error: 'SYSTEM ERROR',
            warning: 'WARNING'
        };
        return titles[type] || 'NOTIFICATION';
    }
    
    success(message, title) {
        return this.show(message, 'success', title);
    }
    
    error(message, title) {
        return this.show(message, 'error', title);
    }
    
    warning(message, title) {
        return this.show(message, 'warning', title);
    }
    
    info(message, title) {
        return this.show(message, 'info', title);
    }
}

/**
 * Modal System
 */
class ModalManager {
    constructor() {
        this.activeModal = null;
        this.backdrop = null;
    }
    
    open(content, options = {}) {
        this.close();
        
        // Create backdrop
        this.backdrop = document.createElement('div');
        this.backdrop.className = 'modal-backdrop';
        this.backdrop.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            backdrop-filter: blur(5px);
            z-index: 1000;
            display: flex;
            align-items: center;
            justify-content: center;
            animation: modal-backdrop-in 0.3s ease;
        `;
        
        // Create modal content
        const modalContent = document.createElement('div');
        modalContent.className = 'modal-content';
        modalContent.style.cssText = `
            background: rgba(75, 74, 74, 0.538);
            backdrop-filter: blur(13px);
            -webkit-backdrop-filter: blur(13px);
            border: 1px solid var(--color-glass-border);
            border-radius: var(--border-radius-md);
            padding: var(--spacing-xl);
            max-width: ${options.maxWidth || '500px'};
            width: 90%;
            max-height: 90vh;
            overflow-y: auto;
            position: relative;
            animation: modal-content-in 0.3s ease;
        `;
        
        // Close button
        const closeBtn = document.createElement('button');
        closeBtn.innerHTML = '&times;';
        closeBtn.style.cssText = `
            position: absolute;
            top: var(--spacing-md);
            right: var(--spacing-md);
            background: none;
            border: none;
            color: var(--color-text-secondary);
            font-size: 1.5rem;
            cursor: pointer;
            transition: color 0.2s ease;
        `;
        closeBtn.onmouseenter = () => closeBtn.style.color = 'var(--color-accent-primary)';
        closeBtn.onmouseleave = () => closeBtn.style.color = 'var(--color-text-secondary)';
        closeBtn.onclick = () => this.close();
        
        modalContent.appendChild(closeBtn);
        
        if (typeof content === 'string') {
            const contentDiv = document.createElement('div');
            contentDiv.innerHTML = content;
            modalContent.appendChild(contentDiv);
        } else if (content instanceof HTMLElement) {
            modalContent.appendChild(content);
        }
        
        this.backdrop.appendChild(modalContent);
        document.body.appendChild(this.backdrop);
        this.activeModal = this.backdrop;
        
        // Close on backdrop click
        this.backdrop.addEventListener('click', (e) => {
            if (e.target === this.backdrop && !options.preventBackdropClose) {
                this.close();
            }
        });
        
        // Close on ESC
        const escHandler = (e) => {
            if (e.key === 'Escape') {
                this.close();
                document.removeEventListener('keydown', escHandler);
            }
        };
        document.addEventListener('keydown', escHandler);
        
        return modalContent;
    }
    
    close() {
        if (this.activeModal) {
            const content = this.activeModal.querySelector('.modal-content');
            if (content) {
                content.style.animation = 'modal-content-out 0.3s ease forwards';
            }
            setTimeout(() => {
                if (this.activeModal && this.activeModal.parentNode) {
                    this.activeModal.parentNode.removeChild(this.activeModal);
                }
                this.activeModal = null;
            }, 300);
        }
    }
    
    confirm(message, title = 'CONFIRM ACTION') {
        return new Promise((resolve) => {
            const content = document.createElement('div');
            content.innerHTML = `
                <h3 style="font-family: var(--font-display); font-size: 1.1rem; color: var(--color-accent-primary); margin-bottom: var(--spacing-md); text-transform: uppercase; letter-spacing: 2px;">${title}</h3>
                <p style="color: var(--color-text-secondary); margin-bottom: var(--spacing-xl); line-height: 1.6;">${message}</p>
                <div style="display: flex; gap: var(--spacing-md); justify-content: flex-end;">
                    <button class="btn" id="modal-cancel">CANCEL</button>
                    <button class="btn btn-danger" id="modal-confirm">CONFIRM</button>
                </div>
            `;
            
            const modal = this.open(content, { preventBackdropClose: true });
            
            modal.querySelector('#modal-cancel').addEventListener('click', () => {
                this.close();
                resolve(false);
            });
            
            modal.querySelector('#modal-confirm').addEventListener('click', () => {
                this.close();
                resolve(true);
            });
        });
    }
}

/**
 * Loading Screen Manager
 */
class LoadingManager {
    constructor() {
        this.element = null;
        this.progressBar = null;
        this.init();
    }
    
    init() {
        this.element = document.createElement('div');
        this.element.className = 'loading-screen';
        this.element.innerHTML = `
            <div>
                <img style="height: 100px;" src="assets/logo.png">
            </div>
            <div class="loading-text">INITIALIZING SYSTEMS...</div>
            <div class="loading-progress">
                <div class="loading-progress-bar"></div>
            </div>
        `;
        document.body.appendChild(this.element);
        this.progressBar = this.element.querySelector('.loading-progress-bar');
    }
    
    setProgress(percent) {
        if (this.progressBar) {
            this.progressBar.style.width = `${percent}%`;
        }
    }
    
    hide() {
        if (this.element) {
            this.setProgress(100);
            setTimeout(() => {
                this.element.classList.add('hidden');
                setTimeout(() => {
                    if (this.element && this.element.parentNode) {
                        this.element.parentNode.removeChild(this.element);
                    }
                }, 3000);
            }, 0);
        }
    }
}

/**
 * Time Display
 */
function updateTimeDisplay() {
    const timeElements = document.querySelectorAll('.current-time');
    const now = new Date();
    const timeString = now.toLocaleTimeString('en-US', { 
        hour12: false, 
        hour: '2-digit', 
        minute: '2-digit',
        second: '2-digit'
    });
    timeElements.forEach(el => {
        el.textContent = timeString;
    });
}

/**
 * Utility Functions
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function throttle(func, limit) {
    let inThrottle;
    return function executedFunction(...args) {
        if (!inThrottle) {
            func(...args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}

function generateId() {
    return Date.now().toString(36) + Math.random().toString(36).substr(2);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Export singletons
export const toast = new ToastManager();
export const modal = new ModalManager();
export const loading = new LoadingManager();

// Export utilities
export {
    updateTimeDisplay,
    debounce,
    throttle,
    formatNumber,
    generateId,
    escapeHtml
};
