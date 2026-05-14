const API_BASE_URL = '/api/v1';

class API {
    constructor() {
        this.token = localStorage.getItem('access_token');
    }

    setToken(token, role, name, id) {
        this.token = token;
        localStorage.setItem('access_token', token);
        if (role) localStorage.setItem('user_role', role);
        if (name) localStorage.setItem('user_name', name);
        if (id) localStorage.setItem('user_id', id);
    }

    logout() {
        this.token = null;
        localStorage.removeItem('access_token');
        localStorage.removeItem('user_role');
        localStorage.removeItem('user_name');
        localStorage.removeItem('user_id');
        window.location.href = '/login';
    }

    async request(endpoint, options = {}) {
        const url = `${API_BASE_URL}${endpoint}`;
        
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers,
        };

        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }

        const config = {
            ...options,
            headers,
        };

        try {
            const response = await fetch(url, config);
            
            if (response.status === 401) {
                this.logout();
                return null;
            }

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                let detail = errorData.detail;
                if (typeof detail === 'string' && detail.startsWith('[')) {
                    try { detail = JSON.parse(detail); } catch(e) {}
                }
                let errorMsg = detail || 'API request failed';
                if (Array.isArray(detail)) {
                    errorMsg = detail.map(err => {
                        const field = err.loc ? String(err.loc[err.loc.length - 1]).toLowerCase() : 'field';
                        let msg = err.msg || '';
                        if (msg.startsWith('String ')) msg = msg.substring(7);
                        if (msg.startsWith('Value error, ')) msg = msg.substring(13);
                        return `${field} ${msg.charAt(0).toLowerCase() + msg.slice(1)}`;
                    }).join('<br>');
                } else if (typeof errorMsg !== 'string') {
                    errorMsg = JSON.stringify(errorMsg);
                }
                throw new Error(errorMsg);
            }

            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    // Auth
    async login(email, password) {
        const formData = new FormData();
        formData.append('username', email);
        formData.append('password', password);

        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            const errorData = await response.json();
            let detail = errorData.detail;
            if (typeof detail === 'string' && detail.startsWith('[')) {
                try { detail = JSON.parse(detail); } catch(e) {}
            }
            let errorMsg = 'Login failed';
            if (detail) {
                if (Array.isArray(detail)) {
                    errorMsg = detail.map(err => {
                        const field = err.loc ? String(err.loc[err.loc.length - 1]).toLowerCase() : 'field';
                        let msg = err.msg || '';
                        if (msg.startsWith('String ')) msg = msg.substring(7);
                        if (msg.startsWith('Value error, ')) msg = msg.substring(13);
                        return `${field} ${msg.charAt(0).toLowerCase() + msg.slice(1)}`;
                    }).join('<br>');
                } else {
                    errorMsg = typeof detail === 'string' ? detail : JSON.stringify(detail);
                }
            }
            throw new Error(errorMsg);
        }

        const data = await response.json();
        this.setToken(data.access_token, data.role, data.name, data.id);
        return data;
    }

    async register(userData) {
        return this.request('/auth/register', {
            method: 'POST',
            body: JSON.stringify(userData),
        });
    }

    // Courses
    async getCourses(params = {}) {
        const query = new URLSearchParams(params).toString();
        return this.request(`/courses/?${query}`);
    }

    async getCourse(id) {
        return this.request(`/courses/${id}`);
    }

    async createCourse(courseData) {
        return this.request('/courses/', {
            method: 'POST',
            body: JSON.stringify(courseData),
        });
    }

    async updateCourse(id, courseData) {
        return this.request(`/courses/${id}`, {
            method: 'PUT',
            body: JSON.stringify(courseData),
        });
    }

    async deleteCourse(id) {
        return this.request(`/courses/${id}`, {
            method: 'DELETE',
        });
    }

    // Course Content (Modules & Lessons)
    async getCourseModules(courseId) {
        return this.request(`/content/courses/${courseId}/modules`);
    }

    async createModule(moduleData) {
        return this.request('/content/modules', {
            method: 'POST',
            body: JSON.stringify(moduleData),
        });
    }

    async updateModule(moduleId, moduleData) {
        return this.request(`/content/modules/${moduleId}`, {
            method: 'PATCH',
            body: JSON.stringify(moduleData),
        });
    }

    async deleteModule(moduleId) {
        return this.request(`/content/modules/${moduleId}`, {
            method: 'DELETE',
        });
    }

    async createLesson(lessonData) {
        return this.request('/content/lessons', {
            method: 'POST',
            body: JSON.stringify(lessonData),
        });
    }

    async getLesson(lessonId) {
        return this.request(`/content/lessons/${lessonId}`);
    }

    async updateLesson(lessonId, lessonData) {
        return this.request(`/content/lessons/${lessonId}`, {
            method: 'PATCH',
            body: JSON.stringify(lessonData),
        });
    }

    async deleteLesson(lessonId) {
        return this.request(`/content/lessons/${lessonId}`, {
            method: 'DELETE',
        });
    }

    // Analytics
    async getInstructorDashboard() {
        return this.request('/analytics/instructor/dashboard');
    }

    // Enrollments
    async enroll(courseId) {
        return this.request('/enrollments/', {
            method: 'POST',
            body: JSON.stringify({ course_id: courseId }),
        });
    }
    
    async getMyEnrollments() {
        return this.request('/enrollments/me');
    }

    async getCourseEnrollments(courseId) {
        return this.request(`/enrollments/course/${courseId}/all`);
    }

    async dropCourse(enrollmentId) {
        return this.request(`/enrollments/${enrollmentId}`, {
            method: 'DELETE',
        });
    }

    async gradeStudent(enrollmentId, gradeData) {
        return this.request(`/enrollments/${enrollmentId}/grade`, {
            method: 'PATCH',
            body: JSON.stringify(gradeData),
        });
    }

    async getMyWaitlist() {
        return this.request('/enrollments/me/waitlist');
    }

    // Waitlist
    async joinWaitlist(courseId) {
        return this.request('/waitlist/', {
            method: 'POST',
            body: JSON.stringify({ course_id: courseId }),
        });
    }

    async leaveWaitlist(courseId) {
        return this.request(`/waitlist/${courseId}`, {
            method: 'DELETE',
        });
    }

    // User Profile
    async getMyProfile() {
        return this.request('/users/me');
    }

    async updateMyProfile(profileData) {
        return this.request('/users/me', {
            method: 'PATCH',
            body: JSON.stringify(profileData),
        });
    }

    // Reviews
    async getCourseReviews(courseId) {
        return this.request(`/reviews/course/${courseId}`);
    }

    async createReview(reviewData) {
        return this.request('/reviews/', {
            method: 'POST',
            body: JSON.stringify(reviewData),
        });
    }

}

const api = new API();
window.api = api;
