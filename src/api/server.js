// server.js
const express = require('express');
const robotPaymentHandler = require('./robotPaymentHandler');

const app = express();
const port = process.env.PORT || 3000;

app.use(express.json());
app.use('/api', robotPaymentHandler);

app.listen(port, () => {
    console.log(`Server is running on port ${port}`);
});