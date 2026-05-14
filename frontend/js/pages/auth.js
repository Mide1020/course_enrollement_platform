window.Pages.login = async () => {
    return `
        <div style="max-width: 400px; margin: 4rem auto;" class="fade-in">
            <div class="card glass">
                <h2 class="text-center" style="margin-bottom: 2rem;">Welcome Back</h2>
                <form id="login-form">
                    <div class="form-group">
                        <label>Email Address</label>
                        <input type="email" id="login-email" required placeholder="name@company.com">
                    </div>
                    <div class="form-group">
                        <label>Password</label>
                        <input type="password" id="login-password" required placeholder="••••••••">
                    </div>
                    <button type="submit" id="login-btn" class="btn btn-primary" style="width: 100%; margin-top: 1rem;">Login</button>
                </form>
                <p class="text-center text-muted" style="margin-top: 1.5rem; font-size: 0.9rem;">
                    Don't have an account? <a href="/register" onclick="route(event)" style="color: var(--primary);">Sign up</a>
                </p>
            </div>
        </div>
    `;
};

window.Init.login = () => {
    const form = document.getElementById('login-form');
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = document.getElementById('login-email').value;
        const password = document.getElementById('login-password').value;
        const btn = document.getElementById('login-btn');

        try {
            btn.disabled = true;
            btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Logging in...';
            await api.login(email, password);
            window.router.navigate('/dashboard');
        } catch (error) {
            window.showToast(error.message, 'error');
        } finally {
            btn.disabled = false;
            btn.innerHTML = 'Login';
        }
    });
};

window.Pages.register = async () => {
    return `
        <div style="max-width: 450px; margin: 2rem auto;" class="fade-in">
            <div class="card glass">
                <h2 class="text-center" style="margin-bottom: 2rem;">Create Account</h2>
                <form id="register-form">
                    <div class="form-group">
                        <label>Full Name</label>
                        <input type="text" id="reg-name" required placeholder="John Doe">
                    </div>
                    <div class="form-group">
                        <label>Email Address</label>
                        <input type="email" id="reg-email" required placeholder="name@company.com">
                    </div>
                    <div class="form-group">
                        <label>Password</label>
                        <input type="password" id="reg-password" required placeholder="••••••••">
                    </div>
                    <div class="form-group">
                        <label>Role</label>
                        <select id="reg-role" class="glass">
                            <option value="student">Student</option>
                            <option value="instructor">Instructor</option>
                        </select>
                    </div>
                    <button type="submit" id="register-btn" class="btn btn-primary" style="width: 100%; margin-top: 1rem;">Create Account</button>
                </form>
                <p class="text-center text-muted" style="margin-top: 1.5rem; font-size: 0.9rem;">
                    Already have an account? <a href="/login" onclick="route(event)" style="color: var(--primary);">Login</a>
                </p>
            </div>
        </div>
    `;
};

window.Init.register = () => {
    const form = document.getElementById('register-form');
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const userData = {
            name: document.getElementById('reg-name').value,
            email: document.getElementById('reg-email').value,
            password: document.getElementById('reg-password').value,
            role: document.getElementById('reg-role').value,
        };
        const btn = document.getElementById('register-btn');

        try {
            btn.disabled = true;
            btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Creating account...';
            await api.register(userData);
            window.showToast('Account created! Please log in.', 'success');
            window.router.navigate('/login');
        } catch (error) {
            window.showToast(error.message, 'error');
        } finally {
            btn.disabled = false;
            btn.innerHTML = 'Create Account';
        }
    });
};

