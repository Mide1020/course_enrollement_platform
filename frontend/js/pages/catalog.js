window.Pages.catalog = async () => {
    return `
        <div class="header-with-actions fade-in" style="margin-bottom: 3rem;">
            <div>
                <h1>Course Catalog</h1>
                <p class="text-muted">Explore our diverse range of learning materials.</p>
            </div>
            <div class="filters-row glass" style="padding: 1rem; margin-top: 2rem; display: flex; gap: 1rem; align-items: center; flex-wrap: wrap;">
                <select id="filter-difficulty" class="glass" style="flex: 1; min-width: 150px;">
                    <option value="">All Difficulties</option>
                    <option value="Beginner">Beginner</option>
                    <option value="Intermediate">Intermediate</option>
                    <option value="Advanced">Advanced</option>
                </select>
                <input type="text" id="search-input" placeholder="Search courses..." class="glass" style="flex: 2; min-width: 200px;">
                <button class="btn btn-primary" id="apply-filters-btn">Apply</button>
            </div>
        </div>

        <div id="course-list" class="grid grid-3">
            <div class="loader-container"><div class="loader"></div></div>
        </div>
    `;
};

window.Init.catalog = async () => {
    const listContainer = document.getElementById('course-list');
    const filterBtn = document.getElementById('apply-filters-btn');
    
    const renderCourses = async (params = {}) => {
        if (!listContainer) return;
        listContainer.innerHTML = '<div class="loader-container"><div class="loader"></div></div>';
        try {
            const courses = await api.getCourses(params);
            if (courses.length === 0) {
                listContainer.innerHTML = '<div class="card glass text-center" style="grid-column: 1/-1;"><p class="text-muted">No courses found matching your criteria.</p></div>';
                return;
            }

            listContainer.innerHTML = courses.map(course => {
                const isFull = course.enrollment_count >= course.capacity;
                const spotsLeft = course.capacity - course.enrollment_count;
                return `
                <div class="card glass fade-in">
                    <div style="height: 140px; background: linear-gradient(135deg, #1e293b, #334155); border-radius: 12px; margin-bottom: 1.5rem; display: flex; align-items: center; justify-content: center;">
                        <i class="fas fa-book" style="font-size: 3rem; color: rgba(255,255,255,0.1);"></i>
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.75rem;">
                        <span style="font-size: 0.8rem; padding: 4px 12px; background: var(--bg-glass); border-radius: 6px; color: var(--primary); font-weight: 500;">
                            ${course.category || 'General'}
                        </span>
                        <span style="color: var(--text-muted); font-size: 0.85rem;">
                            <i class="fas fa-signal"></i> ${course.difficulty_level || 'Beginner'}
                        </span>
                    </div>
                    <h3 style="margin-bottom: 0.5rem;">${course.title}</h3>
                    <p class="text-muted" style="font-size: 0.85rem; margin-bottom: 0.5rem;">Code: ${course.code}</p>
                    ${course.description ? `<p class="text-muted" style="font-size: 0.9rem; margin-bottom: 1rem; line-height: 1.5;">${course.description}</p>` : ''}
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-top: auto; padding-top: 1rem; border-top: 1px solid var(--border);">
                        <span style="font-size: 0.85rem; color: ${isFull ? 'var(--error)' : 'var(--text-muted)'};">
                            <i class="fas fa-users"></i>
                            ${isFull ? 'Full' : `${spotsLeft} spot${spotsLeft !== 1 ? 's' : ''} left`}
                        </span>
                        ${isFull
                            ? `<button class="btn btn-outline waitlist-btn" data-id="${course.id}" style="padding: 0.6rem 1.25rem; border-color: var(--warning); color: var(--warning);">
                                <i class="fas fa-clock"></i> Join Waitlist
                               </button>`
                            : `<button class="btn btn-outline enroll-btn" data-id="${course.id}" style="padding: 0.6rem 1.25rem;">Enroll</button>`
                        }
                    </div>
                </div>
            `}).join('');

            // Enroll buttons
            document.querySelectorAll('.enroll-btn').forEach(btn => {
                btn.addEventListener('click', async (e) => {
                    const id = e.currentTarget.getAttribute('data-id');
                    if (!localStorage.getItem('access_token')) {
                        window.showToast('Please log in to enroll in a course.', 'error');
                        window.router.navigate('/login');
                        return;
                    }
                    await window.handleEnroll(id, e.currentTarget);
                });
            });

            // Waitlist buttons
            document.querySelectorAll('.waitlist-btn').forEach(btn => {
                btn.addEventListener('click', async (e) => {
                    const id = e.currentTarget.getAttribute('data-id');
                    if (!localStorage.getItem('access_token')) {
                        window.showToast('Please log in to join the waitlist.', 'error');
                        window.router.navigate('/login');
                        return;
                    }
                    await window.handleWaitlist(id, e.currentTarget);
                });
            });

        } catch (error) {
            listContainer.innerHTML = `<p class="text-error">Error loading courses: ${error.message}</p>`;
        }
    };

    if (filterBtn) {
        filterBtn.addEventListener('click', () => {
            const difficulty = document.getElementById('filter-difficulty').value;
            const search = document.getElementById('search-input').value;
            renderCourses({ difficulty, search });
        });
    }

    await renderCourses();
};

window.handleEnroll = async (id, btn) => {
    const originalText = btn.innerHTML;
    try {
        btn.disabled = true;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
        await api.enroll(id);
        window.showToast('Enrolled successfully!', 'success');
        window.router.navigate('/dashboard');
    } catch (error) {
        window.showToast(error.message, 'error');
        btn.disabled = false;
        btn.innerHTML = originalText;
    }
};

window.handleWaitlist = async (id, btn) => {
    const originalText = btn.innerHTML;
    try {
        btn.disabled = true;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
        await api.joinWaitlist(id);
        window.showToast("You've joined the waitlist! We'll notify you when a spot opens.", 'success');
        btn.innerHTML = '<i class="fas fa-check"></i> On Waitlist';
    } catch (error) {
        window.showToast(error.message, 'error');
        btn.disabled = false;
        btn.innerHTML = originalText;
    }
};


window.Init.catalog = async () => {
    const listContainer = document.getElementById('course-list');
    const filterBtn = document.getElementById('apply-filters-btn');
    
    const renderCourses = async (params = {}) => {
        if (!listContainer) return;
        listContainer.innerHTML = '<div class="loader-container"><div class="loader"></div></div>';
        try {
            const courses = await api.getCourses(params);
            listContainer.innerHTML = courses.map(course => `
                <div class="card glass fade-in">
                    <div style="height: 140px; background: linear-gradient(135deg, #1e293b, #334155); border-radius: 12px; margin-bottom: 1.5rem; display: flex; align-items: center; justify-content: center;">
                        <i class="fas fa-book" style="font-size: 3rem; color: rgba(255,255,255,0.1);"></i>
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.75rem;">
                        <span style="font-size: 0.8rem; padding: 4px 12px; background: var(--bg-glass); border-radius: 6px; color: var(--primary); font-weight: 500;">
                            ${course.category || 'General'}
                        </span>
                        <span style="color: var(--text-muted); font-size: 0.85rem;">
                            <i class="fas fa-signal"></i> ${course.difficulty_level || 'Beginner'}
                        </span>
                    </div>
                    <h3 style="margin-bottom: 0.75rem;">${course.title}</h3>
                    <p class="text-muted" style="font-size: 0.95rem; margin-bottom: 2rem;">Code: ${course.code}</p>
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span class="text-muted"><i class="fas fa-users"></i> ${course.enrollment_count || 0}</span>
                        <button class="btn btn-outline enroll-btn" data-id="${course.id}" style="padding: 0.6rem 1.25rem;">Enroll</button>
                    </div>
                </div>
            `).join('');

            // Attach event listeners to buttons
            document.querySelectorAll('.enroll-btn').forEach(btn => {
                btn.addEventListener('click', async (e) => {
                    const id = e.currentTarget.getAttribute('data-id');
                    await window.handleEnroll(id);
                });
            });

            if (courses.length === 0) {
                listContainer.innerHTML = '<div class="card glass text-center" style="grid-column: 1/-1;"><p class="text-muted">No courses found matching your criteria.</p></div>';
            }
        } catch (error) {
            listContainer.innerHTML = `<p class="text-error">Error loading courses: ${error.message}</p>`;
        }
    };

    if (filterBtn) {
        filterBtn.addEventListener('click', () => {
            const difficulty = document.getElementById('filter-difficulty').value;
            const search = document.getElementById('search-input').value;
            renderCourses({ difficulty, search });
        });
    }

    await renderCourses();
};

window.handleEnroll = async (id) => {
    try {
        await api.enroll(id);
        window.showToast('Enrolled successfully!');
        window.router.navigate('/dashboard');
    } catch (error) {
        window.showToast(error.message, 'error');
    }
};
