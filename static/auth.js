// static/auth.js
const backendURL = '/api/auth';

const loginForm = document.getElementById('loginForm');
const registerForm = document.getElementById('registerForm');

function showToast(message, type = 'error') {
    const toastContainer = document.getElementById('toastContainer');
    if (!toastContainer) {
        const newContainer = document.createElement('div');
        newContainer.id = 'toastContainer';
        document.body.appendChild(newContainer);
    }
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    document.getElementById('toastContainer').appendChild(toast);
    setTimeout(() => toast.remove(), 4000);
}

if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = document.getElementById('loginEmail').value;
        const password = document.getElementById('loginPassword').value;
        try {
            const res = await fetch(`${backendURL}/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password }),
            });
            const data = await res.json();
            if (!res.ok) throw new Error(data.message);

            localStorage.setItem('authToken', data.token);
            window.location.href = '/app'; // Redirect to main app
        } catch (error) {
            showToast(error.message || 'Login failed.');
        }
    });
}

if (registerForm) {
    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const name = document.getElementById('registerName').value;
        const email = document.getElementById('registerEmail').value;
        const password = document.getElementById('registerPassword').value;
        // REMOVED: The line that tried to get 'dietaryPreference'

        try {
            const res = await fetch(`${backendURL}/register`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                // UPDATED: The body now only sends the correct fields
                body: JSON.stringify({ name, email, password }),
            });
            const data = await res.json();
            if (!res.ok) throw new Error(data.message);

            showToast('Registration successful! Please log in.', 'success');
            setTimeout(() => {
                window.location.href = '/login'; // Redirect to login page
            }, 1500);
        } catch (error) {
            showToast(error.message || 'Registration failed.');
        }
    });
}

