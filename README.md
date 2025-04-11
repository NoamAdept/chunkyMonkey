
# chunkyMonkey: A Real-Time Packet Chunker & Reassembler

This project demonstrates how to:
- Compress and chunk large files
- Send them over a TCP socket in randomized packet order
- Reassemble them **in real-time** on the receiving end
- Verify integrity using SHA-256 checksums

---

## 🚀 Features

- ✅ Custom chunking with compression
- ✅ SHA-256 integrity checks
- ✅ Out-of-order delivery support
- ✅ Socket-based real-time transmission
- ✅ CLI tools for both sender and receiver

---

## 📁 Project Structure

```bash
.
├── chunker.py     # Main tool: chunker + reassembler + socket server
├── socketer.py     # TCP client to send chunks to the server
```

---

## 🛠️ Installation

```bash
git clone https://github.com/NoamAdept/packet-chunker-demo.git
cd packet-chunker-demo
python3 -m venv venv
source venv/bin/activate
```

---

## 🖥️ How to Use

### 🛰️ Start the Server
This receives chunked packets and reassembles them:

```bash
python chunker.py --serve --output received_file.txt
```

- Listens on port `9000` by default
- Outputs the reconstructed file to `received_file.txt`

---

### 📤 Send a File from the Client

In another terminal:

```bash
python socketer.py --input myfile.txt --shuffle
```

Optional flags:
- `--host 192.168.1.5` — send to a remote server
- `--port 9999` — custom port
- `--chunk-size 512` — set chunk size

---

## 📸 Demo Walkthrough

1. Create or pick a file (`myfile.txt`)
2. Open two terminals:
   - **Terminal 1 (server):** `python packet_chunker_demo.py --serve --output out.txt`
   - **Terminal 2 (client):** `python socket_chunk_client.py --input myfile.txt --shuffle`
3. Watch chunk logs as they’re received.
4. Verify the output:
   ```bash
   diff myfile.txt out.txt
   ```

---

## 🧪 Example Output

```
📡 Listening for packets on port 9000...
🔌 Connected by ('127.0.0.1', 57321)
📥 Received chunk #5 (228 bytes)
📥 Received chunk #2 (228 bytes)
...
✅ File reassembled and saved to received_file.txt
```

---

## 🤓 How It Works: Chunk Structure Explained
Each chunk includes metadata and a slice of the compressed file to ensure reliable and verifiable reconstruction. The sequence number ensures chunks are reassembled in the correct order, the total count signals when the file is complete, and the SHA-256 checksum guarantees that the final reassembled data matches the original compressed stream — even if chunks arrive out of order.

┌────────────┬──────────────┬────────────┬─────────────┬─────────────────────┐
│ Sequence # │ Total Chunks │ Data Length│   Data       │ SHA-256 Checksum   │
│  (4 bytes) │   (4 bytes)  │  (4 bytes) │ (variable)  │  (32 bytes)         │
└────────────┴──────────────┴────────────┴─────────────┴─────────────────────┘
This layout ensures every chunk is self-describing, enabling the receiver to safely reorder, verify, and decompress the original file from independent parts.

---

## 🧠 Ideas for Expansion

- 🌐 Web-based live chunk visualizer
- 📂 Chunk streaming over UDP
- 💬 Interactive progress bars or logs
- 🔐 Add encryption


