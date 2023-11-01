document.addEventListener("DOMContentLoaded", function () {
    const userMessageInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');


    function sendMessage() {
        const userMessage = userMessageInput.value;
        if (userMessage) {
            fetch('/ai-search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message: userMessage })
            })
                .then(response => response.json())
                .then(data => {
                    const outgoingChat = document.createElement('li');
                    outgoingChat.classList.add('chat', 'outgoing');
                    outgoingChat.innerHTML = `<p>${userMessage}</p>`;
                    document.querySelector('.chatbox').appendChild(outgoingChat);

                    const botMessage = data.message;
                    const incomingChat = document.createElement('li');
                    incomingChat.classList.add('chat', 'incoming');
                    incomingChat.innerHTML = `<p>${botMessage}</p>`;
                    document.querySelector('.chatbox').appendChild(incomingChat);


                    userMessageInput.value = '';
                })
                .catch(error => {
                    console.error('Error:', error);
                });
        }
    }


    userMessageInput.addEventListener("keydown", function (event) {
        if (event.key === "Enter") {
            sendMessage();
        }
    });


    sendBtn.addEventListener('click', sendMessage);

    const chatContainer = document.querySelector(".chat-messages-container");

    chatContainer.addEventListener("scroll", function () {
        const isScrollable = chatContainer.scrollHeight > chatContainer.clientHeight;
        if (isScrollable) {
            chatContainer.style.overflowY = "scroll";
        } else {
            chatContainer.style.overflowY = "auto";
        }
    });
});