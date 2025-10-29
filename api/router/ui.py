from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["ui"])

@router.get("/room-chat", response_class=HTMLResponse)
def room_chat():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>Chat Room – WebSocket Test</title>
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <style>
    :root { font-family: system-ui, Arial, sans-serif; }
    body { margin: 0; padding: 24px; background: #0b1220; color: #e6eefc; }
    .wrap { max-width: 900px; margin: 0 auto; }
    h1 { margin: 0 0 16px; font-size: 22px; }
    .row { display: flex; gap: 12px; margin-bottom: 12px; flex-wrap: wrap; }
    input, button, textarea {
      background: #101A33; color: #e6eefc; border: 1px solid #2b3a62; border-radius: 8px;
      padding: 10px 12px; font-size: 14px;
    }
    input, button { height: 40px; }
    input[type="number"] { width: 120px; }
    button { cursor: pointer; }
    button.primary { background: #2b6ef3; border-color: #2b6ef3; }
    button.danger { background: #e03131; border-color: #e03131; }
    #log {
      height: 360px; overflow: auto; background: #0f1a32; border: 1px solid #2b3a62;
      border-radius: 8px; padding: 12px; line-height: 1.45; white-space: pre-wrap;
    }
    .msg { margin: 0; }
    .sys { color: #9fb0d8; }
    .you { color: #9ae6b4; }
    .bot { color: #f7c948; }
    .footer { opacity: .7; margin-top: 10px; font-size: 12px; }
  </style>
</head>
<body>
  <div class="wrap">
    <h1>Chat Room – WebSocket Tester</h1>

    <div class="row">
      <label>Room ID:
        <input id="roomId" type="number" placeholder="e.g. 1" />
      </label>
      <label>Username:
        <input id="username" type="text" placeholder="e.g. johndoe" />
      </label>
      <button id="connectBtn" class="primary">Connect</button>
      <button id="disconnectBtn" class="danger" disabled>Disconnect</button>
    </div>

    <div id="log" aria-live="polite"></div>

    <div class="row">
      <input id="message" type="text" placeholder="Type a message and press Enter…" style="flex:1" />
      <button id="sendBtn">Send</button>
    </div>

    <div class="footer">This page connects to <code>/ws/chat/{room_id}/{username}</code>. It auto-selects <code>wss://</code> on HTTPS.</div>
  </div>

  <script>
    const roomInput = document.getElementById('roomId');
    const userInput = document.getElementById('username');
    const connectBtn = document.getElementById('connectBtn');
    const disconnectBtn = document.getElementById('disconnectBtn');
    const logEl = document.getElementById('log');
    const msgInput = document.getElementById('message');
    const sendBtn = document.getElementById('sendBtn');

    let ws = null;

    function log(line, cls = 'sys') {
      const p = document.createElement('p');
      p.className = `msg ${cls}`;
      p.textContent = line;
      logEl.appendChild(p);
      logEl.scrollTop = logEl.scrollHeight;
    }

    function getWsUrl(roomId, username) {
      const proto = location.protocol === 'https:' ? 'wss' : 'ws';
      return `${proto}://${location.host}/ws/chat/${roomId}/${username}`;
    }

    connectBtn.addEventListener('click', () => {
      const roomId = roomInput.value.trim();
      const username = userInput.value.trim();
      if (!roomId || !username) { alert('Please enter Room ID and Username'); return; }
      const url = getWsUrl(roomId, username);

      ws = new WebSocket(url);
      log(`Connecting to ${url} ...`);

      ws.onopen = () => {
        log('✔ Connected', 'sys');
        connectBtn.disabled = true;
        disconnectBtn.disabled = false;
        msgInput.focus();
      };

      ws.onmessage = (evt) => {
        log(`Bot: ${evt.data}`, 'bot');
      };

      ws.onclose = () => {
        log('✖ Disconnected', 'sys');
        connectBtn.disabled = false;
        disconnectBtn.disabled = true;
      };

      ws.onerror = (e) => {
        log('⚠ WebSocket error (see console)', 'sys');
        console.error(e);
      };
    });

    disconnectBtn.addEventListener('click', () => {
      if (ws && ws.readyState === WebSocket.OPEN) ws.close();
    });

    function sendMsg() {
      const text = msgInput.value.trim();
      if (!text) return;
      if (!ws || ws.readyState !== WebSocket.OPEN) {
        alert('WebSocket is not connected.');
        return;
      }
      ws.send(text);
      log(`You: ${text}`, 'you');
      msgInput.value = '';
    }

    sendBtn.addEventListener('click', sendMsg);
    msgInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') sendMsg();
    });
  </script>
</body>
</html>
    """
