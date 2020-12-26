'''
importing required modules
'''
import re
import time
from jnpr.junos import Device 

'''
Extracting junos log messages
'''
def logParsing(file_in):

	'''regex to break down junos log in chunk'''
	datetimestamp_log = r'(\w+\s+\d+)'
	timestamp_log = r'(\d+:\d+:\d+.\d+)'
	devicename_log = r'(\S+)'
	process_log = r'(\w+\[\d+\]:|kernel:|mobiled:)'
	error_code_log = r'(\S+)'
	error_message_log = r'(.*)'
	separator_log = r'\s+'
	
	'''Complete log line from regex view'''
	syslog_re = (
		datetimestamp_log + separator_log + 
		timestamp_log + separator_log +
		devicename_log + separator_log + 
		process_log + separator_log +
		error_code_log + separator_log + 
		error_message_log)

	'''parsing log line with regex''' 
	formatted_output=[]
	with open(file_in, 'r') as f:
		for line in f:
			try:
				matched_line = re.match(syslog_re,line)
				formatted_line = list(matched_line.groups())
				#print(formatted_line)
				formatted_output.append(formatted_line)
			except AttributeError:
				pass

	return(formatted_output)
	###['Nov 14', '00:19:23.170', '111N-P1-CNR01-RE0', 'mib2d[73894]:', '%DAEMON-4-SNMP_TRAP_LINK_DOWN:', 'ifIndex 570, ifAdminStatus up(1), ifOperStatus down(2), ifName xe-0/0/1']

def debugLinkDown(formatted_output):
	for item in formatted_output:
		if "SNMP_TRAP_LINK_DOWN" in item[4]: 
			print(item)
			down_intf = re.match(r'.*([x|g|e][e|t]-\d+\/\d+\/\d+(:\d+)?)', item[5])
			print('Please check the related circuit and router for inft:', down_intf.group(1))
			cmd = "show interfaces " + down_intf.group(1) + " terse"
			getJunosCLI(cmd)

def debugDDOSViolation(formatted_output): 
	for item in formatted_output:
		if "DDOS_PROTOCOL_VIOLATION_SET" in item[4]:
			print(item)
			violated_protocol = re.match(r'.*exception\s+(\S+):(\S+)\s+exceeded', item[5])
			# .* resolve:mcast-v4 .*
			#group(1) = resolve 
			#group(2) = mcast-v4
			print("\n***violated protocol: ", violated_protocol.group(1),violated_protocol.group(2),"\n")
			cmd = "show ddos protocols " + violated_protocol.group(1) + " " + violated_protocol.group(2)
			getJunosCLI(cmd)
			
def getJunosCLI(cmd):
	hostname="tango.ultralab.juniper.net"
	username="labroot"
	dev = Device(host=hostname, user=username, passwd='lab123')
	
	try:
		dev.open()
		print("***Connected to device***")
	except Exception as err:
		print(err)
	
	print("***collect debug CLI output***\n>" + cmd + "\n")
	print("***round 1***")
	output1= (dev.cli(cmd,warning=False))
	print(output1)
	time.sleep(3)
	print("***round 2***")
	output2= (dev.cli(cmd,warning=False))
	print(output2)
	dev.close()

if __name__ == '__main__':

	'''input a messages file and parse it '''
	my_file="messages.txt"
	formatted_output=logParsing(my_file)

	'''###extract interested info:
	for item in formatted_output:
		if "mgd" in item[3]: 
			print(item) 
	'''
	
	debugLinkDown(formatted_output)
	#debugDDOSViolation(formatted_output)