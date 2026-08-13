const Database = require('better-sqlite3');
const { hashPassword } = require('../services/password-service');

function createDatabase() {
    const database = new Database(':memory:');
    database.pragma('foreign_keys = ON');
    return database;
}

function initializeSchema(database) {
    database.exec(`
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            pass TEXT NOT NULL
        );
        CREATE TABLE courses (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            price REAL NOT NULL,
            active INTEGER NOT NULL
        );
        CREATE TABLE enrollments (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            course_id INTEGER NOT NULL REFERENCES courses(id)
        );
        CREATE TABLE payments (
            id INTEGER PRIMARY KEY,
            enrollment_id INTEGER NOT NULL UNIQUE REFERENCES enrollments(id) ON DELETE CASCADE,
            amount REAL NOT NULL,
            status TEXT NOT NULL
        );
        CREATE TABLE audit_logs (
            id INTEGER PRIMARY KEY,
            action TEXT NOT NULL,
            created_at DATETIME NOT NULL
        );
    `);

    database.prepare('INSERT INTO users (name, email, pass) VALUES (?, ?, ?)')
        .run('Leonan', 'leonan@fullcycle.com.br', hashPassword('123'));
    database.prepare('INSERT INTO courses (title, price, active) VALUES (?, ?, ?)')
        .run('Clean Architecture', 997.00, 1);
    database.prepare('INSERT INTO courses (title, price, active) VALUES (?, ?, ?)')
        .run('Docker', 497.00, 1);
    const enrollment = database.prepare(
        'INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)',
    ).run(1, 1);
    database.prepare(
        'INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)',
    ).run(enrollment.lastInsertRowid, 997.00, 'PAID');
}

module.exports = { createDatabase, initializeSchema };
