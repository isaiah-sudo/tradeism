/**
 * Firebase Firestore 1v1 PvP Matchmaker & Real-time Synchronization.
 * Fully compatible with the desktop Python FirebaseManager protocol.
 */

// Firestore Document Serializer & Deserializer
function jsToFirestoreValue(val) {
    if (typeof val === 'boolean') return { booleanValue: val };
    if (typeof val === 'number') {
        if (Number.isInteger(val)) return { integerValue: String(val) };
        return { doubleValue: val };
    }
    if (typeof val === 'string') return { stringValue: val };
    if (val === null || val === undefined) return { nullValue: null };
    if (Array.isArray(val)) {
        return { arrayValue: { values: val.map(jsToFirestoreValue) } };
    }
    if (typeof val === 'object') {
        const fields = {};
        for (const [k, v] of Object.entries(val)) {
            fields[k] = jsToFirestoreValue(v);
        }
        return { mapValue: { fields } };
    }
    return { stringValue: String(val) };
}

function firestoreValueToJs(valObj) {
    if (!valObj || typeof valObj !== 'object') return valObj;
    if ('stringValue' in valObj) return valObj.stringValue;
    if ('integerValue' in valObj) return parseInt(valObj.integerValue, 10);
    if ('doubleValue' in valObj) return parseFloat(valObj.doubleValue);
    if ('booleanValue' in valObj) return valObj.booleanValue;
    if ('nullValue' in valObj) return null;
    if ('mapValue' in valObj) {
        const fields = valObj.mapValue.fields || {};
        const res = {};
        for (const [k, v] of Object.entries(fields)) {
            res[k] = firestoreValueToJs(v);
        }
        return res;
    }
    if ('arrayValue' in valObj) {
        const values = valObj.arrayValue.values || [];
        return values.map(firestoreValueToJs);
    }
    return null;
}

function firestoreDocToDict(docJson) {
    const fields = docJson.fields || {};
    const res = {};
    for (const [k, v] of Object.entries(fields)) {
        res[k] = firestoreValueToJs(v);
    }
    return res;
}

function dictToFirestoreDoc(data) {
    const fields = {};
    for (const [k, v] of Object.entries(data)) {
        fields[k] = jsToFirestoreValue(v);
    }
    return { fields };
}

class SimulatedOpponentBot {
    static BOT_NAMES = [
        "WallSt_Titan", "DiamondHands_99", "AlphaScalper", "BullishApe",
        "OptionsSlayer", "MomentumTrader", "YOLO_God", "QuantAlgo_X"
    ];

    constructor(name = null) {
        this.name = name || SimulatedOpponentBot.BOT_NAMES[Math.floor(Math.random() * SimulatedOpponentBot.BOT_NAMES.length)];
        this.equity = 25000.0;
        this.pnl = 0.0;
        this.pnlPct = 0.0;
        this.status = "playing";
        this.trend = (Math.random() > 0.5 ? 1 : -1) * (0.5 + Math.random());
    }

    tick() {
        // Random walk
        const delta = (this.trend * 15.0) + ((Math.random() - 0.5) * 60.0);
        if (Math.random() < 0.06) {
            this.trend = (Math.random() > 0.5 ? 1 : -1) * (0.5 + Math.random());
        }

        this.equity = Math.max(1000.0, Number((this.equity + delta).toFixed(2)));
        this.pnl = Number((this.equity - 25000.0).toFixed(2));
        this.pnlPct = Number(((this.pnl / 25000.0) * 100).toFixed(2));

        return {
            name: this.name,
            equity: this.equity,
            pnl: this.pnl,
            pnl_pct: this.pnlPct,
            status: this.status
        };
    }
}

class FirebaseMatchmaker {
    constructor() {
        this.apiKey = "AIzaSyAPXfhZrr1vndo_2xge6DxVyyGEFHQaIPY";
        this.projectId = "tradisim-188a6";
        this.authDomain = "tradisim-188a6.firebaseapp.com";
        this.userId = "";
        this.idToken = "";
        this.displayName = "";

        this.activeMatchId = null;
        this.playerSlot = null; // "player1" or "player2"
        this.opponentBot = null;
        this.isMockMode = false;
    }

    get firestoreBaseUrl() {
        return `https://firestore.googleapis.com/v1/projects/${this.projectId}/databases/(default)/documents`;
    }

    async signInAnonymous(name) {
        if (name) this.displayName = name.trim();
        if (!this.displayName) {
            this.displayName = `WebTrader_${Math.floor(100 + Math.random() * 900)}`;
        }

        try {
            const res = await fetch(`https://identitytoolkit.googleapis.com/v1/accounts:signUp?key=${this.apiKey}`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ returnSecureToken: true })
            });

            if (res.ok) {
                const data = await res.json();
                this.userId = data.localId || `web_${Date.now()}`;
                this.idToken = data.idToken;
                return { success: true, userId: this.userId };
            } else {
                console.warn("[Firebase] Auth fallback to local session id");
                this.userId = `web_guest_${Math.floor(10000 + Math.random() * 90000)}`;
                return { success: true, userId: this.userId };
            }
        } catch (e) {
            console.warn("[Firebase] Auth error, using fallback ID:", e);
            this.userId = `web_guest_${Math.floor(10000 + Math.random() * 90000)}`;
            return { success: true, userId: this.userId };
        }
    }

    setAuthenticatedSession(userId, email = "", displayName = "", idToken = "", refreshToken = "") {
        this.userId = userId;
        this.email = email;
        this.displayName = displayName || (email ? email.split('@')[0] : "Trader");
        this.idToken = idToken;
        this.refreshTokenStr = refreshToken;
        this.isAnonymous = false;
    }

    signOut() {
        this.userId = "";
        this.email = "";
        this.displayName = "";
        this.idToken = "";
        this.refreshTokenStr = "";
        this.isAnonymous = true;
    }

    async signInEmail(email, password) {
        try {
            const res = await fetch(`https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=${this.apiKey}`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email, password, returnSecureToken: true })
            });
            const data = await res.json();
            if (res.ok) {
                this.setAuthenticatedSession(data.localId, email, data.displayName, data.idToken, data.refreshToken);
                return { success: true, data };
            } else {
                return { success: false, error: data.error?.message || "Sign in failed" };
            }
        } catch (e) {
            return { success: false, error: e.message };
        }
    }

    async signUpEmail(email, password, displayName = "") {
        try {
            const res = await fetch(`https://identitytoolkit.googleapis.com/v1/accounts:signUp?key=${this.apiKey}`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email, password, returnSecureToken: true })
            });
            const data = await res.json();
            if (res.ok) {
                if (displayName) {
                    try {
                        await fetch(`https://identitytoolkit.googleapis.com/v1/accounts:update?key=${this.apiKey}`, {
                            method: "POST",
                            headers: { "Content-Type": "application/json" },
                            body: JSON.stringify({ idToken: data.idToken, displayName, returnSecureToken: true })
                        });
                    } catch (e) {}
                }
                this.setAuthenticatedSession(data.localId, email, displayName || data.displayName, data.idToken, data.refreshToken);
                return { success: true, data };
            } else {
                return { success: false, error: data.error?.message || "Registration failed" };
            }
        } catch (e) {
            return { success: false, error: e.message };
        }
    }

    async saveUserProfile(userId, profileData) {
        if (!userId) return false;
        return await this._firestoreSet(`users/${userId}`, profileData, true);
    }

    async loadUserProfile(userId) {
        if (!userId) return null;
        return await this._firestoreGet(`users/${userId}`);
    }

    async _firestoreGet(path) {
        const headers = {};
        if (this.idToken) headers["Authorization"] = `Bearer ${this.idToken}`;
        try {
            const res = await fetch(`${this.firestoreBaseUrl}/${path}`, { headers });
            if (res.ok) {
                const doc = await res.json();
                return firestoreDocToDict(doc);
            }
        } catch (e) {
            console.error(`[Firebase] Get error on ${path}:`, e);
        }
        return null;
    }

    async _firestoreSet(path, data, merge = true) {
        const headers = { "Content-Type": "application/json" };
        if (this.idToken) headers["Authorization"] = `Bearer ${this.idToken}`;
        try {
            const body = dictToFirestoreDoc(data);
            let url = `${this.firestoreBaseUrl}/${path}`;
            if (merge) {
                const keys = Object.keys(data);
                if (keys.length > 0) {
                    const maskParams = keys.map(k => `updateMask.fieldPaths=${encodeURIComponent(k)}`).join('&');
                    url += `?${maskParams}`;
                }
            }
            const res = await fetch(url, {
                method: "PATCH",
                headers,
                body: JSON.stringify(body)
            });
            return res.ok;
        } catch (e) {
            console.error(`[Firebase] Set error on ${path}:`, e);
            return false;
        }
    }

    async _firestoreDelete(path) {
        const headers = {};
        if (this.idToken) headers["Authorization"] = `Bearer ${this.idToken}`;
        try {
            const res = await fetch(`${this.firestoreBaseUrl}/${path}`, {
                method: "DELETE",
                headers
            });
            return res.ok;
        } catch (e) {
            return false;
        }
    }

    async findMatch(onStatusUpdate, abortSignal, customDisplayName) {
        if (customDisplayName) {
            this.displayName = customDisplayName.trim();
        }
        if (!this.displayName) {
            this.displayName = `WebTrader_${Math.floor(100 + Math.random() * 900)}`;
        }
        if (!this.userId) {
            await this.signInAnonymous(this.displayName);
        }

        const queuePath = `match_queue/${this.userId}`;
        const now = Date.now() / 1000;

        if (onStatusUpdate) onStatusUpdate("Searching global matchmaking queue...");

        try {
            // 1. Register self in queue as waiting (overwrite any stale entry)
            await this._firestoreSet(queuePath, {
                name: this.displayName,
                status: "waiting",
                timestamp: now
            }, false);

            // Polling loop: up to 15 seconds before bot fallback
            const pollStart = Date.now();
            while ((Date.now() - pollStart) < 15000) {
                if (abortSignal && abortSignal.aborted) {
                    await this._firestoreDelete(queuePath);
                    return null;
                }

                await new Promise(r => setTimeout(r, 500));

                // A. Check if our ticket was matched by another player
                const ticket = await this._firestoreGet(queuePath);
                if (ticket && ticket.status === "matched") {
                    const matchId = ticket.match_id;
                    const slot = ticket.player_slot || "player2";
                    let seed = ticket.seed || 12345;
                    let startTime = ticket.start_time || (Date.now() / 1000);
                    let oppName = ticket.opponent_name || "Opponent";
                    let oppUid = ticket.opponent_uid || "";

                    // Fetch match document with short retries for replication
                    let matchDoc = null;
                    for (let attempt = 0; attempt < 4; attempt++) {
                        matchDoc = await this._firestoreGet(`matches/${matchId}`);
                        if (matchDoc) break;
                        await new Promise(r => setTimeout(r, 250));
                    }

                    await this._firestoreDelete(queuePath);

                    if (matchDoc) {
                        const oppSlot = slot === "player2" ? "player1" : "player2";
                        const oppData = matchDoc[oppSlot] || {};
                        oppName = oppData.name || oppName;
                        oppUid = oppData.uid || oppUid;
                        seed = matchDoc.seed || seed;
                        startTime = matchDoc.start_time || startTime;
                    }

                    this.activeMatchId = matchId;
                    this.playerSlot = slot;
                    this.opponentBot = null;

                    return {
                        matchId: matchId,
                        seed: seed,
                        durationSeconds: 180,
                        startTime: startTime,
                        playerSlot: slot,
                        opponent: {
                            uid: oppUid,
                            name: oppName,
                            equity: 25000.0,
                            pnl: 0.0,
                            pnl_pct: 0.0
                        }
                    };
                }

                // B. Look for other waiting candidates in match_queue
                const headers = {};
                if (this.idToken) headers["Authorization"] = `Bearer ${this.idToken}`;
                let documents = [];
                try {
                    const listRes = await fetch(`${this.firestoreBaseUrl}/match_queue`, { headers });
                    if (listRes.ok) {
                        const listData = await listRes.json();
                        documents = listData.documents || [];
                    }
                } catch (err) {
                    console.warn("[Firebase] Queue fetch error:", err);
                }

                const currTime = Date.now() / 1000;
                const candidates = [];
                for (const doc of documents) {
                    const docName = (doc.name || "").split("/").pop();
                    const data = firestoreDocToDict(doc);
                    if (docName !== this.userId && data.status === "waiting") {
                        const t = data.timestamp || 0;
                        if ((currTime - t) < 60.0) {
                            data.uid = docName;
                            candidates.push(data);
                        }
                    }
                }

                if (candidates.length > 0) {
                    // Sort candidates by timestamp (oldest first)
                    candidates.sort((a, b) => (a.timestamp || 0) - (b.timestamp || 0));
                    const cand = candidates[0];
                    const candUid = cand.uid;
                    const candName = cand.name || "Opponent";
                    const candTs = cand.timestamp || 0;

                    // Deterministic tie-breaker: Lower UID creates match
                    const shouldCreate = (this.userId < candUid);
                    if (shouldCreate) {
                        const matchId = `m_${this.userId.slice(0, 4)}_${candUid.slice(0, 4)}_${Math.floor(currTime)}`;
                        const seed = Math.floor(100000 + Math.random() * 900000);

                        const matchData = {
                            match_id: matchId,
                            seed: seed,
                            duration_seconds: 180,
                            start_time: currTime + 2.0,
                            status: "active",
                            player1: {
                                uid: this.userId,
                                name: this.displayName,
                                equity: 25000.0,
                                pnl: 0.0,
                                pnl_pct: 0.0,
                                status: "playing",
                                last_update: currTime
                            },
                            player2: {
                                uid: candUid,
                                name: candName,
                                equity: 25000.0,
                                pnl: 0.0,
                                pnl_pct: 0.0,
                                status: "playing",
                                last_update: currTime
                            }
                        };

                        // 1. Create match room in Firestore
                        await this._firestoreSet(`matches/${matchId}`, matchData, false);

                        // 2. Update opponent's ticket with match details and OUR name
                        await this._firestoreSet(`match_queue/${candUid}`, {
                            name: candName,
                            status: "matched",
                            match_id: matchId,
                            seed: seed,
                            start_time: currTime + 2.0,
                            player_slot: "player2",
                            opponent_name: this.displayName,
                            opponent_uid: this.userId,
                            timestamp: currTime
                        }, false);

                        // 3. Clean up our own ticket
                        await this._firestoreDelete(queuePath);

                        this.activeMatchId = matchId;
                        this.playerSlot = "player1";
                        this.opponentBot = null;

                        return {
                            matchId: matchId,
                            seed: seed,
                            durationSeconds: 180,
                            startTime: currTime + 2.0,
                            playerSlot: "player1",
                            opponent: {
                                uid: candUid,
                                name: candName,
                                equity: 25000.0,
                                pnl: 0.0,
                                pnl_pct: 0.0
                            }
                        };
                    }
                }
            }

            // Fallback: Deploy simulated rival bot after 15s
            if (onStatusUpdate) onStatusUpdate("Deploying Wall Street Rival Bot for instant showdown...");
            await this._firestoreDelete(queuePath);
            this.opponentBot = new SimulatedOpponentBot();
            this.activeMatchId = `rival_match_${Date.now()}`;
            this.playerSlot = "player1";

            return {
                matchId: this.activeMatchId,
                seed: Math.floor(100000 + Math.random() * 900000),
                durationSeconds: 180,
                startTime: Date.now() / 1000,
                playerSlot: "player1",
                opponent: {
                    uid: "bot_rival",
                    name: this.opponentBot.name,
                    equity: 25000.0,
                    pnl: 0.0,
                    pnl_pct: 0.0
                }
            };

        } catch (e) {
            console.error("[Firebase] Matchmaking error:", e);
            await this._firestoreDelete(queuePath);

            // Fallback bot
            this.opponentBot = new SimulatedOpponentBot();
            this.activeMatchId = `rival_match_${Date.now()}`;
            this.playerSlot = "player1";

            return {
                matchId: this.activeMatchId,
                seed: Math.floor(100000 + Math.random() * 900000),
                durationSeconds: 180,
                startTime: Date.now() / 1000,
                playerSlot: "player1",
                opponent: {
                    uid: "bot_rival",
                    name: this.opponentBot.name,
                    equity: 25000.0,
                    pnl: 0.0,
                    pnl_pct: 0.0
                }
            };
        }
    }

    async updatePlayerMetrics(equity, pnl, pnlPct) {
        if (this.opponentBot) {
            return this.opponentBot.tick();
        }

        if (!this.activeMatchId || !this.playerSlot) return null;

        const oppSlot = this.playerSlot === "player1" ? "player2" : "player1";
        const now = Date.now() / 1000;

        // Update my slot
        const myData = {};
        myData[this.playerSlot] = {
            uid: this.userId,
            name: this.displayName,
            equity: Number(equity.toFixed(2)),
            pnl: Number(pnl.toFixed(2)),
            pnl_pct: Number(pnlPct.toFixed(2)),
            status: "playing",
            last_update: now
        };

        // Fire and forget update
        this._firestoreSet(`matches/${this.activeMatchId}`, myData);

        // Fetch opponent slot
        const matchDoc = await this._firestoreGet(`matches/${this.activeMatchId}`);
        if (matchDoc && matchDoc[oppSlot]) {
            const oppData = matchDoc[oppSlot];
            return {
                name: oppData.name || "Opponent",
                equity: oppData.equity !== undefined ? oppData.equity : 25000.0,
                pnl: oppData.pnl !== undefined ? oppData.pnl : 0.0,
                pnl_pct: oppData.pnl_pct !== undefined ? oppData.pnl_pct : 0.0,
                status: oppData.status || "playing"
            };
        }
        return null;
    }

    async getLatestOpponentMetrics() {
        if (this.opponentBot) {
            return this.opponentBot.tick();
        }

        if (!this.activeMatchId || !this.playerSlot) return null;
        const oppSlot = this.playerSlot === "player1" ? "player2" : "player1";

        try {
            const matchDoc = await this._firestoreGet(`matches/${this.activeMatchId}`);
            if (matchDoc && matchDoc[oppSlot]) {
                const oppData = matchDoc[oppSlot];
                return {
                    name: oppData.name || "Opponent",
                    equity: oppData.equity !== undefined ? oppData.equity : 25000.0,
                    pnl: oppData.pnl !== undefined ? oppData.pnl : 0.0,
                    pnl_pct: oppData.pnl_pct !== undefined ? oppData.pnl_pct : 0.0,
                    status: oppData.status || "playing"
                };
            }
        } catch (e) {
            console.error("[Firebase] getLatestOpponentMetrics error:", e);
        }
        return null;
    }

    async forfeitOrLeave() {
        if (this.activeMatchId && this.playerSlot && !this.opponentBot) {
            const myData = { status: "ended" };
            myData[this.playerSlot] = { status: "forfeited" };
            this._firestoreSet(`matches/${this.activeMatchId}`, myData);
        }
        this.activeMatchId = null;
        this.playerSlot = null;
        this.opponentBot = null;
    }
}
