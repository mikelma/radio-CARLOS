import socket
import atexit

class Rotor():
    def __init__(host, port):
        self.s = socket.socket(socket.AF_INET,
                               socket.SOCK_STREAM)
        self.s.connect((host, port))

        # automatically close the socket when the program exits
        atexit.register(self.close)

    def set_pos(self, azim, elev, verbose=False):
        cmd = f"P {float(azim)} {float(elev)}\n"
        if verbose:
            print(f"Sending command: {cmd}")
        s.sendall(cmd.encode("ascii"))

    def close(self):
        self.s.close()
