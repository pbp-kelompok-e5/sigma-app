/**
 * AJAX Utilities for Sigma App
 * Provides helper functions for AJAX requests with toast notifications
 */

/**
 * Make a POST request with CSRF token
 * @param {string} url - The endpoint URL
 * @param {object} data - Data to send (will be JSON stringified)
 * @param {object} options - Additional options (onSuccess, onError, showToast)
 * @returns {Promise}
 */
function ajaxPost(url, data = {}, options = {}) {
    const {
        onSuccess = null,
        onError = null,
        showToast = true,
        successMessage = 'Operation successful',
        errorMessage = 'An error occurred',
    } = options;

    // Get CSRF token from cookie
    const csrfToken = getCookie('csrftoken');

    return fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
        },
        body: JSON.stringify(data),
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (showToast && data.success) {
            showSuccessToast(data.message || successMessage);
        }
        if (onSuccess) {
            onSuccess(data);
        }
        return data;
    })
    .catch(error => {
        console.error('AJAX Error:', error);
        if (showToast) {
            showErrorToast(errorMessage);
        }
        if (onError) {
            onError(error);
        }
        throw error;
    });
}

/**
 * Make a DELETE request with CSRF token
 * @param {string} url - The endpoint URL
 * @param {object} options - Additional options
 * @returns {Promise}
 */
function ajaxDelete(url, options = {}) {
    const {
        onSuccess = null,
        onError = null,
        showToast = true,
        successMessage = 'Deleted successfully',
        errorMessage = 'Failed to delete',
    } = options;

    const csrfToken = getCookie('csrftoken');

    return fetch(url, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
        },
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (showToast && data.success) {
            showSuccessToast(data.message || successMessage);
        }
        if (onSuccess) {
            onSuccess(data);
        }
        return data;
    })
    .catch(error => {
        console.error('AJAX Error:', error);
        if (showToast) {
            showErrorToast(errorMessage);
        }
        if (onError) {
            onError(error);
        }
        throw error;
    });
}

/**
 * Make a GET request
 * @param {string} url - The endpoint URL
 * @param {object} options - Additional options
 * @returns {Promise}
 */
function ajaxGet(url, options = {}) {
    const {
        onSuccess = null,
        onError = null,
        showToast = false,
        errorMessage = 'Failed to fetch data',
    } = options;

    return fetch(url, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        },
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (onSuccess) {
            onSuccess(data);
        }
        return data;
    })
    .catch(error => {
        console.error('AJAX Error:', error);
        if (showToast) {
            showErrorToast(errorMessage);
        }
        if (onError) {
            onError(error);
        }
        throw error;
    });
}

/**
 * Get CSRF token from cookies
 * @param {string} name - Cookie name
 * @returns {string} Cookie value
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/**
 * Show loading state on element
 * @param {HTMLElement} element - Element to show loading state
 * @param {string} loadingText - Text to show while loading
 */
function showLoading(element, loadingText = 'Loading...') {
    element.disabled = true;
    element.dataset.originalText = element.textContent;
    element.textContent = loadingText;
    element.classList.add('opacity-50', 'cursor-not-allowed');
}

/**
 * Hide loading state on element
 * @param {HTMLElement} element - Element to hide loading state
 */
function hideLoading(element) {
    element.disabled = false;
    element.textContent = element.dataset.originalText || 'Submit';
    element.classList.remove('opacity-50', 'cursor-not-allowed');
}

/**
 * Debounce function for search/filter operations
 * @param {Function} func - Function to debounce
 * @param {number} wait - Wait time in milliseconds
 * @returns {Function} Debounced function
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

/**
 * Throttle function for scroll/resize operations
 * @param {Function} func - Function to throttle
 * @param {number} limit - Limit time in milliseconds
 * @returns {Function} Throttled function
 */
function throttle(func, limit) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

