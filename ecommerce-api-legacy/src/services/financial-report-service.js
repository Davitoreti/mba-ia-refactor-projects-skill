class FinancialReportService {
    constructor({ repository }) {
        this.repository = repository;
    }

    execute({ limit = 100, offset = 0 } = {}) {
        const courses = new Map();

        for (const row of this.repository.getFinancialReportRows({ limit, offset })) {
            if (!courses.has(row.course_id)) {
                courses.set(row.course_id, {
                    course: row.course_title,
                    revenue: 0,
                    students: [],
                });
            }

            if (row.enrollment_id === null) {
                continue;
            }

            const course = courses.get(row.course_id);
            if (row.payment_status === 'PAID') {
                course.revenue += row.payment_amount;
            }
            course.students.push({
                student: row.student_name || 'Unknown',
                paid: row.payment_amount || 0,
            });
        }

        return Array.from(courses.values());
    }
}

module.exports = { FinancialReportService };
