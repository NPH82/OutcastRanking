/**
 * Dark Mode Toggle Functionality
 * Shared across all templates to eliminate code duplication
 */

// Dark Mode Toggle Function
function toggleDarkMode() {
    const body = document.body;
    const darkModeBtn = document.getElementById('darkModeBtn');
    
    if (body.getAttribute('data-theme') === 'dark') {
        body.removeAttribute('data-theme');
        darkModeBtn.innerHTML = '🌙';
        localStorage.setItem('theme', 'light');
    } else {
        body.setAttribute('data-theme', 'dark');
        darkModeBtn.innerHTML = '☀️';
        localStorage.setItem('theme', 'dark');
    }
}

// Load saved theme on page load
document.addEventListener('DOMContentLoaded', function() {
    const savedTheme = localStorage.getItem('theme');
    const darkModeBtn = document.getElementById('darkModeBtn');
    
    if (darkModeBtn) {
        if (savedTheme === 'dark') {
            document.body.setAttribute('data-theme', 'dark');
            darkModeBtn.innerHTML = '☀️';
        } else {
            darkModeBtn.innerHTML = '🌙';
        }
    }
});