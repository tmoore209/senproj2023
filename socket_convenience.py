import socket

BUFF_SIZE = 65536
def CreateSocket(timeout=0, port=0):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, BUFF_SIZE)
    if port:
        s.bind(('0.0.0.0', int(port)))
    if timeout:
        s.settimeout(timeout)
    return s

_local_ip = ""
def GetLocalIp():
    global _local_ip
    if not _local_ip:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('192.255.255.255', 1))
        _local_ip = s.getsockname()[0]
        s.close()
    return _local_ip

def GetSocketPort(s):
    return s.getsockname()[1]

def utf8send(sock, msg, ip, port=None):
    if port == None:
        ip, port = ip
    print(f"""\
    sock ({type(sock)}) {sock},
    msg  ({type(msg)}) {msg},
    ip   ({type(ip)}) {ip},
    port ({type(port)}) {port}
    """)
    if isinstance(msg, str):
        msg = msg.encode('utf8')
    sock.sendto(msg, (ip, int(port)))


def utf8get(sock, split=False) -> (str, str, int):
    msg, (addr, port) = sock.recvfrom(BUFF_SIZE)
    msg = msg.decode("utf8")
    if split:
        msg = msg.split(" ")
    return msg, addr, int(port)


####
##
####
import dataclass

@dataclass
class RudpSegment:
    pass


class RUDP:
    """Reliable UDP port"""

    def __init__(self, timeout:int=0, port:int=0):
        self.socket = CreateSocket(timeout=timeout, port=port)

    def utf8send(msg, ip:str, port:int) -> None:
        utf8send(self.socket, msg, ip, port)

    def utf8get(split:bool=False) -> (str, str, int):
        return utf8get(self.socket, split)

    def _sendto(msg, ip:str, port:int=None) -> None:
        if port:
            ip  ip, port
        self.socket.sendto(msg, (ip,port))

    def _recvfrom(BUFF_SIZE) -> (str, int):
        return self.socket.recvfrom(BUFF_SIZE)

    def connect(self, ip:str, initialPort:int):
        pass

if __name__ == "__main__":
    from sys import argv
    if "rudp" in argv:
        sock = RUDP()
        
