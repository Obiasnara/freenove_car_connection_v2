import json
from aiortc import RTCIceCandidate, RTCPeerConnection, RTCSessionDescription, RTCConfiguration, RTCIceServer
import asyncio
from aiortc.contrib.media import MediaPlayer
import websockets



class WebSocketSignaling:
    def __init__(self, host, port):
        self._host = host
        self._port = port
        self._websocket = None
        self.pc = None
        self.ice_candidates = []
        self.local_ice_candidates = []
        print('WebsocketSignaling', self._host, self._port)

    async def connect(self):
        self._websocket = await websockets.connect("ws://" + str(self._host) + ":" + str(self._port)+"/socket")
        self.pc = RTCPeerConnection(configuration=RTCConfiguration(iceServers=[RTCIceServer(urls=['stun:157.245.38.231:3478'])]))
        # Create a video track from the video stream
        self.pc.addTransceiver('video', direction='sendonly')
        video_track = MediaPlayer("test.mp4", format="mp4")
        
        self.pc.addTrack(video_track.video)
        print('Video track added to peer connection')

        @self.pc.on("iceconnectionstatechange")
        async def on_iceconnectionstatechange():
            print("ICE connection state is", self.pc.iceConnectionState)
            if self.pc.iceConnectionState == "failed":
                await self.close()
            
        @self.pc.on("icecandidate")
        def on_icecandidate(candidate):
            print('ICE CANDIDATE INCOMING', candidate)
            if candidate:
                self.ice_candidates.append(candidate)
                self.pc.addIceCandidate(candidate)

        @self.pc.on('connectionstatechange')
        async def on_connectionstatechange():
            print("Connection state is %s" % self.pc.connectionState)
            if self.pc.connectionState == "failed":
                await self.pc.close()
                
    async def create_data_channel(self):
        self.data_channel = self.pc.createDataChannel("data")
        @self.data_channel.on("message")
        async def on_message(message):
            print('MESSAGE RECEIVED')
        @self.data_channel.on("open")
        async def on_open():
            print('DATA CHANNEL OPEN')
        @self.data_channel.on("close")
        async def on_close():
            print('DATA CHANNEL CLOSED')

    async def close(self):
        if self._websocket is not None and self._websocket.open is True:
            await self.send(None)
            await self._websocket.close()

    async def receive(self):
        try:
            data = await self._websocket.recv()
        except asyncio.IncompleteReadError:
            return
        ret = self.object_from_string(data)
        if ret == None:
            print("remote host says good bye!")

        return ret

    async def send(self, descr):
        data = self.object_to_string(descr)
        await self._websocket.send(data + '\n')
    
    async def create_offer(self):
        offer = await self.pc.createOffer()
        await self.pc.setLocalDescription(offer)
        print('Local description set')
        await self.send(offer)


    async def add_ice_candidate(self, candidate):
        await self.pc.addIceCandidate(candidate)
    
    async def send_ice_candidates(self):
        for candidate in self.ice_candidates:
            await self.send(candidate)

    def object_from_string(self,message_str):
        message = json.loads(message_str)
        message = message
        return message

    def object_to_string(self,obj):
        if isinstance(obj, RTCSessionDescription):
            message = {
                    'sdp': obj.sdp,
                    'type': obj.type
            }
        elif isinstance(obj, RTCIceCandidate):
            # print('SENDING ICE CANDIDATE', obj)
            pass
        else:
            message = {'type': 'bye'}
        return json.dumps(message, sort_keys=True)
    


async def connect_signaling_server():
    
    signaling = WebSocketSignaling('157.245.38.231', 8000)
    await signaling.connect()
    await signaling.create_data_channel()

    # Create an offer
    offer = await signaling.pc.createOffer()
    await signaling.pc.setLocalDescription(offer)
    print('Local description set')
    await signaling.send(offer)

    while True:
        message = await signaling.receive()
        print('MESSAGE RECEIVED')
        if message is None:
            print("Signaling server closed the connection.")
            break
        else:
            if 'type' in message and message['type'] == 'answer':
                
                answer = RTCSessionDescription(
                    type='answer',
                    sdp=message['sdp']
                )
                await signaling.pc.setRemoteDescription(answer)
                print('Remote description set')
            elif 'type' in message and message['type'] == 'iceCandidate':
                temp = message['iceCandidate']
                print('ICE CANDIDATE RECEIVED', message['iceCandidate']["candidate"])
                candidate = message['iceCandidate']["candidate"].split(' ')
                ip = candidate[4]
                port = candidate[5]
                protocol = candidate[7]
                priority = candidate[3]
                foundation = candidate[0].split(':')[1]
                component = candidate[1]
                type = candidate[7]
                # Create RTCIceCandidate object
                rtc_candidate = RTCIceCandidate(
                    ip=ip,
                    port=port,
                    protocol=protocol,
                    priority=priority,
                    foundation=foundation,
                    component=component,
                    type=type,
                    sdpMid=temp['sdpMid'],
                    sdpMLineIndex=temp['sdpMLineIndex']
                )
                await signaling.pc.addIceCandidate(rtc_candidate)
            elif 'type' in message and message['type'] == 'iceCandidates':
                print('ICE CANDIDATES RECEIVED')
                for ice_candidate in message['iceCandidates']:
                    candidate = ice_candidate["candidate"].split(' ')
                    ip = candidate[4]
                    port = candidate[5]
                    protocol = candidate[7]
                    priority = candidate[3]
                    foundation = candidate[0].split(':')[1]
                    component = candidate[1]
                    type = candidate[7]
                    # Create RTCIceCandidate object
                    rtc_candidate = RTCIceCandidate(
                        ip=ip,
                        port=port,
                        protocol=protocol,
                        priority=priority,
                        foundation=foundation,
                        component=component,
                        type=type,
                        sdpMid=ice_candidate['sdpMid'],
                        sdpMLineIndex=ice_candidate['sdpMLineIndex']
                    )
                    await signaling.pc.addIceCandidate(rtc_candidate)
                    print('ICE CANDIDATE ADDED')
            else:
                print('Unknown message:', message)
        # Handle the received message here
    await signaling.close()


async def main():
    await connect_signaling_server()

asyncio.run(main())
