import sys
sys.path.append(r'./forza_motorsport')

from fdp import ForzaDataPacket

def nextFdp(server_socket, format):
    message, _ = server_socket.recvfrom(1024)
    return ForzaDataPacket(message, packet_format=format)
