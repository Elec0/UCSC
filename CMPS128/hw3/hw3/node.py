import sys, os, requests, re
from collections import defaultdict 
from flask import Flask, request, redirect, jsonify, Response, make_response

app = Flask(__name__)

"""

This project is a lot more complicated than the last one.
We need a bit more structure than everything in one function this time.

1. Since we need to approximately evenly split up keys into nodes, we need a hashing function for keys. (hash_key)
    This hash function should take the set of nodes that are available, and the key/value pair, and generate a node in which to store the key/value pair.
    
2. Need to be able to add and remove nodes, and redistribute the keys across the remaining nodes.
    (Proposed protocol for REMOVING a node. 
        TODO: Please refine if you have anything you see wrong)
    a. Node N that receives message to remove a node E.
    c. N forwards message to E
    d. E broadcasts to other nodes that E is no longer online.
    e. E loops through the key/value pairs it has stored and re-hashes them, re-adding them using existing endpoints.
    f. E returns success
    g. N returns success
    
    (Proposed protocol for ADDING a node.
        TODO: Please refine if you have anything you see wrong)
    Assumption: Our hash function can return an entirely different result given a different set of nodes. 
        So, when a node is added it is possible that every key/value pair in all the nodes might need to be moved around. 
    a. Node N receives message to create a new node E.
    b. N broadcasts to all nodes, including E, the new set of VIEW parameters
    c. N waits for acks from all nodes.
    d. On acks from all nodes, N broadcasts the message to rehash and redistribute all existing key/value pairs, and follows this message itself.
        Note: E will have no key/value pairs to rehash and redistribute, so it will do nothing, even though it will execute the function.
        -- After this rehash and redistribute message, all nodes send an ack to N.
    e. Once acks from all nodes have been accumulated, and N is finished itself, return success.
    
3. When adding/removing a key/value pair (Acts very similarly to prior project)
    a. When a key/value pair comes in, hash it.
    b. If the resulting node is not the current node, forward the message to that node.
       Else, store the key/value pair, return success.    
"""


#GLOBALS
kvs = defaultdict(dict)
main_instance = True # To be removed
VIEW = '\0'                     # Environment variable for ip+ports of all other nodes in the cluster.
cluster = []                    # List of strings parsed from VIEW
ourIndex = -1                   # The index in cluster that this node is at
IP_PORT = '\0'                  # The environment variable the IP+PORT is passed in to
IP = '\0'                       # The IP of this node. Parsed from IP_PORT
PORT = '\0'                     # The PORT of this node. Parsed from IP_PORT
MIMETYPE= 'application/json'    # Return type
MAX_VALUE_SIZE=1572864          #1.5megs=1572864

# STATICS
ERR_KEY_NONE = 'key does not exist'
ERR_KEY_LENGTH = 'key is too long'
ERR_TIMEOUT = 'service is not available'
ERR_OTHER = 'something has gone wrong'
ERR_VALUE_MISSING = 'value key not present'
ERR_VALUE_SIZE = 'value cannot exceed 1.5megs'
ERR_INVALID_VAR = 'invalid variable'
ERR_INVALID_KEY = 'invalid client specified key'
ERR_INVALID_METHOD = 'invalid method'

'''
obviously mainip no longer applies I'll get to it-Arom
'''
@app.route('/kvs/debug/node/all', methods = ['GET'])
def kvs_debug_node_key_value():
    return jsonify(kvs)

'''
obviously maininstance no longer applies I'll get to it-Arom
'''
@app.route('/kvs/debug/node/view', methods = ['GET'])
def kvs_debug_node_view():
    return jsonify(VIEW)
    
@app.route('/kvs/debug/node/cluster', methods = ['GET'])
def kvs_debug_cluster_view():
    return jsonify(cluster)
"""
    Returns the number of keys in the local dictionary.
    Should this be the keys in the entire cluster? -Arom
    No, it says in the specs it's a per node function. -Aaron
"""
@app.route('/kvs/get_number_of_keys', methods = ['GET'])    
def kvs_get_keys():
    return jsonify(count=len(kvs))


"""
    Function to add/remove a node. See the comment at the top for the protocols this function should follow.
    I agree with this -Arom
"""
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


"""
    Following the protocol for adding a new node.
    This is gonna be more complicated than the removing a node, unfortunately.
"""
def kvs_view_update_add(new_ip_port):
    global cluster, VIEW, ourIndex
    
    # Remove any possible whitespace and convert to ascii
    new_ip_port = new_ip_port.strip().encode("ascii", "ignore")
    
    # No forwarding will happen. Whatever node receives the message will execute the code
    # APPEND the new address to the cluster.
    #   This ensures ourIndex will never change
    cluster.append(new_ip_port)
    
    # Update the VIEW
    VIEW = ','.join(cluster)
    
    # We need to send a message to everyone that isn't us
    withoutUs = list(cluster)
    withoutUs.remove(IP_PORT)
    
    # Send message to all nodes there has been a view change
    for node in withoutUs:
        try: # Handle if anything is down
            resp = requests.put('http://' + node + "/kvs/parse_view", data={'view':VIEW})
            
            # I am pretty sure this is sync anyway, since executing the rest of the code wouldn't make any sense if we had to
            #   throw a listener to get the result, so let's assume that's the case
            # If the response isn't a success, then we have a problem and everything has gone to crap

            
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout): # This should never happen in this project
            return response_error('error', ERR_TIMEOUT, 404) # We timed out, so return that error
    
    # We are assuming that all nodes will be up and able to receive the view change message.
    # When we get to this point, all nodes have been notified of the new view data
    
    # Send a message to rehash and redistribute all existing key/value pairs to everyone in the cluster
    for node in cluster:
        try: # Handle if anything is down
            resp = requests.get('http://' + node + "/kvs/rehash_redistribute")
            
            if resp.status_code == 404:
                return Response(res.text, status=404, mimetype=MIMETYPE)
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout): # This should never happen in this project
            return response_error('error', ERR_TIMEOUT, 404) # We timed out, so return that error

    
    # We are done. Return success
    return Response('{"msg":"success"}', status=200, mimetype=MIMETYPE)
    
"""
    Just separating out the kvs_view_update functions so things don't get too crowded.
    This instructs the node to remove the given ip_port from the cluster
"""
def kvs_view_update_remove(new_ip_port):
    global cluster, VIEW, ourIndex
    
    # We have been instructed to remove the current node
    if new_ip_port == IP_PORT:
        # Remove ourselves from the cluster list
        cluster.remove(IP_PORT)
        
        ourIndex = -1
        # Create a new VIEW variable from the cluster
        VIEW = ','.join(cluster)
                
        # Send a message to each remaining node that there has been a view change
        for node in cluster:
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

        # Have this node go through and rehash all of the keys on this node
        res = requests.get('http://' + IP_PORT + "/kvs/rehash_redistribute")
       
        
        # Send a message to rehash and redistribute all existing key/value pairs to everyone in the cluster
        # We're doing this because something went wrong with the rehashing just the local node's values, and I don't have enough time
        #   to figure out why it isn't working, but it should be.
        for node in cluster:
            try: # Handle if anything is down
                resp = requests.get('http://' + node + "/kvs/rehash_redistribute")
                
                if resp.status_code == 404:
                    return Response(res.text, status=404, mimetype=MIMETYPE)
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout): # This should never happen in this project
                return response_error('error', ERR_TIMEOUT, 404) # We timed out, so return that error
        
        return Response('{"msg":"success"}', status=200, mimetype=MIMETYPE)
        
    else: # Forward the message to the applicable node
        return handle_forwarding(requests.put, new_ip_port, "/kvs/view_update")
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
    value = None
    global ourIndex, kvs, cluster
    
    # Only get the value if it actually exists in the request URL, otherwise we get an error
    if "value" in request.values:
        value = request.values['value']
    else:
        return response_error("error", ERR_VALUE_MISSING, 404)
        
    # Error checking
    if value == None:
        return response_error("error", '', 404)
    elif len(value) > MAX_VALUE_SIZE:
        return response_error("error", ERR_VALUE_SIZE, 404)
    
    # Find the node the key should be stored on
    nodeInt = hash_key(key, cluster)
    
    # The key/value pair should be stored on our node
    if nodeInt == ourIndex:
        repl = "0"
        if key_exists(kvs, key):
            repl = "1"
        kvs[key] = value
        return Response('{"replaced":' + repl + ',"msg":"success","owner":"' + IP_PORT + '"}', status=201-int(repl), mimetype=MIMETYPE)
        # Note on the status: 201 is created, 200 is successful.
    else: # The key/value pair is stored on a different node, forward the request there
        return handle_forwarding(requests.put, cluster[nodeInt], "/kvs")
"""
    Handling GET requests
"""
def kvs_get(key):
    global cluster, kvs
    
    nodeInt = hash_key(key, cluster)
    
    # If the key is stored on our node
    if nodeInt == ourIndex:
        if key_exists(kvs, key):
            reply = {"msg":"success", "value": str(kvs[key])} 
            return make_response(jsonify(reply),200)
        else:
            return response_error("error", ERR_KEY_NONE, 404)
    else: # Key is stored on a different node
        return handle_forwarding(requests.get, cluster[nodeInt], "/kvs")
        
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
def handle_forwarding(req_type, ip, path):
    try: # Handle if the node is down
        resp = req_type('http://' + ip + path, request.values)
        
        # If the status code is not 404, send it
        if resp.status_code != 404:
            return (resp.text, resp.status_code, resp.headers.items())
            
        else: # We have an error, send the error message
            return Response(res.text, status=404, mimetype=MIMETYPE)
            
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        return response_error('error', ERR_TIMEOUT, 404) # We timed out, so return that error

"""
    This is a method so other nodes can get updated views when nodes are added/removed
"""
@app.route("/kvs/parse_view", methods = ["PUT"])
def parse_view():
    global VIEW, cluster, ourIndex
    
    # Example input: VIEW="10.0.0.20:8080,10.0.0.21:8080"
    VIEW = request.values["view"]
    # Take the input and split it up and insert into the cluster for easier access than parsing a string every time
    cluster = VIEW.split(',')
    cluster_t = [x.strip() for x in cluster]
    cluster = cluster_t
    ourIndex = cluster.index(IP_PORT)
    
    # Return success as an ack, if needed
    return Response('{"msg:success"}', status=200, mimetype=MIMETYPE)

    
"""
    This is called when a new node is added.
    The node is required to loop through its values, make a copy of the key/value, delete it, then re-add it to the cluster
"""
@app.route("/kvs/rehash_redistribute", methods = ["GET"])
def rehash_redistribute():
    global VIEW, cluster, ourIndex, kvs
    
    # Make a copy so we don't worry about deleting anything
    kvs_copy = kvs.copy()
    
    # Delete everything in the node after making the copy
    # We can't do this using the endpoint because by this point VIEW has already been changed,
    #   which means there's a very high chance the node won't be where the hash function expects it to be.
    # All of that to say, just clear the kvs locally.
    kvs.clear()
    
    # Now go back and re-add everything
    for key,value in kvs_copy.items():
        res = requests.put("http://" + IP_PORT + "/kvs", data={'key':key, 'value':value})
        
        if res.status_code >= 400:
            print("There has been an error distributing the keys.")
    
    
    # Return success as an ack, if needed
    return Response('{"msg:success"}', status=200, mimetype=MIMETYPE)


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
    Return True or False if key is in the KVS
"""
def key_exists(store, k):
    return k in store
    
"""
    General function to easily return an error. No need to worry about mistyping the JSON format with it.
"""
def response_error(msg, err, stat):
    error_msg = ''
    if err != '': # If there isn't an error part of the message, don't display that bit
        error_msg = ', "error":"' + err + '"'
    return Response('{"msg":"' + msg + '"' + error_msg + '}', status=stat, mimetype=MIMETYPE)

'''
    I see your logic with this Aaron, for whatever reason the status=stat triggers a "python-syntaxerror-non-keyword-after-keyword-arg" -Arom
    return Response('{"msg":"' + msg + '"' + error_msg + '}', status=stat, MIMETYPE)
'''
    
"""
    Main Flask initialization
"""
if __name__ == '__main__':
    
    VIEW = os.environ.get('VIEW', '\0')
    
    if VIEW != '\0':
        # Take the input and split it up and insert into the cluster for easier access than parsing a string every time
        cluster = VIEW.split(',')
        cluster_t = [x.strip() for x in cluster]
        cluster = cluster_t

    
    IP_PORT = os.environ.get('ip_port', '\0:0')
    
    # Just to keep the code consistent from the last project. Should probably change this eventually?
    IP = IP_PORT.split(':')[0].strip()
    PORT = int(IP_PORT.split(':')[1].strip())
    
    if IP == '\0' or PORT == 0:
        sys.exit("The ip_port variable was improperly defined.")
    
    if VIEW != '\0':
        ourIndex = cluster.index(IP_PORT)
    
    print (IP, PORT, VIEW)
    app.run(host=IP,port=PORT,threaded=True)
