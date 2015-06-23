#!/usr/bin/env python
import socket,sys,select

if len(sys.argv) < 4:
	print >> sys.stderr, "Usage: %s listen_port destination_address destination_port"%(sys.argv[0])
	sys.exit(1)


allsocks=[]

buffer=20
maxconns=5

lport=int(sys.argv[1]);
daddress=sys.argv[2];
dport=int(sys.argv[3])

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

lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lsock.bind(('',lport))
lsock.listen(maxconns)
allsocks.append(lsock)

	
while 1:
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
								allsocks[c-1].sendall(allsocks[c].recv(buffer))
							except:
								killsocket(c)
						else:
							try:
								allsocks[c+1].sendall(allsocks[c].recv(buffer))
							except:
								killsocket(c)
			except:
				pass

	if len(a[2])>0:
		if b == lsock:
			for c in range(1,len(allsocks)):
				allsocks[c].shutdown();
				allsocks[c].close();
			sys.exit(1)
		else:
			for b in a[0]:
				for c in range(1,len(allsocks)):
					if allsocks[c]== b:
						killsocket(c)
			
