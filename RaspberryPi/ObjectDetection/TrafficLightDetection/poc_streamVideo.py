"""
A proof of concept of the traffic light detection
"""
import io
import socket
import struct
import time
import picamera

class SplitFrames:
    def __init__(self, connection):
        self.connection = connection
        self.stream = io.BytesIO()
        self.count = 0

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            # Start of new frame; send the old one's length
            # then the data
            size = self.stream.tell()
            if size > 0:
                # struct.pack(fmt, v1,v2,..) --> returns a bytes objcect containing values v1, v2, .. packed according to the string fmt format
                self.connection.write(struct.pack('<L', size))  # TODO: don't know what connection.write does
                self.connection.flush()  # flush the data, to send right away. Explanation on flush--> https://stackoverflow.com/a/914321/7359915
                # Change the stream position to the given byte offset (the parameter) --> https://docs.python.org/3/library/io.html#io.IOBase.seek
                self.stream.seek(0)  # change stream position to beginning
                # stream.read(size) --> read up to 'size' bytes from the object and return them (if size = -1, then readall() is called)
                # if 0 bytes are return from stream.read(), and size != 0, then it indicates the end of file
                self.connection.write(self.stream.read(size))
                self.count += 1
                self.stream.seek(0)
        self.stream.write(buf)

if __name__ == "__main__":
    client_socket = socket.socket()
    client_socket.connect(('192.168.1.7', 8000))
    connection = client_socket.makefile('wb')
    duration_video = 18000; #x # of second long video recording  #TODO: maybe instead of fixed duration of video, have it record forever with a stop functionality
    try:
        output = SplitFrames(connection)
        with picamera.PiCamera(resolution='VGA', framerate=30) as camera:
            time.sleep(2)
            start = time.time()
            camera.resolution = (320,240)
            camera.start_recording(output, format='mjpeg')
            # TODO: Link shows method to record until a key press, not wait for a duration: https://raspberrypi.stackexchange.com/q/38892/70993
            # And maybe this link too: https://raspberrypi.stackexchange.com/a/26469/70993
            camera.wait_recording(duration_video)
            camera.stop_recording()
            # Write the terminating 0-length to the connection to let the
            # server know we're done
            connection.write(struct.pack('<L', 0))
    finally:
        connection.close()
        client_socket.close()
        finish = time.time()
    print('Sent %d images in %d seconds at %.2ffps' % (
        output.count, finish-start, output.count / (finish-start)))