/**
 * Breaking News Catalyst Engine for Web Terminal.
 * Identical templates, sentiment, shock multipliers, and momentum drifts to desktop version.
 */

class NewsGenerator {
    constructor(rng = Math.random) {
        this.rng = rng;
        this._nextId = 1;

        this.sectorTemplates = {
            "AI & Tech": [
                { headline: "{name} ({ticker}) reveals next-gen Quantum AI architecture crushing industry benchmarks!", sentiment: "BULLISH", shock: 0.22, drift: 0.035, importance: "BREAKING" },
                { headline: "Whistleblower leaks internal memos claiming {name} ({ticker}) software capabilities are fabricated.", sentiment: "BEARISH", shock: -0.25, drift: -0.040, importance: "BREAKING" },
                { headline: "Cloud hyper-scaler signs massive $10B exclusive infrastructure contract with {name} ({ticker})!", sentiment: "BULLISH", shock: 0.18, drift: 0.025, importance: "MAJOR" },
                { headline: "Cybersecurity emergency: Critical zero-day vulnerability detected in {name} ({ticker}) core stack.", sentiment: "BEARISH", shock: -0.16, drift: -0.025, importance: "MAJOR" },
                { headline: "Silicon Valley venture giant initiates aggressive accumulation of {name} ({ticker}) stock.", sentiment: "BULLISH", shock: 0.11, drift: 0.015, importance: "RUMOR" }
            ],
            "Meme & Retail": [
                { headline: "r/WallStreetBets coordinates massive gamma squeeze on {ticker}! Short sellers scrambling!", sentiment: "BULLISH", shock: 0.32, drift: 0.055, importance: "BREAKING" },
                { headline: "{name} ({ticker}) management announces 20-million share secondary offering directly into rally!", sentiment: "BEARISH", shock: -0.28, drift: -0.045, importance: "BREAKING" },
                { headline: "Celebrity billionaire tweets cryptic rocket emoji pointing to {ticker}!", sentiment: "BULLISH", shock: 0.19, drift: 0.030, importance: "RUMOR" },
                { headline: "Retail brokers throttle trading volume and leverage on {ticker} citing volatility.", sentiment: "BEARISH", shock: -0.14, drift: -0.020, importance: "MAJOR" },
                { headline: "Viral social media movement pledges to 'never sell' {ticker} shares until astronomical targets!", sentiment: "BULLISH", shock: 0.15, drift: 0.025, importance: "RUMOR" }
            ],
            "Biotech": [
                { headline: "FDA grants Breakthrough Therapy Designation for {name}'s ({ticker}) flagship clinical pipeline!", sentiment: "BULLISH", shock: 0.38, drift: 0.065, importance: "BREAKING" },
                { headline: "Phase 3 clinical trial for {name} ({ticker}) suspended abruptly after patient complications!", sentiment: "BEARISH", shock: -0.42, drift: -0.075, importance: "BREAKING" },
                { headline: "Global pharmaceutical giant approaches {name} ({ticker}) with unsolicited takeover proposal.", sentiment: "BULLISH", shock: 0.24, drift: 0.035, importance: "MAJOR" },
                { headline: "Notorious short-seller fund releases devastating investigative exposé on {ticker} efficacy data.", sentiment: "BEARISH", shock: -0.20, drift: -0.035, importance: "RUMOR" },
                { headline: "New England Journal of Medicine publishes peer-reviewed accolades for {ticker} therapeutic results.", sentiment: "BULLISH", shock: 0.16, drift: 0.020, importance: "MAJOR" }
            ],
            "Crypto & Web3": [
                { headline: "Major banking consortium deploys settlement network on {name} ({ticker}) blockchain!", sentiment: "BULLISH", shock: 0.26, drift: 0.040, importance: "BREAKING" },
                { headline: "Regulators issue emergency cease-and-desist against {name} ({ticker}) crypto protocol!", sentiment: "BEARISH", shock: -0.32, drift: -0.050, importance: "BREAKING" },
                { headline: "Sovereign wealth fund confirms strategic digital asset allocation with {ticker}.", sentiment: "BULLISH", shock: 0.18, drift: 0.030, importance: "MAJOR" },
                { headline: "Multi-million dollar bridge hack drains liquidity pools linked to {ticker}.", sentiment: "BEARISH", shock: -0.19, drift: -0.030, importance: "MAJOR" },
                { headline: "Speculation mounts regarding imminent tier-1 exchange listing and derivatives for {ticker}.", sentiment: "BULLISH", shock: 0.12, drift: 0.020, importance: "RUMOR" }
            ],
            "Clean Energy": [
                { headline: "{name} ({ticker}) awarded landmark multi-billion dollar clean federal energy grant!", sentiment: "BULLISH", shock: 0.25, drift: 0.035, importance: "BREAKING" },
                { headline: "Key supply chain bottlenecks force {name} ({ticker}) to slash full-year production guidance in half!", sentiment: "BEARISH", shock: -0.22, drift: -0.035, importance: "BREAKING" },
                { headline: "Breakthrough in energy efficiency patent puts {name} ({ticker}) years ahead of rivals.", sentiment: "BULLISH", shock: 0.17, drift: 0.025, importance: "MAJOR" },
                { headline: "Tariff dispute threatens raw material supplies essential for {ticker} facilities.", sentiment: "BEARISH", shock: -0.15, drift: -0.020, importance: "MAJOR" }
            ],
            "Aerospace & Defense": [
                { headline: "Pentagon awards {name} ({ticker}) classified next-gen defense contract!", sentiment: "BULLISH", shock: 0.23, drift: 0.030, importance: "BREAKING" },
                { headline: "Rocket launch vehicle from {name} ({ticker}) suffers catastrophic pad anomaly during test.", sentiment: "BEARISH", shock: -0.24, drift: -0.035, importance: "BREAKING" },
                { headline: "Allied nations place massive export orders for {ticker} autonomous defense systems.", sentiment: "BULLISH", shock: 0.15, drift: 0.020, importance: "MAJOR" },
                { headline: "Congressional oversight committee probes cost overruns at {ticker} aerospace division.", sentiment: "BEARISH", shock: -0.12, drift: -0.015, importance: "RUMOR" }
            ],
            "Finance & Commodities": [
                { headline: "Record gold & commodity price surges drive monster earnings for {name} ({ticker})!", sentiment: "BULLISH", shock: 0.20, drift: 0.025, importance: "BREAKING" },
                { headline: "Severe regulatory audit reveals reserve shortfalls at {name} ({ticker})!", sentiment: "BEARISH", shock: -0.26, drift: -0.040, importance: "BREAKING" },
                { headline: "Global central bank liquidity expansion triggers massive rally in {ticker}.", sentiment: "BULLISH", shock: 0.14, drift: 0.020, importance: "MAJOR" },
                { headline: "Credit rating agency downgrades {name} ({ticker}) to junk status on debt concerns.", sentiment: "BEARISH", shock: -0.18, drift: -0.025, importance: "MAJOR" }
            ],
            "Consumer & Media": [
                { headline: "{name}'s ({ticker}) new interactive release sets all-time viral engagement records!", sentiment: "BULLISH", shock: 0.19, drift: 0.025, importance: "BREAKING" },
                { headline: "Mass consumer boycott erupts against {name} ({ticker}) following public relations debacle.", sentiment: "BEARISH", shock: -0.21, drift: -0.030, importance: "BREAKING" },
                { headline: "Subscription numbers beat Wall Street estimates by 400% for {ticker}.", sentiment: "BULLISH", shock: 0.13, drift: 0.020, importance: "MAJOR" },
                { headline: "Streaming piracy and copyright disputes cloud revenue outlook for {ticker}.", sentiment: "BEARISH", shock: -0.11, drift: -0.015, importance: "RUMOR" }
            ],
            "Logistics & Transport": [
                { headline: "Freight rates skyrocket 250% following canal blockage; {name} ({ticker}) profits explode!", sentiment: "BULLISH", shock: 0.24, drift: 0.030, importance: "BREAKING" },
                { headline: "Dockworkers strike shuts down all operations for {name} ({ticker}) indefinitely!", sentiment: "BEARISH", shock: -0.25, drift: -0.035, importance: "BREAKING" },
                { headline: "Major e-commerce giant signs 5-year priority logistics agreement with {ticker}.", sentiment: "BULLISH", shock: 0.15, drift: 0.020, importance: "MAJOR" },
                { headline: "Fuel surcharge spike eats deeply into {ticker} operating margins.", sentiment: "BEARISH", shock: -0.12, drift: -0.018, importance: "MAJOR" }
            ],
            "Penny Wildcard": [
                { headline: "MICRO-CAP MANIA: Penny stock {name} ({ticker}) explodes +45% on astronomical buying volume!", sentiment: "BULLISH", shock: 0.45, drift: 0.070, importance: "BREAKING" },
                { headline: "SEC halts trading on {ticker} pending investigation into unlawful pump-and-dump promotion!", sentiment: "BEARISH", shock: -0.48, drift: -0.080, importance: "BREAKING" },
                { headline: "Subreddit trading army discovers low-float penny stock {ticker}! Rocket initiated!", sentiment: "BULLISH", shock: 0.35, drift: 0.050, importance: "RUMOR" },
                { headline: "Dilution alert: {name} ({ticker}) files toxic convertible debt financing.", sentiment: "BEARISH", shock: -0.30, drift: -0.045, importance: "MAJOR" }
            ]
        };

        this.marketTemplates = [
            { headline: "Federal Reserve unexpectedly slashes interest rates by 50 bps! Equity markets explode higher!", sentiment: "BULLISH", shock: 0.08, drift: 0.020, importance: "BREAKING" },
            { headline: "Inflation print comes in blistering hot! Fed hints at emergency rate hikes; broad sell-off!", sentiment: "BEARISH", shock: -0.09, drift: -0.025, importance: "BREAKING" },
            { headline: "Global geopolitical tension eases; international trade flows resume normalized pace.", sentiment: "BULLISH", shock: 0.06, drift: 0.015, importance: "MAJOR" },
            { headline: "Sudden oil supply disruption triggers inflation fears across all financial sectors.", sentiment: "BEARISH", shock: -0.07, drift: -0.018, importance: "MAJOR" },
            { headline: "Treasury yields tumble as central banks inject liquidity back into interbank lending.", sentiment: "BULLISH", shock: 0.07, drift: 0.015, importance: "MAJOR" }
        ];
    }

    setRng(rng) {
        this.rng = rng;
    }

    generateRandomNews(availableStocks) {
        let template;
        let ticker = "MARKET";
        let headline = "";
        let sentiment = "NEUTRAL";
        let baseShock = 0;
        let baseDrift = 0;
        let importance = "BREAKING";

        if (this.rng() < 0.15 || !availableStocks || availableStocks.length === 0) {
            template = this.marketTemplates[Math.floor(this.rng() * this.marketTemplates.length)];
            ticker = "MARKET";
            headline = template.headline;
            sentiment = template.sentiment;
            baseShock = template.shock;
            baseDrift = template.drift;
            importance = template.importance;
        } else {
            const stock = availableStocks[Math.floor(this.rng() * availableStocks.length)];
            ticker = stock.ticker;
            const sector = stock.sector;
            const templates = this.sectorTemplates[sector] || this.sectorTemplates["AI & Tech"];
            template = templates[Math.floor(this.rng() * templates.length)];

            headline = template.headline.replace("{name}", stock.name).replace("{ticker}", ticker);
            sentiment = template.sentiment;
            baseShock = template.shock;
            baseDrift = template.drift;
            importance = template.importance;
        }

        const variance = 0.85 + (this.rng() * 0.40); // 0.85 to 1.25
        const shock = Number((baseShock * variance).toFixed(3));
        const drift = Number((baseDrift * variance).toFixed(4));

        const now = Date.now() / 1000;
        const d = new Date();
        const timeStr = [
            String(d.getHours()).padStart(2, '0'),
            String(d.getMinutes()).padStart(2, '0'),
            String(d.getSeconds()).padStart(2, '0')
        ].join(':');

        return {
            id: this._nextId++,
            timestamp: now,
            timeStr: timeStr,
            ticker: ticker,
            headline: headline,
            sentiment: sentiment,
            shockPct: shock,
            momentumDrift: drift,
            importance: importance
        };
    }
}
