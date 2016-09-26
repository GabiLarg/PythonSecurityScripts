import socket

target_host = "127.1.1.0"
target_port = 80

#criando um objeto socket 

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

#enviando dados
client.sendto("Hello World",(target_host, target_port))

#recebendo dados

data, addr = client.recvfrom(4096)

print data