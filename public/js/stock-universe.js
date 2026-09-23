/**
 * Stock Universe: 100 diverse, volatile intraday stocks across 10 sectors.
 * Matches desktop Day Trading Simulator definitions.
 */

const STOCK_DEFINITIONS = [
    // 1. AI, Tech & Semiconductors (10 stocks)
    { ticker: "NVXP", name: "NovaX AI Tech", sector: "AI & Tech", price: 84.50, volatility: 0.018 },
    { ticker: "AIPL", name: "Apex Intelligence Labs", sector: "AI & Tech", price: 142.30, volatility: 0.020 },
    { ticker: "QLAB", name: "Quantum Compute Labs", sector: "AI & Tech", price: 65.20, volatility: 0.022 },
    { ticker: "DATX", name: "DataCloud Matrix", sector: "AI & Tech", price: 38.40, volatility: 0.019 },
    { ticker: "CYBR", name: "CyberShield Sentinel", sector: "AI & Tech", price: 52.10, volatility: 0.017 },
    { ticker: "ROBO", name: "Automata Robotics", sector: "AI & Tech", price: 29.80, volatility: 0.024 },
    { ticker: "CHIP", name: "Silicon Foundry Corp", sector: "AI & Tech", price: 112.50, volatility: 0.016 },
    { ticker: "NEUR", name: "NeuralSync Systems", sector: "AI & Tech", price: 44.75, volatility: 0.025 },
    { ticker: "SaaS", name: "OmniCloud Software", sector: "AI & Tech", price: 78.90, volatility: 0.015 },
    { ticker: "OPTC", name: "Photonics NanoOptics", sector: "AI & Tech", price: 19.30, volatility: 0.023 },

    // 2. Meme & Retail WallStreetBets Squeezes (10 stocks)
    { ticker: "MOON", name: "Lunar Rocket Labs", sector: "Meme & Retail", price: 12.20, volatility: 0.035 },
    { ticker: "APES", name: "Diamond Hands Retail", sector: "Meme & Retail", price: 8.40, volatility: 0.038 },
    { ticker: "STON", name: "Stonks Infinite Inc", sector: "Meme & Retail", price: 4.50, volatility: 0.042 },
    { ticker: "YOLO", name: "High Leverage Holdings", sector: "Meme & Retail", price: 15.60, volatility: 0.036 },
    { ticker: "DIAM", name: "Diamond Core Gems", sector: "Meme & Retail", price: 6.80, volatility: 0.040 },
    { ticker: "HODL", name: "Retain Capital Group", sector: "Meme & Retail", price: 3.25, volatility: 0.044 },
    { ticker: "TEND", name: "Crispy Gains Ventures", sector: "Meme & Retail", price: 18.90, volatility: 0.032 },
    { ticker: "MEME", name: "Viral Trend Network", sector: "Meme & Retail", price: 7.10, volatility: 0.039 },
    { ticker: "WEN",  name: "Moon Lambo Corp", sector: "Meme & Retail", price: 9.45, volatility: 0.034 },
    { ticker: "DOGE", name: "Shiba Retail Stores", sector: "Meme & Retail", price: 2.80, volatility: 0.045 },

    // 3. Biotech, Oncology & Genomics (10 stocks)
    { ticker: "BIOX", name: "BioCure Genetics", sector: "Biotech", price: 38.40, volatility: 0.028 },
    { ticker: "DRUG", name: "PharmaCure Therapeutics", sector: "Biotech", price: 22.10, volatility: 0.032 },
    { ticker: "GENE", name: "Genome CRISPR Science", sector: "Biotech", price: 48.70, volatility: 0.026 },
    { ticker: "CRSP", name: "Targeted Gene Splicers", sector: "Biotech", price: 62.00, volatility: 0.024 },
    { ticker: "VACC", name: "VaxImmune Labs", sector: "Biotech", price: 17.50, volatility: 0.034 },
    { ticker: "CURE", name: "OncoCell BioPharma", sector: "Biotech", price: 11.80, volatility: 0.036 },
    { ticker: "PHRM", name: "NovaMedica Solutions", sector: "Biotech", price: 85.30, volatility: 0.018 },
    { ticker: "CLIN", name: "Clinical Trials Plus", sector: "Biotech", price: 27.60, volatility: 0.027 },
    { ticker: "TMRX", name: "TumorX Diagnostics", sector: "Biotech", price: 14.90, volatility: 0.033 },
    { ticker: "HEAL", name: "Regenerative Stem Cell", sector: "Biotech", price: 9.20, volatility: 0.037 },

    // 4. Crypto, Blockchain & Web3 (10 stocks)
    { ticker: "CRPT", name: "BlockBit Labs", sector: "Crypto & Web3", price: 22.80, volatility: 0.030 },
    { ticker: "BCON", name: "Beacon Chain Ventures", sector: "Crypto & Web3", price: 34.50, volatility: 0.028 },
    { ticker: "ETHX", name: "SmartContract Infra", sector: "Crypto & Web3", price: 56.40, volatility: 0.026 },
    { ticker: "BLOK", name: "Decentralized Ledger", sector: "Crypto & Web3", price: 14.10, volatility: 0.034 },
    { ticker: "DEFI", name: "Liquidity Pool Group", sector: "Crypto & Web3", price: 8.90, volatility: 0.038 },
    { ticker: "COIN", name: "Digital Exchange Pro", sector: "Crypto & Web3", price: 125.00, volatility: 0.022 },
    { ticker: "HASH", name: "MegaWatt Mining Co", sector: "Crypto & Web3", price: 6.40, volatility: 0.041 },
    { ticker: "SATX", name: "SatVault Treasury", sector: "Crypto & Web3", price: 42.10, volatility: 0.027 },
    { ticker: "LEDG", name: "Hardware Key Secure", sector: "Crypto & Web3", price: 19.80, volatility: 0.029 },
    { ticker: "MINT", name: "Tokenized Real Assets", sector: "Crypto & Web3", price: 11.20, volatility: 0.035 },

    // 5. Clean Energy, EV & Batteries (10 stocks)
    { ticker: "APEX", name: "Apex Green Energy", sector: "Clean Energy", price: 45.10, volatility: 0.020 },
    { ticker: "VOLT", name: "HyperVolt Motors EV", sector: "Clean Energy", price: 32.70, volatility: 0.025 },
    { ticker: "SOLR", name: "Helios Solar Power", sector: "Clean Energy", price: 18.40, volatility: 0.023 },
    { ticker: "WIND", name: "AeroTurbine Energy", sector: "Clean Energy", price: 26.90, volatility: 0.021 },
    { ticker: "NEXU", name: "Nexus Smart Grid", sector: "Clean Energy", price: 39.50, volatility: 0.019 },
    { ticker: "BATT", name: "SolidState Cell Corp", sector: "Clean Energy", price: 54.20, volatility: 0.024 },
    { ticker: "HYDR", name: "HydroFuel Clean H2", sector: "Clean Energy", price: 13.80, volatility: 0.031 },
    { ticker: "ATOM", name: "Small Modular Nuclear", sector: "Clean Energy", price: 72.00, volatility: 0.022 },
    { ticker: "LITH", name: "Lithium Brine Miners", sector: "Clean Energy", price: 21.60, volatility: 0.028 },
    { ticker: "ELEC", name: "GridCharge Infra", sector: "Clean Energy", price: 16.30, volatility: 0.027 },

    // 6. Defense, Space & Aerospace (10 stocks)
    { ticker: "ROCK", name: "Orbital Rocket Dynamics", sector: "Aerospace & Defense", price: 58.60, volatility: 0.022 },
    { ticker: "ORBT", name: "Constellation Satellite", sector: "Aerospace & Defense", price: 24.30, volatility: 0.026 },
    { ticker: "SPAC", name: "DeepSpace Exploration", sector: "Aerospace & Defense", price: 16.70, volatility: 0.030 },
    { ticker: "AERO", name: "Supersonic Aero Defense", sector: "Aerospace & Defense", price: 94.20, volatility: 0.016 },
    { ticker: "LOCK", name: "Aegis Defense Systems", sector: "Aerospace & Defense", price: 180.50, volatility: 0.014 },
    { ticker: "DRON", name: "Autonomous Drone Swarm", sector: "Aerospace & Defense", price: 31.40, volatility: 0.027 },
    { ticker: "DEFN", name: "Patriot Armaments", sector: "Aerospace & Defense", price: 67.80, volatility: 0.017 },
    { ticker: "STAR", name: "StarComm Relay Corp", sector: "Aerospace & Defense", price: 41.20, volatility: 0.023 },
    { ticker: "MISL", name: "Hypersonic Guidance Inc", sector: "Aerospace & Defense", price: 118.00, volatility: 0.018 },
    { ticker: "SATL", name: "Earth Imager MicroSats", sector: "Aerospace & Defense", price: 12.90, volatility: 0.031 },

    // 7. Finance, Commodities & Gold (10 stocks)
    { ticker: "GOLD", name: "Apex Gold Bullion Mine", sector: "Finance & Commodities", price: 76.40, volatility: 0.017 },
    { ticker: "SILV", name: "Sterling Silver Reserves", sector: "Finance & Commodities", price: 28.10, volatility: 0.022 },
    { ticker: "BANK", name: "Horizon Merchant Bank", sector: "Finance & Commodities", price: 55.30, volatility: 0.015 },
    { ticker: "PAYX", name: "InstantPay Global Net", sector: "Finance & Commodities", price: 92.40, volatility: 0.018 },
    { ticker: "LOAN", name: "PeerLend Micro Credit", sector: "Finance & Commodities", price: 14.50, volatility: 0.029 },
    { ticker: "COMM", name: "Commodities Global Desk", sector: "Finance & Commodities", price: 46.80, volatility: 0.019 },
    { ticker: "PRME", name: "Prime Brokerage Group", sector: "Finance & Commodities", price: 135.00, volatility: 0.014 },
    { ticker: "CAPX", name: "Venture Growth Equity", sector: "Finance & Commodities", price: 33.20, volatility: 0.023 },
    { ticker: "FINT", name: "AlgoTrading Software", sector: "Finance & Commodities", price: 68.70, volatility: 0.020 },
    { ticker: "URAN", name: "Yellowcake Uranium Corp", sector: "Finance & Commodities", price: 23.90, volatility: 0.026 },

    // 8. Consumer, Gaming & Media (10 stocks)
    { ticker: "PLAY", name: "NextGen Interactive", sector: "Consumer & Media", price: 36.80, volatility: 0.021 },
    { ticker: "VRXX", name: "Oasis VR Holographics", sector: "Consumer & Media", price: 27.40, volatility: 0.028 },
    { ticker: "GAME", name: "PixelStorm Studios", sector: "Consumer & Media", price: 42.50, volatility: 0.024 },
    { ticker: "STRM", name: "OmniStream Media Net", sector: "Consumer & Media", price: 88.00, volatility: 0.018 },
    { ticker: "BEVG", name: "Pulse Energy Drinks", sector: "Consumer & Media", price: 51.30, volatility: 0.016 },
    { ticker: "FOOD", name: "PlantMeat Alternative", sector: "Consumer & Media", price: 15.20, volatility: 0.032 },
    { ticker: "FASH", name: "Luxe Apparel Global", sector: "Consumer & Media", price: 64.90, volatility: 0.017 },
    { ticker: "CHEF", name: "Ghost Kitchen Franchise", sector: "Consumer & Media", price: 9.80, volatility: 0.034 },
    { ticker: "CASN", name: "Grand Mirage Gaming", sector: "Consumer & Media", price: 31.10, volatility: 0.023 },
    { ticker: "TOYS", name: "Collectibles & Hobby", sector: "Consumer & Media", price: 13.60, volatility: 0.029 },

    // 9. Shipping, Transport & Logistics (10 stocks)
    { ticker: "SHIP", name: "Oceanic Container Lines", sector: "Logistics & Transport", price: 41.50, volatility: 0.022 },
    { ticker: "RAIL", name: "CrossCountry Freight", sector: "Logistics & Transport", price: 110.20, volatility: 0.013 },
    { ticker: "FLYX", name: "AirCargo Express Jet", sector: "Logistics & Transport", price: 35.80, volatility: 0.021 },
    { ticker: "CARG", name: "Global Port Terminals", sector: "Logistics & Transport", price: 29.40, volatility: 0.020 },
    { ticker: "TANK", name: "Crude Supertankers", sector: "Logistics & Transport", price: 19.50, volatility: 0.027 },
    { ticker: "LOGX", name: "Autonomous Warehouse", sector: "Logistics & Transport", price: 48.30, volatility: 0.022 },
    { ticker: "PORT", name: "Pacific Docklands Inc", sector: "Logistics & Transport", price: 57.60, volatility: 0.016 },
    { ticker: "TRUK", name: "LongHaul Fleet EV", sector: "Logistics & Transport", price: 16.80, volatility: 0.028 },
    { ticker: "DELV", name: "LastMile Delivery Drone", sector: "Logistics & Transport", price: 22.40, volatility: 0.025 },
    { ticker: "RAXX", name: "Intermodal Container Co", sector: "Logistics & Transport", price: 38.10, volatility: 0.019 },

    // 10. Penny Stocks & Wildcard Scalpers (10 stocks)
    { ticker: "PUMP", name: "Penny Surge Holdings", sector: "Penny Wildcard", price: 1.25, volatility: 0.048 },
    { ticker: "PENY", name: "MicroCap Innovations", sector: "Penny Wildcard", price: 0.85, volatility: 0.050 },
    { ticker: "RISK", name: "High Stakes Biotech", sector: "Penny Wildcard", price: 2.10, volatility: 0.045 },
    { ticker: "WILD", name: "Volatile Asset Trust", sector: "Penny Wildcard", price: 3.40, volatility: 0.042 },
    { ticker: "SPEC", name: "Speculative Venture Co", sector: "Penny Wildcard", price: 1.75, volatility: 0.046 },
    { ticker: "ZERO", name: "Near-Zero Tech Lab", sector: "Penny Wildcard", price: 0.65, volatility: 0.052 },
    { ticker: "LEAP", name: "Moonshot Options Corp", sector: "Penny Wildcard", price: 4.15, volatility: 0.041 },
    { ticker: "BOOM", name: "Explosive Growth Inc", sector: "Penny Wildcard", price: 2.85, volatility: 0.044 },
    { ticker: "DUMP", name: "Turnaround Scrap Corp", sector: "Penny Wildcard", price: 1.40, volatility: 0.047 },
    { ticker: "LOTO", name: "Lottery Ticket Biotech", sector: "Penny Wildcard", price: 0.95, volatility: 0.050 }
];

const SECTORS = [
    "All",
    "AI & Tech",
    "Meme & Retail",
    "Biotech",
    "Crypto & Web3",
    "Clean Energy",
    "Aerospace & Defense",
    "Finance & Commodities",
    "Consumer & Media",
    "Logistics & Transport",
    "Penny Wildcard"
];
