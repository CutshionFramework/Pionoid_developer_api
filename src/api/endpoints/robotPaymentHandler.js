// robotPaymentHandler.js
const express = require('express');
const router = express.Router();
const { JakaRobot } = require('./robot/custom_robots/jaka_robot');

router.post('/handle-robot', async (req, res) => {
    try {
        const robot = new JakaRobot("192.168.0.127");
        await robot.login();
        await robot.power_on();
        await robot.enable_robot();
        await robot.joint_move({ joint_pos: [1, 0, 0, 0, 0, 0], move_mode: 0, is_block: false, speed: 1 });
        await robot.logout();
        res.status(200).send({ message: 'Robot operation successful' });
    } catch (error) {
        console.error('Error handling robot operation:', error);
        res.status(500).send({ message: 'Robot operation failed' });
    }
});

module.exports = router;