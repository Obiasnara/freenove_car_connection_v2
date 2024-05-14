const iceConfiguration = {
    iceServers: [
      {
        urls: "stun:127.0.0.1:3478",
      },
    ],
  };
  ld = false;
  rd = false;

  const peerConnection = new RTCPeerConnection(iceConfiguration);
  // Establish WebSocket connection
  const ws = new WebSocket("ws://127.0.0.1:8000");
  console.log(ws.readyState);
  // Function to send data to Peer 2 via WebSocket
  function sendToPeer2(data) {
    // Send data when WebSocket connection is open
    ws.send(JSON.stringify(data));
  }

  ws.addEventListener("message", function (event) {
    // Parse the incoming message
    const data = JSON.parse(event.data);
    // Check if the message is an SDP answer
    if (data.type === "answer" && !rd) {
      console.log("Received SDP answer");
      // Extract the SDP answer
      const answer = data;
      // Set the SDP answer as the remote description
      peerConnection.setRemoteDescription(answer);
      rd = true;
      // Test that the connection is working by sending a dummy message
    }
    // Check if the message is an ICE candidate
    if (data.iceCandidate && rd) {
      // Extract the ICE candidate
      const candidate = new RTCIceCandidate(data.iceCandidate);
      // Add the ICE candidate to the peer connection
      peerConnection.addIceCandidate(candidate);
      console.log("ICE candidate added");
      console.log(ws.readyState);
    }
  });
  // Event listener for ICE candidates
  peerConnection.addEventListener("icecandidate", (event) => {
    if (!rd || !ld) {
            return;
          }
    if (event.candidate) {
      // Send ICE candidate to Peer 2 via signaling server
      sendToPeer2({ iceCandidate: event });

      const iceCandidate = new RTCIceCandidate(event.candidate);
      peerConnection.addIceCandidate(iceCandidate);
      console.log(peerConnection.connectionState )
      // Send ICE candidate to Peer 2 via WebSocket
      ws.send(JSON.stringify({ iceCandidate: event.candidate }));
      console.log("ICE candidate sent to Peer 2");
      
    }
  });
  // Function to send SDP offer to Peer 2
  function sendOffer(offer) {
    // Send offer to Peer 2 via WebSocket
    sendToPeer2(offer);
  }
  

  const constraints = { audio: true, video: true };
  const selfVideo = document.querySelector("video.selfview");
  const remoteVideo = document.querySelector("video.remoteview");

  async function start() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia(constraints);
      for (const track of stream.getTracks()) {
        peerConnection.addTrack(track, stream);
        console.log("Added local video track");
      }
      // Add the current video to the HTML video element
      selfVideo.srcObject = stream;
      
    } catch (err) {
      console.error(err);
    }

    // Create and send SDP offer to Peer 2
    // Send a dummy offer to trigger ICE candidate gathering
    peerConnection
      .createOffer()
      .then((offer) => {
        peerConnection.setLocalDescription(offer);
        ld = true;
        console.log("Local description set");
        // Send offer to Peer 2
        sendOffer(offer);
      })
      .catch((error) => {
        console.error("Error creating offer:", error);
      });
  }

  peerConnection.ontrack = ({ track, streams }) => {
    // Check if the track is a video track
    if (track.kind === "video") {
      // Get the remote video element
      const remoteVideo = document.querySelector("video.remoteview");
      // Check if the remote video element already has a srcObject
      if (!remoteVideo.srcObject) {
        console.log("Received remote video track");
        // Assign the stream containing the received track to the remote video element
        remoteVideo.srcObject = streams[0];
      }
    }
  };

  