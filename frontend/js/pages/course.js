// Course Classroom Page
// Route: /courses/:id
// This is the student's learning interface once they are enrolled.

window.Pages.course = async (courseId) => {
    return `
        <div class="fade-in" style="padding: 1rem;">
            <div id="course-header" style="margin-bottom: 2rem;">
                <a href="/dashboard" onclick="route(event)" class="btn btn-outline" style="padding: 0.5rem 1rem; margin-bottom: 1.5rem; display: inline-flex;">
                    <i class="fas fa-arrow-left" style="margin-right: 0.5rem;"></i> Back to Dashboard
                </a>
                <div class="loader-container"><div class="loader"></div></div>
            </div>

            <div id="classroom-layout" style="display: none; gap: 2rem;" class="classroom-grid">
                <!-- Sidebar: Syllabus -->
                <aside id="course-sidebar" style="display: flex; flex-direction: column; gap: 2rem; align-self: start; position: sticky; top: 100px;">
                    <!-- Sidebar: Syllabus -->
                    <div id="course-syllabus" class="card glass" style="padding: 1.5rem;">
                        <h3 style="margin-bottom: 1.5rem; font-size: 1rem; text-transform: uppercase; letter-spacing: 0.1em; color: var(--text-muted);">
                            <i class="fas fa-list-ul" style="margin-right: 0.5rem;"></i>Course Syllabus
                        </h3>
                        <div id="modules-list">
                            <div class="loader-container" style="padding: 2rem;"><div class="loader"></div></div>
                        </div>
                    </div>

                    <!-- Sidebar: Reviews -->
                    <div id="course-reviews-card" class="card glass" style="padding: 1.5rem;">
                         <h3 style="margin-bottom: 1.5rem; font-size: 1rem; text-transform: uppercase; letter-spacing: 0.1em; color: var(--text-muted);">
                            <i class="fas fa-star" style="margin-right: 0.5rem;"></i>Student Reviews
                        </h3>
                        <div id="reviews-list">
                            <div class="loader-container" style="padding: 1rem;"><div class="loader"></div></div>
                        </div>
                        <button class="btn btn-outline" id="open-review-btn" style="width: 100%; margin-top: 1rem; font-size: 0.85rem;">
                            <i class="fas fa-pen"></i> Leave a Review
                        </button>
                    </div>
                </aside>

                <!-- Main: Lesson Viewer -->
                <main id="lesson-viewer" style="min-height: 400px;">
                    <div class="card glass text-center" style="padding: 4rem;">
                        <i class="fas fa-hand-pointer" style="font-size: 3rem; color: var(--text-dim); margin-bottom: 1.5rem;"></i>
                        <p class="text-muted" style="font-size: 1.1rem;">Select a lesson from the syllabus to start learning.</p>
                    </div>
                </main>
            </div>

            <!-- Review Modal -->
            <div id="review-modal" class="modal-overlay" style="display: none;">
                <div class="modal-content glass">
                    <h2 style="margin-bottom: 1rem;">Course Review</h2>
                    <p class="text-muted" style="margin-bottom: 1.5rem;">Share your experience with other students.</p>
                    <form id="review-form">
                        <div class="form-group">
                            <label>Rating</label>
                            <div class="rating-input" style="display: flex; gap: 0.5rem; margin-top: 0.5rem;">
                                ${[1, 2, 3, 4, 5].map(i => `
                                    <input type="radio" name="rating" value="${i}" id="star${i}" style="display:none;" ${i === 5 ? 'checked' : ''}>
                                    <label for="star${i}" class="star" style="cursor:pointer; font-size: 1.5rem; color: #cbd5e1;"><i class="fas fa-star"></i></label>
                                `).join('')}
                            </div>
                        </div>
                        <div class="form-group">
                            <label>Your Comment</label>
                            <textarea id="review-comment" class="glass" rows="4" required placeholder="What did you think of the course?"></textarea>
                        </div>
                        <button type="submit" id="submit-review-btn" class="btn btn-primary" style="width: 100%;">Submit Review</button>
                    </form>
                </div>
            </div>
        </div>
    `;
};

window.Init.course = async (courseId) => {
    const headerEl = document.getElementById('course-header');
    const layoutEl = document.getElementById('classroom-layout');
    const modulesList = document.getElementById('modules-list');

    try {
        // Load course details and content in parallel
        const [course, modules] = await Promise.all([
            api.getCourse(courseId),
            api.getCourseModules(courseId)
        ]);

        // Render course header
        headerEl.innerHTML = `
            <a href="/dashboard" onclick="route(event)" class="btn btn-outline" style="padding: 0.5rem 1rem; margin-bottom: 1.5rem; display: inline-flex;">
                <i class="fas fa-arrow-left" style="margin-right: 0.5rem;"></i> Back to Dashboard
            </a>
            <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 1rem;">
                <div>
                    <h1 style="margin-bottom: 0.5rem;">${course.title}</h1>
                    <p class="text-muted">
                        <span style="color: var(--primary); font-weight: 600;">${course.code}</span>
                        &nbsp;·&nbsp; ${course.category || 'General'}
                        &nbsp;·&nbsp; <i class="fas fa-signal"></i> ${course.difficulty_level || 'Beginner'}
                    </p>
                    ${course.description ? `<p class="text-muted" style="margin-top: 0.75rem; max-width: 700px;">${course.description}</p>` : ''}
                </div>
                <div style="text-align: right;">
                    <span class="text-muted" style="font-size: 0.9rem;">
                        <i class="fas fa-book-open" style="color: var(--primary);"></i> 
                        ${modules.length} Module${modules.length !== 1 ? 's' : ''}
                        &nbsp;·&nbsp;
                        <i class="fas fa-play-circle" style="color: var(--primary);"></i>
                        ${modules.reduce((sum, m) => sum + (m.lessons ? m.lessons.length : 0), 0)} Lessons
                    </span>
                </div>
            </div>
            <hr style="border-color: var(--border); margin-top: 1.5rem;">
        `;

        // Render syllabus
        if (modules.length === 0) {
            modulesList.innerHTML = `
                <div class="text-center" style="padding: 2rem;">
                    <i class="fas fa-hard-hat" style="font-size: 2rem; color: var(--text-dim); margin-bottom: 1rem;"></i>
                    <p class="text-muted">Content is being prepared by the instructor.</p>
                </div>
            `;
        } else {
            modulesList.innerHTML = modules.map((module, mIdx) => `
                <div style="margin-bottom: 1.5rem;">
                    <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.75rem; padding-bottom: 0.5rem; border-bottom: 1px solid var(--border);">
                        <span style="width: 28px; height: 28px; background: var(--primary); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.75rem; font-weight: 700; flex-shrink: 0;">
                            ${mIdx + 1}
                        </span>
                        <h4 style="margin: 0; font-size: 0.95rem;">${module.title}</h4>
                    </div>
                    <ul style="list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 0.35rem;">
                        ${module.lessons && module.lessons.length > 0
                            ? module.lessons.map((lesson, lIdx) => `
                                <li>
                                    <button class="lesson-btn" data-lesson-id="${lesson.id}" data-lesson-title="${lesson.title}" data-content-type="${lesson.content_type}" data-content="${encodeURIComponent(lesson.content_data || '')}"
                                        style="width: 100%; text-align: left; background: none; border: none; cursor: pointer; padding: 0.6rem 0.5rem; border-radius: 8px; color: var(--text-muted); display: flex; align-items: center; gap: 0.6rem; transition: all 0.2s; font-size: 0.9rem;">
                                        <i class="fas fa-${lesson.content_type === 'video' ? 'play-circle' : lesson.content_type === 'file' ? 'file-download' : 'file-alt'}" style="color: var(--primary); width: 16px; flex-shrink: 0;"></i>
                                        <span>${lIdx + 1}. ${lesson.title}</span>
                                    </button>
                                </li>
                            `).join('')
                            : '<li style="padding: 0.5rem; color: var(--text-dim); font-size: 0.85rem;">No lessons yet.</li>'
                        }
                    </ul>
                </div>
            `).join('');
        }

        // Show the layout
        layoutEl.style.display = 'grid';

        // Lesson button interaction
        document.querySelectorAll('.lesson-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                // Highlight active lesson
                document.querySelectorAll('.lesson-btn').forEach(b => {
                    b.style.background = 'none';
                    b.style.color = 'var(--text-muted)';
                });
                btn.style.background = 'var(--bg-glass)';
                btn.style.color = 'var(--text-main)';

                // Render lesson content
                const title = btn.getAttribute('data-lesson-title');
                const type = btn.getAttribute('data-content-type');
                const content = decodeURIComponent(btn.getAttribute('data-content'));
                renderLesson(title, type, content);
            });
        });
        
        // Load Reviews
        loadReviews(courseId);

        // Review interaction
        const reviewModal = document.getElementById('review-modal');
        const openReviewBtn = document.getElementById('open-review-btn');
        if (openReviewBtn) openReviewBtn.onclick = () => reviewModal.style.display = 'flex';
        
        // Star selection logic
        document.querySelectorAll('.rating-input label').forEach(label => {
            label.onclick = () => {
                const rating = document.getElementById(label.getAttribute('for')).value;
                document.querySelectorAll('.rating-input label').forEach((l, i) => {
                    l.style.color = (i < rating) ? 'var(--warning)' : '#cbd5e1';
                });
            };
        });
        // Initial star color
        document.querySelectorAll('.rating-input label').forEach((l, i) => {
            if (i < 5) l.style.color = 'var(--warning)';
        });

        document.getElementById('review-form').onsubmit = async (e) => {
            e.preventDefault();
            const rating = document.querySelector('input[name="rating"]:checked').value;
            const comment = document.getElementById('review-comment').value;
            const btn = document.getElementById('submit-review-btn');
            
            try {
                btn.disabled = true;
                await api.createReview({ course_id: courseId, rating: parseInt(rating), comment });
                window.showToast('Review submitted!');
                reviewModal.style.display = 'none';
                loadReviews(courseId);
            } catch (err) {
                window.showToast(err.message, 'error');
                btn.disabled = false;
            }
        };

        window.addEventListener('click', (event) => {
            if (event.target == reviewModal) reviewModal.style.display = 'none';
        });

    } catch (error) {
        if (error.message.includes('enrolled')) {
            headerEl.innerHTML = `
                <div class="card glass text-center" style="padding: 4rem;">
                    <i class="fas fa-lock" style="font-size: 3rem; color: var(--error); margin-bottom: 1.5rem;"></i>
                    <h2 style="margin-bottom: 1rem;">Access Denied</h2>
                    <p class="text-muted" style="margin-bottom: 2rem;">You must be enrolled in this course to view its content.</p>
                    <a href="/courses" onclick="route(event)" class="btn btn-primary">Browse Courses</a>
                </div>
            `;
            layoutEl.style.display = 'none';
        } else {
            headerEl.innerHTML = `<p style="color: var(--error);">Error loading course: ${error.message}</p>`;
        }
    }
};

function renderLesson(title, type, content) {
    const viewer = document.getElementById('lesson-viewer');
    let contentHtml = '';

    if (type === 'video') {
        // Try to embed as an iframe (YouTube, Vimeo) or a raw video tag
        const isYoutube = content.includes('youtube.com') || content.includes('youtu.be');
        if (isYoutube) {
            const videoId = content.split('v=')[1]?.split('&')[0] || content.split('/').pop();
            contentHtml = `
                <div style="position: relative; padding-top: 56.25%; border-radius: 12px; overflow: hidden; background: #000; margin-bottom: 1.5rem;">
                    <iframe src="https://www.youtube.com/embed/${videoId}" frameborder="0" allowfullscreen
                        style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;"></iframe>
                </div>`;
        } else {
            contentHtml = `
                <div style="margin-bottom: 1.5rem;">
                    <video controls style="width: 100%; border-radius: 12px; background: #000;">
                        <source src="${content}">
                        Your browser does not support the video tag.
                    </video>
                </div>`;
        }
    } else if (type === 'file') {
        contentHtml = `
            <div class="card glass text-center" style="padding: 3rem; margin-bottom: 1.5rem;">
                <i class="fas fa-file-download" style="font-size: 3rem; color: var(--primary); margin-bottom: 1rem;"></i>
                <p class="text-muted" style="margin-bottom: 1.5rem;">This lesson includes a downloadable resource.</p>
                <a href="${content}" target="_blank" class="btn btn-primary">
                    <i class="fas fa-download"></i> Download File
                </a>
            </div>`;
    } else {
        // Text / markdown content
        contentHtml = `
            <div class="card glass" style="padding: 2rem; margin-bottom: 1.5rem; line-height: 1.8; color: var(--text-main);">
                ${content ? content.replace(/\n/g, '<br>') : '<p class="text-muted">No content available for this lesson yet.</p>'}
            </div>`;
    }

    viewer.innerHTML = `
        <div class="fade-in">
            <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1.5rem;">
                <div style="width: 44px; height: 44px; background: var(--primary); border-radius: 12px; display: flex; align-items: center; justify-content: center;">
                    <i class="fas fa-${type === 'video' ? 'play' : type === 'file' ? 'file' : 'font'}" style="color: white;"></i>
                </div>
                <h2 style="margin: 0; font-size: 1.4rem;">${title}</h2>
            </div>
            ${contentHtml}
        </div>
    `;
}

async function loadReviews(courseId) {
    const list = document.getElementById('reviews-list');
    if (!list) return;
    
    try {
        const reviews = await api.getCourseReviews(courseId);
        if (reviews.length === 0) {
            list.innerHTML = '<p class="text-muted" style="font-size: 0.85rem;">No reviews yet.</p>';
            return;
        }
        
        list.innerHTML = reviews.slice(0, 5).map(r => `
            <div style="margin-bottom: 1rem; padding-bottom: 1rem; border-bottom: 1px solid var(--border);">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.25rem;">
                    <span style="font-weight: 600; font-size: 0.85rem;">${r.user.name}</span>
                    <span style="color: var(--warning); font-size: 0.75rem;">
                        ${Array(r.rating).fill('<i class="fas fa-star"></i>').join('')}
                    </span>
                </div>
                <p style="font-size: 0.85rem; color: var(--text-muted); line-height: 1.4; margin: 0;">${r.comment}</p>
            </div>
        `).join('');
    } catch (e) {
        list.innerHTML = '<p class="text-error">Error loading reviews</p>';
    }
}
