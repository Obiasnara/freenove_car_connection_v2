import json
import asyncio
import cv2
from websockets.sync.client import connect
from aiortc import VideoStreamTrack, RTCPeerConnection, RTCSessionDescription, RTCIceCandidate, RTCConfiguration, RTCIceServer

ld = False
rd = False
peer_connection = RTCPeerConnection(configuration=RTCConfiguration(
    iceServers=[RTCIceServer(
        urls=['stun:157.245.38.231:3478'])]))


async def send_answer(answer):
    await websocket.send(answer)

async def handle_offer(offer):
    global ld, rd
    if ld and rd:
        websocket.send(json.dumps({"sdp": peer_connection.localDescription.sdp, "type": peer_connection.localDescription.type}))
        return
    sdp_offer = RTCSessionDescription(sdp=offer["sdp"], type="offer")
    await peer_connection.setRemoteDescription(sdp_offer)
    answer = await peer_connection.createAnswer()
    await peer_connection.setLocalDescription(answer)

    ld = True
    rd = True
    websocket.send(json.dumps({"sdp": answer.sdp, "type": answer.type}))
    print("Sent answer")

async def on_ice_candidate(candidate):
    if not rd or not ld:
        return
    await peer_connection.addIceCandidate(RTCIceCandidate(candidate))
    await websocket.send(json.dumps({"iceCandidate": candidate}))

@peer_connection.on("track")
def on_track(track):
    print("Received track")

@peer_connection.on("iceconnectionstatechange")
def on_ice_connection_state_change():
    print("ICE connection state is", peer_connection.iceConnectionState)

@peer_connection.on("icegatheringstatechange")
def on_ice_gathering_state_change():
    print("ICE gathering state is", peer_connection.iceGatheringState)

@peer_connection.on("signalingstatechange")
def on_signaling_state_change():
    print("Signaling state is", peer_connection.signalingState)

@peer_connection.on("icecandidate")
async def on_ice_candidate(candidate):
    print("Received ice candidate")
    await websocket.send(json.dumps({"iceCandidate": candidate}))

@peer_connection.on("datachannel")
def on_datachannel(channel):
    print("Received data channel")

@peer_connection.on("connectionstatechange")
def on_connection_state_change():
    print("Connection state is", peer_connection.connectionState)

@peer_connection.on("negotiationneeded")
def on_negotiation_needed():
    print("Negotiation needed")

 


# Define a custom video track class
class OpenCVVideoStreamTrack(VideoStreamTrack):
    def __init__(self, video_capture):
        super().__init__()
        self.video_capture = video_capture

    async def recv(self):
        frame = self.video_capture.read()[1]
        return frame, self.time # Return frame and timestamp

async def main():
    global websocket
    with connect("ws://157.245.38.231:8000") as websocket:  # Use async context manager
        # Create video stream
        video_stream = cv2.VideoCapture(0)
        # Create a video track from the video stream
        video_track = OpenCVVideoStreamTrack(video_stream)
        # Add video track to peer connection
        peer_connection.addTrack(video_track)
        # Start gathering ICE candidates
        await peer_connection.gatherCandidates()
        
        while True:
                message = websocket.recv()
                print("Received message")
                data = json.loads(message)
                print(data["type"])
                if "type" in data and data["type"] == "offer":
                    await handle_offer(data)
                elif "iceCandidate" in data and data["iceCandidate"]:
                    await on_ice_candidate(data["iceCandidate"])


asyncio.run(main())
