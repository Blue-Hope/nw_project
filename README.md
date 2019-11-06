# nw_project
[Yonsei univ. NW] TCP/UDP Communication

## Prerequisite
#### PyQt5 for gui
```pip install PyQt5```

## Usage
#### gui version
server
```python3 gui.py [--port #{}] [--backlog #{}] [--max_data_recv #{}]```

client
```python3 gui.py --user #{user_id} [--port #{}] [--backlog #{}] [--max_data_recv #{}]```

#### cli version
server
```python3 server.py [--port #{}] [--backlog #{}] [--max_data_recv #{}]```

client
```python3 client.py --user #{user_id} [--port #{}] [--backlog #{}] [--max_data_recv #{}]```

* * *
## Reference
https://github.com/blue-hope/simple_proxy_server

## Cf.
v1.0(19.11.06) - no gui chat input feature. use cli
