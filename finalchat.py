import socket
import threading
import random
import math
import pickle

PORT = 6969
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'

def generate_n_phi_n ():
    def is_prime(num):
        if num < 2:
            return False
        for i in range(2, num // 2 + 1):
            if num % i ==0:
                return False
        return True

    def generate_prime(min_val, max_val):
        prime = random.randint(min_val, max_val)
        while not is_prime(prime):
            prime = random.randint(min_val, max_val)
        return prime

    # Generating two random prime numbers.    
    p = generate_prime(1000, 9000)
    q = generate_prime(1000, 9000)

    # If both primes are same generating a new prime.
    while p == q:
        q = generate_prime(1000, 5000)

    # Calculating the value of n and phi_n.
    n = p * q
    phi_n = (p-1)*(q-1)
    return (n,phi_n)

def generate_e(phi_n):
    # e is the PUBLIC KEY.
    e = random.randint(3, phi_n - 1)
    while math.gcd(e, phi_n) != 1:
        e = random.randint(3, phi_n - 1)
    return e

def generate_d (e, phi_n):
    # d is the PRIVATE KEY.
    def mod_inverse(e, phi):
        for d in range(3, phi):
            if(d * e) % phi ==1:
                return d
    d = mod_inverse(e , phi_n)
    return d

choice = input("Enter (1) to host server or (2) to connect to a hosted server ")

if choice=="1":
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    server.listen()
    print("waiting for connections...")
    conn,_= server.accept()
    (n_own, phi_n1) = generate_n_phi_n()
    e_1 = generate_e(phi_n1)
    d = generate_d(e_1, phi_n1)
    conn.send(str(e_1).encode(FORMAT))
    e= int(conn.recv(1024).decode(FORMAT))
    conn.send(str(n_own).encode(FORMAT))
    n_other = int(conn.recv(1024).decode(FORMAT))
    print("Connected to the client. Enter the text to be sent to client.")

elif choice =="2":
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn.connect(ADDR)
    (n_own, phi_n2) = generate_n_phi_n()
    e_2 = generate_e(phi_n2)
    d = generate_d(e_2, phi_n2)
    e = int(conn.recv(1024).decode(FORMAT))
    conn.send(str(e_2).encode(FORMAT))
    n_other = int(conn.recv(1024).decode(FORMAT))
    conn.send(str(n_own).encode(FORMAT))
    print("Connected to the server. Enter the text to be sent to server.")

else:
    exit()



def sending(c):
    while True:
        message = input("")
        
        message_encrypted = [ord(ch) for ch in message]
        ciphertext = [pow(ch,e,n_other) for ch in message_encrypted]
        cipher_bytes = pickle.dumps(ciphertext)
        c.send(cipher_bytes)
        print("You: " + message)

def recieve(c):
    while True:
        data = c.recv(4096) 
        recieved_ciphertext = pickle.loads(data)
        message_decrypted = [pow(ch, d, n_own) for ch in recieved_ciphertext]
        decrypted_message = ''.join(chr(ch) for ch in message_decrypted)
        print(f"Partner: {decrypted_message}")

threading.Thread(target =sending, args=(conn, )).start()
threading.Thread(target=recieve, args = (conn, )).start()
