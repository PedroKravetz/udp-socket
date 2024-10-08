import socket
import hashlib

def verify_checksum(data, checksum):
    return hashlib.md5(data).hexdigest() == checksum

# Configurações do cliente
IP = "127.0.0.1"
PORT = 12345
BUFFER_SIZE = 1500
TIMEOUT = 30

# Cria o socket UDP
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client.settimeout(30)

# Mensagem para o servidor
print("1 para arquivo grande, 0 para arquivo pequeno ou -1 para um arquivo inexistente: ")
x = input()
if int(x)==0:
    file = "/teste.txt"
elif int(x)==1:
    file = "/acidentes2017.csv"
else:
    file = "/inexistente.txt"

message = ("REQU "+file).encode('utf-8')
client.sendto(message, (IP, PORT))

received_data = {}

# Recebe a resposta do servidor
while True:
    try:
        data, server = client.recvfrom(BUFFER_SIZE)
        data_parts = data.decode('utf-8').split(" ")
        print(data)
        if data_parts[0] == "ERRO":
            print("Erro:", data.decode('utf-8'))
            break
        
        if data_parts[0] == "DATA":
            block_number, total_blocks = map(int, data_parts[1].split("/"))
            checksum = data_parts[2]
            block_data = data[len(" ".join(data_parts[:3]))+1:]
            print(block_data)
            # Verifica a integridade do bloco
            if verify_checksum(block_data, checksum):
                received_data[block_number] = block_data
            else:
                print(f"Checksum incorreto no bloco {block_number}. Solicitando retransmissão...")
                client.sendto(f"SEND {block_number}".encode('utf-8'), (IP, PORT))
            
            # Se todos os blocos forem recebidos
            if len(received_data) == total_blocks:
                with open("arquivo_reconstruido.txt", "wb") as f:
                    for i in range(1, total_blocks + 1):
                        f.write(received_data[i])
                print("Arquivo reconstruído com sucesso!")
                break
    except socket.timeout:
        pass