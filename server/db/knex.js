const knex = require('knex');

const connectedknex = knex({
    client: 'sqlite3',
    connection: {
      filename: "./server/angstronomers.sqlite3"
    },
    useNullAsDefault: true
  });

module.exports = connectedknex;