document.addEventListener("DOMContentLoaded", () => {
  const chatHistory = document.getElementById("chat-history");
  const userInput = document.getElementById("user-input");
  const sendBtn = document.getElementById("send-btn");
  const experimentList = document.getElementById("experiment-list");

  // Tabs
  const tabs = document.querySelectorAll(".tab");
  const tabContents = document.querySelectorAll(".tab-content");

  tabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      tabs.forEach((t) => t.classList.remove("active"));
      tabContents.forEach((c) => c.classList.add("hidden"));

      tab.classList.add("active");
      const target = tab.getAttribute("data-target");
      document.getElementById(target).classList.remove("hidden");
    });
  });

  // Chat functionality
  function addMessage(text, type) {
    const msgDiv = document.createElement("div");
    msgDiv.classList.add("message", type);

    const contentDiv = document.createElement("div");
    contentDiv.classList.add("message-content");
    contentDiv.innerText = text; // Use innerText for safety

    msgDiv.appendChild(contentDiv);
    chatHistory.appendChild(msgDiv);
    chatHistory.scrollTop = chatHistory.scrollHeight;
  }

  async function sendMessage() {
    const text = userInput.value.trim();
    if (!text) return;

    addMessage(text, "user");
    userInput.value = "";
    userInput.disabled = true;

    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message: text }),
      });

      const data = await response.json();

      if (data.error) {
        addMessage(`Error: ${data.error}`, "system");
      } else {
        addMessage(data.response, "system");

        // If there was a tool call, we could display it nicely
        // For now, it's appended to the response text in app.py
      }
    } catch (error) {
      addMessage(`Network Error: ${error.message}`, "system");
    } finally {
      userInput.disabled = false;
      userInput.focus();
    }
  }

  sendBtn.addEventListener("click", sendMessage);
  userInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });

  // Load Experiments
  async function loadExperiments() {
    try {
      const response = await fetch("/api/experiments");
      const experiments = await response.json();

      experimentList.innerHTML = "";
      experiments.forEach((exp) => {
        const li = document.createElement("li");
        li.innerText = `${exp.name} (${exp.status})`;
        experimentList.appendChild(li);
      });
    } catch (error) {
      experimentList.innerHTML = "<li>Error loading experiments</li>";
    }
  }

  loadExperiments();
});
