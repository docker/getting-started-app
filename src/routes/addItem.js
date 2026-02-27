const db = require('../persistence');
const crypto = require('crypto'); // Use Node's native crypto module

module.exports = async (req, res) => {
    const item = {
        id: crypto.randomUUID(), // Generates a standard v4 UUID
        name: req.body.name,
        completed: false,
    };

    await db.storeItem(item);
    res.send(item);
};
