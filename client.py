import socket
import threading

rendezvous_server = (
    "https://fileserve.onrender.com",
    9000,
)  # Replace "rendezvous-server-ip" with the IP address of the rendezvous server
destination_id = "10.20.33.69"  # Replace "destination-client-id" with the ID of the destination client
destination_external_addr = None
client_id = None
client_socket = None


def get_local_external_addr():
    # Using a temporary connection to a known external address to get the local external address
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    local_addr = s.getsockname()
    s.close()
    return local_addr


def register_with_rendezvous(local_addr):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.sendto(local_addr.encode(), rendezvous_server)
    s.close()


def request_destination_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.sendto(destination_id.encode(), rendezvous_server)
    dest_addr, _ = s.recvfrom(1024)
    s.close()
    return dest_addr.decode()


def punch_hole(dest_addr):
    global client_socket

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    for i in range(10):
        client_socket.sendto(f"Punching hole #{i+1}".encode(), dest_addr)

    # Start a separate thread to receive messages from the destination client
    threading.Thread(target=receive_messages).start()


def receive_messages():
    global client_socket

    while True:
        data, addr = client_socket.recvfrom(1024)
        print(f"Received from {addr}: {data.decode()}")


if __name__ == "__main__":
    local_external_addr = get_local_external_addr()
    print("Local external address:", local_external_addr)
    print("Client id : ", local_external_addr[0])

    register_with_rendezvous(local_external_addr)

    destination_external_addr = request_destination_address()
    print("Destination external address:", destination_external_addr)

    print("Starting hole punching...")
    punch_hole((destination_external_addr, 9000))

    while True:
        message = input("Enter a message to send: ")
        client_socket.sendto(message.encode(), (destination_external_addr, 9000))
