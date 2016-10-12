#Netcat like Tool from Black Hat Python Book
import sys 
import socket
import getopt 
import threading
import subprocess

listen  = False
command = False
upload  = False
execute = ""
target  = ""
upload_destination  = ""
port    = 0

def usage():
    print "NetCat Like Tool"
    print
    print "Usage: bhpnet.py -t target_host -p port"
    print "-l --listen               - listen on [host]:[port] for incoming connections"
    print "-e --execute=file_to_run  - execute the giiven file upon receiving connection"
    print "-c --command              - initialize a command shell"
    print "-u --upload=destinantion  - upon receiving connection upload a file and write to [destinantion]"
    print
    print
    print "Examples: "
    print "bhpnet.py -t 192.168.0.1 -p 5555 -l -c"
    print "bhpnet.py -t 192.168.0.1 -p 5555 -l -u=c:\\target.exe"
    print "bhpnet.py -t 192.168.0.1 -p 5555 -l -e=\"cat /etc/passwd\""
    print "echo 'ABCDEFGHI' | ./bhpnet.py -t 192.168.11.12 -p 135"
    sys.exit(0)


def client_sender(buffer):
    
    #creating a TCP socket client
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        #connect to the target host
        client.connect((target,port))
        
        if len(buffer):
            client.send(buffer)
        while True:
            
            #wait data back
            recv_len = 1
            response = ""
            
            while recv_len:
                
                data     = client.recv(4096)
                recv_len = len(data)
                response+= data
                
                if recv_len < 4096:
                    break
                
            print response,
            #wait for more input
            buffer = raw_input("")
            buffer+= "\n"
            
            #send if off
            client.send(buffer)
            
    except:
        
        print "[*] Exception! Exiting."
        
        #close connection
        client.close()
        
def server_loop():
    
    global target
    
    #in case no target defned, listen to all interfaces
    if not len(target):
        target = "0.0.0.0"
    
    #defining a TCP socket server
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((target,port))
    server.listen(5)
    
    
    while True:
        client_socket, addr = server.accept()
        
        client_thread = threading.Thread(target=client_handler,
                                         args=(client_socket,))
        client_thread.start()

def client_handler(client_socket):
    global upload
    global execute
    global command
    
    
    #check for upload
    if len(upload_destination):
        
        file_buffer = ""
        
        #keep reading until none is available
        while True:
            data = client_socket.recv(1024)
            
            if not data: 
                break
            else: 
                file_buffer += data
                
        #take this bytes and try to write them out
        
        try: 
            file_descriptor = open(upload_destination, "wb")
            file_descriptor.write(file_buffer)
            file_descriptor.close()
            
            #ack that we wrote the file out
            client_socket.send("SuccessFully saved file to %s\r\n" % upload_destination)
        except:
            client_socket.send("Failed to save file to %s\r\n" % upload_destination)
        
        
        #check for command execution
        if len(execute):
            
            #run the command
            output = run_command(execute)
            
            client_socket.send(output)
            
            
        #if command sheel was requested, enter in another loop
        if command:
            
            while True:
                
                #show simple prompt
                client_socket.send("<BHP:#> ")
                
                #receive data until receive a enter key
                
                cmd_buffer = ""
                
                while "\n" not in cmd_buffer:
                    cmd_buffer += client_socket.recv(1024)
                    
                #send back the command output 
                response = run_command(cmd_buffer)
                
                #send back the response
                client_socket.send(response)
                
def run_command(command):
    #trimm the new line
    
    command = command.rstrip()
    
    #run command and get output back
    try:
        
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
    
    except:
        output = "Failed to execute command.\r\n"
        
    #send output back to client
    
    return output


def main():
    
    global listen
    global port 
    global execute
    global upload_destination
    global target
    
    if not len(sys.argv[1:]):
        usage()
        
        
    try:
        
        options, args = getopt.getopt(sys.argv[1:], "hle:t:p:cu",
                                      ["help","listen","execute","target","port","command","upload"])
    except getopt.GetoptError as err:
        print str(err)
        usage()
        
    for option, arg in options:
        if option in ("-h", "--help"):
            usage()
        elif option in ("-l", "--listen"):
            listen = True
        elif option in ("-e", "--execute"):
            execute = arg
        elif option in ("-c", "--command"):
            command = True
        elif option in ("-u", "--upload"):
            upload = True
        elif option in ("-t", "--target"):
            target = arg
        elif option in ("-p", "--port"):
            port = int(arg)
        else:
            assert False, "Unhandled Option"
        #check if we are going to listen or send data from stdin
        if not listen and len(target) and port > 0:
            buffer = sys.stdin.read()
            
            #send data from buffer
            client_sender(buffer)
            
        if listen: 
            server_loop()
            
main()