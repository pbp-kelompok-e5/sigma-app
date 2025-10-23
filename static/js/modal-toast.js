/**
 * Global Modal and Toast Utilities
 * Provides functions to show/hide modals and toasts with animations
 */

// ===== MODAL UTILITIES =====

/**
 * Show a modal by ID
 * @param {string} modalId - The ID of the modal element
 */
function showModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('show');
        // Prevent body scroll
        document.body.style.overflow = 'hidden';
    }
}

/**
 * Hide a modal by ID
 * @param {string} modalId - The ID of the modal element
 */
function hideModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('show');
        // Restore body scroll
        document.body.style.overflow = 'auto';
    }
}

/**
 * Toggle a modal by ID
 * @param {string} modalId - The ID of the modal element
 */
function toggleModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.toggle('show');
        if (modal.classList.contains('show')) {
            document.body.style.overflow = 'hidden';
        } else {
            document.body.style.overflow = 'auto';
        }
    }
}

/**
 * Initialize modal close buttons
 * Automatically closes modal when close button or backdrop is clicked
 */
function initializeModals() {
    // Close button functionality
    document.querySelectorAll('.modal-close').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const modal = this.closest('.modal');
            if (modal) {
                hideModal(modal.id);
            }
        });
    });

    // Backdrop click to close
    document.querySelectorAll('.modal-backdrop').forEach(backdrop => {
        backdrop.addEventListener('click', function(e) {
            if (e.target === this) {
                const modal = this.closest('.modal');
                if (modal) {
                    hideModal(modal.id);
                }
            }
        });
    });

    // Escape key to close
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            const openModals = document.querySelectorAll('.modal.show');
            if (openModals.length > 0) {
                hideModal(openModals[openModals.length - 1].id);
            }
        }
    });
}

// ===== TOAST UTILITIES =====

/**
 * Show a toast notification
 * @param {string} message - The message to display
 * @param {string} type - The type of toast: 'success', 'error', 'warning', 'info'
 * @param {number} duration - Duration in milliseconds (default: 3000)
 */
function showToast(message, type = 'info', duration = 3000) {
    // Create toast container if it doesn't exist
    let toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        toastContainer.style.position = 'fixed';
        toastContainer.style.bottom = '16px';
        toastContainer.style.right = '16px';
        toastContainer.style.zIndex = '50';
        toastContainer.style.pointerEvents = 'none';
        document.body.appendChild(toastContainer);
    }

    // Create toast element
    const toastId = 'toast-' + Date.now();
    const toast = document.createElement('div');
    toast.id = toastId;
    toast.className = `toast toast-${type}`;
    
    // Determine icon based on type
    let iconSvg = '';
    if (type === 'success') {
        iconSvg = '<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path></svg>';
    } else if (type === 'error') {
        iconSvg = '<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"></path></svg>';
    } else if (type === 'warning') {
        iconSvg = '<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"></path></svg>';
    } else {
        iconSvg = '<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M18 5v8a2 2 0 01-2 2h-5l-5 4v-4H4a2 2 0 01-2-2V5a2 2 0 012-2h12a2 2 0 012 2zm-11-1a1 1 0 11-2 0 1 1 0 012 0zm3 0a1 1 0 11-2 0 1 1 0 012 0zm3 0a1 1 0 11-2 0 1 1 0 012 0z" clip-rule="evenodd"></path></svg>';
    }

    toast.innerHTML = `
        <div class="toast-icon">${iconSvg}</div>
        <div class="toast-message">${DOMPurify.sanitize(message)}</div>
        <button type="button" class="toast-close" aria-label="Close toast">
            <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"></path>
            </svg>
        </button>
    `;

    toastContainer.appendChild(toast);
    toastContainer.style.pointerEvents = 'auto';

    // Trigger animation
    setTimeout(() => {
        toast.classList.add('show');
    }, 10);

    // Close button functionality
    toast.querySelector('.toast-close').addEventListener('click', function() {
        hideToast(toastId);
    });

    // Auto-hide after duration
    if (duration > 0) {
        setTimeout(() => {
            hideToast(toastId);
        }, duration);
    }

    return toastId;
}

/**
 * Hide a toast by ID
 * @param {string} toastId - The ID of the toast element
 */
function hideToast(toastId) {
    const toast = document.getElementById(toastId);
    if (toast) {
        toast.classList.remove('show');
        setTimeout(() => {
            toast.remove();
        }, 300);
    }
}

/**
 * Show a success toast
 * @param {string} message - The message to display
 * @param {number} duration - Duration in milliseconds (default: 3000)
 */
function showSuccessToast(message, duration = 3000) {
    return showToast(message, 'success', duration);
}

/**
 * Show an error toast
 * @param {string} message - The message to display
 * @param {number} duration - Duration in milliseconds (default: 3000)
 */
function showErrorToast(message, duration = 3000) {
    return showToast(message, 'error', duration);
}

/**
 * Show a warning toast
 * @param {string} message - The message to display
 * @param {number} duration - Duration in milliseconds (default: 3000)
 */
function showWarningToast(message, duration = 3000) {
    return showToast(message, 'warning', duration);
}

/**
 * Show an info toast
 * @param {string} message - The message to display
 * @param {number} duration - Duration in milliseconds (default: 3000)
 */
function showInfoToast(message, duration = 3000) {
    return showToast(message, 'info', duration);
}

// Initialize modals when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    initializeModals();
});

