Mininet-based Dumbbell topology Emulator and Analyzer for AQM router
================================================================================

Mininet-based dummbell topology which supports the AQM routers and ECN hosts
referred to [measurement-framework](https://gitlab.lrz.de/tcp-bbr/measurement-framework) configured by J. Aulbach.

  1) This emluation allows the bottleneck router to support active queue management (AQM) scheduler that the host provides such as Taildrop [CoDel](https://man7.org/linux/man-pages/man8/tc-codel.8.html), [RED](https://man7.org/linux/man-pages/man8/tc-red.8.html), [FQ_CoDel](https://man7.org/linux/man-pages/man8/tc-fq_codel.8.html) and so on.

  2) This emulation enables the sender to support ECN feedback with simple option activation.

  3) Additionally, this emulator fully support BBRv2 congestion control algorithm introduced by Google. Therefore, if you install the BBR v2 algorithm in the linux kernel and use it, this emulator provides the traced result in .xls files for each BBRv2 hosts.


Based on
--------------------------------------------------------------------------------
This emulator is written by Python and can be executed on the linux supported mininet`

- [run_mininet.py](https://github.com/syj5385/bbr_dumbbell/blob/master/run_mininet.py)

Requirements
--------------------------------------------------------------------------------
1) python-pip	>> apt-get install python-pip
2) mininet	>> apt-get install mininet
3) ethtool	>> apt-get ethtool
4) moreutils	>> apt-get netcat
5) python	>> apt-get install python
6) dpkt		>> pip install dpkt==1.9.1
7) numpy	>> pip install numpy==1.14.0
8) matplotlib	>> pip install matplotlib==2.1.1

	You can install all of them using 'install.sh' shell script
	ex>  sudo ./install.sh
	
9) Only Reno and CUBIC congestion control algorithms can be used in the Linux kernel for general distribution. Therefore, If you want to perform an experiment using various congestion control algorithms, you should compile and add the congestion control you want to test in the form of a kernel module, or download the full Linux kernel from the web site and install the congestion control you want to add. 

Running
--------------------------------------------------------------------------------
1) ./test.sh
2) Check whether iperf server is opened in the remote host.
3) Insert the remote host address and tcp port number ( Port number is set to 5005 )
4) fill the duration blank -> transmitting time
5) Insert the number of the TCP flow ( up to 3 TCP flow )   >> Press OK
6) Write the start time and congestion control algorithm that each TCP flow uses.
7) Execute!!!!
