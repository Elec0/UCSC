import sys, os, requests, re, time, math, threading, random, json
from collections import defaultdict 
from flask import Flask, request, redirect, jsonify, Response, make_response

app = Flask(__name__)

#GLOBALS
kvs = defaultdict(dict)
partition_id = -1               # The ID of the partition this node is a part of
VIEW = '\0'                     # Environment variable for ip+ports of all other nodes in the cluster.
PARTITION_SIZE = -1             # The max number of nodes in a partition    
PARTITION_NUMS = -1             # Current total number of partitions
cluster = []                    # The IDs of all of the partitions as keys with a list of IP:PORTs as values
ourPartition = -1               # the partition in the cluster
view_index = -1                 # This node's index in the VIEW 'list'
IP_PORT = '\0'                  # The environment variable the IP+PORT is passed in to
IP = '\0'                       # The IP of this node. Parsed from IP_PORT
PORT = '\0'                     # The PORT of this node. Parsed from IP_PORT
vector_clock = []               # List of len(VIEW) that is a vector clock

# STATICS
MIMETYPE= 'application/json'    # Return type
MAX_VALUE_SIZE=1572864          # 1.5megs=1572864
TIMEOUT = 10

# Errors
ERR_KEY_NONE = 'key does not exist'
ERR_KEY_LENGTH = 'key is too long'
ERR_TIMEOUT = 'service is not available'
ERR_OTHER = 'something has gone wrong'
ERR_VALUE_MISSING = 'value key not present'
ERR_CAUSAL_MISSING = 'causal_payload key not present'
ERR_VALUE_SIZE = 'value cannot exceed 1.5megs'
ERR_INVALID_VAR = 'invalid variable'
ERR_INVALID_KEY = 'invalid client specified key'
ERR_INVALID_METHOD = 'invalid method'


####################################
# New endpoints defined in the spec# 
####################################
@app.route('/kvs/get_partition_id',methods = ['GET'])
def kvs_get_partition_id():
    return Response('{"msg":"success", ' + '"partition_id":' + str(partition_id) + '}', status=200, mimetype=MIMETYPE)

# Should return the list of IDs (probably indexes of partition_id_list)
@app.route('/kvs/get_all_partition_ids', methods = ['GET'])
def kvs_get_all_partition_ids():
    return make_response(jsonify({"msg":"success", "partition_id_list":[cluster.index(x) for x in cluster]}), 200)

    # {"msg":"success", "part_id_list":"[1,2,3,4]"}
# Should return partition_id_list at index partition_id
@app.route('/kvs/get_partition_members',methods = ['GET'])
def kvs_get_partition_members():
    part_id = int(request.values['partition_id'])
    #ideally just return the view from any active node in the partition
    return make_response(jsonify({"msg":"success", "partition_members":cluster[part_id]}), 200)

    
@app.route('/kvs/kvs_dump',methods = ['GET'])
def kvs_dump():
    return Response('{"msg":"success", ' + '"kvs":' + str(kvs) + '}', status=200, mimetype=MIMETYPE)
####################################
# End endpoints defined in the spec# 
####################################

@app.route('/kvs/get_number_of_keys', methods = ['GET'])    
def kvs_get_keys():
    return jsonify(count=len(kvs))

@app.route('/kvs/view_update', methods = ['PUT'])
def kvs_view_update():
    temp_dict = request.values
    new_ip_port = temp_dict['ip_port']
    new_type = temp_dict['type']
    
    if new_type == 'add':
        return kvs_view_update_add(new_ip_port)
    
    elif new_type == 'remove':
        return kvs_view_update_remove(new_ip_port)
    
    else:
        return response_error('error', ERR_INVALID_VAR, 404)
    #determine if it's necessary to increment the # of partitions

    #notify all nodes in the partition and potentially the cluster of this change
#    return Response('{"msg":"success"' + '"partition_id":' + partition_id + '"number_of_partitions":' + K '}', status=stat, mimetype=MIMETYPE)



def kvs_view_update_add(new_ip_port):
    global cluster, VIEW, PARTITION_NUMS, PARTITION_SIZE
    #cluster.append(new_ip_port)
    
    # Remove any possible whitespace and convert to ascii
    new_ip_port = new_ip_port.strip().encode("ascii", "ignore")
    
    # Update the VIEW
    VIEW += "," + new_ip_port
    
    view_list = VIEW.split(',')
    
    # We need to send a message to everyone that isn't us
    withoutUs = list(view_list)
    withoutUs.remove(IP_PORT)
    
    # Send message to all nodes there has been a view change
    for node in withoutUs:
        try: # Handle if anything is down
            resp = requests.put('http://' + node + "/kvs/parse_view", data={'view':VIEW})
            
            # I am pretty sure this is sync anyway, since executing the rest of the code wouldn't make any sense if we had to
            #   throw a listener to get the result, so let's assume that's the case
            # If the response isn't a success, then we have a problem and everything has gone to crap

            
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout): # This CAN happen in this project
            pass
            #return response_error('error', ERR_TIMEOUT, 404) # We timed out, so return that error
    
    # We are assuming that all nodes will be up and able to receive the view change message.
    # When we get to this point, all nodes have been notified of the new view data
    
    # Update ourselves
    requests.put('http://' + IP_PORT + '/kvs/parse_view', data={'view':VIEW})
    
    
    # Send a message to rehash and redistribute all existing key/value pairs to everyone in the cluster
    for node in view_list:
        try: # Handle if anything is down
            resp = requests.get('http://' + node + "/kvs/rehash_redistribute")
            if resp.status_code == 404:
                return Response(res.text, status=404, mimetype=MIMETYPE)
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            pass
            #return response_error('error', ERR_TIMEOUT, 404) # We timed out, so return that erro
    
    # We are done. Return success
    
    return Response('{"msg":"success", "partition_id":' + str(hash_partition(new_ip_port.split(',')[0].strip(), PARTITION_NUMS)) + ', "number_of_partitions":' + str(PARTITION_NUMS) + '}', status=200, mimetype=MIMETYPE)
    
"""
    Just separating out the kvs_view_update functions so things don't get too crowded.
    This instructs the node to remove the given ip_port from the cluster
"""
def kvs_view_update_remove(new_ip_port):
    global cluster, VIEW, ourIndex
    
    # We have been instructed to remove the current node
    if new_ip_port == IP_PORT:
        # Remove ourselves from the view list
        view_list = VIEW.split(',')
        view_list.remove(IP_PORT)
        
        view_index = -1
        # Create a new VIEW variable from the cluster
        VIEW = ','.join(view_list)
                
        # Send a message to each remaining node that there has been a view change
        for node in view_list:
            try: # Handle if the node is down
                # Send the message to the node
                resp = requests.put('http://' + node + "/kvs/parse_view", data={'view':VIEW})
                
                # If the status code is 404 break out of the protocol, because something has gone wrong
                # This means it is not fault-tolerant, but that's fine
                if resp.status_code == 404:
                    return Response(res.text, status=404, mimetype=MIMETYPE)
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
                return response_error('error', ERR_TIMEOUT, 404) # We timed out, so return that error
        
        # Now all the nodes have an updated VIEW list
        # Now we need to update ourself
        requests.put('http://' + IP_PORT + '/kvs/parse_view', data={'view':VIEW})
        
        # Have this node go through and rehash all of the keys on this node
        res = requests.get('http://' + IP_PORT + "/kvs/rehash_redistribute")
       
        
        # Send a message to rehash and redistribute all existing key/value pairs to everyone in the cluster
        # We're doing this because something went wrong with the rehashing just the local node's values, and I don't have enough time
        #   to figure out why it isn't working, but it should be.
        for node in view_list:
            try: # Handle if anything is down
                resp = requests.get('http://' + node + "/kvs/rehash_redistribute")
                
                if resp.status_code == 404:
                    return Response(res.text, status=404, mimetype=MIMETYPE)
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout): # This should never happen in this project
                return response_error('error', ERR_TIMEOUT, 404) # We timed out, so return that error
        
        return Response('{"msg":"success", "number_of_partitions":' + str(PARTITION_NUMS) + '}', status=200, mimetype=MIMETYPE)
        
    else: # Forward the message to the applicable node
        return handle_forwarding(requests.put, new_ip_port, "/kvs/view_update")

        
"""
    This is a method so other nodes can get updated views when nodes are added/removed
"""
@app.route("/kvs/parse_view", methods = ["PUT"])
def parse_view():
    global VIEW, cluster, view_index
    
    # Example input: VIEW="10.0.0.20:8080,10.0.0.21:8080"
    VIEW = request.values["view"]
    # Take the input and split it up and insert into the cluster for easier access than parsing a string every time
    view_list = VIEW.split(',')
    view_t = [x.strip() for x in view_list]
    view_list = view_t
    
    if IP_PORT in view_list:
        view_index = view_list.index(IP_PORT)
    
    # Do the actual updating and resetting of all of the variables
    update_partitions(view_list)
    
    # Return success as an ack, if needed
    return Response('{"msg:success"}', status=200, mimetype=MIMETYPE)

    
    
def update_partitions(view_list):
    global PARTITION_NUMS, vector_clock, cluster, partition_id, view_index
    # Current number of partitions (they might not all be full up to PARTITION_SIZE)
    PARTITION_NUMS = int(math.floor(len(view_list) / PARTITION_SIZE))
    
    print("update_partitions: ", PARTITION_NUMS, len(view_list))
    if len(view_list) % PARTITION_SIZE != 0:
        PARTITION_NUMS += 1
    print("after if:", PARTITION_NUMS)
    
    vector_clock = [0]*len(view_list)

    # Initialize the cluster list to size K
    cluster = [None]*PARTITION_NUMS

    for node in view_list:
        # Index of node's partition
        hashed = hash_partition(node, PARTITION_NUMS)
        if not cluster[hashed]:
            cluster[hashed] = []
        # Put the node in the proper partition list
        cluster[hashed].append(node.strip())
        
    partition_id = hash_partition(IP, PARTITION_NUMS)

    # Retrieve this node's index in the VIEW list and store that
    view_index = view_list.index(IP_PORT)
    
"""
    This is called when a new node is added.
    The node is required to loop through its values, make a copy of the key/value, delete it, then re-add it to the cluster
"""
@app.route("/kvs/rehash_redistribute", methods = ["GET"])
def rehash_redistribute():
    global kvs
    
    # Make a copy so we don't worry about deleting anything
    kvs_copy = kvs.copy()
    
    # Delete everything in the node after making the copy
    # We can't do this using the endpoint because by this point VIEW has already been changed,
    #   which means there's a very high chance the node won't be where the hash function expects it to be.
    # All of that to say, just clear the kvs locally.
    kvs.clear()
    
    # Now go back and re-add everything
    for key,value in kvs_copy.items():
        res = requests.put("http://" + IP_PORT + "/kvs", data={'key':key, 'value':value, 'causal_payload':''})
        if res.status_code >= 400:
            print("There has been an error distributing the keys.")
    # Return success as an ack, if needed
    return Response('{"msg:success"}', status=200, mimetype=MIMETYPE)


"""
    The new main method. I think it's better to rewrite it than try to edit the old one
"""
@app.route('/kvs', methods = ['GET','PUT','DELETE'])
def kvs_main_scale():
    temp_dict = request.values
    key = temp_dict['key']
    
    
    if not re.match('^[a-zA-Z0-9_]{1,250}', key):
        return response_error('error', ERR_INVALID_KEY, 404)
    elif len(key) > 250:
        return response_error('error', ERR_KEY_LENGTH, 404)
    if request.method == "PUT":
        return kvs_put(key)
    elif request.method == "GET":
        return kvs_get(key)
    elif request.method == "DELETE":
        return kvs_del(key)

"""
    Handling PUT requests
"""
def kvs_put(key):
    global partition_id, kvs, cluster, PARTITION_NUMS, PARTITION_SIZE
    value = None
    causal_payload = ""
    
    # Only get the value if it actually exists in the request URL, otherwise we get an error
    if "value" in request.values:
        value = request.values['value']
    else:
        return response_error("error", ERR_VALUE_MISSING, 404)
        
    if "causal_payload" in request.values:
        causal_payload = request.values['causal_payload']
    
    # Error checking
    if len(value) > MAX_VALUE_SIZE:
        return response_error("error", ERR_VALUE_SIZE, 404)
    
    # Find the partition the key should be stored on
    partition_loc = hash_partition(key, PARTITION_NUMS)
    
    # The node in the partition we're talking to
    node_loc = 0
    
    # The key/value pair should be stored on our node
    repl = 0
    if partition_loc == partition_id: # If request takes place on the correct destination node
        if key_exists(kvs, key):
            repl = 1
        kvs[key] = value
        
        vector_clock[view_index] += 1
        vc_output = ""
        for v in vector_clock:
            vc_output += str(v) + "."
        vc_output = vc_output[:-1]
        
        if not 'forward' in request.values:
            for node in cluster[partition_loc]:
                print(node)
                if node != IP_PORT: # Make sure we aren't sending to ourselves
                    try:
                        new_values = request.values.to_dict()
                        new_values['forward'] = 'false'
                        handle_forwarding(requests.put, node, "/kvs", new_values)
                    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
                        # The node has crashed, ignore it for now
                        pass
                    

        return Response('{"msg":"success"' + ', "partition_id":' + str(partition_loc) + ', "causal_payload":"' + vc_output +'", "timestamp":"' + str(time.time()) + '"}', status=201-repl, mimetype=MIMETYPE)

    else: # The key/value pair is stored on a different partition, forward the request there
        while node_loc < len(cluster[partition_loc]) - 1:
            try:
                resp = handle_forwarding(requests.put, cluster[partition_loc][node_loc], "/kvs")
                return resp
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
                # Node timed out, so try another node
                node_loc += 1
"""
    Handling GET requests
"""
def kvs_get(key):
    global partition_id, kvs, cluster, K
    causal_payload = ""
    
    if "causal_payload" in request.values:
        causal_payload = request.values['causal_payload']
    
    # Find the partition the key should be stored on
    partition_loc = hash_partition(key, PARTITION_NUMS)
    
    # The node in the partition we're talking to
    node_loc = 0
    
    # The key/value pair should be stored on our node
    repl = 0
    if partition_loc == partition_id: # If request takes place on the correct destination node
        
        vector_clock[view_index] += 1
        vc_output = ""
        for v in vector_clock:
            vc_output += str(v) + "."
        vc_output = vc_output[:-1]
        
        if key_exists(kvs, key):
            reply = {"msg":"success", "value": str(kvs[key]), "partition_id":partition_loc, "causal_payload":str(vc_output), "timestamp":str(time.time()) }
            return make_response(jsonify(reply),200)
        else:
            return response_error("error", ERR_KEY_NONE, 404)
        
    else: # The key/value pair is stored on a different partition, forward the request there
        while node_loc < len(cluster[partition_loc]) - 1:
            try:
                resp = handle_forwarding(requests.get, cluster[partition_loc][node_loc], "/kvs")
                return resp
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
                # Node timed out, so try another node
                node_loc += 1
"""
    Handling DELETE requests
"""
def kvs_del(key):  
    global cluster, kvs
    # Find the node that should have its key removed
    nodeInt = hash_key(key, cluster)
    
    # The key/value pair should be stored on our node
    if nodeInt == ourIndex:
        if key_exists(kvs, key):
        	del kvs[key]
        	return Response('{"msg":"success"}', status=200, mimetype=MIMETYPE)
	else:
		return response_error("error", ERR_KEY_NONE, 404)
    else: # The key/value pair is stored on a different node, forward the request there
        return handle_forwarding(requests.delete, cluster[nodeInt], "/kvs")
    
"""
    Call this from the forwarding node. Pass in the relevant method to forward with (requests.put, for example)
    Returns a relevant response, so this can just be returned directly.
    Path is the route to take, i.e.: "/kvs"
"""
def handle_forwarding(req_type, ip, path, new_values=None):
    try: # Handle if the node is down
        if new_values != None:
            resp = req_type('http://' + ip + path, new_values, timeout=TIMEOUT)
        else:
            resp = req_type('http://' + ip + path, request.values, timeout=TIMEOUT)
        
        # If the status code is not 404, send it
        if resp.status_code != 404:
            return (resp.text, resp.status_code, resp.headers.items())
            
        else: # We have an error, send the error message
            return Response(resp.text, status=404, mimetype=MIMETYPE)
            
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        return response_error('error', ERR_TIMEOUT, 404) # We timed out, so return that error

"""
    General function to easily return an error. No need to worry about mistyping the JSON format with it.
"""
def response_error(msg, err, stat):
    error_msg = ''
    if err != '': # If there isn't an error part of the message, don't display that bit
        error_msg = ', "error":"' + err + '"'
    return Response('{"msg":"' + msg + '"' + error_msg + '}', status=stat, mimetype=MIMETYPE)


@app.route("/kvs/info_dump", methods = ["PUT"])
def info_dump():
    global vector_clock, kvs
    
    new_kvs = json.loads(request.values['kvs'])
    new_clock = request.values['vector']
    new_clock_list = new_clock.split(".")
    kvs = new_kvs
    new_vector_clock = []
    for x in new_clock_list:
        new_vector_clock.append(int(x))
    
    vector_clock = new_vector_clock
    return make_response(jsonify({'msg':'success'}), 200)
    
    
"""

"""
@app.route("/kvs/compare_clocks", methods = ["PUT"])
def compare_clocks():
    global vector_clock, kvs
    other_clock = request.values['clock']
    other_clock_list = other_clock.split(".")
    other_ip_port = request.values['ip_port']
    
    other_sum = 0
    my_sum = 0
    for x in other_clock_list:
        other_sum += int(x)
    for x in vector_clock:
        my_sum += x
        
    # If I am more up to date, info dump to the other node
    
    if my_sum > other_sum:
        v_c = ""
        for x in vector_clock:
            v_c += str(x) + "."
        v_c = v_c[:-1]
        requests.put('http://' + other_ip_port + '/kvs/info_dump', data={'kvs':json.dumps(kvs), 'vector':v_c})
        return make_response(jsonify({"msg":"true"}), 200)
    elif my_sum < other_sum:
        return make_response(jsonify({"msg":"false"}), 200)
    else:
        return make_response(jsonify({"msg":"true"}), 200)
"""
    This is a timed event that syncs with one other node in the partition
"""
def anti_entropy():
    global vector_clock, cluster
    
    # Get a random node in our partition that's not us
    if len(cluster[partition_id]) > 1:
        node = None
        while True:
            node = random.choice(cluster[partition_id])
            if node != IP_PORT: # Node isn't us
                break
        
        try:
            v_c = ""
            for x in vector_clock:
                v_c += str(x) + "."
            v_c = v_c[:-1]
            
            check = requests.put('http://' + node + '/kvs/compare_clocks', data={'clock':v_c, 'ip_port':IP_PORT})
            if check.json()['msg'] == 'false':
                requests.put('http://' + node + '/kvs/info_dump', data={'kvs':json.dumps(kvs)})
        
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            pass
    threading.Timer(2+random.randrange(1), anti_entropy).start()
            
# ***********************
# ** Generic Functions **
# ***********************

"""
    Takes key and returns an index (0 - len(cluster)) of which node should store the key/value pair.
"""
def hash_key(key, clust):
    # My current idea, sum the int values of the key, and modulus with the number of nodes
    # It's simple, and hopefully won't produce too lopsided a result.
    sum = 0
    for c in key:
        sum += ord(c)
    return sum % len(clust)
    
"""
    The hashing function to determine what partition the IP should go into
"""
def hash_partition(cur_ip, k):
    sum = 0
    for c in cur_ip:
        sum += ord(c)
    return sum % k

"""
    Return True or False if key is in the KVS
"""
def key_exists(store, k):
    return k in store

    
"""
    Main Flask initialization
"""
if __name__ == '__main__':
    VIEW = os.environ.get('VIEW', '\0')

    # Number of partitions
    PARTITION_SIZE = int(os.environ.get('K','-1'))
    IP_PORT = os.environ.get('ip_port', '\0:0')
    
    IP = IP_PORT.split(':')[0].strip()
    PORT = int(IP_PORT.split(':')[1].strip())
    
    if PARTITION_SIZE == -1:
        sys.exit("The number of partitions K was improperly defined");
        
    if IP == '\0' or PORT == 0:
        sys.exit("The ip_port variable was improperly defined.")
    
    if VIEW != '\0':
        # Take view input and split into partitions which are lists of the IP_PORTs that go in them
        view_list = VIEW.split(',')
        
        # Current number of partitions (they might not all be full up to PARTITION_SIZE)
        PARTITION_NUMS = int(math.floor(len(view_list) / PARTITION_SIZE))
        
        if len(view_list) % PARTITION_SIZE != 0:
            PARTITION_NUMS += 1
            
        vector_clock = [0]*len(view_list)
        
        # Initialize the cluster list to size K
        cluster = [None]*PARTITION_NUMS
        
        for node in view_list:
            # Index of node's partition
            hashed = hash_partition(node, PARTITION_NUMS)
            if not cluster[hashed]:
                cluster[hashed] = []
            # Put the node in the proper partition list
            cluster[hashed].append(node.strip())
            
        partition_id = hash_partition(IP, PARTITION_NUMS)
        
        # Retrieve this node's index in the VIEW list and store that
        view_index = view_list.index(IP_PORT)
    
    # Schedule function every second
    threading.Timer(2, anti_entropy).start()
    
    app.run(host=IP,port=PORT,threaded=True)
