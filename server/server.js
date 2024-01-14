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

// Route to query the last row of a specified table
app.get('/queryLastRow/:tableName', async (req, res) => {
  try {
    const tableName = req.params.tableName;
    const lastRow = await dbFunctions.queryLastRow(tableName);
    
    // If lastRow is 0, it means the table does not exist
    if (lastRow === 0) {
      return res.status(404).send('Table does not exist or no rows in the table.');
    }
    res.json(lastRow);
  } catch (error) {
    res.status(500).send(error.message);
  }
});

// Route to query the last frequency and amplitude
app.get('/getTestSetting/:insertId', async (req, res) => {
  try {
    const insertId = req.params.insertId;
    const testSetting = await dbFunctions.getTestSetting(insertId);
    
    // If testSetting is null or undefined, it indicates no record was found
    if (!testSetting) {
      return res.status(404).send('No record found for the provided insertId.');
    }
    res.json(testSetting);
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
    res.json({ message: 'Test started successfully', testId: result.testId, frequency: result.frequency, amplitude: result.amplitude });
  } catch (error) {
    res.status(500).send(error.message);
  }
});

// Route to change test settings
app.post('/changeTestSetting/:insertId', async (req, res) => {
  const insertId = req.params.insertId;
  const form = req.body;
  try {
    const result = await dbFunctions.changeTestSetting(form, insertId);
    res.status(200).json(result);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Route to update the end test
app.put('/test-end/:insertId', async (req, res) => {
  try {
    const insertId = req.params.insertId;
    await dbFunctions.testEndActive(insertId);
    res.status(200).send(`Test with ID ${insertId} has been successfully updated.`);
  } catch (error) {
    res.status(500).send(error.message);
  }
});

app.delete('/deleteTest/:testId', async (req, res) => {
  const testId = req.params.testId;
  try {
    await dbFunctions.deleteTestByTestId(testId);
    res.status(200).json({ message: `Test with testId ${testId} successfully deleted` });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

const PORT = 2999;
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
