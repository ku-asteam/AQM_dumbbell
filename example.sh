python run_mininet.py -b 50 -l 62500 -r 0 -p 0 -e 0 -q '' -n bbr2_reno_10ms -c bbr2:10ms,reno:10ms -d 50 -i 10

#
# -b : bottleneck bandwidth = 50 Mbps
#
# -l : bottleneck buffer size = 62,500 byte
#    BDP = Bandwidth Delay Product
#    50 Mbps x 10ms = 500 kbit = 500,000bit = 62,500 byte ( 1 BDP )
#
# -r : delay between switch 2 and switch 3 : 0 ms
#
# -p : packet loss -> 0 %
#
# -e : enable ecn (Explicit Congestion Notification)
# 	0 : tail drop scheduling
#	1 : CoDel 
# 	In order to use ecn signal, you should select Active Queue management Scheduling method in qdisc 
#
#
# -q : AQM scheduling method
#
# 
# -n : output directory name  -> bbr_cubic_10ms_mm_dd_HH_MM_SS
#
# -c : congestion algorithm1:delay1,congestion algorithm2:delay2
#
# -d : duration of test
#
# -i : starting interval among flows
# 
