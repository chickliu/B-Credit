### generate abi file
```
python3 contract_abi.py 
```

### start consumer
```
python3 storm_consumer.py
```

### push db data to consumer
```
python3 storm_publisher.py
```

### pull blockchain data to db
```
python3 puller.py
```
