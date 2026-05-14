window.Pages.dashboard = async () => {
    const name = localStorage.getItem('user_name') || 'Student';
    return `
        <div class="fade-in" style="padding: 1rem;">
            <div style="margin-bottom: 3rem;">
                <h1>Welcome back, ${name}!</h1>
                <p class="text-muted">Here are your active enrollments and learning progress.</p>
            </div>
            
            <div id="enrolled-courses" class="grid grid-2" style="gap: 2rem;">
                <div class="loader-container"><div class="loader"></div></div>
            </div>
        </div>
    `;
};

window.Init.dashboard = async () => {
    const container = document.getElementById('enrolled-courses');
    if (!container) return;

    try {
        const enrollments = await api.getMyEnrollments();
        
        container.innerHTML = enrollments.map(e => `
            <div class="card glass">
                <div style="display: flex; gap: 2rem; align-items: center;">
                    <div style="width: 100px; height: 100px; background: var(--bg-glass); border-radius: 12px; display: flex; align-items: center; justify-content: center; border: 1px solid var(--border);">
                        <i class="fas fa-play" style="color: var(--primary); font-size: 1.5rem;"></i>
                    </div>
                    <div style="flex: 1;">
                        <h3 style="font-size: 1.25rem; margin-bottom: 0.5rem;">${e.course.title}</h3>
                        <p class="text-muted">Code: <span style="color: var(--text-main);">${e.course.code}</span></p>
                        <p class="text-muted">Status: <span style="color: var(--success); text-transform: capitalize; font-weight: 600;">${e.status}</span>
                        ${e.grade ? ` &nbsp;|&nbsp; Grade: <span style="color: var(--warning); font-weight: 600;">${e.grade}</span>` : ''}
                        </p>
                    </div>
                </div>
                <div style="margin-top: 2rem; display: flex; justify-content: space-between; align-items: center;">
                    <span class="text-muted" style="font-size: 0.9rem;">
                        <i class="fas fa-calendar" style="margin-right: 0.4rem;"></i>
                        Enrolled ${new Date(e.created_at).toLocaleDateString()}
                    </span>
                    <div style="display: flex; gap: 0.5rem;">
                        <button class="btn btn-outline drop-btn" data-id="${e.id}" style="padding: 0.6rem 1rem; font-size: 0.9rem; color: var(--error); border-color: rgba(239, 68, 68, 0.2);">
                            Drop
                        </button>
                        <a href="/courses/${e.course.id}" class="btn btn-primary" style="padding: 0.6rem 1.25rem; font-size: 0.9rem;" onclick="route(event)">
                            Continue Learning <i class="fas fa-arrow-right" style="font-size: 0.8rem; margin-left: 0.25rem;"></i>
                        </a>
                    </div>
                </div>
            </div>
        `).join('');
        
        // Add drop logic
        document.querySelectorAll('.drop-btn').forEach(btn => {
            btn.onclick = async () => {
                if (confirm('Are you sure you want to drop this course?')) {
                    try {
                        btn.disabled = true;
                        await api.dropCourse(btn.dataset.id);
                        window.showToast('Course dropped');
                        window.Init.dashboard();
                    } catch (err) {
                        window.showToast(err.message, 'error');
                        btn.disabled = false;
                    }
                }
            };
        });
        
        if (enrollments.length === 0) {
            container.innerHTML = `
                <div class="card glass text-center" style="grid-column: 1/-1; padding: 4rem;">
                    <i class="fas fa-book-open" style="font-size: 3rem; color: var(--text-dim); margin-bottom: 1.5rem;"></i>
                    <p class="text-muted" style="font-size: 1.1rem; margin-bottom: 2rem;">You are not enrolled in any courses yet.</p>
                    <a href="/courses" class="btn btn-primary" onclick="route(event)">Browse Catalog</a>
                </div>
            `;
        }
    } catch (error) {
        console.error('Failed to load dashboard', error);
        container.innerHTML = `<p class="text-error">Error loading your dashboard: ${error.message}</p>`;
    }
};
