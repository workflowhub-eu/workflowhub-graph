from fastapi.testclient import TestClient

from .main import app

client = TestClient(app)

################################################################################
# Test correctly formed GET calls for endpoints defined in main.py

def test_help():
    response = client.get("/omnicli/help/")
    assert response.status_code == 200
    assert response.json() == {"output":"  help                                 : Print this help message\n  quit                                 : Quit the interactive terminal\n  log <level>                          : Change the log level\n  list <url>                           : List the contents of a folder\n  stat <url>                           : Print information about a specified file or folder\n  cd <url>                             : Makes paths relative to the specified folder\n  push <url>                           : Makes paths relative to the specified folder\n                                         You can restore the original folder with pop\n  pop                                  : Restores a folder pushed with 'push'\n  copy <src> <dst>                     : Copies a file or folder from src to dst (overwrites dst)\n  move <src> <dst>                     : Moves a file or folder from src to dst (overwrites dst)\n  del <url>                            : Deletes the specified file or folder\n  mkdir <url>                          : Create a folder\n  cat <url>                            : Print the contents of a file\n  cver                                 : Print the client version\n  rver                                 : Print the USD Resolver Plugin version\n  sver <url>                           : Print the server version\n  load <url>                           : Load a USD file\n  save [url]                           : Save a previously loaded USD file (optionally to a different URL)\n  close                                : Close a previously loaded USD file\n  lock [url]                           : Lock a USD file (defaults to loaded stage root)\n  unlock [url]                         : Unlock a USD file (defaults to loaded stage root)\n  getacls <url>                        : Print the ACLs for a URL\n  setacls <url> <user|group> <r|w|a|-> : Change the ACLs for a user or group for a URL\n                                         Specify '-' to remove that user|group from the ACLs\n  auth [username] [password]           : Set username/password for authentication\n                                         Password defaults to username; blank reverts to standard auth\n  checkpoint <url> [comment]           : Create a checkpoint of a URL\n  listCheckpoints <url>                : List all checkpoints of a URL\n  restoreCheckpoint <url>              : Restore a checkpoint\n  disconnect <url>                     : Disconnect from a server\n  join <url>                           : Join a channel. Only one channel can be joined at a time.\n  send <message>                       : Send a message to the joined channel.\n  leave                                : Leave the joined channel\n"}


def test_log():
    response = client.get("/omnicli/log/")
    assert response.status_code == 422
    assert response.json() == {"detail":[{"loc":["query","level"],"msg":"field required","type":"value_error.missing"}]}

    response = client.get("/omnicli/log/?level=info")
    assert response.status_code == 200
    assert response.json() == {"output":"Log level set to info"}
    
