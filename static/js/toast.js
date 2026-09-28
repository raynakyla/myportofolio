let toastHideTimeout;

function showToast(title, message, type = 'normal', duration = 3000) {
    const toast = document.getElementById('toast-component');
    const icon = document.getElementById('toast-icon');
    const titleElement = document.getElementById('toast-title');
    const messageElement = document.getElementById('toast-message');

    if (!toast || !icon || !titleElement || !messageElement) {
        return;
    }

    const toastType = ['success', 'error'].includes(type) ? type : 'normal';
    const icons = { success: '✓', error: '!', normal: '✦' };

    clearTimeout(toastHideTimeout);
    toast.classList.remove('toast--success', 'toast--error', 'toast--normal');
    toast.classList.add(`toast--${toastType}`);
    toast.setAttribute('role', toastType === 'error' ? 'alert' : 'status');
    toast.setAttribute('aria-live', toastType === 'error' ? 'assertive' : 'polite');
    toast.setAttribute('aria-hidden', 'false');
    icon.textContent = icons[toastType];
    titleElement.textContent = title;
    messageElement.textContent = message;
    toast.classList.add('is-visible');

    toastHideTimeout = setTimeout(() => {
        toast.classList.remove('is-visible');
        toast.setAttribute('aria-hidden', 'true');
    }, duration);
}
