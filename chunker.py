import zlib
import hashlib
import random
import argparse
import os
import socket
import threading

# =============================
# CHUNKER
# =============================
def chunk_file_with_checksum(file_bytes, chunk_size=1024):
    compressed = zlib.compress(file_bytes)
    file_checksum = hashlib.sha256(compressed).digest()
    total_chunks = (len(compressed) + chunk_size - 1) // chunk_size
    chunks = []

    for i in range(total_chunks):
        start = i * chunk_size
        end = start + chunk_size
        data = compressed[start:end]
        header = (
            i.to_bytes(4, 'big') +
            total_chunks.to_bytes(4, 'big') +
            len(data).to_bytes(4, 'big')
        )
        chunks.append(header + data + file_checksum)
    return chunks

# =============================
# REASSEMBLER
# =============================
def reassemble_chunks_with_checksum(chunks):
    buffer = {}
    total_chunks = None
    file_checksum = None

    for chunk in chunks:
        seq_num = int.from_bytes(chunk[0:4], 'big')
        total_chunks = int.from_bytes(chunk[4:8], 'big') if total_chunks is None else total_chunks
        data_len = int.from_bytes(chunk[8:12], 'big')
        data = chunk[12:12 + data_len]
        checksum = chunk[12 + data_len:12 + data_len + 32]
        file_checksum = checksum if file_checksum is None else file_checksum
        buffer[seq_num] = data

    if len(buffer) < total_chunks:
        raise ValueError("Missing chunks, cannot reassemble.")

    compressed = b''.join(buffer[i] for i in range(total_chunks))
    computed_checksum = hashlib.sha256(compressed).digest()
    if computed_checksum != file_checksum:
        raise ValueError("Checksum mismatch! File corrupted.")
    return zlib.decompress(compressed)

# =============================
# SOCKET SERVER
# =============================
def recv_exact(conn, n):
    data = b''
    while len(data) < n:
        packet = conn.recv(n - len(data))
        if not packet:
            raise ConnectionError("Incomplete chunk received.")
        data += packet
    return data

def start_socket_server(port=9000, output_path="received_output.bin"):
    print(f"📡 Listening for packets on port {port}...")
    buffer = []

    def handle_client(conn):
        try:
            while True:
                try:
                    length_prefix = recv_exact(conn, 4)
                    chunk_size = int.from_bytes(length_prefix, 'big')
                    chunk = recv_exact(conn, chunk_size)
                    buffer.append(chunk)
                    print(f"📥 Received chunk #{int.from_bytes(chunk[0:4], 'big')} ({len(chunk)} bytes)")
                except ConnectionError:
                    print("📴 Connection closed cleanly.")
                    break
        finally:
            conn.close()
            try:
                reassembled = reassemble_chunks_with_checksum(buffer)
                with open(output_path, 'wb') as f:
                    f.write(reassembled)
                print(f"✅ File reassembled and saved to {output_path}")
            except Exception as e:
                print(f"❌ Failed to reassemble: {e}")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("0.0.0.0", port))
        s.listen(1)
        while True:
            conn, addr = s.accept()
            print(f"🔌 Connected by {addr}")
            threading.Thread(target=handle_client, args=(conn,)).start()

# =============================
# CLI
# =============================
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str)
    parser.add_argument("--output", type=str)
    parser.add_argument("--chunk-size", type=int, default=1024)
    parser.add_argument("--serve", action="store_true")
    args = parser.parse_args()

    if args.serve:
        start_socket_server(output_path=args.output or "received_output.bin")
        return

    if not args.input or not os.path.exists(args.input):
        print("❌ Please provide a valid input file path with --input")
        return

    with open(args.input, "rb") as f:
        file_data = f.read()

    print(f"📦 Chunking '{args.input}' ({len(file_data)} bytes)...")
    chunks = chunk_file_with_checksum(file_data, chunk_size=args.chunk_size)
    random.shuffle(chunks)
    print(f"🔄 {len(chunks)} chunks generated and shuffled.")
    print("🔧 Reassembling...")
    reassembled = reassemble_chunks_with_checksum(chunks)

    if args.output:
        with open(args.output, "wb") as f:
            f.write(reassembled)
        print(f"✅ Reassembled file saved to '{args.output}'")
    else:
        print("✅ Reassembly complete (no output file specified)")

if __name__ == "__main__":
    main()

