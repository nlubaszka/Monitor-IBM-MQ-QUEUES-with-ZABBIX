#!/usr/bin/python3.4
"""
-- Details --
      Version: 0.01
   Created by: Norbert Lubaszka
      Contact: nor.lubaszka@gmail.com
Creation date: 2023-01-10

-- Requirements --
1. IBM MQ Client installed on given server, where script is placed.
2. Python installed in version 3.4. If You want other, just make it compatible with pymqi module and IBM MQ Client (remember to change shebang).
3. Install all modules from requirements.txt. Fell free to change versions of modules.
4. Remember to have network movement open to IBM MQ Servers that You will look for data in.

-- Usage --
Script with is used, to monitor given parameter of given queue, with is hosted on IBM MQ server.
Data about queue are stored in configuration file, and called by given name (argv 1), also You have to specify parameter with should be retrieved (argv 2).
Retrieved information are returned on STDO of script, with make it ZABBIX friendly.

-- Zabbix integration --
First of all, You need to link script under function in ZABBIX CLIENT. To do it, simply open configuration file, than (somewhere around line 340) add line like this:

UserParameter=get.mq.parameter[*],/path/to/get_queue_parameter.py $1 $2

Where "get.mq.parameter" is Your own function name. Now You are free to use it in ZABBIX items related to server where You placed this script.
For example item like "get.mq.parameter[TEST_QUEUE, DEPTH]" will retrieve depth of queue called in configuration file by TEST_QUEUE and than You can use it in triggers.
"""

# Required modules
import pymqi
import json
import sys
import os

# Variables definition
script_dir = os.path.dirname(os.path.realpath(__file__))
queues_definition_file = "/queues_definition.json"
called_by = sys.argv[1]
parameter_to_retrieve = sys.argv[2]

# Check if queue definition file exists, if yes fetch it
if not os.path.isfile(script_dir + queues_definition_file):
    sys.exit("Queues definition file was not found under path: " + script_dir + queues_definition_file)

try:
    with open(script_dir + queues_definition_file, "r") as f:
        queue_definition = json.loads(f.read())
except Exception as ex:
    sys.exit("There was error while getting queue definition file (" + script_dir + queues_definition_file + "): " + str(ex))

# Get connection information for queue with should be checked from queue definitions
queue_to_check = list(filter(lambda queue: queue["CALL_BY"] == called_by, queue_definition["QUEUES_DEFINITION"]))

# If there are other amount of queues than one retrieved, exit with error
if len(queue_to_check) == 0:
    sys.exit("Queue called by " + called_by + " was not found in configuration file.")

if len(queue_to_check) > 1:
    sys.exit("Found more than one queue called by " + called_by + ".")

# Set connection information for queue with should be checked
queue_to_check = queue_to_check[0]

try:
    # Attempt connection do MQ server defined under given queue
    conn_info = '%s(%s)' % (queue_to_check["HOST"], queue_to_check["PORT"])
    qmgr = pymqi.connect(queue_to_check["QUEUE_MANAGER"], queue_to_check["CHANNEL"], conn_info)
    pcf = pymqi.PCFExecute(qmgr)

    # Search for defined queue and retrieve result of search
    attrs = {
        pymqi.CMQC.MQCA_Q_NAME: queue_to_check["QUEUE_NAME"]
    }
    result = pcf.MQCMD_INQUIRE_Q(attrs)
except Exception as ex:
    sys.exit("There was error while getting data for queue called by " + called_by + ": " + str(ex))

# If there are other amount of queues than one retrieved, exit with error
if len(result) == 0:
    sys.exit("Queue matching attributes for " + called_by + " was not retrieved.")

if len(result) > 1:
    sys.exit("Found more than one queue matching attributes for " + called_by + ".")

# Base on requested parameter, return it in STD
if parameter_to_retrieve == "DEPTH":
    print(result[0][pymqi.CMQC.MQIA_CURRENT_Q_DEPTH])
else:
    sys.exit("Trying to retrieve unknown parameter " + parameter_to_retrieve + " for queue called by " + called_by)

# Disconnect from MQ server
qmgr.disconnect()