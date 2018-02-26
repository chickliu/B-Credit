## this is a demo blockchain project based on a ethereum private chain. 

### requirement
```
sudo apt-get update
sudo apt-get install software-properties-common
sudo add-apt-repository -y ppa:ethereum/ethereum
sudo add-apt-repository -y ppa:ethereum/ethereum-dev
sudo apt-get update
sudo apt-get install solc
sudo pip3 install "web3==3.16.4" "py-solc==2.1.0" "amqpstorm==2.2.2" "Django>2.0,<3.0" "asgi-rabbitmq==0.5.5" "asgi-redis==1.4.3"
```

### comment

#### 1. you should deploy a private chain, may using a cmd as below:
```
geth --identity testetherum --mine --minerthreads 6 --targetgaslimit 18000000 --gasprice 4000000000 --rpc --rpccorsdomain * --rpcaddr 0.0.0.0 --rpcport 8020 --datadir ./chain --port 8010 --rpcapi db,eth,net,personal,miner,admin,web3 --networkid 1010
```

#### 2. settings, using the file "{project_base_dir}/src/btc_cacheserver/settings-zm.py" as a template.

#### 3. using "{project_base_dir}/src/deploy.py" to deploy a contract.

#### 4. using "{project_base_dir}/src/consumer.py" to write data.

#### 5. runserver:
```
python3 manage.py runserver 0.0.0.0:10077
```
