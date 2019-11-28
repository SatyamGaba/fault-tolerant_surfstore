# fault-tolerant_surfstore
A cloud-based file storage system patterned on Dropbox that can survive server failure, datacenter failure, and network failures

### Usage
./run-server.sh config.ini <server_id> <br/>
./run-client.sh <server_ip_addr> <base_folder_to_sync> <chunk_size>
