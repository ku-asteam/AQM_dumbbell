TCPGuiTester - Application for logging and tracing tcp flows in real time with visualizing Graph.
================================================================================

Application for logging the throughput, RTT, cwnd in real time.
!
[!GuiTester screenshot](figure.png)


Based on
--------------------------------------------------------------------------------
TCPGuiTester is written by Java and executed on GNU/Linux 4.x

This application uses tcplog and tcpinfo


Requirements
--------------------------------------------------------------------------------
1) Java (JDK)  >> apt-get install openjdk-11-jdk
2) tcplog      >> git clone https://git.scc.kit.edu/CPUnetLOG/TCPlog (required git)
3) yad 	       >> apt-get install yad
4) tcpinfo     >> apt-get install python3 python3-pip
               >> pip3 install tcpinfo   (Reboot required)

	You can install them using 'install.sh' shell script
	ex>  sudo ./install.sh

Running
--------------------------------------------------------------------------------
1) ./test.sh
2) Check whether iperf server is opened in the remote host.
3) Insert the remote host address and tcp port number ( Port number is set to 5005 )
4) fill the duration blank -> transmitting time
5) Insert the number of the TCP flow ( up to 3 TCP flow )   >> Press OK
6) Write the start time and congestion control algorithm that each TCP flow uses.
7) Execute!!!!
