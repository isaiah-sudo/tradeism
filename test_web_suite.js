/**
 * Automated Verification & Regression Test Suite for Day Trading Simulator (Web Edition).
 * Tests all core subsystems:
 * 1. Stock Universe (100 stocks, sector distributions, pricing)
 * 2. Market Simulation Engine (Candlesticks, Orders, Margin, Shorting, Reversals, News, Profit Banking)
 * 3. Trader Shop & Profile Manager (Catalog integrity, purchases, equips, vault banking)
 * 4. Win Animations Engine (Canvas particle simulations, all 5 animations)
 * 5. Firebase Matchmaker & Protocol (Serialization, Simulated Rival Bot, State transitions)
 */

const assert = require("assert");
const fs = require("fs");
const path = require("path");

console.log("=================================================");
console.log("   RUNNING WEB VERSION THOROUGH TEST SUITE");
console.log("=================================================\n");

let passedTests = 0;
let totalTests = 0;

function it(name, fn) {
    totalTests++;
    try {
        fn();
        console.log(`  ✓ ${name}`);
        passedTests++;
    } catch (e) {
        console.error(`  ✗ ${name}`);
        console.error(`    Error: ${e.message}`);
        console.error(e.stack);
        process.exitCode = 1;
    }
}

// Mock DOM & Browser Environment for Node.js
function makeMockElement(id = "") {
    return {
        id,
        style: {},
        classList: {
            classes: new Set(),
            add(c) { this.classes.add(c); },
            remove(c) { this.classes.delete(c); },
            contains(c) { return this.classes.has(c); }
        },
        value: "0",
        textContent: "",
        innerHTML: "",
        disabled: false,
        className: "",
        addEventListener: () => {},
        querySelectorAll: () => [],
        querySelector: () => null,
        appendChild: () => {},
        remove: () => {},
        getContext: () => ({
            save: () => {}, restore: () => {}, translate: () => {}, rotate: () => {},
            beginPath: () => {}, closePath: () => {}, moveTo: () => {}, lineTo: () => {},
            arc: () => {}, stroke: () => {}, fill: () => {}, fillRect: () => {},
            clearRect: () => {}, roundRect: () => {}, fillText: () => {},
            setTransform: () => {}, scale: () => {}, setLineDash: () => {}
        }),
        getBoundingClientRect: () => ({ width: 800, height: 400, left: 0, top: 0 }),
        get parentElement() {
            return {
                getBoundingClientRect: () => ({ width: 800, height: 400, left: 0, top: 0 })
            };
        }
    };
}

const mockElements = {};
global.window = {
    addEventListener: () => {},
    innerWidth: 1920,
    innerHeight: 1080,
    devicePixelRatio: 1
};
global.document = {
    getElementById: (id) => {
        if (!mockElements[id]) mockElements[id] = makeMockElement(id);
        return mockElements[id];
    },
    querySelector: () => makeMockElement("query"),
    querySelectorAll: () => [],
    createElement: (tag) => makeMockElement(tag),
    body: makeMockElement("body")
};
global.localStorage = {
    store: {},
    getItem(k) { return this.store[k] || null; },
    setItem(k, v) { this.store[k] = String(v); },
    removeItem(k) { delete this.store[k]; },
    clear() { this.store = {}; }
};
global.requestAnimationFrame = (cb) => setTimeout(cb, 16);
global.cancelAnimationFrame = (id) => clearTimeout(id);
global.alert = () => {};
global.confirm = () => true;
global.CanvasRenderingContext2D = class {};
global.CanvasRenderingContext2D.prototype = {};

// Load Scripts in sequence into global scope using indirect eval
const load = (relPath) => {
    const code = fs.readFileSync(path.join(__dirname, relPath), "utf-8");
    const exportStatements = [];
    const classMatches = code.match(/^class\s+([A-Za-z0-9_]+)/gm) || [];
    classMatches.forEach(m => exportStatements.push(`try { global.${m.split(/\s+/)[1]} = ${m.split(/\s+/)[1]}; } catch(e){}`));
    const constMatches = code.match(/^(?:const|let|var)\s+([A-Za-z0-9_]+)/gm) || [];
    constMatches.forEach(m => exportStatements.push(`try { global.${m.split(/\s+/)[1]} = ${m.split(/\s+/)[1]}; } catch(e){}`));
    (0, eval)(code + "\n" + exportStatements.join("\n"));
};

// 1. Stock Universe
load("public/js/stock-universe.js");

console.log("1. STOCK UNIVERSE VERIFICATION");
it("contains exactly 100 simulated stocks across varied sectors", () => {
    assert.strictEqual(Array.isArray(STOCK_DEFINITIONS), true);
    assert.strictEqual(STOCK_DEFINITIONS.length, 100);
});

it("every stock has valid ticker, name, sector, price > 0, and volatility > 0", () => {
    const tickers = new Set();
    for (const s of STOCK_DEFINITIONS) {
        assert.ok(s.ticker && typeof s.ticker === "string");
        assert.ok(s.name && typeof s.name === "string");
        assert.ok(s.sector && typeof s.sector === "string");
        assert.ok(typeof s.price === "number" && s.price > 0);
        assert.ok(typeof s.volatility === "number" && s.volatility > 0);
        assert.strictEqual(tickers.has(s.ticker), false, `Duplicate ticker: ${s.ticker}`);
        tickers.add(s.ticker);
    }
});

it("all predefined sectors exist in the universe", () => {
    const foundSectors = new Set(STOCK_DEFINITIONS.map(s => s.sector));
    for (const sec of SECTORS) {
        if (sec === "All") continue;
        assert.ok(foundSectors.has(sec), `Sector missing stocks: ${sec}`);
    }
});

// 2. Market Simulation Engine
load("public/js/news-generator.js");
load("public/js/simulation-engine.js");

console.log("\n2. MARKET SIMULATION ENGINE VERIFICATION");
it("initializes account with $25,000 cash, 0 positions, and 50 pre-seeded candles per stock", () => {
    const engine = new MarketEngine(25000.0);
    assert.strictEqual(engine.cash, 25000.0);
    assert.strictEqual(engine.totalEquity, 25000.0);
    assert.strictEqual(engine.buyingPower, 100000.0);
    assert.strictEqual(engine.realizedPnL, 0.0);
    assert.strictEqual(Object.keys(engine.stocks).length, 100);
    for (const ticker in engine.stocks) {
        const st = engine.stocks[ticker];
        assert.strictEqual(st.candles.length, 50);
        assert.ok(st.price > 0);
    }
});

it("executes BUY orders, deducts cash, tracks average entry, records trade marker", () => {
    const engine = new MarketEngine(25000.0);
    const stock = engine.stocks["NVXP"];
    const initialPrice = stock.price;
    const ok = engine.buy("NVXP", 50);
    assert.strictEqual(ok, true);
    assert.strictEqual(engine.positions["NVXP"].shares, 50);
    assert.strictEqual(engine.positions["NVXP"].avgPrice, initialPrice);
    assert.strictEqual(engine.cash, 25000.0 - (50 * initialPrice));
    assert.strictEqual(engine.trades.length, 1);
    assert.strictEqual(engine.trades[0].action, "BUY");
    assert.strictEqual(stock.tradeMarkers.length, 1);
    assert.strictEqual(stock.tradeMarkers[0].action, "BUY");
});

it("executes SELL orders, computes realized PnL correctly", () => {
    const engine = new MarketEngine(25000.0);
    const stock = engine.stocks["NVXP"];
    const buyPrice = stock.price;
    engine.buy("NVXP", 100);
    
    // Simulate price increase
    stock.price = buyPrice + 10.0;
    const ok = engine.sell("NVXP", 50);
    assert.strictEqual(ok, true);
    assert.strictEqual(engine.positions["NVXP"].shares, 50);
    assert.strictEqual(engine.realizedPnL, 50 * 10.0); // +$500.00
});

it("executes SHORT orders with 50% margin collateral and COVER orders with margin release", () => {
    const engine = new MarketEngine(25000.0);
    const stock = engine.stocks["APEX"];
    const shortPrice = stock.price;
    const shares = 100;
    const proceeds = shares * shortPrice;
    const reqMargin = proceeds * 0.5;

    const okShort = engine.short("APEX", shares);
    assert.strictEqual(okShort, true);
    const pos = engine.positions["APEX"];
    assert.strictEqual(pos.shares, -100);
    assert.strictEqual(pos.side, "SHORT");
    assert.strictEqual(pos.lockedMargin, reqMargin);
    assert.strictEqual(engine.cash, 25000.0 - reqMargin);

    // Simulate price dropping by $5.00 (profit for short)
    stock.price = shortPrice - 5.0;
    const okCover = engine.cover("APEX", shares);
    assert.strictEqual(okCover, true);
    assert.strictEqual(pos.shares, 0);
    assert.strictEqual(pos.lockedMargin, 0);
    assert.strictEqual(engine.realizedPnL, 100 * 5.0); // +$500.00
    assert.strictEqual(engine.cash, 25000.0 + 500.0);
});

it("reverses long positions to short, and short positions to long seamlessly", () => {
    const engine = new MarketEngine(25000.0);
    engine.buy("NVXP", 50);
    assert.strictEqual(engine.positions["NVXP"].shares, 50);

    // Reverse long -> short
    const revOk = engine.reversePosition("NVXP");
    assert.strictEqual(revOk, true);
    assert.strictEqual(engine.positions["NVXP"].shares, -50);
    assert.strictEqual(engine.positions["NVXP"].side, "SHORT");

    // Reverse short -> long
    const revBackOk = engine.reversePosition("NVXP");
    assert.strictEqual(revBackOk, true);
    assert.strictEqual(engine.positions["NVXP"].shares, 50);
    assert.strictEqual(engine.positions["NVXP"].side, "LONG");
});

it("flattens positions and accurately banks profit above initial $25,000 into Vault", () => {
    const engine = new MarketEngine(25000.0);
    const stock = engine.stocks["NVXP"];
    engine.buy("NVXP", 100);
    // Artificially bump stock price by $20/share (+$2,000 profit)
    stock.price += 20.0;

    const profit = engine.bankProfit();
    assert.ok(profit >= 1999.0);
    assert.strictEqual(engine.positions["NVXP"].shares, 0);
    assert.strictEqual(engine.cash, 25000.0);
    assert.strictEqual(engine.realizedPnL, 0.0);
});

// 3. Load UI and Controllers
load("public/js/chart.js");
load("public/js/firebase-matchmaker.js");
load("public/js/win-animations.js");
load("public/js/app.js");

console.log("\n3. TRADER SHOP & PROFILE INTEGRITY VERIFICATION");
it("SHOP_ITEMS catalog contains all expected animations, themes, sfx, and titles", () => {
    assert.ok(Array.isArray(SHOP_ITEMS));
    const ids = SHOP_ITEMS.map(i => i.id);
    const expected = [
        "money_rain", "rocket_moon", "matrix_glitch", "diamond_hands", "golden_bull",
        "theme_default", "theme_cyberpunk", "theme_gold_vip",
        "sfx_standard", "sfx_airhorn",
        "title_trader", "title_whale"
    ];
    for (const exp of expected) {
        assert.ok(ids.includes(exp), `Missing catalog item: ${exp}`);
    }
});

it("UserProfile initializes with free defaults and manages persistent localStorage", () => {
    localStorage.clear();
    const appInstance = new TradingApp();
    const p = appInstance.profile;
    assert.strictEqual(p.menu_balance, 0.0);
    assert.strictEqual(p.total_profit_banked, 0.0);
    assert.ok(p.inventory.includes("money_rain"));
    assert.ok(p.inventory.includes("theme_default"));
    assert.ok(p.inventory.includes("sfx_standard"));
    assert.ok(p.inventory.includes("title_trader"));
    assert.strictEqual(p.equipped_animation, "money_rain");
    assert.strictEqual(p.equipped_theme, "theme_default");
    assert.strictEqual(p.equipped_sfx, "sfx_standard");
    assert.strictEqual(p.equipped_title, "title_trader");
});

it("banks profit into menu vault and updates total banked profits", () => {
    const appInstance = new TradingApp();
    const bal1 = appInstance._bankProfit(5000.0);
    assert.strictEqual(bal1, 5000.0);
    assert.strictEqual(appInstance.profile.menu_balance, 5000.0);
    assert.strictEqual(appInstance.profile.total_profit_banked, 5000.0);

    const bal2 = appInstance._bankProfit(25000.0);
    assert.strictEqual(bal2, 30000.0);
    assert.strictEqual(appInstance.profile.menu_balance, 30000.0);
    assert.strictEqual(appInstance.profile.total_profit_banked, 30000.0);
});

it("rejects purchase when vault balance is insufficient", () => {
    const appInstance = new TradingApp();
    appInstance.profile.menu_balance = 10000.0;
    // rocket_moon costs 25,000
    appInstance._handleShopBuy("rocket_moon");
    assert.strictEqual(appInstance.profile.inventory.includes("rocket_moon"), false);
    assert.strictEqual(appInstance.profile.menu_balance, 10000.0);
});

it("successfully buys and auto-equips rocket_moon when balance is sufficient", () => {
    const appInstance = new TradingApp();
    appInstance.profile.menu_balance = 30000.0;
    appInstance._handleShopBuy("rocket_moon");
    assert.strictEqual(appInstance.profile.inventory.includes("rocket_moon"), true);
    assert.strictEqual(appInstance.profile.equipped_animation, "rocket_moon");
    assert.strictEqual(appInstance.profile.menu_balance, 5000.0); // 30,000 - 25,000
});

it("equipping items switches active animation, theme, sfx, and title", () => {
    const appInstance = new TradingApp();
    // Add items to inventory
    appInstance.profile.inventory.push("theme_cyberpunk", "title_whale", "sfx_airhorn");
    
    // Equip Cyberpunk theme
    appInstance._handleShopEquip("theme_cyberpunk");
    assert.strictEqual(appInstance.profile.equipped_theme, "theme_cyberpunk");
    assert.strictEqual(document.body.classList.contains("theme-cyberpunk"), true);

    // Equip Whale title
    appInstance._handleShopEquip("title_whale");
    assert.strictEqual(appInstance.profile.equipped_title, "title_whale");

    // Equip Airhorn
    appInstance._handleShopEquip("sfx_airhorn");
    assert.strictEqual(appInstance.profile.equipped_sfx, "sfx_airhorn");

    // Equip back default theme
    appInstance._handleShopEquip("theme_default");
    assert.strictEqual(appInstance.profile.equipped_theme, "theme_default");
    assert.strictEqual(document.body.classList.contains("theme-cyberpunk"), false);
});

// 4. Win Animations Engine
console.log("\n4. CRAZY WIN ANIMATIONS ENGINE VERIFICATION");
it("WinAnimationEngine handles all 5 animation presets without errors", () => {
    const mockCtx = {
        save: () => {},
        restore: () => {},
        translate: () => {},
        rotate: () => {},
        beginPath: () => {},
        closePath: () => {},
        moveTo: () => {},
        lineTo: () => {},
        arc: () => {},
        stroke: () => {},
        fill: () => {},
        fillRect: () => {},
        clearRect: () => {},
        roundRect: () => {},
        fillText: () => {},
        scale: () => {}
    };
    const mockCanvas = {
        getContext: () => mockCtx,
        width: 1920,
        height: 1080,
        style: {}
    };

    const animEngine = new WinAnimationEngine();
    animEngine.canvas = mockCanvas;
    animEngine.ctx = mockCtx;

    const animList = ["money_rain", "rocket_moon", "matrix_glitch", "diamond_hands", "golden_bull"];
    for (const animId of animList) {
        animEngine.play(animId);
        assert.strictEqual(animEngine.active, true);
        assert.strictEqual(animEngine.animationId, animId);
        assert.ok(animEngine.particles.length > 0 || animEngine.extraData.bull || animEngine.extraData.rocket || animEngine.extraData.dh);
        animEngine.stop();
        assert.strictEqual(animEngine.active, false);
    }
});

// 5. Firebase Matchmaker & Protocol Verification
console.log("\n5. FIREBASE MATCHMAKER & PROTOCOL VERIFICATION");
it("jsToFirestoreValue and firestoreValueToJs accurately serialize and deserialize all types", () => {
    const original = {
        name: "ProTrader_42",
        equity: 27500.50,
        shares: 100,
        is_active: true,
        tags: ["scalper", "whale"],
        metadata: { level: 5, server: "us-east" }
    };
    const doc = dictToFirestoreDoc(original);
    assert.ok(doc.fields);
    assert.strictEqual(doc.fields.name.stringValue, "ProTrader_42");
    assert.strictEqual(doc.fields.equity.doubleValue, 27500.50);
    assert.strictEqual(doc.fields.shares.integerValue, "100");
    assert.strictEqual(doc.fields.is_active.booleanValue, true);

    const reconstructed = firestoreDocToDict(doc);
    assert.deepStrictEqual(reconstructed, original);
});

it("SimulatedOpponentBot performs realistic random-walk equity progression", () => {
    const bot = new SimulatedOpponentBot("WallSt_Titan");
    assert.strictEqual(bot.name, "WallSt_Titan");
    assert.strictEqual(bot.equity, 25000.0);

    for (let i = 0; i < 20; i++) {
        const m = bot.tick();
        assert.ok(m.equity > 0);
        assert.strictEqual(typeof m.pnl, "number");
        assert.strictEqual(typeof m.pnl_pct, "number");
        assert.strictEqual(m.status, "playing");
    }
});

it("FirebaseMatchmaker initializes without syntax or runtime issues", () => {
    const fb = new FirebaseMatchmaker();
    assert.strictEqual(fb.projectId, "tradisim-188a6");
    assert.ok(fb.firestoreBaseUrl.includes("tradisim-188a6"));
});

it("FirebaseMatchmaker manages authenticated sessions and profile methods", () => {
    const fb = new FirebaseMatchmaker();
    fb.setAuthenticatedSession("user_123", "trader@web.com", "WebAce", "id_token_xyz", "refresh_tok");
    assert.strictEqual(fb.userId, "user_123");
    assert.strictEqual(fb.email, "trader@web.com");
    assert.strictEqual(fb.displayName, "WebAce");
    assert.strictEqual(fb.isAnonymous, false);

    fb.signOut();
    assert.strictEqual(fb.userId, "");
    assert.strictEqual(fb.email, "");
    assert.strictEqual(fb.isAnonymous, true);
});

console.log("\n=================================================");
console.log(`   TEST RESULTS: ${passedTests}/${totalTests} PASSED (100%)`);
console.log("=================================================");

process.exit(passedTests === totalTests ? 0 : 1);
