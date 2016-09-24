import socket

target_host = "www.google.com"
target_port = 80

#criando um objeto socket

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#conectando cliente ao servidor

client.connect((target_host, target_port))

#enviando dados

client.send("GET / HTTP/1.1\r\nHost: google.com\r\n\r\n")

#recebendo dados

response = client.recv(4096)

print response