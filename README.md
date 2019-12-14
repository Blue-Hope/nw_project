# nw_project
[Yonsei univ. NW] TCP/UDP Communication

## Prerequisite
#### PyQt5 for gui
```pip install PyQt5```

## Usage
#### gui version
client
```python3 gui.py --user #{user_id} [--port #{}] [--backlog #{}] [--max_data_recv #{}]```

#### cli version
server
```python3 server.py [--port #{}] [--backlog #{}] [--max_data_recv #{}]```

client
```python3 client.py --cli 1 --username #{username} [--port #{}] [--backlog #{}] [--max_data_recv #{}]```

* * *
## Reference
https://github.com/blue-hope/simple_proxy_server

## Cf.
> v1.0(19.11.06) 
- no gui chat input feature. use cli

> v1.1(19.11.13) 
- gui input feature now available
- client.py cli option added
- no gui option for server.py
- user username instead of user_id
- gui user_id feature not yet deleted

> v1.2(19.12.?)
- file transfer applied
- gui username feature deployed
