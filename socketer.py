import socket
import argparse
import os
import random
import time
from chunker import chunk_file_with_checksum

def send_chunks_to_server(host, port, chunks):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        for chunk in chunks:
            s.sendall(len(chunk).to_bytes(4, 'big'))  # Prefix chunk size
            s.sendall(chunk)                          # Send chunk
        time.sleep(0.1)  # Let server finish reading
        print(f"✅ All {len(chunks)} chunks sent to {host}:{port}")

def main():
    parser = argparse.ArgumentParser(description="Send chunked packets to a socket server.")
    parser.add_argument("--input", type=str, required=True, help="Path to the input file")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Destination host")
    parser.add_argument("--port", type=int, default=9000, help="Destination port")
    parser.add_argument("--chunk-size", type=int, default=1024, help="Chunk size")
    parser.add_argument("--shuffle", action="store_true", help="Shuffle chunks before sending")
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print("❌ Input file does not exist.")
        return

    with open(args.input, "rb") as f:
        file_data = f.read()

    chunks = chunk_file_with_checksum(file_data, chunk_size=args.chunk_size)

    if args.shuffle:
        print("🔀 Shuffling chunks before sending...")
        random.shuffle(chunks)

    send_chunks_to_server(args.host, args.port, chunks)

if __name__ == "__main__":
    main()

