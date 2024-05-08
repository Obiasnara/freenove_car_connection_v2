import asyncio
import websockets
import json
from aiortc import RTCPeerConnection, RTCIceCandidate, RTCSessionDescription, VideoStreamTrack
import cv2
import threading

# Create a peer connection
peer_connection = RTCPeerConnection()

# Function to send data to peer via WebSocket
async def send_to_peer(data):
    async with websockets.connect('ws://127.0.0.1:8000') as websocket:
        await websocket.send(json.dumps(data))

# Event listener for ICE candidates
async def on_ice_candidate(candidate):
    await send_to_peer({"iceCandidate": candidate})

# Add ICE candidate handler to peer connection
peer_connection.onicecandidate = on_ice_candidate

# Function to send SDP offer to peer
async def send_offer(offer):
    # Convert RTCSessionDescription to dictionary
    offer_dict = {"type": offer.type, "sdp": offer.sdp}
    # Send the offer as JSON to the peer
    await send_to_peer(json.dumps(offer_dict))

# Function to create a VideoStreamTrack from the frame
def create_video_track(frame):
    # Convert the frame to RGB format
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    # Resize the frame to 640x480
    rgb_frame = cv2.resize(rgb_frame, (640, 480))
    # Create the MediaStreamTrack object
    event_emitter = VideoStreamTrack()
    # Set the frame to the MediaStreamTrack object
    event_emitter.frame = rgb_frame
    # Return the MediaStreamTrack object
    return event_emitter

# Function to start streaming video
async def start():
    cap = cv2.VideoCapture(0)
    while True:
        # Read frame from the video capture object
        ret, frame = cap.read()
        if not ret:
            break
        
        # Create a VideoStreamTrack from the frame
        video_track = create_video_track(frame)

        # Add video track to peer connection
        peer_connection.addTrack(video_track)

        # Create SDP offer
        offer = await peer_connection.createOffer()
        await peer_connection.setLocalDescription(offer)

        # Send SDP offer to peer
        await send_offer(peer_connection.localDescription)

# Function to handle incoming messages from WebSocket
async def handle_message(message):
    print(f"Received message: {message}")
    try:
        data = json.parse(message)
        if isinstance(data, dict) and 'type' in data:
            if data['type'] == 'answer':
                print("Received SDP answer")
                # Convert the received session description dictionary to RTCSessionDescription
                answer = RTCSessionDescription(sdp=data['sdp'], type='answer')
                await peer_connection.setRemoteDescription(answer)
            elif data['type'] == 'iceCandidate':
                print("Received ICE candidate")
                candidate = RTCIceCandidate(candidate=data['candidate'])
                await peer_connection.addIceCandidate(candidate)
        else:
            print("Invalid message format or missing 'type' field.")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")

# WebSocket handler
async def websocket_handler(uri):
    async with websockets.connect(uri) as websocket:
        async for message in websocket:
            print(f"Received message: {message}")
            await handle_message(message)

def start_video_stream():
    asyncio.run(start())

def start_websocket(uri):
    asyncio.run(websocket_handler(uri))

def main():
    # Start streaming video 
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    video_thread = threading.Thread(target=start_video_stream)
    video_thread.start()

    # Connect to WebSocket server
    print("Connecting to WebSocket server")
    asyncio.run(start_websocket("ws://127.0.0.1:8000"))

if __name__ == "__main__":
    main()
