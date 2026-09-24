import os
import sys
import json
import time
import random
import threading
import urllib.request
import urllib.error
import ssl
from typing import Optional, Dict, Any, Tuple

class _Response:
    def __init__(self, status_code: int, text: str):
        self.status_code = status_code
        self.text = text

    def json(self) -> Dict[str, Any]:
        if not self.text:
            return {}
        try:
            return json.loads(self.text)
        except Exception:
            return {}

class _HttpClient:
    @staticmethod
    def _request(method: str, url: str, json_data: Optional[Dict[str, Any]] = None,
                 headers: Optional[Dict[str, str]] = None, timeout: float = 8.0) -> _Response:
        req_headers = {"User-Agent": "DayTradeSim/1.1", "Content-Type": "application/json"}
        if headers:
            req_headers.update(headers)
        body = json.dumps(json_data).encode("utf-8") if json_data is not None else None
        req = urllib.request.Request(url, data=body, headers=req_headers, method=method)
        ctx = ssl.create_default_context()
        try:
            with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
                return _Response(r.status, r.read().decode("utf-8", errors="replace"))
        except urllib.error.HTTPError as e:
            try:
                err_text = e.read().decode("utf-8", errors="replace")
            except Exception:
                err_text = ""
            return _Response(e.code, err_text)
        except Exception as e:
            return _Response(0, str(e))

    def get(self, url: str, headers: Optional[Dict[str, str]] = None, timeout: float = 8.0) -> _Response:
        return self._request("GET", url, headers=headers, timeout=timeout)

    def post(self, url: str, json: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None, timeout: float = 8.0) -> _Response:
        return self._request("POST", url, json_data=json, headers=headers, timeout=timeout)

    def patch(self, url: str, json: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None, timeout: float = 8.0) -> _Response:
        return self._request("PATCH", url, json_data=json, headers=headers, timeout=timeout)

    def delete(self, url: str, headers: Optional[Dict[str, str]] = None, timeout: float = 8.0) -> _Response:
        return self._request("DELETE", url, headers=headers, timeout=timeout)

http = _HttpClient()

def get_config_file() -> str:
    exe_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    local_cfg = os.path.join(exe_dir, "firebase_config.json")
    if os.path.exists(local_cfg):
        return local_cfg
    if hasattr(sys, '_MEIPASS'):
        bundle_cfg = os.path.join(sys._MEIPASS, "firebase_config.json")
        if os.path.exists(bundle_cfg):
            return bundle_cfg
    return local_cfg

CONFIG_FILE = get_config_file()

def python_to_firestore_value(val: Any) -> Dict[str, Any]:
    if isinstance(val, bool):
        return {"booleanValue": val}
    elif isinstance(val, int):
        return {"integerValue": str(val)}
    elif isinstance(val, float):
        return {"doubleValue": float(val)}
    elif isinstance(val, str):
        return {"stringValue": val}
    elif isinstance(val, dict):
        return {"mapValue": {"fields": {k: python_to_firestore_value(v) for k, v in val.items()}}}
    elif isinstance(val, list):
        return {"arrayValue": {"values": [python_to_firestore_value(v) for v in val]}}
    elif val is None:
        return {"nullValue": None}
    return {"stringValue": str(val)}

def firestore_value_to_python(val_dict: Dict[str, Any]) -> Any:
    if not isinstance(val_dict, dict):
        return val_dict
    if "stringValue" in val_dict:
        return val_dict["stringValue"]
    if "integerValue" in val_dict:
        return int(val_dict["integerValue"])
    if "doubleValue" in val_dict:
        return float(val_dict["doubleValue"])
    if "booleanValue" in val_dict:
        return bool(val_dict["booleanValue"])
    if "mapValue" in val_dict:
        fields = val_dict["mapValue"].get("fields", {})
        return {k: firestore_value_to_python(v) for k, v in fields.items()}
    if "arrayValue" in val_dict:
        values = val_dict["arrayValue"].get("values", [])
        return [firestore_value_to_python(v) for v in values]
    if "nullValue" in val_dict:
        return None
    return None

def firestore_doc_to_dict(doc_json: Dict[str, Any]) -> Dict[str, Any]:
    fields = doc_json.get("fields", {})
    return {k: firestore_value_to_python(v) for k, v in fields.items()}

def dict_to_firestore_doc(data: Dict[str, Any]) -> Dict[str, Any]:
    return {"fields": {k: python_to_firestore_value(v) for k, v in data.items()}}


class SimulatedOpponentBot:
    """Simulates a live opponent when playing in mock/demo mode or when testing offline."""
    BOT_NAMES = [
        "WallSt_Titan", "DiamondHands_99", "AlphaScalper", "BullishApe",
        "OptionsSlayer", "MomentumTrader", "YOLO_God", "QuantAlgo_X"
    ]

    def __init__(self, name: Optional[str] = None):
        self.name = name or random.choice(self.BOT_NAMES)
        self.equity = 25000.0
        self.pnl = 0.0
        self.pnl_pct = 0.0
        self.status = "playing"
        self._trend = random.choice([-1.0, 1.0]) * random.uniform(0.5, 1.5)

    def tick(self) -> Dict[str, Any]:
        """Simulate realistic equity volatility."""
        delta = random.gauss(self._trend * 15.0, 45.0)
        if random.random() < 0.06:
            # Random trade payoff / loss
            delta += random.choice([-1, 1]) * random.uniform(150, 600)
            self._trend = random.choice([-1.0, 1.0]) * random.uniform(0.5, 1.5)

        self.equity = max(1000.0, self.equity + delta)
        self.pnl = self.equity - 25000.0
        self.pnl_pct = (self.pnl / 25000.0) * 100.0

        return {
            "name": self.name,
            "equity": round(self.equity, 2),
            "pnl": round(self.pnl, 2),
            "pnl_pct": round(self.pnl_pct, 2),
            "status": self.status
        }


class FirebaseManager:
    """
    Manages Firebase Authentication, Matchmaking Queue, and Real-time Match Synchronization
    via standard lightweight REST APIs.
    """
    def __init__(self):
        self.api_key = ""
        self.project_id = ""
        self.auth_domain = ""
        self.user_id = ""
        self.id_token = ""
        self.display_name = ""
        self.is_anonymous = True

        self.active_match_id: Optional[str] = None
        self.player_slot: Optional[str] = None  # "player1" or "player2"
        self.opponent_bot: Optional[SimulatedOpponentBot] = None
        self.is_mock_mode = False

        self._load_config()

    def _load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    data = json.load(f)
                    self.api_key = data.get("apiKey", "").strip()
                    self.project_id = data.get("projectId", "").strip()
                    self.auth_domain = data.get("authDomain", "").strip()
            except Exception as e:
                print(f"[FirebaseManager] Config load error: {e}")

        # Check if configured with valid credentials
        if not self.api_key or "YOUR_FIREBASE" in self.api_key or not self.project_id or "YOUR_FIREBASE" in self.project_id:
            self.is_mock_mode = True
        else:
            self.is_mock_mode = False

    def save_config(self, api_key: str, project_id: str, auth_domain: str = ""):
        self.api_key = api_key.strip()
        self.project_id = project_id.strip()
        self.auth_domain = auth_domain.strip()
        data = {
            "apiKey": self.api_key,
            "projectId": self.project_id,
            "authDomain": self.auth_domain
        }
        with open(CONFIG_FILE, "w") as f:
            json.dump(data, f, indent=2)
        self._load_config()

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key and "YOUR_FIREBASE" not in self.api_key and self.project_id and "YOUR_FIREBASE" not in self.project_id)

    # --- AUTHENTICATION ---

    def sign_in_anonymous(self, display_name: str) -> Tuple[bool, str]:
        """Sign in anonymously (Guest trader for instant Omegle matching)."""
        self.display_name = display_name or f"Trader_{random.randint(100, 999)}"
        if self.is_mock_mode:
            self.user_id = f"mock_{random.randint(10000, 99999)}"
            self.id_token = "mock_token"
            return True, "Mock guest session ready."

        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={self.api_key}"
        payload = {"returnSecureToken": True}
        try:
            resp = http.post(url, json=payload, timeout=8)
            data = resp.json()
            if resp.status_code == 200:
                self.user_id = data.get("localId", f"user_{int(time.time())}")
                self.id_token = data.get("idToken", "")
                self.is_anonymous = True
                return True, "Guest sign-in successful!"
            else:
                err_msg = data.get("error", {}).get("message", "Auth failed")
                return False, f"Auth Error: {err_msg}"
        except Exception as e:
            return False, f"Connection Error: {e}"

    def sign_in_email(self, email: str, password: str, display_name: str = "") -> Tuple[bool, str]:
        """Sign in with existing email and password."""
        if self.is_mock_mode:
            self.user_id = f"mock_{email.split('@')[0]}"
            self.display_name = display_name or email.split('@')[0]
            return True, "Mock email session ready."

        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={self.api_key}"
        payload = {"email": email, "password": password, "returnSecureToken": True}
        try:
            resp = http.post(url, json=payload, timeout=8)
            data = resp.json()
            if resp.status_code == 200:
                self.user_id = data.get("localId")
                self.id_token = data.get("idToken")
                self.display_name = display_name or data.get("displayName") or email.split('@')[0]
                self.is_anonymous = False
                return True, "Sign-in successful!"
            else:
                err_msg = data.get("error", {}).get("message", "Sign in failed")
                return False, f"Sign In Error: {err_msg}"
        except Exception as e:
            return False, f"Connection Error: {e}"

    def sign_up_email(self, email: str, password: str, display_name: str) -> Tuple[bool, str]:
        """Register a new user account with email and password."""
        if self.is_mock_mode:
            self.user_id = f"mock_{email.split('@')[0]}"
            self.display_name = display_name or email.split('@')[0]
            return True, "Mock account created."

        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={self.api_key}"
        payload = {"email": email, "password": password, "returnSecureToken": True}
        try:
            resp = http.post(url, json=payload, timeout=8)
            data = resp.json()
            if resp.status_code == 200:
                self.user_id = data.get("localId")
                self.id_token = data.get("idToken")
                self.display_name = display_name or email.split('@')[0]
                self.is_anonymous = False
                return True, "Account registered successfully!"
            else:
                err_msg = data.get("error", {}).get("message", "Registration failed")
                return False, f"Sign Up Error: {err_msg}"
        except Exception as e:
            return False, f"Connection Error: {e}"

    # --- FIRESTORE HELPERS ---

    def _firestore_url(self, path: str) -> str:
        return f"https://firestore.googleapis.com/v1/projects/{self.project_id}/databases/(default)/documents/{path}"

    def _firestore_get(self, path: str) -> Optional[Dict[str, Any]]:
        headers = {}
        if self.id_token:
            headers["Authorization"] = f"Bearer {self.id_token}"
        try:
            resp = http.get(self._firestore_url(path), headers=headers, timeout=5)
            if resp.status_code == 200:
                return firestore_doc_to_dict(resp.json())
        except Exception as e:
            print(f"[FirebaseManager] Get error on {path}: {e}")
        return None

    def _firestore_set(self, path: str, data: Dict[str, Any], merge: bool = True) -> bool:
        headers = {}
        if self.id_token:
            headers["Authorization"] = f"Bearer {self.id_token}"
        try:
            doc_body = dict_to_firestore_doc(data)
            url = self._firestore_url(path)
            if merge and data:
                mask_params = "&".join(f"updateMask.fieldPaths={k}" for k in data.keys())
                url = f"{url}?{mask_params}"
            resp = http.patch(url, json=doc_body, headers=headers, timeout=5)
            return resp.status_code == 200
        except Exception as e:
            print(f"[FirebaseManager] Set error on {path}: {e}")
            return False

    def _firestore_delete(self, path: str) -> bool:
        headers = {}
        if self.id_token:
            headers["Authorization"] = f"Bearer {self.id_token}"
        try:
            resp = http.delete(self._firestore_url(path), headers=headers, timeout=5)
            return resp.status_code in (200, 204)
        except Exception:
            return False

    # --- OMEGLE-STYLE MATCHMAKING ---

    def find_match(self, cancel_event: threading.Event) -> Optional[Dict[str, Any]]:
        """
        Omegle matchmaking queue:
        1. Checks for waiting opponent.
        2. If found, matches immediately and creates match room.
        3. If none found, enters queue and waits up to 30s.
        4. If cancel_event is set or timeout occurs, aborts cleanly.
        """
        if self.is_mock_mode:
            # Simulate searching for 1.5 seconds, then match with a live bot opponent!
            for _ in range(15):
                if cancel_event.is_set():
                    return None
                time.sleep(0.1)

            self.opponent_bot = SimulatedOpponentBot()
            self.active_match_id = f"mock_match_{int(time.time())}"
            self.player_slot = "player1"
            return {
                "match_id": self.active_match_id,
                "seed": random.randint(100000, 999999),
                "duration_seconds": 180,
                "start_time": time.time(),
                "player_slot": "player1",
                "opponent": {
                    "uid": "bot_opponent",
                    "name": self.opponent_bot.name,
                    "equity": 25000.0,
                    "pnl": 0.0,
                    "pnl_pct": 0.0
                }
            }

        # Real Firebase Firestore Matchmaking
        queue_path = f"match_queue/{self.user_id}"
        list_url = self._firestore_url("match_queue")
        now = time.time()

        try:
            # 1. Query existing queue
            resp = http.get(list_url, timeout=5)
            documents = resp.json().get("documents", []) if resp.status_code == 200 else []

            # Find valid candidate: status == "waiting", not self, not stale (> 45s)
            found_candidate: Optional[Dict[str, Any]] = None
            for doc in documents:
                doc_name = doc.get("name", "").split("/")[-1]
                data = firestore_doc_to_dict(doc)
                if doc_name != self.user_id and data.get("status") == "waiting":
                    t = data.get("timestamp", 0)
                    if (now - t) < 45.0:
                        found_candidate = data
                        found_candidate["uid"] = doc_name
                        break

            if found_candidate:
                # We found an opponent! Create match room
                opp_uid = found_candidate["uid"]
                opp_name = found_candidate.get("name", "Opponent")
                match_id = f"m_{self.user_id[:4]}_{opp_uid[:4]}_{int(now)}"
                seed = random.randint(100000, 999999)

                match_data = {
                    "match_id": match_id,
                    "seed": seed,
                    "duration_seconds": 180,
                    "start_time": now + 2.0,  # 2 second grace countdown
                    "status": "active",
                    "player1": {
                        "uid": opp_uid,
                        "name": opp_name,
                        "equity": 25000.0,
                        "pnl": 0.0,
                        "pnl_pct": 0.0,
                        "status": "playing",
                        "last_update": now
                    },
                    "player2": {
                        "uid": self.user_id,
                        "name": self.display_name,
                        "equity": 25000.0,
                        "pnl": 0.0,
                        "pnl_pct": 0.0,
                        "status": "playing",
                        "last_update": now
                    }
                }

                # Save match room
                self._firestore_set(f"matches/{match_id}", match_data, merge=False)

                # Notify opponent ticket
                self._firestore_set(f"match_queue/{opp_uid}", {
                    "name": opp_name,
                    "status": "matched",
                    "match_id": match_id,
                    "seed": seed,
                    "timestamp": now
                }, merge=False)

                # Remove self from queue if present
                self._firestore_delete(queue_path)

                self.active_match_id = match_id
                self.player_slot = "player2"
                return {
                    "match_id": match_id,
                    "seed": seed,
                    "duration_seconds": 180,
                    "start_time": now + 2.0,
                    "player_slot": "player2",
                    "opponent": {
                        "uid": opp_uid,
                        "name": opp_name,
                        "equity": 25000.0,
                        "pnl": 0.0,
                        "pnl_pct": 0.0
                    }
                }

            # 2. No opponent found yet -> Register in queue as waiting
            self._firestore_set(queue_path, {
                "name": self.display_name,
                "status": "waiting",
                "timestamp": now
            }, merge=False)

            # Poll for match assignment or cancel (Fast pairing within 12 seconds)
            poll_start = time.time()
            while time.time() - poll_start < 12.0:
                if cancel_event.is_set():
                    self._firestore_delete(queue_path)
                    return None

                time.sleep(1.0)
                ticket = self._firestore_get(queue_path)
                if ticket and ticket.get("status") == "matched":
                    match_id = ticket.get("match_id")
                    match_doc = self._firestore_get(f"matches/{match_id}")
                    self._firestore_delete(queue_path)

                    if match_doc:
                        self.active_match_id = match_id
                        self.player_slot = "player1"
                        opp = match_doc.get("player2", {})
                        return {
                            "match_id": match_id,
                            "seed": match_doc.get("seed", 12345),
                            "duration_seconds": match_doc.get("duration_seconds", 180),
                            "start_time": match_doc.get("start_time", time.time()),
                            "player_slot": "player1",
                            "opponent": {
                                "uid": opp.get("uid", ""),
                                "name": opp.get("name", "Opponent"),
                                "equity": opp.get("equity", 25000.0),
                                "pnl": opp.get("pnl", 0.0),
                                "pnl_pct": opp.get("pnl_pct", 0.0)
                            }
                        }

            # If no human opponent joined within 12s, deploy dynamic rival bot so player can duel immediately!
            self._firestore_delete(queue_path)
            self.opponent_bot = SimulatedOpponentBot()
            self.active_match_id = f"rival_match_{int(time.time())}"
            self.player_slot = "player1"
            return {
                "match_id": self.active_match_id,
                "seed": random.randint(100000, 999999),
                "duration_seconds": 180,
                "start_time": time.time(),
                "player_slot": "player1",
                "opponent": {
                    "uid": "bot_rival",
                    "name": self.opponent_bot.name,
                    "equity": 25000.0,
                    "pnl": 0.0,
                    "pnl_pct": 0.0
                }
            }

        except Exception as e:
            print(f"[FirebaseManager] Matchmaking error: {e}")
            self._firestore_delete(queue_path)
            # Fallback to simulated opponent on any network error
            self.opponent_bot = SimulatedOpponentBot()
            self.active_match_id = f"rival_match_{int(time.time())}"
            self.player_slot = "player1"
            return {
                "match_id": self.active_match_id,
                "seed": random.randint(100000, 999999),
                "duration_seconds": 180,
                "start_time": time.time(),
                "player_slot": "player1",
                "opponent": {
                    "uid": "bot_rival",
                    "name": self.opponent_bot.name,
                    "equity": 25000.0,
                    "pnl": 0.0,
                    "pnl_pct": 0.0
                }
            }

    # --- IN-GAME METRIC SYNC ---

    def update_player_metrics(self, equity: float, pnl: float, pnl_pct: float) -> Optional[Dict[str, Any]]:
        """
        Updates my equity/pnl in the match room and returns the latest opponent metrics.
        Called every tick or throttled to 1-2s.
        """
        if self.opponent_bot:
            return self.opponent_bot.tick()

        if not self.active_match_id or not self.player_slot:
            return None

        opp_slot = "player2" if self.player_slot == "player1" else "player1"
        now = time.time()

        # Update my metrics in Firestore (merge=True ensures opponent's slot is preserved!)
        self._firestore_set(f"matches/{self.active_match_id}", {
            self.player_slot: {
                "uid": self.user_id,
                "name": self.display_name,
                "equity": round(equity, 2),
                "pnl": round(pnl, 2),
                "pnl_pct": round(pnl_pct, 2),
                "status": "playing",
                "last_update": now
            }
        }, merge=True)

        # Fetch opponent's metrics
        match_doc = self._firestore_get(f"matches/{self.active_match_id}")
        if match_doc:
            opp_data = match_doc.get(opp_slot, {})
            if opp_data:
                return {
                    "name": opp_data.get("name", "Opponent"),
                    "equity": opp_data.get("equity", 25000.0),
                    "pnl": opp_data.get("pnl", 0.0),
                    "pnl_pct": opp_data.get("pnl_pct", 0.0),
                    "status": opp_data.get("status", "playing")
                }
        return None

    def get_latest_opponent_metrics(self) -> Optional[Dict[str, Any]]:
        """Synchronously returns the freshest opponent metrics right before concluding match."""
        if self.opponent_bot:
            return self.opponent_bot.tick()
        if not self.active_match_id or not self.player_slot:
            return None
        opp_slot = "player2" if self.player_slot == "player1" else "player1"
        try:
            match_doc = self._firestore_get(f"matches/{self.active_match_id}")
            if match_doc:
                opp_data = match_doc.get(opp_slot, {})
                if opp_data:
                    return {
                        "name": opp_data.get("name", "Opponent"),
                        "equity": opp_data.get("equity", 25000.0),
                        "pnl": opp_data.get("pnl", 0.0),
                        "pnl_pct": opp_data.get("pnl_pct", 0.0),
                        "status": opp_data.get("status", "playing")
                    }
        except Exception:
            pass
        return None

    def forfeit_or_leave(self):
        """Called when a player clicks Omegle 'Next' or closes match."""
        if not self.is_mock_mode and self.active_match_id and self.player_slot:
            try:
                self._firestore_set(f"matches/{self.active_match_id}", {
                    self.player_slot: {
                        "status": "forfeited"
                    },
                    "status": "ended"
                }, merge=True)
            except Exception:
                pass
        self.active_match_id = None
        self.player_slot = None
        self.opponent_bot = None
