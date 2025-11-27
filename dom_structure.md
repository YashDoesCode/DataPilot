# DOM Structure for DataPilot

This document outlines the planned HTML structure for the web interface.

## Layout Overview

```html
<body>
  <div id="app-container">
    <!-- Header Section -->
    <header id="main-header">
      <div class="logo-container">
        <img src="assets/logo.svg" alt="DataPilot Logo" class="logo" />
        <h1 class="app-title">DataPilot</h1>
      </div>
      <nav class="main-nav">
        <ul>
          <li><a href="#dashboard" class="active">Dashboard</a></li>
          <li><a href="#experiments">Experiments</a></li>
          <li><a href="#settings">Settings</a></li>
        </ul>
      </nav>
      <div class="user-profile">
        <span class="username">User</span>
        <img src="assets/avatar.png" alt="User Avatar" class="avatar" />
      </div>
    </header>

    <div id="main-layout">
      <!-- Sidebar Section -->
      <aside id="sidebar">
        <div class="sidebar-section">
          <h3>Recent Experiments</h3>
          <ul class="experiment-list">
            <!-- List items dynamically populated -->
            <li class="experiment-item">Experiment #101</li>
            <li class="experiment-item">Experiment #100</li>
          </ul>
        </div>
        <div class="sidebar-section">
          <h3>Quick Actions</h3>
          <button class="btn-primary" id="new-experiment-btn">
            New Experiment
          </button>
        </div>
      </aside>

      <!-- Main Content Area -->
      <main id="content-area">
        <!-- Chat Interface -->
        <section id="chat-interface">
          <div class="chat-history" id="chat-history">
            <!-- Chat messages go here -->
            <div class="message system">
              Welcome to DataPilot. How can I help you today?
            </div>
          </div>
          <div class="chat-input-area">
            <textarea
              id="user-input"
              placeholder="Describe your experiment goal..."
            ></textarea>
            <button id="send-btn">Send</button>
          </div>
        </section>

        <!-- Experiment Workspace (Split View) -->
        <section id="workspace">
          <div class="tabs">
            <button class="tab active" data-target="code-view">Code</button>
            <button class="tab" data-target="logs-view">Logs</button>
            <button class="tab" data-target="results-view">Results</button>
          </div>
          <div class="tab-content" id="code-view">
            <!-- Code Editor or Viewer -->
            <pre><code class="language-python"># Generated code appears here</code></pre>
          </div>
          <div class="tab-content hidden" id="logs-view">
            <!-- Execution Logs -->
          </div>
          <div class="tab-content hidden" id="results-view">
            <!-- Visualizations and Metrics -->
          </div>
        </section>
      </main>
    </div>

    <!-- Footer Section -->
    <footer id="main-footer">
      <div class="status-bar">
        <span class="status-item"
          >Status: <span class="status-indicator online"></span> Ready</span
        >
        <span class="status-item">Model: Gemini 2.5 Pro</span>
      </div>
    </footer>
  </div>
</body>
```
