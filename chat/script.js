let currentUser = null;
const messagesDiv = document.getElementById("messages");
const header = document.getElementById("chatHeader");

function selectUser(user) {
  currentUser = user;
  header.innerText = "Chat with " + user;
  messagesDiv.innerHTML = ""; // clear messages
}

function sendMessage() {
  if (!currentUser) {
    alert("Select a user first!");
    return;
  }
  const input = document.getElementById("msgInput");
  if (input.value.trim() === "") return;

  const time = new Date().toLocaleTimeString([], {hour: '2-digit', minute: '2-digit'});

  // create sent message
  const sent = document.createElement("div");
  sent.className = "msg sent";
  sent.innerHTML = input.value + `<span class="time">${time}</span>`;
  messagesDiv.appendChild(sent);

  // auto reply (demo)
  setTimeout(() => {
    const reply = document.createElement("div");
    reply.className = "msg received";
    reply.innerHTML = "Hi! <span class='time'>" + time + "</span>";
    messagesDiv.appendChild(reply);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
  }, 800);

  messagesDiv.scrollTop = messagesDiv.scrollHeight;
  input.value = "";
}