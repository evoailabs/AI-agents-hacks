# !echo "OK" > index.html
# !python3 -m http.server 9090 > server.log 2>&1 &
# !curl -v http://127.0.0.1:9090/

import gradio as gr
import time
import sys

# 1. Configuration
TARGET_PORT = 9090  # The port your http.server is running on
DUMMY_PORT = 7860   # A temporary port for the Gradio "Ghost" app

def start_hijacked_tunnel():
    print(f"[*] Initializing tunnel hijacker...")
    print(f"[*] Target: Sharing local port {TARGET_PORT} via Gradio...")

    # Step 1: Locate Gradio's internal networking module
    try:
        from gradio import networking
    except ImportError:
        print("Error: Could not find gradio. Please run: pip install gradio")
        return

    # Step 2: Create a wrapper (Hijacker)
    # This intercepts the call to start the tunnel and changes the port to 9090
    real_setup_tunnel = networking.setup_tunnel

    def hijacked_setup_tunnel(*args, **kwargs):
        # We look for 'local_port' in arguments and force it to 9090
        if 'local_port' in kwargs:
            kwargs['local_port'] = TARGET_PORT
        elif len(args) >= 2:
            # If passed as positional argument (usually the 2nd one)
            args = list(args)
            args[1] = TARGET_PORT
        
        print(f"[*] HIJACK SUCCESS: Redirecting tunnel from {DUMMY_PORT} -> {TARGET_PORT}")
        return real_setup_tunnel(*args, **kwargs)

    # Step 3: Replace the real function with our hijacker
    networking.setup_tunnel = hijacked_setup_tunnel

    # Step 4: Launch a dummy interface
    # Gradio will handle all the API tokens, certificates, and binaries automatically.
    # It thinks it's sharing DUMMY_PORT, but our hijacker forces it to 9090.
    with gr.Blocks() as demo:
        gr.Markdown(f"### Tunnel Active\nForwarding public traffic to localhost:{TARGET_PORT}")

    print("[*] Requesting public URL from Gradio...")
    demo.launch(
        share=True, 
        server_port=DUMMY_PORT,
        prevent_thread_lock=False # Keep it running
    )

if __name__ == "__main__":
    # Reminder: Ensure your other server is running first!
    # Terminal 1: python3 -m http.server 9090
    try:
        start_hijacked_tunnel()
    except KeyboardInterrupt:
        print("\nStopping tunnel...")
        sys.exit(0)
