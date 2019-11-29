from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
from socketserver import ThreadingMixIn

import argparse
import hashlib
import xmlrpc.client
import random
import time
import threading

BlockStore = {}
FileInfoMap = {}

class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

class threadedXMLRPCServer(ThreadingMixIn, SimpleXMLRPCServer):
    pass

class timerClass():
    '''Timer'''
    def __init__(self):
        self.t_a = 1500
        self.t_b = 2500
        self.start = int(time.time()*1000)
        self.timeout = random.randint(self.t_a,self.t_b)

    def now(self):
        return int(time.time()*1000) - self.start
    def reset(self):
        self.start = int(time.time()*1000)
        self.timeout = random.randint(self.t_a,self.t_b)


# A simple ping, returns true
def ping():
    """A simple ping method"""
    #print("Ping()")
    return True

# Gets a block, given a specific hash value
def getblock(h):
    """Gets a block"""
    # print("GetBlock(" + h + ")")

    #blockData = bytes(4)
    blockData = BlockStore[h]
    #print(BlockStore)
    return blockData

# Puts a block
def putblock(b):
    """Puts a block"""
    # print("PutBlock()", b)

    h = hashlib.sha256(b.data).hexdigest()
    # print("index: ", h)
    BlockStore[h] = b.data
    return True

# Given a list of hashes, return the subset that are on this server
def hasblocks(hashlist):
    """Determines which blocks are on this server"""
    # print("HasBlocks()")

    haslist = []
    haslist = [hashes for hashes in hashlist if hashes in BlockStore.keys()]

    return haslist

# Retrieves the server's FileInfoMap
def getfileinfomap():
    """Gets the fileinfo map"""
    # print("GetFileInfoMap()")

    result = FileInfoMap
    return result

# Update a file's fileinfo entry
def updatefile(filename, version, hashlist):
    """Updates a file's fileinfo entry"""
    # print("UpdateFile()")

    if filename in FileInfoMap.keys():
        #file already exist in cloud
        last_version = FileInfoMap[filename]
        if (version == last_version[0]+1):
            FileInfoMap[filename] = tuple((version, hashlist))
        else:
            "send error"
            return False
    else:
        #new file (version should be 1)
        FileInfoMap[filename] = tuple((version, hashlist))
    return True

# PROJECT 3 APIs below

# Queries whether this metadata store is a leader
# Note that this call should work even when the server is "crashed"
def isLeader():
    """Is this metadata store a leader?"""
    print("IsLeader()")
    if state == 0:
        return True
    return False

# "Crashes" this metadata store
# Until Restore() is called, the server should reply to all RPCs
# with an error (unless indicated otherwise), and shouldn't send
# RPCs to other servers
def crash():
    """Crashes this metadata store"""
    global is_crashed
    print("Crash()")
    is_crashed = True
    return True

# "Restores" this metadata store, allowing it to start responding
# to and sending RPCs to other nodes
def restore():
    """Restores this metadata store"""
    global is_crashed
    print("Restore()")
    is_crashed = False
    return True


# "IsCrashed" returns the status of this metadata node (crashed or not)
# This method should always work, even when the node is crashed
def isCrashed():
    """Returns whether this node is crashed or not"""
    print("IsCrashed()")
    return is_crashed


def requestVote(client):
    global vote_counter
    try:
        if client.voteHandler(current_term, idx):#, last_log_index, last_log_term): #true or false
            #print("vote accepted")
            vote_counter +=1
    except Exception as e:
        #print("in except for " + str(client))        
        pass
        # print("Server: " + str(e))

def voteHandler(cand_term, cand_id):#, cand_last_log_index, cand_last_log_term):
    global voted_for
    global current_term
    global state

    #print(current_term, cand_term)
    if current_term < cand_term:
        # if cand_last_log_index > last_log_index:
        voted_for = cand_id
        current_term = cand_term
        state = 2
        return True
    else:
        return False    

    # # ***** also check log
    #     self.votedFor = cand_id
    #     self.currentTerm = cand_term
    #     return True  
    # return False


def appendEntries(client):
    try:
        client.heartbeatHandler(current_term, idx)
    except Exception as e:
        #print("in except for " + str(client))        
        pass
    pass
    # self.timer.reset()
    # client = xmlrpc.client.ServerProxy("http://" + server_info[voter_id])
    # client.heartbeatHandler(self.id, self.currentTerm)

def heartbeatHandler(leader_term, leader_id):
    global timer
    global current_term
    print("received heartbeat by: " + str(leader_id)+" in term " + str(leader_term))
    current_term = leader_term
    timer.reset()

def requestVoteHandler():
    global current_term
    global state
    global vote_counter
    global timer

    timer = timerClass()
    timer.reset()
    while True:
        if state !=0:
            if timer.now() > timer.timeout:
                state = 1  # candidate
                current_term +=1
                vote_counter = 0 #initialized
                vote_counter += 1 # vote for self
                timer.reset()
                th11_list = []
                for cl in client_list:
                    th11_list.append(threading.Thread(target = requestVote, args=(cl, )))
                    th11_list[-1].start()
                for t in th11_list:
                    t.join()
                #print(vote_counter)
                if vote_counter > (num_servers/2):
                    state = 0 #leader elected
                    print("I am the king in term: " + str(current_term) +", votes: " + str(vote_counter))
                    # immediately send hearbeat here somehow
        else:
            if timer.now() > 1000:
                timer.start = int(time.time()*1000)
                th_heartbeat = []
                for cl in client_list:
                    th_heartbeat.append(threading.Thread(target = appendEntries, args=(cl, )))
                    th_heartbeat[-1].start()
                for t in th_heartbeat:
                    t.join()
    
        
def raftThread():
    global state
    global is_crashed
    global current_term
    global voted_for
    global client_list
    
    client_list = []
    for i in server_info.keys():
        if i!=idx:
            cl = xmlrpc.client.ServerProxy("http://"+server_info[i])
            client_list.append(cl)

    th11 = threading.Thread(target = requestVoteHandler, )
    th11.start()
    th11.join()

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="SurfStore server")
    parser.add_argument('config_file', help='path to config file')
    parser.add_argument('idx', help='server id')
    args = parser.parse_args()

    config_file = args.config_file
    idx = int(args.idx)

    server_info = {}

    with open(config_file,'r') as file:
        next(file)
        for line in file:
            server_info[int(line.split(' ')[0][-2])] = line.split(' ')[1][:-1]

    address, port = server_info[idx].split(':')
    port = int(port)

    num_servers = len(server_info)
    state = 2   # 0: Leader; 1: Candidate; 2: Follower
    is_crashed = False
    current_term = 1
    voted_for = None
    # last_log_index = 0
    # last_log_term = 

    print("Attempting to start XML-RPC Server at "+ address+":"+str(port))
    server = threadedXMLRPCServer((address, port), requestHandler=RequestHandler)
    th1 = threading.Thread(target = raftThread)
    th1.start()
    # th1.join()
    server.register_introspection_functions()
    server.register_function(ping,"surfstore.ping")
    server.register_function(getblock,"surfstore.getblock")
    server.register_function(putblock,"surfstore.putblock")
    server.register_function(hasblocks,"surfstore.hasblocks")
    server.register_function(getfileinfomap,"surfstore.getfileinfomap")
    server.register_function(updatefile,"surfstore.updatefile")

    server.register_function(isLeader,"surfstore.isleader")
    server.register_function(crash,"surfstore.crash")
    server.register_function(restore,"surfstore.restore")
    server.register_function(isCrashed,"surfstore.iscrashed")

    server.register_function(voteHandler,"voteHandler")
    server.register_function(heartbeatHandler, "heartbeatHandler")
    # server.register_function()

    print("Started successfully.")
    print("Accepting requests. (Halt program to stop.)")
    server.serve_forever()
    # except Exception as e:
    #     print("Server: " + str(e))


        # idx from config.ini

        # server = serverClass(localhost,8080, idx)

        # for idx in all_ids:
        #     server.requestVote(idx)
