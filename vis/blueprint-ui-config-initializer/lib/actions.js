import oxigraph from 'oxigraph';
import * as queries from './queries.js';
import { prettify } from './prettyprint.js';
import { runGraphQuery, parametrizeQuery, writeDataToFile, readClassesFromFile, loadTurtleFileIntoStore } from './glue.js';
import chalk from 'chalk';
import createDebug from 'debug';
const debug_sparql = createDebug('sparql');

async function fetchClasses(options) {
    console.log(`output filename: ${options.output}`);

    const data = await runGraphQuery(queries.constructCandidateClasses, 'constructCandidateClasses');

    if (data) {
        writeDataToFile(options.output, data);
    }
}

async function fetchLinks(options) {
    console.log(`classes filename: ${options.classes}`);
    console.log(`output filename: ${options.output}`);

    const classes = await readClassesFromFile(options.classes);

    if (classes === undefined) {
        return console.error(chalk.red(`Aborting`));
    } else if (classes.size === 0) {
        return console.error(chalk.red(`Aborting. No classes found in file ${options.classes}`));
    }
    
    const query = parametrizeQuery(queries.constructCandidateLinks, ["%%values-cls%%", "%%values-linktype%%"], classes);    
    const data = await runGraphQuery(query, 'constructCandidateLinks');    
    const prettyTurtle = await prettify(data);
    
    if (prettyTurtle) {
        writeDataToFile(options.output, prettyTurtle);
    }
}

async function fetchDetails(options) {
    console.log(`classes filename: ${options.classes}`);
    console.log(`output filename: ${options.output}`);

    const classes = await readClassesFromFile(options.classes);

    if (classes === undefined) {
        return console.error(chalk.red(`Aborting`));
    } else if (classes.size === 0) {
        return console.error(chalk.red(`Aborting. No classes found in file ${options.classes}`));
    }
        
    const query = parametrizeQuery(queries.constructCandidateDetails, ["%%values-cls%%"], classes);    
    const data = await runGraphQuery(query, 'constructCandidateDetails');    
    const prettyTurtle = await prettify(data);

    if (prettyTurtle) {
        writeDataToFile(options.output, prettyTurtle);
    }
}

async function generateConfig(options) {
    console.log(`classes filename: ${options.classes}`);
    console.log(`links filename: ${options.links}`);
    console.log(`details filename: ${options.details}`);
    console.log(`output filename: ${options.output}`);

    console.log(chalk.blue(`Combining the files and generating the config ...`));

    const inMemoryStore = new oxigraph.Store();
    let loadingOK = true;
    loadingOK &= loadTurtleFileIntoStore(options.classes, inMemoryStore);
    loadingOK &= loadTurtleFileIntoStore(options.links, inMemoryStore);
    loadingOK &= loadTurtleFileIntoStore(options.details, inMemoryStore);

    if (!loadingOK) {
        return console.error(chalk.red(`Aborting`));
    }

    const query = queries.constructConfig;
    debug_sparql(query);
    const blueprintConfig = new oxigraph.Store(inMemoryStore.query(query));
    const data = blueprintConfig.dump({format: "application/trig"});
    const prettyTurtle = await prettify(data);

    if (prettyTurtle) {
        writeDataToFile(options.output, prettyTurtle);
    }
}

export {
    fetchClasses,
    fetchLinks,
    fetchDetails,
    generateConfig
}
