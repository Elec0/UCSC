import sys, os, requests,re
from collections import defaultdict 
from flask import Flask, request, redirect, jsonify, Response, make_response
#from flask.ext.api import status
app = Flask(__name__)

#GLOBALS
kvs = defaultdict(dict)
main_instance = True
IP = '\0'
PORT = '\0'
MAINIP = '\0'
MIMETYPE= 'application/json'
MAX_VALUE_SIZE=1572864 #1.5megs=1572864
#All Keys and Values
@app.route('/kvs/all', methods = ['GET'])
def kvs_all():
    if request.method == 'GET':
        if main_instance == True:#main instance
            return jsonify(kvs)
        else:#forwarding instance
            res = requests.get('http://'+MAINIP+'/kvs/all')
            return res.text

@app.route('/kvs', methods = ['GET','POST','PUT','DELETE'])
def kvs_main():
    temp_dict = request.values
    key = temp_dict['key']
    value = None
    if not re.match('^[a-zA-Z0-9_]{1,250}', key):
        return Response('{"msg":"error", "error":"invalid client specified key"}', status=404, mimetype=MIMETYPE)
    elif len(key) > 250:
        return Response('{"msg":"error", "error":"key is too long"}', status=404, mimetype=MIMETYPE)

    # Only get the value if it actually exists in the request URL, otherwise we get an error
    if 'value' in temp_dict:
        value = temp_dict['value']
   
    if request.method == 'PUT':
        if value == None:
            return Response('{"msg":"error"}',status=404, mimetype=MIMETYPE)
        if len(value) > MAX_VALUE_SIZE:
            return Response('{"msg":"error","error""value cannot exceet 1.5megs"}', status=404, mimetype=MIMETYPE)
        if main_instance == True:#main instance
            if key_exists(kvs, key) == True:
                kvs[key] = value
                return Response('{"replaced":"1","msg":"success"}', status=200, mimetype=MIMETYPE)
            else:
                kvs[key] = value
                return Response('{"replaced":"0","msg":"success"}', status=201, mimetype=MIMETYPE)
        else:#forwarding instance 
            try:
                res = requests.put('http://'+MAINIP+'/kvs', temp_dict);
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
                reply = {"msg":"error", "error":"service is not available"}
                return make_response(jsonify(reply), 404)
            else:
                if res.status_code == 201:
                    return Response('{"replaced":"0","msg":"success"}', status=201, mimetype=MIMETYPE)
                else:
                    return Response('{"replaced":1,"msg":"success"}', status=200, mimetype=MIMETYPE)
    elif request.method == 'POST':
        if main_instance == True:#main instance
            if key_exists(kvs, key):
                kvs[key] = value
                return jsonify({'replaced':'1','msg':'success'})
            else:
                kvs[key] = value
                return jsonify({'replaced':'0','msg':'success'})
        else:#forwarding instance 
            res = requests.post('http://'+MAINIP+'/kvs', temp_dict);
            return res.text 
    elif request.method == 'GET': 
        if main_instance == True:#main instance
            if key_exists(kvs, key):
                reply = {"msg":"success","value": str(kvs[key])} 
                return make_response(jsonify(reply),200)
            else:
                reply = {"msg":"error", "error":"key does not exist"}
                return make_response(jsonify(reply), 404)
        else:#forwarding instance 
            try:
                res = requests.get('http://'+MAINIP+'/kvs?key='+key)
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
                reply = {"msg":"error", "error":"service is not available"}
                return make_response(jsonify(reply), 404)
            else:
                if res.status_code == 404:
                    return Response(res.text, status=404, mimetype=MIMETYPE)
                else:
                    val = res.text;
                    return Response(res.text, status=200, mimetype=MIMETYPE)
    elif request.method == 'DELETE':        
        if main_instance == True:#main instance
            if key_exists(kvs, key):
                del kvs[key]
                reply = {"msg":"success"} 
                return make_response(jsonify(reply),200)
            else:
                reply = {"msg":"error", "error":"key does not exist"}
                return make_response(jsonify(reply), 404)
        else:#forwarding instance 
            try:
                res = requests.delete('http://'+MAINIP+'/kvs?key='+key)
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
                reply = {"msg":"error", "error":"service is not available"}
                return make_response(jsonify(reply), 404) 
            else:
                if res.status_code == 404:
                    return Response(res.text, status=404, mimetype=MIMETYPE)
                else:
                    return Response(res.text, status=200, mimetype=MIMETYPE)
    else:
        return jsonify({'msg:':'error',"error":"wtf"})

"""
    We have code duplicated multiple times, this will make things more readable.
"""
def key_exists(kvs, key):
    for k in kvs:
        if key in kvs:
            return True
    return False
        
if __name__ == '__main__':
        IP = os.environ.get('IP','\0')
        PORT = int(os.environ.get('PORT',0))
        if IP == '\0' or PORT == 0:
            sys.exit("either a host(ip) or a port were not specified")
            
        MAINIP = os.environ.get('MAINIP','\0')
        if MAINIP == '\0' :
            print("Main instance")
        else:
            main_instance = False
            print("Forwarding instance")
        print (IP, PORT, MAINIP)
        app.run(host=IP,port=PORT,threaded=True)
