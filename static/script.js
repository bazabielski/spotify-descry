
document.addEventListener("DOMContentLoaded", function () {
    const loginButton = document.getElementById("loginButton");
    loginButton.addEventListener("click", function () {



        fetch("/login")
            .then(response => response.json())
            .then(data => {

                window.location.href = data.auth_url;
            });
    });
    const recommendedLink = document.getElementById('recommended-link');
    recommendedLink.addEventListener('click', function (event) {

        fetch("/login")
            .then(response => response.json())
            .then(data => {

                window.location.href = data.auth_url;
            });
    });
    const aiSearch = document.getElementById('ai-search');

    aiSearch.addEventListener('click', function (event) {

        window.location.href = '/ai';
    });
    const chatbox = document.querySelector('.chatbox');
    const chatboxContent = chatbox.querySelector('ul.chatbox');
    const userInputElement = document.getElementById('user-input');
    const sendButton = document.getElementById('send-btn');

    sendButton.addEventListener('click', function () {
        const userMessage = userInputElement.value;
        appendMessage('user', userMessage);
        userInputElement.value = '';


        fetch('/ai-search', {
            method: 'POST',
            body: JSON.stringify({ message: userMessage }),
            headers: {
                'Content-Type': 'application/json'
            }
        })
            .then(response => response.json())
            .then(data => {
                const botMessage = data.message;
                appendMessage('bot', botMessage);
            });
    });

    function appendMessage(sender, message) {
        const messageElement = document.createElement('li');
        messageElement.classList.add('chat', 'outgoing');
        messageElement.innerHTML = `<p>${sender}: ${message}</p>`;
        chatboxContent.appendChild(messageElement);
    }
});