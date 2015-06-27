#!/usr/bin/env python
import socket,sys,select,argparse

ap=argparse.ArgumentParser(description='A TCP/UDP Proxy program',usage="Usage: %s [-u] [-m] [-h] [-o file] listen_port destination_address destination_port"%(sys.argv[0]),)

ap.add_argument('-u','--udp',help="UDP Proxy", action="store_true")
ap.add_argument('-o','--output',type=argparse.FileType('w'),help="Output text to file")
ap.add_argument('-m','--maxconns',type=int,help="Maximum number of connections in TCP mode",default=5)
ap.add_argument('lport')
ap.add_argument('daddress')
ap.add_argument('dport')
args=ap.parse_args()

allsocks=[]
buffer=20
lport=int(args.lport)
daddress=args.daddress
dport=int(args.dport)

def socketshut(c):
	try:
		allsocks[c].shutdown(socket.SHUT_RDWR);
		allsocks[c].close();
	except:
		pass

def killsocket(c):
	socketshut(c)
	allsocks.remove(allsocks[c])
	if c%2 == 0:
		socketshut(c-1)
		allsocks.remove(allsocks[c-1])
	else:
		socketshut(c)
		allsocks.remove(allsocks[c])

if args.udp:
	lsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	lsock.bind(('',lport))

else:
	lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	lsock.bind(('',lport))
	lsock.listen(args.maxconns)

allsocks.append(lsock)

	
while 1:
	try:
		if args.udp:
			d=lsock.recvfrom(1024)
			if args.output:
				args.output.write("%s"%d[0])
			dsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			dsock.sendto(d[0],(daddress,dport))
			r=dsock.recvfrom(1024)
			args.output.write("%s"%r[0])
			lsock.sendto(r[0],d[1])
		else:
			a=select.select(allsocks,[],allsocks,60)
			for b in a[0]:
				if b == lsock:
					(csock, address) = lsock.accept()
					csock.setblocking(0)
					dsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
					dsock.connect((daddress,dport))
					dsock.setblocking(0)
					allsocks.append(csock)
					allsocks.append(dsock)
				else:
					try:
						for c in range(1,len(allsocks)):
							if allsocks[c]== b:
								if c%2 == 0:
									try:
										data=allsocks[c].recv(buffer)
										if args.output:
											args.output.write("%s"%data)
										allsocks[c-1].sendall(data)
									except:
										killsocket(c)
								else:
									try:
										data=allsocks[c].recv(buffer)
										if args.output:
											args.output.write("%s"%data)
										allsocks[c+1].sendall(data)
									except:
										killsocket(c)
					except:
						pass

			if len(a[2])>0:
				if b == lsock:
					for c in range(1,len(allsocks)):
						socketshut(c)
					sys.exit(1)
				else:
					for b in a[0]:
						for c in range(1,len(allsocks)):
							if allsocks[c]== b:
								killsocket(c)
	except KeyboardInterrupt:
		if args.output:
			args.output.close()
		if not args.udp:
			for c in range(1,len(allsocks)):
				socketshut(c)
		sys.exit(0)
