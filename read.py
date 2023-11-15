import bluetooth
import os
import socket

class BT:
    def __init__(self, name, file_addr="device_addr"):
        self.name = name
        if not os.path.exists(file_addr):
            self.device_addr = self.find_device()
            self.save_addr(self.device_addr)
        else:
            self.device_addr = self.read_addr().strip()
        
        self.sock = self.connect_device()

    def save_addr(self, device_addr): open('ds4_addr', 'w').write(device_addr)
    def read_addr(self): return open('device_addr', 'r').read()

    def find_device(self):
        print("Discovering devices")
        devices = bluetooth.discover_devices(duration=10, lookup_names=True, flush_cache=True)
        print(devices)
        if len(devices) == 0:
            raise Exception("No bluetooth device has been detected")

        device_addr = None
        for addr, name in devices:
            if name == self.name:
                device_addr = addr
                print(f"Controller found (address: {device_addr})")
                break
        
        if not device_addr:
            raise Exception("DualShock4 device has not been detected")

        return device_addr 
    
    def connect_device(self, port=0x0017):
        sock = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_SEQPACKET,socket.BTPROTO_L2CAP)
        sock.connect((self.device_addr, port))
        print("yo")

        return sock 
    
    def read(self, size=1024):
        data = self.sock.recv(size)
        return data

if __name__ == "__main__":
    from proto import avrcp

    reader = BT("WATCH8")
    packets = avrcp.Packets(reader.sock)
    packets.sendcapabilityreq()

    #packets.requesteventvolume()
    parser = avrcp.Parse(packets=packets)

    while True:
        print("Waiting on read:")
        data=reader.read(1024)
        s=""
        for b in data:
           s+= ("%02x" % b)+" "

        print(s)
        parser.parse_avrcp(data)
        print("Status: Playback=%d\n" % (avrcp.playback_status))
     
