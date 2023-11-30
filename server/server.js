const express = require('express');
const dbFunctions = require('./db/dbUtils'); // assuming your functions are in dbFunctions.js
const cors = require('cors');

const app = express();

// Enable CORS for all routes
app.use(cors());
app.use(express.json());
// Route to query all rows
app.get('/queryAllRows/:tableName', async (req, res) => {
  try {
    const rows = await dbFunctions.queryAllRows(req.params.tableName);
    res.json(rows);
  } catch (error) {
    res.status(500).send(error.message);
  }
});

// Route to query rows by testId
app.get('/queryRowsByTestId/:tableName/:testId', async (req, res) => {
  try {
    const rows = await dbFunctions.queryRowsByTestId(req.params.tableName, req.params.testId);
    res.json(rows);
  } catch (error) {
    res.status(500).send(error.message);
  }
});

// Route to delete a table
app.delete('/deleteTable/:tableName', async (req, res) => {
  try {
    await dbFunctions.deleteTable(req.params.tableName);
    res.send(`Table ${req.params.tableName} deleted successfully`);
  } catch (error) {
    res.status(500).send(error.message);
  }
});

// Route to start a test
app.post('/startTest', async (req, res) => {
  try {
    result = await dbFunctions.startTest(req.body);
    res.json({ message: 'Test started successfully', testId: result.testId });
  } catch (error) {
    res.status(500).send(error.message);
  }
});

const PORT = 80;
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
