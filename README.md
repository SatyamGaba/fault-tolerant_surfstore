# fault-tolerant_surfstore
A cloud-based file storage system patterned on Dropbox that can survive server failure, datacenter failure, and network failures

### Usage
```bash
./run-server.sh <config_file> <server_id> <br/>
./run-client.sh <server_ip_addr> <base_folder_to_sync> <chunk_size>
```
> #### example:
>```bash
>>./run-server.sh config.ini 0` <br/> 
>> ./run-client.sh localhost:9001 ./client1 4096
```
