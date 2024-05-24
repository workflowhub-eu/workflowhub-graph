import pexpect
import json
import ontospy
import requests
import os
import uuid

from contextlib import asynccontextmanager
from llama_index.llms.ollama import Ollama
from llama_index.core.llms import ChatMessage

from fastapi import FastAPI, HTTPException, File, UploadFile, Request

# -----------------------------------------------------------------------------
# Constants

FUSEKI_URL = os.getenv("FUSEKI_URL")

# -----------------------------------------------------------------------------
# Lifespan with Ollama model

ollama = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create an Ollama instance
    ollama['model'] = Ollama(
        model="llama3",
        base_url="http://randall-ollama:11434",
        request_timeout=30.0,
        #json_mode=True
    )
    yield

    ollama['model'].clear()
    
# -----------------------------------------------------------------------------
# Session

app = FastAPI(lifespan=lifespan)

# -----------------------------------------------------------------------------
# Routes

# Route which accepts a json payload and uploads it to the triplestore
@app.post("/upload/message")
async def upload_message(request: Request):
    data = await request.json()

    # Extract the triples from the data
    triples_n3 = []
    for metric in data['metrics']:
        # Randomly generate unique identifier for the message
        message_id = f"{uuid.uuid4()}"
        
        # Deconstruct topic into series of linked triples
        topic = metric['tags']['topic']
        topic_parts = topic.split('/')

        # Head triple (a message was recorded at timestamp)
        triples_n3.append(f'<{topic}> <message> <{metric["timestamp"]}> .')
        triples_n3.append(f'<{metric["timestamp"]}> <message> <{message_id}> .')
        
        # Value triple
        triples_n3.append(f'<{message_id}> <value> <{metric["fields"]["value"]}> .')
        
    # Upload the triples to the triplestore
    for triple in triples_n3:
        try:
            query = f"update=insert data {{ {triple} }}"
            req = requests.post(f"{FUSEKI_URL}/asdf/update",
                                data=str(query),
                                auth=('admin', 'admin',),
                                headers={'Content-Type': 'application/x-www-form-urlencoded'}
                                )
        except requests.exceptions.RequestException as e:
            print(f"Triple: {triple} caused an error!")
            print(e)
            return {"error": e}
    
    return

@app.post("/upload/crate")
def upload_crate(file: UploadFile):   
    fileString = file.file.read()
    model = ontospy.Ontospy(data=fileString,
                            rdf_format="json-ld",
                            verbose=False,
                            hide_implicit_types=False,
                            hide_base_schemas=False,
                            hide_implicit_preds=False,
                            hide_individuals=False
                            )

    # Extract the triples from the model
    triples = model.query("SELECT ?s ?p ?o WHERE { ?s ?p ?o }")
    print(triples)
    
    # Upload the triples to the triplestore
    for triple in triples:
        # Convert to n3 format
        triple_n3 = f'<{triple[0]}> <{triple[1]}> "{triple[2]}" .'

        # Add to the query
        query = f"update=insert data {{ {triple_n3} }}"

        try:
            req = requests.post(f"{FUSEKI_URL}/asdf/update",
                                data=str(query),
                                auth=('admin', 'admin',),
                                headers={'Content-Type': 'application/x-www-form-urlencoded'}
                                )
        except requests.exceptions.RequestException as e:
            print(f"Triple: {triple} caused an error!")
            print(e)
            return {"error": e}
    print(req.text)

    return {"filename": file.filename}


# -----------------------------------------------------------------------------
# Chat endpoints

@app.post("/chat")
def chat(request: Request, query: str):
    # Get the answer to the query
    response = ollama['model'].complete(query)

    return {"response": response}

