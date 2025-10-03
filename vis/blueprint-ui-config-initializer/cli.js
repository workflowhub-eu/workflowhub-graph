import { Command } from 'commander';
import * as actions from './lib/actions.js';

const program = new Command();

program
.name('blueprint-ui-config-initializer')
.description('Initializer for Zazuko Blueprint UI configuration');


program.command('fetch-classes')
  .description('Fetch candidate classes from SPARQL_ENDPOINT')
  .option('--output <filename>', 'output filename', '_classes.ttl')
  .action(actions.fetchClasses);


program.command('fetch-links')
  .description('Fetch candidate links between given classes from SPARQL_ENDPOINT')
  .option('--classes <filename>', 'classes filename', 'classes.ttl')
  .option('--output <filename>', 'output filename', '_links.ttl')
  .action(actions.fetchLinks);


program.command('fetch-details')
  .description('Fetch candidate details for given classes from SPARQL_ENDPOINT')
  .option('--classes <filename>', 'classes filename', 'classes.ttl')
  .option('--output <filename>', 'output filename', '_details.ttl')
  .action(actions.fetchDetails);


program.command('generate-config')
  .description('Generate Blueprint UI configuration from given classes, links and details')
  .option('--classes <filename>', 'classes filename', 'classes.ttl')
  .option('--links <filename>', 'links filename', 'links.ttl')
  .option('--details <filename>', 'details filename', 'details.ttl')
  .option('--output <filename>', 'output filename', '_blueprint-ui-config.ttl')
  .action(actions.generateConfig);


program.parseAsync();