const AUTH_STORAGE_KEY = 'askasktask_is_auth';

function isAuthed() {
    return localStorage.getItem(AUTH_STORAGE_KEY) === 'true';
}

function applyAuthState() {
    document.body.classList.toggle('is-guest', !isAuthed());
}

function logout() {
    localStorage.setItem(AUTH_STORAGE_KEY, 'false');
    window.location.href = 'index.html'; 
}

function handleFormSubmit(event) {
    event.preventDefault();
    
    localStorage.setItem(AUTH_STORAGE_KEY, 'true');
    
    window.location.href = 'index.html';
}

function initAuth() {
    applyAuthState();

    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', logout);
    }

    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', handleFormSubmit);
    }

    const registerForm = document.getElementById('register-form');
    if (registerForm) {
        registerForm.addEventListener('submit', handleFormSubmit);
    }
}