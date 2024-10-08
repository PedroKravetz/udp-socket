import socket
import os
import hashlib

# Configurações do servidor
IP = "127.0.0.1"
PORT = 12345
BUFFER_SIZE = 1024
DIR = os.getcwd()

def generate_checksum(data):
    return hashlib.md5(data).hexdigest()

def divide_file(file_path, buffer_size):
    with open(file_path, 'rb') as f:
        while True:
            data = f.read(buffer_size)
            if not data:
                break
            yield data

# Cria o socket UDP
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((IP, PORT))

print(f"Servidor UDP rodando em {IP}:{PORT}")

while True:
    # Recebe requisição do cliente
    data, address = server_socket.recvfrom(BUFFER_SIZE)
    request = data.decode('utf-8')

    # Se a requisição for válida
    if request.startswith("REQU"):
        _, file_name = request.split(" ")
        
        if os.path.exists(DIR+file_name):
            # Divide o arquivo em pedaços
            total_size = os.path.getsize(DIR+file_name)
            total_blocks = (total_size // BUFFER_SIZE) + 1
            block_number = 1
            
            for block in divide_file(DIR+file_name, BUFFER_SIZE):
                checksum = generate_checksum(block)
                response = f"DATA {block_number}/{total_blocks} {checksum} ".encode('utf-8') + block
                server_socket.sendto(response, address)
                block_number += 1
        else:
            # Se o arquivo não for encontrado
            error_msg = "ERRO Arquivo não encontrado".encode('utf-8')
            server_socket.sendto(error_msg, address)
    elif request.startswith("SEND"):
        _, block_required, file_name = request.split(" ")
        print(block_required)
        print(file_name)
        if os.path.exists(DIR+file_name):
            # Divide o arquivo em pedaços
            total_size = os.path.getsize(DIR+file_name)
            total_blocks = (total_size // BUFFER_SIZE) + 1
            block_number = 1
            
            for block in divide_file(DIR+file_name, BUFFER_SIZE):
                checksum = generate_checksum(block)
                if int(block_required)==block_number:
                    response = f"DATA {block_number}/{total_blocks} {checksum} ".encode('utf-8') + block
                    server_socket.sendto(response, address)
                block_number += 1
        else:
            # Se o arquivo não for encontrado
            error_msg = "ERRO Arquivo não encontrado".encode('utf-8')
            server_socket.sendto(error_msg, address)