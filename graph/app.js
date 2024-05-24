// Create webserver to serve cytoscape object

const express = require('express');
const app = express();
const port = 8080;

app.get('/', function(request, response){
  response.sendFile(__dirname + '/index.html');
});

app.get('/elements', async function(request, response){
  var graphData = await getGraphData();

  var elements = [];

  // Make subject nodes
  for (var ii = 0; ii < graphData['results']['bindings'].length; ii++) {
    var binding = graphData['results']['bindings'][ii];
    var subject = binding['subject']['value'];
    var subject_node = { data: { id: subject } };
    elements.push(subject_node);
  }

  // Make object nodes and edges
  for (var ii = 0; ii < graphData['results']['bindings'].length; ii++) {
    var binding = graphData['results']['bindings'][ii];

    var subject = binding['subject']['value'];
    var predicate = binding['predicate']['value'];
    var object = binding['object']['value'];

    if (subject === '' || predicate === '' || object === '') {
      continue;
    }

    var subject_node = { data: { id: subject } };
    var object_node = { data: { id: object } };
    var edge = { data: { id: predicate, source: subject, target: object } };

    // If object is already a subject, specify it's parent
    if (!elements.some(function(element) { return element.data.id === object_node.data.id; })) {
      object_node.data.parent = subject;
    }

    elements.push(subject_node);      
    elements.push(object_node);
    elements.push(edge);
  }

  //console.log(elements);
  response.json(elements);
})

app.listen(port, () => {
  console.log(`Example app listening at http://localhost:${port}`);
});


async function getGraphData() {
  var url = process.env.FUSEKI_URL;
  var data = await fetch( url + '/asdf/query', {
    method: 'POST',
    body: "query=SELECT ?subject ?predicate ?object WHERE { ?subject ?predicate ?object } LIMIT 10000",
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      'Accept': 'application/json'
    }
  }).then(function(response) {
    return response.json();
  });

  return data;
}
