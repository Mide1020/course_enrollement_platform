window.Pages.home = async () => {
    return `
        <div class="hero-section text-center fade-in" style="padding: 4rem 0;">
            <h1 style="font-size: 3.5rem; margin-bottom: 1rem; background: linear-gradient(to right, #818cf8, #6366f1); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                Master Your Future
            </h1>
            <p class="text-muted" style="font-size: 1.2rem; max-width: 600px; margin: 0 auto 2rem;">
                Access world-class courses, expert instruction, and a community of learners dedicated to excellence.
            </p>
            <div style="display: flex; gap: 1rem; justify-content: center;">
                <a href="/courses" class="btn btn-primary" onclick="route(event)">Explore Courses</a>
                <a href="/register" class="btn btn-outline" onclick="route(event)">Get Started</a>
            </div>
        </div>

        <section style="margin-top: 5rem;">
            <h2 style="margin-bottom: 2rem;">Why LMS Pro?</h2>
            <div class="grid grid-3">
                <div class="card glass">
                    <i class="fas fa-layer-group" style="color: var(--primary); font-size: 2rem; margin-bottom: 1rem;"></i>
                    <h3>Structured Content</h3>
                    <p class="text-muted">Courses organized into intuitive modules and lessons for optimal learning.</p>
                </div>
                <div class="card glass">
                    <i class="fas fa-file-arrow-up" style="color: var(--primary); font-size: 2rem; margin-bottom: 1rem;"></i>
                    <h3>Rich Resources</h3>
                    <p class="text-muted">Downloadable syllabi, exercise files, and reference materials for every course.</p>
                </div>
                <div class="card glass">
                    <i class="fas fa-chart-line" style="color: var(--primary); font-size: 2rem; margin-bottom: 1rem;"></i>
                    <h3>Analytics Driven</h3>
                    <p class="text-muted">Instructors get real-time data on student performance and course popularity.</p>
                </div>
            </div>
        </section>
    `;
};

window.Init.home = () => {
    // Landing page has no specific init logic for now
};
