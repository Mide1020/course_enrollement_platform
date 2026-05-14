window.Pages.instructor = async () => {
    let name = localStorage.getItem('user_name') || 'Instructor';
    if (name === 'string') name = 'Instructor';
    
    return `
        <div class="fade-in" style="padding: 1rem;">
            <div class="header-with-actions" style="margin-bottom: 3rem;">
                <div>
                    <h1>Instructor Dashboard (${name})</h1>
                    <p class="text-muted">Manage your courses and track student performance.</p>
                </div>
                <button class="btn btn-primary" id="open-create-modal"><i class="fas fa-plus"></i> Create New Course</button>
            </div>
            
            <div id="analytics-overview" class="grid grid-3" style="margin-bottom: 4rem;">
                <div class="card glass text-center">
                    <p class="text-muted" style="font-size: 0.9rem; margin-bottom: 0.5rem;">Total Students</p>
                    <h2 id="total-students" style="font-size: 2.5rem; color: var(--primary);">--</h2>
                </div>
                <div class="card glass text-center">
                    <p class="text-muted" style="font-size: 0.9rem; margin-bottom: 0.5rem;">Total Courses</p>
                    <h2 id="total-courses" style="font-size: 2.5rem; color: var(--primary);">--</h2>
                </div>
                <div class="card glass text-center">
                    <p class="text-muted" style="font-size: 0.9rem; margin-bottom: 0.5rem;">Avg. Rating</p>
                    <h2 id="avg-rating" style="font-size: 2.5rem; color: var(--primary);">--</h2>
                </div>
            </div>

            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem;">
                <h2>Your Courses</h2>
                <button class="btn btn-outline" style="padding: 0.5rem 1rem;" id="refresh-dashboard">
                    <i class="fas fa-sync-alt"></i> Refresh
                </button>
            </div>
            
            <div id="instructor-courses" class="grid grid-1" style="gap: 1.25rem;">
                <div class="loader-container"><div class="loader"></div></div>
            </div>

            <!-- Create Course Modal -->
            <div id="create-course-modal" class="modal-overlay" style="display: none;">
                <div class="modal-content glass fade-in">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem;">
                        <h2>Create New Course</h2>
                        <button id="close-modal" class="btn btn-outline" style="padding: 0.5rem; width: 40px; height: 40px; border-radius: 50%;">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                    <form id="create-course-form">
                        <div class="form-group">
                            <label>Course Title</label>
                            <input type="text" id="course-title" required placeholder="e.g. Advanced Python Patterns">
                        </div>
                        <div class="form-group">
                            <label>Course Code</label>
                            <input type="text" id="course-code" required placeholder="e.g. CS302">
                        </div>
                        <div class="form-group">
                            <label>Description</label>
                            <textarea id="course-description" class="glass" style="width: 100%; padding: 0.8rem; border-radius: 8px; border: 1px solid var(--border); background: var(--bg-glass); color: white; resize: vertical;" placeholder="e.g. A deep dive into advanced Python patterns and best practices."></textarea>
                        </div>
                        <div class="grid grid-2">
                            <div class="form-group">
                                <label>Category</label>
                                <input type="text" id="course-category" placeholder="e.g. Programming">
                            </div>
                            <div class="form-group">
                                <label>Difficulty</label>
                                <select id="course-difficulty" class="glass">
                                    <option value="Beginner">Beginner</option>
                                    <option value="Intermediate">Intermediate</option>
                                    <option value="Advanced">Advanced</option>
                                </select>
                            </div>
                        </div>
                        <div class="form-group">
                            <label>Capacity</label>
                            <input type="number" id="course-capacity" value="30" min="1">
                        </div>
                        <button type="submit" id="submit-course-btn" class="btn btn-primary" style="width: 100%; margin-top: 1rem; padding: 1rem;">
                            Create Course
                        </button>
                    </form>
                </div>
            </div>
        </div>
    `;
};

window.Init.instructor = async () => {
    const modal = document.getElementById('create-course-modal');
    const openBtn = document.getElementById('open-create-modal');
    const closeBtn = document.getElementById('close-modal');
    const form = document.getElementById('create-course-form');
    const refreshBtn = document.getElementById('refresh-dashboard');

    if (openBtn) openBtn.onclick = () => modal.style.display = 'flex';
    if (closeBtn) closeBtn.onclick = () => modal.style.display = 'none';
    if (refreshBtn) refreshBtn.onclick = () => window.Init.instructor();
    
    // Use addEventListener instead of window.onclick to avoid clobbering other handlers
    window.addEventListener('click', (event) => { if (event.target == modal) modal.style.display = 'none'; });

    if (form) {
        form.onsubmit = async (e) => {
            e.preventDefault();
            
            const instructorId = localStorage.getItem('user_id');
            if (!instructorId) {
                window.showToast('Session error: Please log out and log back in to refresh your ID.', 'error');
                return;
            }

            const courseData = {
                title: document.getElementById('course-title').value,
                code: document.getElementById('course-code').value,
                description: document.getElementById('course-description').value,
                category: document.getElementById('course-category').value,
                difficulty_level: document.getElementById('course-difficulty').value,
                capacity: parseInt(document.getElementById('course-capacity').value),
                instructor_id: instructorId
            };

            const btn = document.getElementById('submit-course-btn');
            try {
                btn.disabled = true;
                btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Creating...';
                
                await api.createCourse(courseData);
                
                window.showToast('Course created successfully!');
                modal.style.display = 'none';
                form.reset();
                await window.Init.instructor(); // Reload
            } catch (error) {
                window.showToast(error.message, 'error');
            } finally {
                if (btn) {
                    btn.disabled = false;
                    btn.innerHTML = 'Create Course';
                }
            }
        };
    }

    const container = document.getElementById('instructor-courses');
    try {
        const stats = await api.getInstructorDashboard();
        if (!stats) throw new Error('Could not fetch dashboard stats');

        const studentsElem = document.getElementById('total-students');
        const coursesElem = document.getElementById('total-courses');
        const ratingElem = document.getElementById('avg-rating');
        
        if (studentsElem) studentsElem.textContent = stats.total_active_students || 0;
        if (coursesElem) coursesElem.textContent = stats.total_courses || 0;
        
        const breakdown = stats.course_breakdown || [];
        const allRatings = breakdown.map(c => c.average_rating || 0);
        const avg = allRatings.length ? (allRatings.reduce((a, b) => a + b, 0) / allRatings.length).toFixed(1) : 'N/A';
        if (ratingElem) ratingElem.textContent = avg;

        if (container) {
            container.innerHTML = stats.course_breakdown.map(course => `
                <div class="card glass fade-in" style="display: flex; justify-content: space-between; align-items: center; padding: 1.25rem 2rem;">
                    <div>
                        <h3 style="margin: 0; font-size: 1.25rem;">${course.course_title}</h3>
                        <p class="text-muted" style="font-size: 0.9rem; margin-top: 0.25rem;">
                            Code: <span style="color: var(--text-main);">${course.course_code}</span> | 
                            Students: <span style="color: var(--primary); font-weight: 600;">${course.enrollment_count}</span>
                        </p>
                    </div>
                    <div style="display: flex; gap: 0.75rem;">
                        <a href="/instructor/courses/${course.course_id}" class="btn btn-outline" style="padding: 0.5rem 1rem; font-size: 0.85rem;" onclick="route(event)">
                            <i class="fas fa-cog"></i> Manage
                        </a>
                        <button class="btn btn-outline delete-course-btn" data-id="${course.course_id}" style="padding: 0.5rem 1rem; font-size: 0.85rem; color: var(--error); border-color: rgba(239, 68, 68, 0.2);">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
            `).join('');

            // Add delete logic
            document.querySelectorAll('.delete-course-btn').forEach(btn => {
                btn.onclick = async (e) => {
                    const id = btn.getAttribute('data-id');
                    if (confirm('Are you sure you want to delete this course? This action cannot be undone.')) {
                        try {
                            btn.disabled = true;
                            btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
                            await api.deleteCourse(id);
                            window.showToast('Course deleted successfully');
                            await window.Init.instructor();
                        } catch (error) {
                            window.showToast(error.message, 'error');
                            btn.disabled = false;
                            btn.innerHTML = '<i class="fas fa-trash"></i>';
                        }
                    }
                };
            });

            if (stats.course_breakdown.length === 0) {
                container.innerHTML = '<div class="card glass text-center"><p class="text-muted">You have not created any courses yet.</p></div>';
            }
        }
    } catch (error) {
        console.error('Failed to load instructor dashboard', error);
        if (container) {
            container.innerHTML = `<div class="card glass text-center"><p class="text-error">Error: ${error.message}</p></div>`;
        }
    }
};
