import SparqlClient from 'sparql-http-client/SimpleClient.js';
import fs from 'fs';
import rdfEnv from './rdf-env.js'
import chalk from 'chalk';
import createDebug from 'debug';
const debug_sparql = createDebug('sparql');

const clientOptions = {
    endpointUrl: process.env.SPARQL_ENDPOINT,
    user: process.env.SPARQL_USER,
    password: process.env.SPARQL_PASS
};

function createSparqlClient() {
    logENV();
    return new SparqlClient(clientOptions);
}

const queryOptions = { operation: 'postDirect', headers: { 'Accept': 'text/turtle' } };

function logENV() {
    console.log(`SPARQL_ENDPOINT: ${process.env.SPARQL_ENDPOINT}`);
    console.log(`SPARQL_USER: ${process.env.SPARQL_USER}`);
    console.log(`SPARQL_PASS: ${process.env.SPARQL_PASS !== undefined ? '********' : undefined}`);
}

function parametrizeQuery(queryTemplate, placeholders, classes) {
    if (classes === undefined) {
        return undefined;
    }

    const valuesString = Array.from(classes)
      .map(iri => `\n<${iri}>`)
      .sort()
      .join('');
  
    let query = queryTemplate;
    placeholders.forEach(x => {
      query = query.replaceAll(x, valuesString);
    });
  
    return query;
}

async function runGraphQuery(query, queryId) {
    const client = createSparqlClient();

    console.log(chalk.blue(`Running graph query '${queryId}' ...`));
    debug_sparql(query);

    try {    
        const res = await client.query.construct(query, queryOptions);

        if (!res.ok) {
            return console.error(chalk.red(`Failed to run graph query '${queryId}': HTTP status ${res.status} ${res.statusText}`));
        }

        return await res.text();
    } catch (err) {
        return console.error(chalk.red(`Failed to run graph query: ${err}`));
    }
}

function writeDataToFile(file, data) {
    try {
        fs.writeFileSync(file, data, 'utf8');
        console.log(chalk.green(`File ${file} has been written`));
    } catch (err) {
        console.error(chalk.red(`Failed to write file ${file}: ${err}`));
    }
}

async function readClassesFromFile(file) {
    try {
        const dataset = await rdfEnv.dataset().import(rdfEnv.fromFile(file));
        
        const classes = new Set();
        dataset.filter(matchClassDeclaration)
              .forEach(quad => classes.add(quad.subject.value));
        
        return classes;

    } catch (err) {
        return console.error(chalk.red(`Failed to read classes from file ${file}: ${err}`));
    }
}

function matchClassDeclaration(quad) {
    return quad.predicate.value === 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'
        && quad.object.value === 'http://schema.example.org/blueprint-ui-config-initializer/Class'
}

function loadTurtleFileIntoStore(file, store) {
    try {
        const ttlString = fs.readFileSync(file, 'utf8');    
        store.load(ttlString, { format: "text/turtle" });
        return true;

    } catch (err) {
        return console.error(chalk.red(`Failed to load turtle from file ${file} into in-memory-store: ${err}`));
    }
}

export {
    runGraphQuery,
    parametrizeQuery,
    writeDataToFile,
    readClassesFromFile,
    loadTurtleFileIntoStore
}