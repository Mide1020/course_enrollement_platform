const routes = {
    '/': 'home',
    '/login': 'login',
    '/register': 'register',
    '/courses': 'catalog',
    '/dashboard': 'dashboard',
    '/instructor': 'instructor',
    '/profile': 'profile',
};

class Router {
    constructor() {
        this.viewContainer = document.getElementById('main-view');
        window.addEventListener('popstate', () => this.handleRoute());
        this.handleRoute();
    }

    async navigate(path) {
        window.history.pushState({}, '', path);
        await this.handleRoute();
    }

    async handleRoute() {
        let path = window.location.pathname;
        let view = routes[path] || null;
        let routeParam = null;

        // Handle dynamic routes: /courses/:id and /instructor/courses/:id
        if (!view && path.startsWith('/instructor/courses/')) {
            const courseId = path.replace('/instructor/courses/', '');
            if (courseId) {
                view = 'manage';
                routeParam = courseId;
            }
        } else if (!view && path.startsWith('/courses/')) {
            const courseId = path.replace('/courses/', '');
            if (courseId && courseId.length > 0) {
                view = 'course';
                routeParam = courseId;
            }
        }

        if (!view) view = '404';

        // Handle role-based dashboard redirection
        if (view === 'dashboard') {
            const role = localStorage.getItem('user_role');
            if (role === 'instructor' || role === 'admin') {
                view = 'instructor';
            }
        }
        
        // Show loading state
        this.viewContainer.innerHTML = '<div class="loader-container"><div class="loader"></div></div>';
        
        try {
            const content = await this.loadView(view, routeParam);
            this.viewContainer.innerHTML = content;
            this.viewContainer.classList.add('fade-in');
            
            // Re-trigger animations
            setTimeout(() => this.viewContainer.classList.remove('fade-in'), 400);
            
            // Initialize page-specific logic
            this.initPage(view, routeParam);
        } catch (error) {
            this.viewContainer.innerHTML = `
                <div class="text-center" style="padding: 4rem;">
                    <h1 style="margin-bottom: 1rem;">Something went wrong</h1>
                    <p class="text-muted">${error.message}</p>
                </div>`;
        }
    }

    async loadView(view, param = null) {
        if (typeof window.Pages[view] === 'function') {
            return await window.Pages[view](param);
        }
        return `
            <div class="text-center" style="padding: 6rem 2rem;">
                <h1 style="font-size: 4rem; color: var(--primary); margin-bottom: 1rem;">404</h1>
                <h2 style="margin-bottom: 1rem;">Page Not Found</h2>
                <p class="text-muted" style="margin-bottom: 2rem;">The page you are looking for does not exist.</p>
                <a href="/" onclick="route(event)" class="btn btn-primary">Go Home</a>
            </div>`;
    }

    initPage(view, param = null) {
        if (typeof window.Init[view] === 'function') {
            window.Init[view](param);
        }
        this.updateNavbar();
    }

    updateNavbar() {
        const authSection = document.getElementById('nav-auth-section');
        const token = localStorage.getItem('access_token');
        
        if (token) {
            const role = localStorage.getItem('user_role');
            const dashLabel = (role === 'instructor' || role === 'admin') ? 'My Dashboard' : 'My Dashboard';
            authSection.innerHTML = `
                <a href="/courses" class="nav-link" onclick="route(event)"><i class="fas fa-book"></i> Courses</a>
                <a href="/dashboard" class="nav-link" onclick="route(event)"><i class="fas fa-th-large"></i> ${dashLabel}</a>
                <a href="/profile" class="nav-link" onclick="route(event)"><i class="fas fa-user-circle"></i> Profile</a>
                <button class="btn btn-outline" onclick="api.logout()" style="padding: 0.6rem 1.25rem;">Logout</button>
            `;
        } else {
            authSection.innerHTML = `
                <a href="/courses" class="nav-link" onclick="route(event)"><i class="fas fa-book"></i> Courses</a>
                <a href="/login" class="btn btn-outline" onclick="route(event)">Login</a>
                <a href="/register" class="btn btn-primary" onclick="route(event)">Join Now</a>
            `;
        }
    }
}

// Global route helper
window.route = (event) => {
    event.preventDefault();
    const path = event.currentTarget.getAttribute('href');
    window.router.navigate(path);
};

// Placeholder for page contents
window.Pages = {};
window.Init = {};

window.addEventListener('DOMContentLoaded', () => {
    window.router = new Router();
});
