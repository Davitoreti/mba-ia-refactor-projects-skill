class MemoryCache {
    constructor({ maxEntries }) {
        this.maxEntries = maxEntries;
        this.entries = new Map();
    }

    set(key, value) {
        if (this.entries.size >= this.maxEntries && !this.entries.has(key)) {
            const oldestKey = this.entries.keys().next().value;
            this.entries.delete(oldestKey);
        }
        this.entries.set(key, value);
    }
}

module.exports = { MemoryCache };
