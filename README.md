**Details**<br />
Version: 0.01<br />
Created by: Norbert Lubaszka<br />
Contact: nor.lubaszka@gmail.com<br />
Creation date: 2023-01-10<br />
<br />
**Requirements**
1. IBM MQ Client installed on given server, where script is placed.
2. Python installed in version 3.4. If You want other, just make it compatible with pymqi module and IBM MQ Client (remember to change shebang).
3. Install all modules from requirements.txt. Fell free to change versions of modules.
4. Remember to have network movement open to IBM MQ Servers that You will look for data in.

**Usage** <br />
Script with is used, to monitor given parameter of given queue, with is hosted on IBM MQ server.
Data about queue are stored in configuration file, and called by given name (argv 1), also You have to specify parameter with should be retrieved (argv 2).
Retrieved information are returned on STDO of script, with make it ZABBIX friendly.

**Zabbix integration** <br />
First of all, You need to link script under function in ZABBIX CLIENT. To do it, simply open configuration file, than (somewhere around line 340) add line like this:
<br /><br />
`UserParameter=get.mq.parameter[*],/path/to/get_queue_parameter.py $1 $2`
<br /><br />
Where "get.mq.parameter" is Your own function name. Now You are free to use it in ZABBIX items related to server where You placed this script.
For example item like "_get.mq.parameter[TEST_QUEUE, DEPTH]_" will retrieve depth of queue called in configuration file by TEST_QUEUE and than You can use it in triggers.
