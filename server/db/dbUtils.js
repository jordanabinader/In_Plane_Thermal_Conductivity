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
        table.float('tcDistance');
        table.float('conductivty');
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
    });

    // SQLite3 last inserted row ID
    const insertId = insertResult[0];
    console.log('Inserted ID:', insertId);
    
    // Create additional tables with insertId
    const tablesToCreate = [
      { name: testSettingTableName, fields: (table) => {
        table.float('controlMode').notNullable();
        table.float('frequency').notNullable();
        table.float('amplitude').notNullable();
        table.datetime('datetime').notNullable();
      }},
      { name: powerTableName, fields: (table) => {
        table.float('heaterNum').notNullable();
        table.float('mV').notNullable();
        table.float('mA').notNullable();
        table.float('dutyCycle').notNullable();
        table.datetime('datetime').notNullable();
      }},
      { name: temperatureTableName, fields: (table) => {
        table.datetime('datetime').defaultTo(knex.fn.now());
        table.float('relTime').notNullable();
        table.float('temp1').notNullable();
        table.float('temp2').notNullable();
        table.float('temp3');
        // Add other temperature columns as needed
      }}
    ];

    for (const { name, fields } of tablesToCreate) {
      const tableName = `${name}_${insertId}`;
      if (!await knex.schema.hasTable(tableName)) {
        await knex.schema.createTable(tableName, fields);
      }
    }
    return {
      testId: insertId
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
};
