'''
This is a Py-Ez script to collect logs from Host OS in junos platforms like MX204, MX10003, NG-RE, ACX6360, QFX Fabric, etc 
This script uses pyez StartShell(dev) to login to RE shell and then connect to Host OS
Note: Please use root user to login 
'''

'''import modules'''
from jnpr.junos import Device
from jnpr.junos.utils.start_shell import StartShell
from lxml import etree
from pprint import pprint
from jnpr.junos.factory import loadyaml
from jnpr.junos.op.fpc import FpcInfoTable
import warnings
warnings.filterwarnings('ignore', category = RuntimeWarning)

def get_vmhost_shell(dev):

	'''Login to shell mode'''
	ss=StartShell(dev)
	ss.open()
	
	'''Different ways to collect host output'''
	#vmhost_shell = ss.run('cli -c \'request vmhost exec "df -i"\'')
	###Use ">show interfaces terse routing-instance all" to find out virtual instance and IP to connect to Host OS
	#vmhost_shell = ss.run('rsh -JU __juniper_private4__ 192.168.1.1 "df -i"')
	#vmhost_shell = ss.run('rsh -JU __juniper_private5__ 192.168.1.2 "df -i"')
	vmhost_shell = ss.run('vhclient "df -i"')
	#print(vmhost_shell)
	
	'''Print output'''
	for line in vmhost_shell[1].strip().split('\n')[1:]:
		print(line)
		
	'''Logout from shell mode'''
	ss.close() 

if __name__ == '__main__':
	
	'''Login to device'''
	#with Device(host='h16-37.ultralab.juniper.net',user='root',password='Juniper') as dev: ###Testsing MX204 device 
	with Device(host='10.228.30.11',user='root',password='Juniper') as dev:  ###Testing ACX6360 device 
		print('{:*^50}'.format(' Get vmhost shell info -- shell '))
		get_vmhost_shell(dev)



