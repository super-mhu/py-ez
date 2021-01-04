'''To run the script:'''
'''Example: python monitor_lab_device_utilization.py herndon.ultralab.juniper.net labroot lab123'''

import argparse
import sys
import re 
from jnpr.junos import Device 
from datetime import datetime 

def checkCommitOneDay():
	time_now = dev.cli('show system uptime',warning=False)
	#print(time_now)
	'''Current time: 2020-12-30 17:11:14 UTC'''
	current_time_0 = re.search(r'.*Current\s+time:\s+(\d+-\d+-\d+\s+\d+:\d+:\d+)\s+\S+',time_now)
	current_time=datetime.strptime(current_time_0.group(1), '%Y-%m-%d %H:%M:%S')
	
	commit_last_one_day=0
	commit_history = dev.cli('show system commit',warning=False)
	all_commit_time = re.findall(r'.*\s+(\d+-\d+-\d+\s+\d+:\d+:\d+)',commit_history)
	for commit in all_commit_time:
		t=datetime.strptime(commit, '%Y-%m-%d %H:%M:%S')	
		t_delta = int((current_time - t).total_seconds())
		#print(t_delta)
		if t_delta <= 86400:
			commit_last_one_day += 1
			
	if commit_last_one_day < 1:
		print(f"commits in last one day {commit_last_one_day}: Low")
		return 0
	elif commit_last_one_day <10:
		print(f"commits in last one day {commit_last_one_day}: Medium")
		return 1
	else:
		print(f"commits in last one day {commit_last_one_day}: High")
		return 2 

def checkCommitTenDays():
	time_now = dev.cli('show system uptime',warning=False)
	#print(time_now)
	'''Current time: 2020-12-30 17:11:14 UTC'''
	current_time_0 = re.search(r'.*Current\s+time:\s+(\d+-\d+-\d+\s+\d+:\d+:\d+)\s+\S+',time_now)
	current_time=datetime.strptime(current_time_0.group(1), '%Y-%m-%d %H:%M:%S')
	
	commit_last_ten_days=0
	commit_history = dev.cli('show system commit',warning=False)
	all_commit_time = re.findall(r'.*\s+(\d+-\d+-\d+\s+\d+:\d+:\d+)',commit_history)
	for commit in all_commit_time:
		t=datetime.strptime(commit, '%Y-%m-%d %H:%M:%S')	
		t_delta = int((current_time - t).total_seconds())
		#print(t_delta)
		if t_delta <= 864000:
			commit_last_ten_days += 1
			
	if commit_last_ten_days < 3:
		print(f"commits in last ten days {commit_last_ten_days}: Low")
		return 0
	elif commit_last_ten_days <20:
		print(f"commits in last ten days {commit_last_ten_days}: Medium")
		return 1
	else:
		print(f"commits in last ten days {commit_last_ten_days}: High")
		return 2 

def checkPFEStats():
	input_pps = 0 
	output_pps = 0 
	pfe_stats = dev.cli('show pfe statistics traffic',warning=False)
	pfe_stats_line=pfe_stats.strip().split('\n')
	'''    Input  packets:             44790380                    3 pps   '''
	'''	   Output packets:             60740356                    5 pps   '''
	for line in pfe_stats_line:
		if re.match(r'\s+Input\s+packets.*pps',line):
			input_pps=int(re.match(r'\s+Input\s+packets.*(\d+)\s+pps',line).group(1))
		if re.match(r'\s+Output\s+packets.*pps',line):
			output_pps=int(re.match(r'\s+Output\s+packets.*(\d+)\s+pps',line).group(1)) 
	
	total_pps = input_pps + output_pps
	
	if total_pps < 10:
		print(f"pfe traffic stats {total_pps} pps: Low")
		return 0
	elif total_pps <1000:
		print(f"pfe traffic stats {total_pps} pps: Medium")
		return 1
	else:
		print(f"pfe traffic stats {total_pps} pps: High")
		return 2 

def checkProtocolAdjacencies():
	ospf_neighbor = dev.cli('show ospf neighbor',warning=False)
	full_neighbor = len(re.findall(r'Full', ospf_neighbor))
	
	isis_neighbor = dev.cli('show isis adjacency', warning=False)
	up_neighbor = len(re.findall(r'Up', isis_neighbor)) 
	
	bgp_neighbor = dev.cli('show bgp summary', warning=False)
	est_neighbor = len(re.findall(r'Establ', bgp_neighbor))

	total_neighbor = full_neighbor + up_neighbor + est_neighbor

	if total_neighbor < 1:
		print(f"total running protocols {total_neighbor}: Low")
		return 0
	elif total_neighbor <5:
		print(f"total running protocols {total_neighbor}: Medium")
		return 1
	else:
		print(f"total running protocols {total_neighbor}: High")
		return 2 

def checkRunningInterface():
	interface_terse = dev.cli('show interfaces terse',warning=False)
	'''Only match for physical interface like ge-0/0/0 not logical interface like ge-0/0/0.0'''
	up_up_interface = len(re.findall(r'[gxe][et]-\d+\/\d+\/\d+\s+up\s+up',interface_terse)) 
	if up_up_interface < 1:
		print(f"total connected interface {up_up_interface}: Low")
		return 0
	elif up_up_interface <4:
		print(f"total connected interface {up_up_interface}: Medium")
		return 1
	else:
		print(f"total connected interface {up_up_interface}: High")
		return 2 

if __name__ == '__main__':

	'''Welcome words'''
	print("****Running a script to monitor the utilization of junos lab devices")
	print(
	"\n+-------------------------------------------+----------+---------+----------+"
	"\n|      Monitoring Criteria                  |   Low    |  Medium |  High    |"
	"\n+-------------------------------------------+----------+---------+----------+"
	"\n|      commit in last 1 day                 |    <1    |   <10   |   >=10   |"
	"\n+-------------------------------------------+----------+---------+----------+"
	"\n|      commit in last 10 days               |    <3    |   <20   |   >=20   |"
	"\n+-------------------------------------------+----------+---------+----------+"
	"\n|      pfe traffic stats                    |    <10   |  <1000  |  >=1000  |"
	"\n+-------------------------------------------+----------+---------+----------+"
	"\n|      Up protocol adjacencies              |    <1    |   <5    |   >=5    |"
	"\n+-------------------------------------------+----------+---------+----------+"
	"\n|      Up physical interfaces               |    <1    |   <4    |   >=4    |"
	"\n+-------------------------------------------+----------+---------+----------+")
	
	'''parse arguments'''
	parser = argparse.ArgumentParser()
	parser.add_argument('ip', type=str,help="IP address of the target device")
	parser.add_argument('username', type=str,help="Username of the target device")
	parser.add_argument('password', type=str,help="Password of the target device")
	args=parser.parse_args()

	'''assign arguments'''
	ipaddr=args.ip
	uname=args.username
	passwd=args.password
	#print(ipaddr,uname,passwd)

	'''connect to a junos device via py-ez'''
	try:
		dev=Device(host=ipaddr,user=uname,passwd=passwd)
		dev.open()
	except Exception:
		print('Connection issue, could not connect to device')
		sys.exit()

	print('Connected to device...')

	total_score = checkCommitOneDay() + checkCommitTenDays() + checkPFEStats() + checkProtocolAdjacencies() + checkRunningInterface() 
	#print(total_score)

	if total_score <=2:
		utlization = "Low" 
	elif total_score <=5:
		utlization = "Medium" 
	else:
		utlization = "High" 
	word = "overall lab device utilization " + utlization
	
	print(f"+-------------------------------------------+----------+---------+----------+")
	print(f"|{word.center(75)}|")
	print(f"+-------------------------------------------+----------+---------+----------+")

	
	dev.close() 
	print("Disconnected from device...")

