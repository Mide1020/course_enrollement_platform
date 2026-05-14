// Profile Page — /profile
// Allows users to view and edit their name and bio.

window.Pages.profile = async () => {
    const name = localStorage.getItem('user_name') || 'User';
    const role = localStorage.getItem('user_role') || 'student';
    return `
        <div class="fade-in" style="max-width: 700px; margin: 0 auto; padding: 1rem;">
            <h1 style="margin-bottom: 0.5rem;">My Profile</h1>
            <p class="text-muted" style="margin-bottom: 3rem;">Manage your account details and bio.</p>

            <div class="card glass" style="margin-bottom: 2rem;">
                <div style="display: flex; align-items: center; gap: 2rem; margin-bottom: 2rem;">
                    <div style="width: 80px; height: 80px; border-radius: 50%; background: linear-gradient(135deg, var(--primary), var(--primary-dark)); display: flex; align-items: center; justify-content: center; font-size: 2rem; font-weight: 700; color: white; flex-shrink: 0;">
                        ${name.charAt(0).toUpperCase()}
                    </div>
                    <div>
                        <h2 style="margin: 0 0 0.25rem 0;" id="profile-display-name">${name}</h2>
                        <span style="font-size: 0.85rem; padding: 3px 12px; background: var(--bg-glass); border: 1px solid var(--border); border-radius: 20px; color: var(--primary); text-transform: capitalize;">
                            <i class="fas fa-${role === 'instructor' ? 'chalkboard-teacher' : role === 'admin' ? 'shield-alt' : 'graduation-cap'}"></i>
                            ${role}
                        </span>
                    </div>
                </div>

                <form id="profile-form">
                    <div class="form-group">
                        <label>Full Name</label>
                        <input type="text" id="profile-name" placeholder="Your full name">
                    </div>
                    <div class="form-group">
                        <label>Bio</label>
                        <textarea id="profile-bio" rows="4" placeholder="Tell us a bit about yourself..."
                            style="width: 100%; padding: 0.85rem 1.25rem; background: rgba(15, 23, 42, 0.5); border: 1px solid var(--border); border-radius: 12px; color: white; font-family: inherit; font-size: 1rem; transition: var(--transition); resize: vertical;"></textarea>
                    </div>
                    <button type="submit" id="save-profile-btn" class="btn btn-primary">
                        <i class="fas fa-save"></i> Save Changes
                    </button>
                </form>
            </div>

            <!-- Enrollments section -->
            <div class="card glass">
                <h3 style="margin-bottom: 1.5rem;"><i class="fas fa-book-open" style="color: var(--primary); margin-right: 0.5rem;"></i>My Transcript</h3>
                <div id="transcript-list">
                    <div class="loader-container" style="padding: 2rem;"><div class="loader"></div></div>
                </div>
            </div>
        </div>
    `;
};

window.Init.profile = async () => {
    const form = document.getElementById('profile-form');
    const transcriptEl = document.getElementById('transcript-list');

    // Load current profile data
    try {
        const profile = await api.getMyProfile();
        const nameInput = document.getElementById('profile-name');
        const bioInput = document.getElementById('profile-bio');
        if (nameInput) nameInput.value = profile.name || '';
        if (bioInput) bioInput.value = profile.bio || '';
    } catch (e) {
        console.error('Failed to load profile', e);
    }

    // Load transcript (completed courses)
    try {
        const enrollments = await api.getMyEnrollments();
        if (enrollments.length === 0) {
            transcriptEl.innerHTML = `<p class="text-muted text-center">No enrollments yet. <a href="/courses" onclick="route(event)" style="color: var(--primary);">Browse courses</a></p>`;
        } else {
            transcriptEl.innerHTML = `
                <table style="width: 100%; border-collapse: collapse; font-size: 0.9rem;">
                    <thead>
                        <tr style="color: var(--text-muted); text-align: left; border-bottom: 1px solid var(--border);">
                            <th style="padding: 0.75rem 0.5rem;">Course</th>
                            <th style="padding: 0.75rem 0.5rem;">Status</th>
                            <th style="padding: 0.75rem 0.5rem;">Grade</th>
                            <th style="padding: 0.75rem 0.5rem;">Enrolled</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${enrollments.map(e => `
                            <tr style="border-bottom: 1px solid var(--border);">
                                <td style="padding: 0.9rem 0.5rem;">
                                    <div style="font-weight: 600;">${e.course.title}</div>
                                    <div style="color: var(--text-muted); font-size: 0.8rem;">${e.course.code}</div>
                                </td>
                                <td style="padding: 0.9rem 0.5rem;">
                                    <span style="padding: 3px 10px; border-radius: 20px; font-size: 0.8rem; font-weight: 600; background: var(--bg-glass);
                                        color: ${e.status === 'completed' ? 'var(--success)' : e.status === 'dropped' ? 'var(--error)' : 'var(--info)'}; text-transform: capitalize;">
                                        ${e.status}
                                    </span>
                                </td>
                                <td style="padding: 0.9rem 0.5rem; color: ${e.grade ? 'var(--warning)' : 'var(--text-dim)'}; font-weight: 600;">
                                    ${e.grade || '—'}
                                </td>
                                <td style="padding: 0.9rem 0.5rem; color: var(--text-muted);">
                                    ${new Date(e.created_at).toLocaleDateString()}
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            `;
        }
    } catch (e) {
        transcriptEl.innerHTML = `<p style="color: var(--error);">Could not load transcript.</p>`;
    }

    // Profile form submit
    if (form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const btn = document.getElementById('save-profile-btn');
            const name = document.getElementById('profile-name').value;
            const bio = document.getElementById('profile-bio').value;

            try {
                btn.disabled = true;
                btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Saving...';
                const updated = await api.updateMyProfile({ name, bio });
                // Update localStorage display name
                localStorage.setItem('user_name', updated.name);
                document.getElementById('profile-display-name').textContent = updated.name;
                window.showToast('Profile updated successfully!', 'success');
                window.router.updateNavbar();
            } catch (error) {
                window.showToast(error.message, 'error');
            } finally {
                btn.disabled = false;
                btn.innerHTML = '<i class="fas fa-save"></i> Save Changes';
            }
        });
    }
};
