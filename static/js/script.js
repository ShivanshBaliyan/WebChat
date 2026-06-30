let socket;
let username = 'User';

function initializeWebSocket() {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  socket = new WebSocket(protocol + '//' + window.location.host + '/ws');

  socket.onopen = function (event) {
    console.log('WebSocket connection established.');
    document.getElementById('status').textContent = 'Connected';
    document.getElementById('status').className = 'status connected';
  };

  socket.onmessage = function (event) {
    const data = JSON.parse(event.data);
    const messagesContainer = document.getElementById('messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message ' + (data.isMe ? 'own' : 'other');
    
    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';
    bubble.textContent = data.data;
    
    messageDiv.appendChild(bubble);
    
    const info = document.createElement('div');
    info.className = 'message-info';
    info.textContent = data.username;
    messageDiv.appendChild(info);
    
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  };

  socket.onerror = function (event) {
    console.error('WebSocket error:', event);
    document.getElementById('status').textContent = 'Error';
    document.getElementById('status').className = 'status error';
  };

  socket.onclose = function (event) {
    console.log('WebSocket closed');
    document.getElementById('status').textContent = 'Disconnected';
    document.getElementById('status').className = 'status disconnected';
  };
}

function sendMessage() {
  const input = document.getElementById('message-input');
  const message = input.value.trim();
  
  if (message && socket && socket.readyState === WebSocket.OPEN) {
    const data = {
      message: message,
      username: username
    };
    socket.send(JSON.stringify(data));
    input.value = '';
    input.focus();
  }
}

function joinChat() {
  const usernameInput = document.getElementById('username-input');
  username = usernameInput.value.trim() || 'User';
  
  initializeWebSocket();
  
  document.getElementById('join-section').style.display = 'none';
  document.getElementById('chat-section').style.display = 'flex';
  document.getElementById('message-input').focus();
}
