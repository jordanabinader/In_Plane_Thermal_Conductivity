const knex = require('./knex');


const testSettingTableName = 'test_settings';
const powerTableName = 'power_table';
const temperatureTableName = 'temperature_table';
const testDirectoryTableName = 'test_directory';

// Function to query all rows from a table
async function queryAllRows(tableName) {
  try {
    const rows = await knex.select('*').from(tableName);
    return rows;
  } catch (error) {
    throw error;
  }
}

// Function to query rows by testId
async function queryRowsByTestId(tableName, testId) {
  try {
    const rows = await knex.select('*').from(tableName).where('testId', testId);
    return rows;
  } catch (error) {
    throw error;
  }
}
//7133

// Get last row of the test_directory table
async function queryLastRow(table_name) {
  try {
    // Check if the table exists
    const tableExists = await knex.schema.hasTable(table_name);
    if (!tableExists) {
      return 0;
    }

    // If the table exists, proceed to get the last row
    const row = await knex(table_name).orderBy('testId', 'desc').first();
    return row;
  } catch (error) {
    console.error("Error in queryLastRow:", error);
    throw error;
  }
}



// Function to delete a table
async function deleteTestByTestId(testId) {
  try {
    // Delete the row from the main test directory table
    await knex(testDirectoryTableName)
      .where('testId', testId)
      .del();

    // Drop related tables
    await knex.schema.dropTableIfExists(`${powerTableName}_${testId}`);
    await knex.schema.dropTableIfExists(`${testSettingTableName}_${testId}`);
    await knex.schema.dropTableIfExists(`${temperatureTableName}_${testId}`);

  } catch (error) {
    console.error(`Error occurred while deleting test with testId ${testId}:`, error.message);
    throw error;
  }
}

async function changeTestSetting(form, insertId) {
  try {
    let dataToInsert = {
      datetime: new Date().toISOString().replace('T', ' ').replace('Z', ''),
      controlMode: form.controlMode,
    }
    if (form.controlMode === 'power') {
      dataToInsert.frequency = form.frequency;
      dataToInsert.amplitude = form.amplitude;
    } else if (form.controlMode === 'manual') {
      dataToInsert.frequency = 1;
      dataToInsert.amplitude = form.amplitudeManual;
    }
    changedSetting = await knex(`${testSettingTableName}_${insertId}`).insert(dataToInsert);

    return {
      frequency: changedSetting.frequency,
      amplitude: changedSetting.amplitude
    }
  } catch (error) {
    throw error;
  }
}

async function getTestSetting(insertId) {
  try {

    const lastRecord = await knex(`${testSettingTableName}_${insertId}`)
                             .orderBy('datetime', 'desc')
                             .first();

    if (!lastRecord) {
      throw new Error('No record found');
    }

    return {
      frequency: lastRecord.frequency,
      amplitude: lastRecord.amplitude
    }
  } catch (error) {
    throw error;
  }
}


async function testEndActive(insertId) {
  try {
    await knex({testDirectoryTableName})
    .where({ testID: insertId })
    .update({ active: false});
  } catch (error) {
    console.error('Error in stop active update function:', error);
    throw new Error(`Failed to change active status for test ID ${insertId}: ${error.message}`);
  }
}

async function startTest(form) {

    // Tester to check if testName, material are strings and thermocouple is not an int, and none are empty
    if (typeof form.testName !== 'string' || form.testName.trim() === '') {
      throw new Error('Invalid testName: must be a non-empty string');
    }
    if (typeof form.material !== 'string' || form.material.trim() === '') {
      throw new Error('Invalid material: must be a non-empty string');
    }
    if (typeof form.tcDistance !== 'number' || form.tcDistance === 0) {
      throw new Error('Invalid thermocouple distance: must be a number and non-empty');
    }

  try {
    console.log('StartTest');
    console.log(form);

    // Check and create the testDirectoryTable if not exists
    if (!await knex.schema.hasTable(testDirectoryTableName)) {
      await knex.schema.createTable(testDirectoryTableName, table => {
        table.increments('testId').primary();
        table.string('testName'); // Assuming testName and others are strings
        table.string('material');
        table.float('density'); // Changed from real to float
        table.float('specificHeatCapacity');
        table.datetime('datetime');
        table.float('lowerTime');
        table.float('upperTime');
        table.float('diffusivity');
        table.integer('tcDistance');
        table.float('conductivity');
        table.boolean('active');
      });
      console.log('Table created');
    } else {
      console.log('Table already exists');
    }
    console.log('done')
    // Insert data into testDirectoryTable
    const insertResult = await knex(testDirectoryTableName).insert({
      datetime: new Date().toISOString().replace('T', ' ').replace('Z', ''),
      testName: form.testName,
      material: form.material,
      density: form.density,
      specificHeatCapacity: form.specificHeatCapacity,
      tcDistance: form.tcDistance,
      active: true,
    });

    // SQLite3 last inserted row ID
    const insertId = insertResult[0];
    console.log('Inserted ID:', insertId);
    
    // Create additional tables with insertId
    const tablesToCreate = [
      { name: testSettingTableName, fields: (table) => {
        table.float('controlMode');
        table.float('frequency');
        table.float('amplitude');
        table.datetime('datetime');
      }},
      { name: powerTableName, fields: (table) => {
        table.float('heaterNum');
        table.float('mV');
        table.float('mA');
        table.float('dutyCycle');
        table.datetime('datetime');
      }},
      { name: temperatureTableName, fields: (table) => {
        table.datetime('datetime').defaultTo(knex.fn.now());
        table.float('relTime');
        table.float('temp1');
        table.float('temp2');
        table.float('temp3');
        table.float('temp4');
        table.float('temp5');
        table.float('temp6');
        table.float('temp7');
        table.float('temp8');
      }}
    ];

    for (const { name, fields } of tablesToCreate) {
      const tableName = `${name}_${insertId}`;
      if (!await knex.schema.hasTable(tableName)) {
        await knex.schema.createTable(tableName, fields);
      }
    }
    
    // Insert data into testDirectoryTable
    const testSettingInit = await knex(`${testSettingTableName}_${insertId}`).insert({
      datetime: new Date().toISOString().replace('T', ' ').replace('Z', ''),
      controlMode: 'manual',
      frequency: 1,
      amplitude: 0,
    });

    return {
      testId: insertId,
      frequency: testSettingInit.frequency,
      amplitude: testSettingInit.amplitude
    };

  } catch (error) {
    throw error;
  }
}


// Export functions
module.exports = {
  queryAllRows,
  queryRowsByTestId,
  startTest,
  changeTestSetting,
  testEndActive,
  deleteTestByTestId,
  queryLastRow,
  getTestSetting
};
