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

// Function to delete a table
async function deleteTable(tableName) {
  try {
    await knex.schema.dropTableIfExists(tableName);
  } catch (error) {
    throw error;
  }
}

async function changeTestSetting(form, insertId) {
  try {

    changedSetting = await knex(`${testSettingTableName}_${insertId}`).insert({
      datetime: new Date().toISOString().replace('T', ' ').replace('Z', ''),
      controlMode: 'manual',
      frequency: form.frequency,
      amplitude: form.amplitude,
    });

    return {
      frequency: changedSetting.frequency,
      amplitude: changedSetting.amplitude
    }
  } catch (error) {
    throw error;
  }
}

async function testEndActive(insertId) {
  try {
    await knex({testDirectoryTableName})
    .where({ testID: insertId })
    .update({ active: 'False' });
  } catch (error) {
    console.error('Error in stop active update function:', error);
    throw new Error(`Failed to change active status for test ID ${insertId}: ${error.message}`);
  }
}

async function startTest(form) {
  
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
        table.float('diffusivity');
        table.integer('tcDistance');
        table.float('conductivty');
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
      active: 'True',
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
        // Add other temperature columns as needed
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
      frequency: 0,
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
  deleteTable,
  startTest,
  changeTestSetting,
  testEndActive
};
