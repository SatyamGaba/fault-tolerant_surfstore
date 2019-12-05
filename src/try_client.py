import xmlrpc.client

client = xmlrpc.client.ServerProxy("http://" + "localhost:9001")

# Test ping
# if client.surfstore.crash():
   # print("crash() successful")
if client.surfstore.isLeader():
	print("leader")
else:
	print("not a leader")