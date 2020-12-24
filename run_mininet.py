
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.log import setLogLevel
from mininet.cli import CLI
from mininet.clean import cleanup

from helper.util import sleep_progress_bar

import argparse
import os
import sys
import subprocess
import time
import threading # for trace ss

out_dir = './out'
output_dir = ''

class DumbbellTopo(Topo):
    "Three switchs connected to n senders and receivers."

    def build(self, n=2):
        switch1 = self.addSwitch('s1')
        switch2 = self.addSwitch('s2')
        switch3 = self.addSwitch('s3')

        self.addLink(switch1, switch2)
        self.addLink(switch2, switch3)

        for h in range(n):
            host = self.addHost('h%s' % h, cpu=.5 / n)
            self.addLink(host, switch1)
            receiver = self.addHost('r%s' % h, cpu=1 / n)
            self.addLink(receiver, switch3)

def finally_mininet(qdisc, net, hostlist):
    print ('remove ifb and act_mirred kernel module')
    os.system('rmmod ifb')
    os.system('rmmod act_mirred')

    print ('Disable bbrv2 printk debugging')
    os.system('echo 0 > /sys/module/tcp_bbr2/parameters/debug_port_mask')
    os.system('echo 0 > /sys/module/tcp_bbr2/parameters/debug_with_printk')

def setup_htb_and_qdisc(aqm_switch, qdisc, netem_switch, rate, delay, limit, loss):
    #os.system('rmmod ifb')
    os.system('modprobe ifb numifbs=1')
    os.system('modprobe act_mirred')

    # clear old queueing disciplines (qdisc) on the interfaces
    aqm_switch.cmd('tc qdisc del dev {}-eth1 root'.format(aqm_switch))
    aqm_switch.cmd('tc qdisc del dev {}-eth1 ingress'.format(aqm_switch))
    aqm_switch.cmd('tc qdisc del dev {}-ifb0 root'.format(aqm_switch))
    aqm_switch.cmd('tc qdisc del dev {}-ifb0 ingress'.format(aqm_switch))

    # create ingress ifb0 on client interface.
    aqm_switch.cmd('tc qdisc add dev {}-eth1 handle ffff: ingress'.format(aqm_switch))
    aqm_switch.cmd('ip link add {}-ifb0 type ifb'.format(aqm_switch))
    aqm_switch.cmd('ip link set dev {}-ifb0 up'.format(aqm_switch))
    aqm_switch.cmd('ifconfig {}-ifb0 txqueuelen 1000'.format(aqm_switch))

    # forward all ingress traffic to the ifb device
    aqm_switch.cmd('tc filter add dev {}-eth1 parent ffff: protocol all u32 '
               'match u32 0 0 action mirred egress redirect '
               'dev {}-ifb0'.format(aqm_switch,aqm_switch))

    # create an egress filter on the IFB device
    aqm_switch.cmd('tc qdisc add dev {}-ifb0 root handle 1: '
               'htb default 11'.format(aqm_switch))

    # Add root class HTB with rate limiting 
    aqm_switch.cmd('tc class add dev {}-ifb0 parent 1: classid 1:11 '
               'htb rate {}mbit'.format(aqm_switch,rate))

#aqm_switch.cmd('tc qdisc add dev {}-eth2 root netem delay 10ms'.format(aqm_switch))

    print ('QDISC : {}'.format(qdisc))

#netem_switch.cmd('tc qdisc add dev {}-eth2 root netem delay 10ms'.format(netem_switch))
#print ('{} QDISC : {}'.format(netem_switch,netem_switch.cmd('tc qdisc show dev {}-eth2'.format(netem_switch))))

    
    # Add qdisc for bottleneck
    if qdisc != '':
        aqm_switch.cmd('tc qdisc add dev {}-ifb0 parent 1:11 handle 20: {}'.format(aqm_switch, qdisc))

    else : 
        if int(loss) != 0:
            aqm_switch.cmd('tc qdisc add dev {}-ifb0 parent 1:11 handle 20: netem delay {}ms limit {} loss {}%'.format(aqm_switch,delay, limit, loss))
        else :
            aqm_switch.cmd('tc qdisc add dev {}-ifb0 parent 1:11 handle 20: netem delay {}ms limit {}'.format(aqm_switch,delay, limit))


    # setup network emulator : delay / limit / loss
    # in AQM configuration, limit will be set default txqueuelen
    """
    command = ''
    if loss != 0:
        command = 'tc qdisc add dev {}-eth2 root netem delay {}ms loss {}% limit 1000'.format(netem_switch, delay, loss)
    else:
        command = 'tc qdisc add dev {}-eth2 root netem delay {}ms limit 1000'.format(netem_switch, delay, loss)

    print ("command : {}".format(command))
    netem_switch.cmd(command)
    """


def configure_switch(net, delay=0, limit=1000, rate = 10, loss=0, qdisc='', directory=out_dir):

    print ("Configure 3 switches")
    
    os.system('sysctl -w net.core.rmem_max=250000000 net.ipv4.tcp_rmem=\'4096 131072 250000000\'')
    os.system('sysctl -w net.core.wmem_max=250000000 net.ipv4.tcp_wmem=\'4096  16384 250000000\'')

    s1 = net.get('s1')
    s2 = net.get('s2')
    s3 = net.get('s3')

    s1.cmd('ethtool -K s1-eth1 tso off gso off gro off')
    s1.cmd('ethtool -K s1-eth2 tso off gso off gro off')
    s2.cmd('ethtool -K s2-eth1 tso off gso off gro off')
    s2.cmd('ethtool -K s2-eth2 tso off gso off gro off')
    s3.cmd('ethtool -K s3-eth1 tso off gso off gro off')
    s3.cmd('ethtool -K s3-eth2 tso off gso off gro off')

    setup_htb_and_qdisc(aqm_switch=s2, qdisc = qdisc, netem_switch=s1, rate = rate, delay = delay, limit = limit, loss = loss)

    print ('<switch 1>')
    print ('eth1 : {}'.format(s1.cmd('tc qdisc show dev s1-eth1')))
    print ('eth2 : {}'.format(s1.cmd('tc qdisc show dev s1-eth2')))
    print ('\n<switch 2>')
    print ('eth1 : {}'.format(s2.cmd('tc qdisc show dev s2-eth1')))
    print ('ifb0 : {}'.format(s2.cmd('tc qdisc show dev s2-ifb0')))
    print ('eth2 : {}'.format(s2.cmd('tc qdisc show dev s2-eth2')))
    print ('\n<switch 3>')
    print ('eth1 : {}'.format(s3.cmd('tc qdisc show dev s3-eth1')))
    print ('eth2 : {}'.format(s3.cmd('tc qdisc show dev s3-eth2')))


    print ('------      ++++++      ++++++      ++++++      ------')
    print ('-    -------+    +------+    +      +    +-------    -')
    print ('- hh -======+ s1 +======+ s2 +******+ s3 +======- rr -')
    print ('-    -------+    +------+    +      +    +-------    -')
    print ('------      ++++++      ++++++      ++++++      ------')
    try:
        FNULL=open(os.devnull, 'w')
        subprocess.Popen(['tcpdump', '-i', 's1-eth1', '-n', 'tcp', '-w', '{}/s1.pcap'.format(directory), '-s', '88'], stderr=FNULL)
        subprocess.Popen(['tcpdump', '-i', 's3-eth1', '-n', 'tcp', '-w', '{}/s3.pcap'.format(directory), '-s', '88'], stderr=FNULL)

    except Exception as e:
        print('Error on starting tcpdump\n{}'.format(e))
        sys.exit(1)

    time.sleep(0.2)

def enable_ecn_in_bbr2(host):
    host.cmd('sysctl -w net.ipv4.tcp_ecn=1')
    host.cmd('echo 1 > /sys/module/tcp_bbr2/parameters/ecn_enable')
    host.cmd('echo 0 > /sys/module/tcp_bbr2/parameters/ecn_max_rtt_us')
    #print (host.cmd('egrep . /sys/module/tcp_bbr2/parameters/ecn_enable'))
    #print (host.cmd('egrep . /sys/module/tcp_bbr2/parameters/ecn_max_rtt_us'))

def disable_ecn_in_bbr2(host):
    host.cmd('echo 0 > /sys/module/tcp_bbr2/parameters/ecn_enable')
    host.cmd('echo 5000 > /sys/module/tcp_bbr2/parameters/ecn_max_rtt_us')
    print ("Disable ecn in bbr2 host : {}".format(host))
    #print (host.cmd('egrep . /sys/module/tcp_bbr2/parameters/ecn_enable'))
    #print (host.cmd('egrep . /sys/module/tcp_bbr2/parameters/ecn_max_rtt_us'))
    host.cmd('sysctl -w net.ipv4.tcp_ecn=2')

def configure_host(net, hostlist, bbr2_ecn, duration=10, interval=0):
    for i in range(len(hostlist)):
        tmp = hostlist[i].split(':')
        cca = tmp[0]
        flow_delay = tmp[1]
        send = net.get('h{}'.format(i))
        recv = net.get('r{}'.format(i))

        send.cmd('ethtool -K {}-eth0 tso off gso off gro off'.format(send))
        recv.cmd('ethtool -K {}-eth0 tso off gso off gro off'.format(recv))

#if cca == 'bbr' or cca == 'bbr2':
#       	send.cmd('tc qdisc add dev {}-eth0 root fq pacing'.format(send))
#       else :
        send.cmd('tc qdisc add dev {}-eth0 root netem delay 0.1ms'.format(send))

        send.setIP('10.1.0.{}/8'.format(i))
        recv.setIP('10.2.0.{}/8'.format(i))

        send.cmd('ip route change 10.0.0.0/8 dev {}-eth0 congctl {}'.format(send,cca))
        recv.cmd('tc qdisc add dev {}-eth0 root netem delay {}'.format(recv,flow_delay))
#send.cmd('tcpdump -i {}-eth0 -n tcp -w {}/{}.pacp -s 88 &'.format(send, output_dir, send))

        if cca == "bbr2":
            send.cmd('dmesg -w | grep {} > {} &'.format(recv.IP(), os.path.join(output_dir, 'bbr2_{}.xls'.format(send.IP()))))


        print(send.cmd('tc qdisc show dev {}-eth0'.format(send)))
        print ('{} -> ECN : {}'.format(hostlist[i], bbr2_ecn))
        if int(bbr2_ecn) == 1:
            print (" --> Enable ecn in bbr2 host : {}".format(send)),
            enable_ecn_in_bbr2(send)

#recv.cmd('iperf3 -s -p 10000 &')
#recv.cmd('./server 10000 {} {} &'.format(os.path.join(output_dir,'{}.goodput'.format(recv)), 200))
        recv.cmd('iperf -s -p 10000 &')
#send.cmd('iperf -c {} -p 10000 -t {} &'.format(recv.IP(), duration))
        send.cmd('./ss_script.sh {} >> {}.bbr &'.format(0.02, os.path.join(output_dir, send.IP()))) 
        print ('')

    rest_duration=int(duration)

    for i in range(len(hostlist)):
        send = net.get('h{}'.format(i))
        recv = net.get('r{}'.format(i))
        print ("Send Application")
        send.cmd('iperf -c {} -p 10000 -t {} &'.format(recv.IP(), duration))
        try:
            time.sleep(float(interval))
        except (KeyboardInterrupt, Exception ) as e :
            return
        rest_duration = rest_duration - float(interval)

    start_ss_script(net, interval=0.05)
    progress_bar(duration=rest_duration)
    
    for i in range(len(hostlist)):
        tmp = hostlist[i].split(':')
        cca = tmp[0]
        if int(bbr2_ecn) == 1:
            send = net.get('h{}'.format(i))
            disable_ecn_in_bbr2(send)
    return True

def verifyHost(host):
    # check host string verification 
    hostlist = host.split(',')
    return hostlist

def start_ss_script(net, interval=0.02):
    s2 = net.get('s2')
    s2.cmd('./buffer_script.sh {} {} >> {}.buffer &'.format(0.05, 's2-ifb0', os.path.join(output_dir, 's2-eth2-tbf')))
        
def progress_bar(duration):
    complete = int(duration)
    current_time = 0

    try:
        current_time = sleep_progress_bar((complete - current_time) % 1, current_time = current_time, complete = complete)
        current_time = sleep_progress_bar(complete - current_time, current_time = current_time, complete = complete)
    except (KeyboardInterrupt, Exception ) as e :
        if  isinstance (e, KeyboardInterrupt):
            print ("Keyboard Interrupted. Stop Mininet")

    finally:
        time.sleep(1)
        #net.stop()
        #cleanup()
        #finally_mininet()
        print ("")
        return

def output_directory(target) : 
    if not os.path.exists(out_dir) : 
        os.makedirs(out_dir)

    output_dir = os.path.join(out_dir, '{}_{}'.format(target, time.strftime('%m%d_%H%M%S')))
    os.makedirs(output_dir)

    return output_dir

if __name__ == '__main__':
    # Parsing input argument
    parser = argparse.ArgumentParser()
    parser.add_argument('-b', dest='rate',
                        default=10, help='Initial bandwidth of the bottleneck link (default : 10Mbps)')
    parser.add_argument('-l', dest='limit_byte',
                        default=5, help='Initial bottleneck buffer size in byte (default : 25000b)')
    parser.add_argument('-r', dest='delay', 
                        default=0, help='Iniitial delay switch 1 and switch 3 (default : 0ms)')
    parser.add_argument('-d', dest='duration', 
                        default=10, help='Test duration (default : 10 sec)')
    parser.add_argument('-n', dest='output',
                        default='Congctl', help='Set output directory name (default : Congctl)')
    parser.add_argument('-q', dest='qdisc',
                        default='', help='Set AQM (Active Queue Management) policy on the switch 2 (default : netem)')
    parser.add_argument('-c', dest='host',
                        default='bbr:10ms', help='Set sending host. <example> bbr:10ms  bbr:10ms,cubic:20ms  (default : bbr:10ms)')
    parser.add_argument('-e', dest='my_ecn',
                         default=0, help='enable or disable ECN from switch 2 (default: 1)')
    parser.add_argument('-p', dest='loss',
                        default=0, help='set packet loss rate')
    parser.add_argument('-i', dest='interval',
                        default=0, help='interval among flows')
    arg = parser.parse_args()

    output_dir = output_directory(arg.output)
    
    hostlist = verifyHost(arg.host)
    topo = DumbbellTopo(len(hostlist))
    net = Mininet(topo=topo, link=TCLink)

    #limit = int(arg.rate) *  * 1000 / (8*1514) 
    limit_packet = int(arg.limit_byte) / 1514; # 1514 : mtu size

    print ("ECN enabled : {}".format(arg.my_ecn))

    net.start()

    print ("Enable BBR printk")
    os.system('dmesg -c > /dev/null')
    os.system('echo 55534 > /sys/module/tcp_bbr2/parameters/debug_port_mask')
    os.system('echo 1 > /sys/module/tcp_bbr2/parameters/debug_with_printk')

    configure_switch(net, 
            delay=arg.delay, 
            limit=limit_packet,
            rate=arg.rate, 
            loss=arg.loss, 
            qdisc=arg.qdisc,
            directory = output_dir)

    configure_host(net, hostlist=hostlist, duration=arg.duration, bbr2_ecn=arg.my_ecn, interval = arg.interval)


    #CLI(net)

    finally_mininet(arg.qdisc, net=net, hostlist=hostlist)
    net.stop()
    cleanup()

