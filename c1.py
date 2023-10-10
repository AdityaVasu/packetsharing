import socket
import threading

# Replace "rendezvous_server_ip" with the IP address or domain name of the rendezvous server
rendezvous_server = ("rendezvous_server_ip", 9000)
destination_id = "10.20.33.69"  # Replace with the ID of the destination client
destination_external_addr = None
client_socket = None


def get_local_external_addr():
    try:
        # Using a temporary connection to a known external address to get the local external address
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_addr = s.getsockname()
        s.close()
        return local_addr
    except socket.error as e:
        print("Error getting local external address:", e)
        return None


def register_with_rendezvous(local_addr):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.sendto(str(local_addr).encode(), rendezvous_server)
        s.close()
    except socket.error as e:
        print("Error registering with the rendezvous server:", e)


def request_destination_address():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.sendto(destination_id.encode(), rendezvous_server)
        dest_addr, _ = s.recvfrom(1024)
        s.close()
        return dest_addr.decode()
    except socket.error as e:
        print("Error requesting destination address:", e)
        return None


def punch_hole(dest_addr):
    global client_socket

    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        for i in range(10):
            client_socket.sendto(f"Punching hole #{i+1}".encode(), dest_addr)

        # Start a separate thread to receive messages from the destination client
        threading.Thread(target=receive_messages).start()
    except socket.error as e:
        print("Error while punching hole:", e)


def receive_messages():
    global client_socket

    while True:
        try:
            data, addr = client_socket.recvfrom(1024)
            print(f"Received from {addr}: {data.decode()}")
        except socket.error as e:
            print("Error while receiving messages:", e)


if __name__ == "__main__":
    local_external_addr = get_local_external_addr()
    if local_external_addr:
        print("Local external address:", local_external_addr)
        print("Client id:", local_external_addr[0])

        register_with_rendezvous(local_external_addr)

        destination_external_addr = request_destination_address()
        if destination_external_addr:
            print("Destination external address:", destination_external_addr)

            print("Starting hole punching...")
            punch_hole((destination_external_addr, 9000))

            while True:
                message = input("Enter a message to send: ")
                client_socket.sendto(message.encode(), (destination_external_addr, 9000))
