const db = require('../persistence');
const { randomUUID } = require('crypto');

module.exports = async (req, res) => {
    const item = {
        id: randomUUID(),
        name: req.body.name,
        completed: false,
    };

    await db.storeItem(item);
    res.send(item);
};
