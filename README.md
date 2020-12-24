Mininet-based Dumbbell topology Emulator and Analyzer for AQM router
================================================================================

Mininet-based dummbell topology which supports the AQM routers and ECN hosts
[!GuiTester screenshot](figure.png)


Based on
--------------------------------------------------------------------------------
TCPGuiTester is written by Java and executed on GNU/Linux 4.x

This application uses tcplog and tcpinfo


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
