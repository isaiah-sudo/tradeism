"""
Local Browser Authentication Server for Day Trade Simulator.
Spins up a lightweight local HTTP server to handle Google Sign-In and Email/Password
via the official Firebase Web SDK, redirecting credentials back to the desktop application.
"""

import os
import sys
import json
import time
import socket
import threading
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Optional, Callable, Dict, Any

LOGIN_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Day Trade Simulator • Cloud Sign In</title>
  <style>
    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    body {
      background-color: #0e1117;
      color: #ffffff;
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 100vh;
      padding: 20px;
    }
    .auth-card {
      background: #161a25;
      border: 1px solid #2a2e39;
      border-radius: 12px;
      width: 100%;
      max-width: 440px;
      padding: 32px 28px;
      box-shadow: 0 16px 40px rgba(0, 0, 0, 0.6);
      text-align: center;
    }
    .badge {
      display: inline-block;
      font-size: 11px;
      font-weight: 700;
      color: #00e676;
      background: rgba(0, 230, 118, 0.12);
      border: 1px solid rgba(0, 230, 118, 0.3);
      border-radius: 20px;
      padding: 4px 12px;
      letter-spacing: 0.5px;
      margin-bottom: 12px;
    }
    h1 {
      font-size: 22px;
      font-weight: 800;
      margin-bottom: 6px;
      color: #ffffff;
    }
    p.subtitle {
      font-size: 13px;
      color: #848e9c;
      margin-bottom: 24px;
      line-height: 1.5;
    }
    .btn-google {
      width: 100%;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 12px;
      background: #ffffff;
      color: #1f1f1f;
      font-size: 14px;
      font-weight: 600;
      padding: 12px 16px;
      border-radius: 8px;
      border: none;
      cursor: pointer;
      transition: background 0.18s, transform 0.12s;
    }
    .btn-google:hover {
      background: #f1f3f4;
      transform: translateY(-1px);
    }
    .btn-google svg {
      width: 18px;
      height: 18px;
    }
    .divider {
      display: flex;
      align-items: center;
      text-align: center;
      margin: 22px 0;
      color: #4f5869;
      font-size: 12px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }
    .divider::before, .divider::after {
      content: '';
      flex: 1;
      border-bottom: 1px solid #2a2e39;
    }
    .divider::before { margin-right: 12px; }
    .divider::after { margin-left: 12px; }

    .tabs {
      display: flex;
      background: #0e1117;
      border-radius: 8px;
      padding: 3px;
      margin-bottom: 18px;
      border: 1px solid #2a2e39;
    }
    .tab-btn {
      flex: 1;
      background: transparent;
      border: none;
      color: #848e9c;
      font-size: 13px;
      font-weight: 600;
      padding: 8px 0;
      border-radius: 6px;
      cursor: pointer;
      transition: all 0.2s;
    }
    .tab-btn.active {
      background: #2962ff;
      color: #ffffff;
    }

    .form-group {
      text-align: left;
      margin-bottom: 14px;
    }
    label {
      display: block;
      font-size: 12px;
      font-weight: 600;
      color: #c5c8d1;
      margin-bottom: 6px;
    }
    input {
      width: 100%;
      background: #0e1117;
      border: 1px solid #2a2e39;
      border-radius: 6px;
      padding: 10px 12px;
      font-size: 14px;
      color: #ffffff;
      outline: none;
      transition: border-color 0.2s;
    }
    input:focus {
      border-color: #2962ff;
    }

    .btn-submit {
      width: 100%;
      background: #00c853;
      color: #ffffff;
      border: none;
      font-size: 14px;
      font-weight: 700;
      padding: 12px;
      border-radius: 8px;
      cursor: pointer;
      margin-top: 8px;
      transition: background 0.2s, transform 0.1s;
    }
    .btn-submit:hover {
      background: #00e676;
      color: #000000;
      transform: translateY(-1px);
    }
    .btn-submit:disabled {
      background: #2a2e39;
      color: #848e9c;
      cursor: not-allowed;
      transform: none;
    }

    .status-msg {
      margin-top: 14px;
      font-size: 13px;
      line-height: 1.4;
      display: none;
    }
    .status-msg.error {
      display: block;
      color: #ff5252;
      background: rgba(255, 82, 82, 0.1);
      border: 1px solid rgba(255, 82, 82, 0.25);
      border-radius: 6px;
      padding: 8px 12px;
    }
    .status-msg.info {
      display: block;
      color: #29b6f6;
    }

    .success-card {
      display: none;
      text-align: center;
      padding: 10px 0;
    }
    .success-icon {
      font-size: 52px;
      margin-bottom: 12px;
    }
    .success-title {
      font-size: 20px;
      font-weight: 800;
      color: #00e676;
      margin-bottom: 8px;
    }
    .success-desc {
      font-size: 14px;
      color: #c5c8d1;
      line-height: 1.5;
      margin-bottom: 18px;
    }
    .btn-close-tab {
      background: #222631;
      color: #ffffff;
      border: 1px solid #2a2e39;
      font-size: 13px;
      font-weight: 600;
      padding: 10px 18px;
      border-radius: 6px;
      cursor: pointer;
    }
  </style>

  <!-- Firebase Web SDK Compat -->
  <script src="https://www.gstatic.com/firebasejs/10.13.0/firebase-app-compat.js"></script>
  <script src="https://www.gstatic.com/firebasejs/10.13.0/firebase-auth-compat.js"></script>
</head>
<body>

  <div class="auth-card" id="authBox">
    <div class="badge">DAY TRADE SIMULATOR</div>
    <h1>Trader Sign In</h1>
    <p class="subtitle">Sign in to sync your trader name, money vault, and shop items across devices.</p>

    <!-- Google Sign In Button -->
    <button type="button" class="btn-google" id="btnGoogle">
      <svg viewBox="0 0 18 18">
        <path fill="#4285F4" d="M17.64 9.2c0-.637-.057-1.251-.164-1.84H9v3.481h4.844c-.209 1.125-.843 2.078-1.796 2.717v2.258h2.908c1.702-1.567 2.684-3.874 2.684-6.616z"/>
        <path fill="#34A853" d="M9 18c2.43 0 4.467-.806 5.956-2.184l-2.908-2.258c-.806.54-1.837.86-3.048.86-2.344 0-4.328-1.584-5.036-3.711H.957v2.332A8.997 8.997 0 0 0 9 18z"/>
        <path fill="#FBBC05" d="M3.964 10.707c-.18-.54-.282-1.117-.282-1.707s.102-1.167.282-1.707V4.961H.957A8.996 8.996 0 0 0 0 9c0 1.452.348 2.827.957 4.039l3.007-2.332z"/>
        <path fill="#EA4335" d="M9 3.58c1.321 0 2.508.454 3.44 1.345l2.582-2.58C13.463.891 11.426 0 9 0A8.997 8.997 0 0 0 .957 4.961L3.964 7.293C4.672 5.166 6.656 3.58 9 3.58z"/>
      </svg>
      Sign in with Google
    </button>

    <div class="divider">or with email</div>

    <!-- Sign In / Sign Up Tabs -->
    <div class="tabs">
      <button type="button" class="tab-btn active" id="tabSignIn">Sign In</button>
      <button type="button" class="tab-btn" id="tabSignUp">Create Account</button>
    </div>

    <!-- Form -->
    <form id="authForm">
      <div class="form-group" id="groupName" style="display: none;">
        <label for="inputName">Trader Nickname</label>
        <input type="text" id="inputName" placeholder="e.g. WallStreetBull" autocomplete="nickname">
      </div>

      <div class="form-group">
        <label for="inputEmail">Email Address</label>
        <input type="email" id="inputEmail" placeholder="trader@example.com" required autocomplete="email">
      </div>

      <div class="form-group">
        <label for="inputPassword">Password</label>
        <input type="password" id="inputPassword" placeholder="••••••••" required autocomplete="current-password">
      </div>

      <button type="submit" class="btn-submit" id="btnSubmit">Sign In</button>
    </form>

    <div id="statusMsg" class="status-msg"></div>
  </div>

  <!-- Success Card -->
  <div class="auth-card" id="successBox" style="display: none;">
    <div class="success-icon">🎉</div>
    <div class="success-title">Successfully Signed In!</div>
    <div class="success-desc" id="successDesc">
      Welcome back! All your progress (name, vault money, and shop items) is securely synced with Day Trade Simulator.
    </div>
    <p style="font-size: 13px; color: #848e9c; margin-bottom: 20px;">
      You can now close this browser tab and return to the game.
    </p>
    <button type="button" class="btn-close-tab" onclick="window.close()">Close Window</button>
  </div>

  <script>
    const firebaseConfig = {
      apiKey: "{{API_KEY}}",
      authDomain: "{{AUTH_DOMAIN}}",
      projectId: "{{PROJECT_ID}}"
    };

    let isFirebaseReady = false;
    let auth = null;

    try {
      if (typeof firebase !== 'undefined' && firebase.initializeApp) {
        firebase.initializeApp(firebaseConfig);
        auth = firebase.auth();
        isFirebaseReady = true;
      }
    } catch (e) {
      console.error("Firebase init error:", e);
    }

    const tabSignIn = document.getElementById('tabSignIn');
    const tabSignUp = document.getElementById('tabSignUp');
    const groupName = document.getElementById('groupName');
    const btnSubmit = document.getElementById('btnSubmit');
    const authForm = document.getElementById('authForm');
    const btnGoogle = document.getElementById('btnGoogle');
    const statusMsg = document.getElementById('statusMsg');
    const authBox = document.getElementById('authBox');
    const successBox = document.getElementById('successBox');
    const successDesc = document.getElementById('successDesc');

    let mode = 'signin';

    tabSignIn.onclick = () => {
      mode = 'signin';
      tabSignIn.classList.add('active');
      tabSignUp.classList.remove('active');
      groupName.style.display = 'none';
      btnSubmit.innerText = 'Sign In';
      clearStatus();
    };

    tabSignUp.onclick = () => {
      mode = 'signup';
      tabSignUp.classList.add('active');
      tabSignIn.classList.remove('active');
      groupName.style.display = 'block';
      btnSubmit.innerText = 'Create Account';
      clearStatus();
    };

    function showStatus(text, type='error') {
      statusMsg.className = 'status-msg ' + type;
      statusMsg.innerText = text;
      statusMsg.style.display = 'block';
    }

    function clearStatus() {
      statusMsg.style.display = 'none';
      statusMsg.innerText = '';
    }

    async function sendAuthToApp(authData) {
      showStatus("Connecting to Day Trade Simulator app...", "info");
      try {
        const resp = await fetch('/callback', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(authData)
        });
        const resJson = await resp.json();
        if (resJson.status === 'ok') {
          authBox.style.display = 'none';
          successBox.style.display = 'block';
          const name = authData.displayName || authData.email || 'Trader';
          successDesc.innerText = `Welcome, ${name}! Your profile progress (name, money, and shop items) is now saved and synced.`;
        } else {
          showStatus(resJson.error || "Failed to communicate with application.");
        }
      } catch (err) {
        showStatus("Could not reach Day Trade Simulator. Please verify the game is still running.");
      }
    }

    // Google Sign-In
    btnGoogle.onclick = async () => {
      clearStatus();
      if (!isFirebaseReady || !auth) {
        showStatus("Firebase client is not available. Please check network connection.");
        return;
      }
      btnGoogle.disabled = true;
      btnGoogle.innerText = "Connecting to Google...";

      try {
        const provider = new firebase.auth.GoogleAuthProvider();
        const result = await auth.signInWithPopup(provider);
        const user = result.user;
        const idToken = await user.getIdToken();
        await sendAuthToApp({
          uid: user.uid,
          email: user.email || '',
          displayName: user.displayName || '',
          idToken: idToken,
          refreshToken: user.refreshToken || ''
        });
      } catch (err) {
        console.error(err);
        let msg = err.message || "Google sign-in failed.";
        if (err.code === 'auth/popup-closed-by-user') {
          msg = "Sign-in popup was closed before completion.";
        }
        showStatus(msg);
      } finally {
        btnGoogle.disabled = false;
        btnGoogle.innerHTML = `
          <svg viewBox="0 0 18 18">
            <path fill="#4285F4" d="M17.64 9.2c0-.637-.057-1.251-.164-1.84H9v3.481h4.844c-.209 1.125-.843 2.078-1.796 2.717v2.258h2.908c1.702-1.567 2.684-3.874 2.684-6.616z"/>
            <path fill="#34A853" d="M9 18c2.43 0 4.467-.806 5.956-2.184l-2.908-2.258c-.806.54-1.837.86-3.048.86-2.344 0-4.328-1.584-5.036-3.711H.957v2.332A8.997 8.997 0 0 0 9 18z"/>
            <path fill="#FBBC05" d="M3.964 10.707c-.18-.54-.282-1.117-.282-1.707s.102-1.167.282-1.707V4.961H.957A8.996 8.996 0 0 0 0 9c0 1.452.348 2.827.957 4.039l3.007-2.332z"/>
            <path fill="#EA4335" d="M9 3.58c1.321 0 2.508.454 3.44 1.345l2.582-2.58C13.463.891 11.426 0 9 0A8.997 8.997 0 0 0 .957 4.961L3.964 7.293C4.672 5.166 6.656 3.58 9 3.58z"/>
          </svg>
          Sign in with Google`;
      }
    };

    // Email / Password Form
    authForm.onsubmit = async (e) => {
      e.preventDefault();
      clearStatus();
      if (!isFirebaseReady || !auth) {
        showStatus("Firebase client is not ready.");
        return;
      }

      const email = document.getElementById('inputEmail').value.trim();
      const password = document.getElementById('inputPassword').value;
      const nickname = document.getElementById('inputName').value.trim();

      if (!email || !password) return;

      btnSubmit.disabled = true;
      btnSubmit.innerText = mode === 'signin' ? 'Signing In...' : 'Creating Account...';

      try {
        let userCred;
        if (mode === 'signup') {
          userCred = await auth.createUserWithEmailAndPassword(email, password);
          if (nickname && userCred.user) {
            await userCred.user.updateProfile({ displayName: nickname });
          }
        } else {
          userCred = await auth.signInWithEmailAndPassword(email, password);
        }

        const user = userCred.user;
        const idToken = await user.getIdToken();
        await sendAuthToApp({
          uid: user.uid,
          email: user.email || '',
          displayName: nickname || user.displayName || '',
          idToken: idToken,
          refreshToken: user.refreshToken || ''
        });
      } catch (err) {
        console.error(err);
        let msg = err.message || "Authentication failed.";
        if (err.code === 'auth/invalid-credential' || err.code === 'auth/wrong-password') {
          msg = "Invalid email or password.";
        } else if (err.code === 'auth/user-not-found') {
          msg = "No account found with this email.";
        } else if (err.code === 'auth/email-already-in-use') {
          msg = "An account with this email already exists.";
        } else if (err.code === 'auth/weak-password') {
          msg = "Password should be at least 6 characters.";
        }
        showStatus(msg);
      } finally {
        btnSubmit.disabled = false;
        btnSubmit.innerText = mode === 'signin' ? 'Sign In' : 'Create Account';
      }
    };
  </script>
</body>
</html>
"""


class _AuthHTTPHandler(BaseHTTPRequestHandler):
    server: "AuthCallbackServer"

    def log_message(self, format, *args):
        # Suppress default noisy console logging
        pass

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path in ("/", "/index.html"):
            html = self.server.get_rendered_html()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(html.encode("utf-8"))))
            self.end_headers()
            self.wfile.write(html.encode("utf-8"))
        elif parsed.path == "/favicon.ico":
            self.send_response(204)
            self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/callback":
            length = int(self.headers.get("Content-Length", 0))
            body_bytes = self.rfile.read(length)
            try:
                data = json.loads(body_bytes.decode("utf-8"))
            except Exception:
                data = {}

            if data and data.get("uid"):
                self.server.auth_result = data
                resp_body = json.dumps({"status": "ok"}).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Content-Length", str(len(resp_body)))
                self.end_headers()
                self.wfile.write(resp_body)

                # Trigger success callback on host
                if self.server.on_success:
                    self.server.on_success(data)

                # Schedule server shutdown
                threading.Thread(target=self._delayed_shutdown, daemon=True).start()
            else:
                resp_body = json.dumps({"status": "error", "error": "Invalid auth payload"}).encode("utf-8")
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(resp_body)
        else:
            self.send_response(404)
            self.end_headers()

    def _delayed_shutdown(self):
        time.sleep(1.2)
        self.server.stop()


class AuthCallbackServer(HTTPServer):
    """
    Local HTTP server designed to receive Firebase OAuth & Email logins from the browser.
    """
    def __init__(self, api_key: str, project_id: str, auth_domain: str,
                 on_success: Optional[Callable[[Dict[str, Any]], None]] = None):
        super().__init__(("127.0.0.1", 0), _AuthHTTPHandler)
        self.api_key = api_key
        self.project_id = project_id
        self.auth_domain = auth_domain
        self.on_success = on_success
        self.auth_result: Optional[Dict[str, Any]] = None
        self._thread: Optional[threading.Thread] = None
        self._is_running = False

    def get_port(self) -> int:
        return self.server_address[1]

    def get_url(self) -> str:
        return f"http://127.0.0.1:{self.get_port()}"

    def get_rendered_html(self) -> str:
        return LOGIN_HTML_TEMPLATE.replace("{{API_KEY}}", self.api_key)\
                                  .replace("{{PROJECT_ID}}", self.project_id)\
                                  .replace("{{AUTH_DOMAIN}}", self.auth_domain)

    def start(self):
        """Starts the server listening in a daemon thread."""
        if self._is_running:
            return
        self._is_running = True
        self._thread = threading.Thread(target=self.serve_forever, daemon=True)
        self._thread.start()

    def stop(self):
        """Stops the server safely."""
        if not self._is_running:
            return
        self._is_running = False
        try:
            self.shutdown()
        except Exception:
            pass
