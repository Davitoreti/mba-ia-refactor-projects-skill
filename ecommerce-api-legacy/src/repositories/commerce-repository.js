const { initializeSchema } = require('../models/database');

class CommerceRepository {
    constructor(database) {
        this.database = database;
    }

    initialize() {
        initializeSchema(this.database);
    }

    findActiveCourse(courseId) {
        return this.database.prepare(
            'SELECT id, title, price FROM courses WHERE id = ? AND active = 1',
        ).get(courseId);
    }

    completeCheckout({ name, email, passwordHash, course }) {
        const transaction = this.database.transaction(() => {
            let user = this.database.prepare('SELECT id FROM users WHERE email = ?').get(email);

            if (!user) {
                const created = this.database.prepare(
                    'INSERT INTO users (name, email, pass) VALUES (?, ?, ?)',
                ).run(name, email, passwordHash);
                user = { id: Number(created.lastInsertRowid) };
            }

            const enrollment = this.database.prepare(
                'INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)',
            ).run(user.id, course.id);
            const enrollmentId = Number(enrollment.lastInsertRowid);

            this.database.prepare(
                'INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)',
            ).run(enrollmentId, course.price, 'PAID');
            this.database.prepare(
                "INSERT INTO audit_logs (action, created_at) VALUES (?, datetime('now'))",
            ).run(`Checkout curso ${course.id} por ${user.id}`);

            return { enrollmentId, userId: user.id };
        });

        return transaction();
    }

    getFinancialReportRows({ limit, offset }) {
        return this.database.prepare(`
            WITH selected_courses AS (
                SELECT id, title
                FROM courses
                ORDER BY id
                LIMIT ? OFFSET ?
            )
            SELECT
                c.id AS course_id,
                c.title AS course_title,
                e.id AS enrollment_id,
                u.name AS student_name,
                p.amount AS payment_amount,
                p.status AS payment_status
            FROM selected_courses c
            LEFT JOIN enrollments e ON e.course_id = c.id
            LEFT JOIN users u ON u.id = e.user_id
            LEFT JOIN payments p ON p.enrollment_id = e.id
            ORDER BY c.id, e.id
        `).all(limit, offset);
    }

    deleteUser(userId) {
        return this.database.transaction(() => this.database.prepare(
            'DELETE FROM users WHERE id = ?',
        ).run(userId))();
    }
}

module.exports = { CommerceRepository };
