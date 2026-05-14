// Global Utilities & Toast System
window.showToast = (message, type = 'success') => {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast toast-${type} fade-in`;
    const icon = type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle';
    
    const displayMessage = typeof message === 'string' ? message : JSON.stringify(message);
    
    toast.innerHTML = `
        <i class="fas ${icon}" style="font-size: 1.25rem;"></i>
        <span style="font-weight: 500;">${displayMessage}</span>
    `;
    
    container.appendChild(toast);
    
    // Auto-remove
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(20px)';
        toast.style.transition = 'all 0.3s ease-out';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
};

// Global Error Handler
window.addEventListener('error', (event) => {
    console.error('Uncaught error:', event.error);
    // Silent fail for non-critical errors, log for debugging
});
