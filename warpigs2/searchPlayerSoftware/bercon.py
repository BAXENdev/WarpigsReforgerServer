import socket
import struct
import zlib
import time
import sys

class BERconResponse():
    def __init__(self, success=False, response='', errorMessage=''):
        self.success = success
        self.response = response
        self.errorMessage = errorMessage
    
    def __str__(self):
        if self.success:
            return self.response
        else:
            return self.errorMessage

class BERconClient:
    def __init__(self, host: str, port: int, password: str, responseTimeout: int = 1):
        self.server = (host, port)
        self.password = password
        self.responseTimeout = max(responseTimeout, 1)
        self.socket: socket.socket = None

    def sendMessage(self, payload: bytes):
        crc = zlib.crc32(payload) & 0xFFFFFFFF
        header = b'BE' + struct.pack('<I', crc) + b'\xFF'
        self.socket.sendto(header + payload, self.server)
    
    def _recv_packet(self) -> bytes:
        try:
            data, _ = self.socket.recvfrom(1024)
            # print("TESTING1111")
            # print(data, "\n")
            # print("TESTING222")
            if not data.startswith(b'BE'):
                raise ValueError("Invalid packet header")
            return data[:7], data[7:]  # Skip the 7-byte header
        except socket.timeout:
            return None, None
        
    def listenForResponse(self, responseTimeout=1) -> str:
        timeout = time.time() + responseTimeout
        acknowledged = False
        output = []
        countResponses = 0
        while time.time() < timeout:
            header, response = self._recv_packet()
            if header is None:
                continue

            countResponses += 1
            packet_type = response[0]

            # Command Packet ACK [0x01, 0x00]
            if packet_type == 0x01:
                acknowledged = True
                # print(f"[ACK] Command sequence {seq} acknowledged.")

            elif packet_type == 0x02:
                seq = response[1]
                message = response[2:]
                output.append([seq, message])
                self.sendMessage(b'\x02' + bytes([seq]))

        if not acknowledged:
            pass

        output.sort(key=lambda x: x[0])
        message = '\n'.join(msg.decode('utf-8', errors='ignore') for _, msg in output)
        return message

    def login(self):
        self.sendMessage(b'\x00' + self.password.encode('ascii'))
        header, response = self._recv_packet()
        if not response or response != b'\x00\x01':
            return False
        return True

    def sendCommand(self, command: str) -> bool:
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.bind(('', 0))
            self.socket.settimeout(1)
            if not self.login():
                return BERconResponse(errorMessage="Failed to log in")
            self.sendMessage(b'\x01\x00' + command.encode('ascii'))
            response = self.listenForResponse()
            self.sendMessage(b'\x01\x00' + "@logout".encode('ascii'))
            self.socket.close()
            return BERconResponse(success=True, response=response)
        except Exception as error:
            return BERconResponse(errorMessage=str(error))

def main():
    if len(sys.argv) != 4:
        print("Pass args: ipAddress port password to program")
        sys.exit(1)
    _, ipAddress, port, password = sys.argv
    port = int(port)

    berconClient = BERconClient(ipAddress, port, password)

    while True:
        command = input("BERcon> ")
        if command in (""):
            continue
        elif command.lower() in ("quit", "exit"):
            break
        else:
            print(berconClient.sendCommand(command))

if __name__ == '__main__':
    main()