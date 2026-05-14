// Course Management Page for Instructors
// Route: /instructor/courses/:id

window.Pages.manage = async (courseId) => {
    return `
        <div class="fade-in" style="padding: 1rem;">
            <div id="manage-header" style="margin-bottom: 3rem;">
                <a href="/instructor" onclick="route(event)" class="btn btn-outline" style="padding: 0.5rem 1rem; margin-bottom: 1.5rem; display: inline-flex;">
                    <i class="fas fa-arrow-left" style="margin-right: 0.5rem;"></i> Back to Dashboard
                </a>
                <div class="loader-container"><div class="loader"></div></div>
            </div>

            <div class="tab-container" style="margin-bottom: 2rem;">
                <button class="tab-btn active" data-tab="content">Curriculum</button>
                <button class="tab-btn" data-tab="students">Students & Grading</button>
                <button class="tab-btn" data-tab="settings">Course Settings</button>
            </div>

            <div id="tab-content" class="tab-pane active">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem;">
                    <h2>Course Curriculum</h2>
                    <button class="btn btn-primary" id="add-module-btn"><i class="fas fa-plus"></i> Add Module</button>
                </div>
                <div id="modules-management-list">
                    <div class="loader-container"><div class="loader"></div></div>
                </div>
            </div>

            <div id="tab-students" class="tab-pane">
                <h2>Enrolled Students</h2>
                <div id="students-list" style="margin-top: 1.5rem;">
                    <div class="loader-container"><div class="loader"></div></div>
                </div>
            </div>

            <div id="tab-settings" class="tab-pane">
                <h2>Course Settings</h2>
                <div class="card glass" style="margin-top: 1.5rem; max-width: 600px;">
                    <form id="edit-course-form">
                        <div class="form-group">
                            <label>Course Title</label>
                            <input type="text" id="edit-course-title" required>
                        </div>
                        <div class="form-group">
                            <label>Description</label>
                            <textarea id="edit-course-description" class="glass" rows="4"></textarea>
                        </div>
                        <div class="grid grid-2">
                             <div class="form-group">
                                <label>Category</label>
                                <input type="text" id="edit-course-category">
                            </div>
                            <div class="form-group">
                                <label>Capacity</label>
                                <input type="number" id="edit-course-capacity">
                            </div>
                        </div>
                        <button type="submit" class="btn btn-primary" style="margin-top: 1rem;">Update Course</button>
                    </form>
                </div>
            </div>

            <!-- Modals -->
            <div id="module-modal" class="modal-overlay" style="display: none;">
                <div class="modal-content glass">
                    <h2 id="module-modal-title">Add Module</h2>
                    <form id="module-form" style="margin-top: 1.5rem;">
                        <input type="hidden" id="module-id">
                        <div class="form-group">
                            <label>Module Title</label>
                            <input type="text" id="module-title" required>
                        </div>
                        <button type="submit" class="btn btn-primary" style="width: 100%;">Save Module</button>
                    </form>
                </div>
            </div>

            <div id="lesson-modal" class="modal-overlay" style="display: none;">
                <div class="modal-content glass">
                    <h2 id="lesson-modal-title">Add Lesson</h2>
                    <form id="lesson-form" style="margin-top: 1.5rem;">
                        <input type="hidden" id="lesson-id">
                        <input type="hidden" id="lesson-module-id">
                        <div class="form-group">
                            <label>Lesson Title</label>
                            <input type="text" id="lesson-title" required>
                        </div>
                        <div class="form-group">
                            <label>Content Type</label>
                            <select id="lesson-type" class="glass">
                                <option value="text">Text / Markdown</option>
                                <option value="video">Video URL</option>
                                <option value="file">File / Download URL</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Content Data (URL or Text)</label>
                            <textarea id="lesson-content" class="glass" rows="5" required></textarea>
                        </div>
                        <button type="submit" class="btn btn-primary" style="width: 100%;">Save Lesson</button>
                    </form>
                </div>
            </div>
        </div>
    `;
};

window.Init.manage = async (courseId) => {
    const header = document.getElementById('manage-header');
    const moduleList = document.getElementById('modules-management-list');
    const studentList = document.getElementById('students-list');
    
    // Tab switching logic
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.onclick = () => {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
            btn.classList.add('active');
            document.getElementById(`tab-${btn.dataset.tab}`).classList.add('active');
        };
    });

    const loadData = async () => {
        try {
            const course = await api.getCourse(courseId);
            header.innerHTML = `
                <a href="/instructor" onclick="route(event)" class="btn btn-outline" style="padding: 0.5rem 1rem; margin-bottom: 1.5rem; display: inline-flex;">
                    <i class="fas fa-arrow-left" style="margin-right: 0.5rem;"></i> Back to Dashboard
                </a>
                <h1>Manage: ${course.title}</h1>
                <p class="text-muted">Code: ${course.code} | ID: ${course.id}</p>
            `;

            // Pre-fill settings form
            document.getElementById('edit-course-title').value = course.title;
            document.getElementById('edit-course-description').value = course.description || '';
            document.getElementById('edit-course-category').value = course.category || '';
            document.getElementById('edit-course-capacity').value = course.capacity;

            // Load Modules
            const modules = await api.getCourseModules(courseId);
            renderModules(modules);

            // Load Students
            const allEnrollments = await api.getCourseEnrollments(courseId);
            renderStudents(allEnrollments);

        } catch (e) {
            header.innerHTML = `<p class="text-error">Error: ${e.message}</p>`;
        }
    };

    function renderModules(modules) {
        if (modules.length === 0) {
            moduleList.innerHTML = '<div class="card glass text-center"><p class="text-muted">No modules yet. Add one to get started.</p></div>';
            return;
        }

        moduleList.innerHTML = modules.map(m => `
            <div class="card glass" style="margin-bottom: 1.5rem; padding: 1.5rem;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; border-bottom: 1px solid var(--border); padding-bottom: 1rem;">
                    <h3 style="margin: 0;">${m.title}</h3>
                    <div style="display: flex; gap: 0.5rem;">
                        <button class="btn btn-outline edit-module-btn" data-id="${m.id}" data-title="${m.title}" style="padding: 0.4rem 0.8rem; font-size: 0.8rem;"><i class="fas fa-edit"></i></button>
                        <button class="btn btn-outline delete-module-btn" data-id="${m.id}" style="padding: 0.4rem 0.8rem; font-size: 0.8rem; color: var(--error);"><i class="fas fa-trash"></i></button>
                        <button class="btn btn-primary add-lesson-btn" data-module-id="${m.id}" style="padding: 0.4rem 0.8rem; font-size: 0.8rem;"><i class="fas fa-plus"></i> Add Lesson</button>
                    </div>
                </div>
                <div style="display: flex; flex-direction: column; gap: 0.5rem;">
                    ${m.lessons && m.lessons.length > 0 ? m.lessons.map(l => `
                        <div style="display: flex; justify-content: space-between; align-items: center; background: var(--bg-glass); padding: 0.75rem 1rem; border-radius: 8px;">
                            <div style="display: flex; align-items: center; gap: 0.75rem;">
                                <i class="fas fa-${l.content_type === 'video' ? 'play-circle' : l.content_type === 'file' ? 'file-download' : 'file-alt'}" style="color: var(--primary);"></i>
                                <span>${l.title}</span>
                            </div>
                            <div style="display: flex; gap: 0.4rem;">
                                <button class="btn btn-outline edit-lesson-btn" data-id="${l.id}" data-module-id="${m.id}" data-title="${l.title}" data-type="${l.content_type}" data-content="${encodeURIComponent(l.content_data)}" style="padding: 0.25rem 0.5rem; font-size: 0.75rem;"><i class="fas fa-edit"></i></button>
                                <button class="btn btn-outline delete-lesson-btn" data-id="${l.id}" style="padding: 0.25rem 0.5rem; font-size: 0.75rem; color: var(--error);"><i class="fas fa-trash"></i></button>
                            </div>
                        </div>
                    `).join('') : '<p class="text-muted" style="font-size: 0.9rem;">No lessons in this module.</p>'}
                </div>
            </div>
        `).join('');

        attachModuleListeners();
    }

    function renderStudents(enrollments) {
        if (!enrollments || enrollments.length === 0) {
            studentList.innerHTML = '<div class="card glass text-center"><p class="text-muted">No students enrolled yet.</p></div>';
            return;
        }

        studentList.innerHTML = `
            <table style="width: 100%; border-collapse: collapse;">
                <thead>
                    <tr style="text-align: left; border-bottom: 1px solid var(--border);">
                        <th style="padding: 1rem;">Student Name</th>
                        <th style="padding: 1rem;">Status</th>
                        <th style="padding: 1rem;">Current Grade</th>
                        <th style="padding: 1rem;">Actions</th>
                    </tr>
                </thead>
                <tbody>
                    ${enrollments.map(e => `
                        <tr style="border-bottom: 1px solid var(--border);">
                            <td style="padding: 1rem;">${e.user.name}<br><small class="text-muted">${e.user.email}</small></td>
                            <td style="padding: 1rem;"><span style="text-transform: capitalize;">${e.status}</span></td>
                            <td style="padding: 1rem;"><strong>${e.grade || 'Not Graded'}</strong></td>
                            <td style="padding: 1rem;">
                                <button class="btn btn-outline grade-btn" data-id="${e.id}" data-name="${e.user.name}" data-grade="${e.grade || ''}" style="padding: 0.4rem 0.8rem; font-size: 0.8rem;">
                                    <i class="fas fa-graduation-cap"></i> Grade
                                </button>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;

        attachStudentListeners();
    }

    // Modal logic and event attachments
    const moduleModal = document.getElementById('module-modal');
    const lessonModal = document.getElementById('lesson-modal');

    document.getElementById('add-module-btn').onclick = () => {
        document.getElementById('module-modal-title').innerText = 'Add Module';
        document.getElementById('module-id').value = '';
        document.getElementById('module-title').value = '';
        moduleModal.style.display = 'flex';
    };

    document.getElementById('module-form').onsubmit = async (e) => {
        e.preventDefault();
        const id = document.getElementById('module-id').value;
        const title = document.getElementById('module-title').value;
        try {
            if (id) {
                await api.updateModule(id, { title });
            } else {
                await api.createModule({ course_id: courseId, title, order: 0 });
            }
            window.showToast('Module saved');
            moduleModal.style.display = 'none';
            loadData();
        } catch (err) { window.showToast(err.message, 'error'); }
    };

    document.getElementById('lesson-form').onsubmit = async (e) => {
        e.preventDefault();
        const id = document.getElementById('lesson-id').value;
        const moduleId = document.getElementById('lesson-module-id').value;
        const data = {
            module_id: moduleId,
            title: document.getElementById('lesson-title').value,
            content_type: document.getElementById('lesson-type').value,
            content_data: document.getElementById('lesson-content').value,
            order: 0
        };
        try {
            if (id) {
                await api.updateLesson(id, data);
            } else {
                await api.createLesson(data);
            }
            window.showToast('Lesson saved');
            lessonModal.style.display = 'none';
            loadData();
        } catch (err) { window.showToast(err.message, 'error'); }
    };

    function attachModuleListeners() {
        document.querySelectorAll('.edit-module-btn').forEach(btn => {
            btn.onclick = () => {
                document.getElementById('module-modal-title').innerText = 'Edit Module';
                document.getElementById('module-id').value = btn.dataset.id;
                document.getElementById('module-title').value = btn.dataset.title;
                moduleModal.style.display = 'flex';
            };
        });

        document.querySelectorAll('.delete-module-btn').forEach(btn => {
            btn.onclick = async () => {
                if (confirm('Delete this module?')) {
                    await api.deleteModule(btn.dataset.id);
                    loadData();
                }
            };
        });

        document.querySelectorAll('.add-lesson-btn').forEach(btn => {
            btn.onclick = () => {
                document.getElementById('lesson-modal-title').innerText = 'Add Lesson';
                document.getElementById('lesson-id').value = '';
                document.getElementById('lesson-module-id').value = btn.dataset.moduleId;
                document.getElementById('lesson-title').value = '';
                document.getElementById('lesson-type').value = 'text';
                document.getElementById('lesson-content').value = '';
                lessonModal.style.display = 'flex';
            };
        });

        document.querySelectorAll('.edit-lesson-btn').forEach(btn => {
            btn.onclick = () => {
                document.getElementById('lesson-modal-title').innerText = 'Edit Lesson';
                document.getElementById('lesson-id').value = btn.dataset.id;
                document.getElementById('lesson-module-id').value = btn.dataset.moduleId;
                document.getElementById('lesson-title').value = btn.dataset.title;
                document.getElementById('lesson-type').value = btn.dataset.type;
                document.getElementById('lesson-content').value = decodeURIComponent(btn.dataset.content);
                lessonModal.style.display = 'flex';
            };
        });

        document.querySelectorAll('.delete-lesson-btn').forEach(btn => {
            btn.onclick = async () => {
                if (confirm('Delete this lesson?')) {
                    await api.deleteLesson(btn.dataset.id);
                    loadData();
                }
            };
        });
    }

    function attachStudentListeners() {
        document.querySelectorAll('.grade-btn').forEach(btn => {
            btn.onclick = async () => {
                const grade = prompt(`Enter grade for ${btn.dataset.name}:`, btn.dataset.grade);
                if (grade !== null) {
                    try {
                        await api.gradeStudent(btn.dataset.id, { grade, status: 'completed' });
                        window.showToast('Grade updated');
                        loadData();
                    } catch (err) { window.showToast(err.message, 'error'); }
                }
            };
        });
    }

    // Settings form
    document.getElementById('edit-course-form').onsubmit = async (e) => {
        e.preventDefault();
        const data = {
            title: document.getElementById('edit-course-title').value,
            description: document.getElementById('edit-course-description').value,
            category: document.getElementById('edit-course-category').value,
            capacity: parseInt(document.getElementById('edit-course-capacity').value)
        };
        try {
            await api.updateCourse(courseId, data);
            window.showToast('Course settings updated');
            loadData();
            const curriculumTab = document.querySelector('.tab-btn[data-tab="content"]');
            if (curriculumTab) curriculumTab.click();
        } catch (err) { window.showToast(err.message, 'error'); }
    };

    window.onclick = (event) => {
        if (event.target == moduleModal) moduleModal.style.display = 'none';
        if (event.target == lessonModal) lessonModal.style.display = 'none';
    };

    loadData();
};
