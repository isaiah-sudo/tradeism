"""
Stock Universe: 100 diverse, volatile intraday stocks across 10 sectors.
"""

STOCK_DEFINITIONS = [
    # 1. AI, Tech & Semiconductors (10 stocks)
    ("NVXP", "NovaX AI Tech", "AI & Tech", 84.50, 0.018),
    ("AIPL", "Apex Intelligence Labs", "AI & Tech", 142.30, 0.020),
    ("QLAB", "Quantum Compute Labs", "AI & Tech", 65.20, 0.022),
    ("DATX", "DataCloud Matrix", "AI & Tech", 38.40, 0.019),
    ("CYBR", "CyberShield Sentinel", "AI & Tech", 52.10, 0.017),
    ("ROBO", "Automata Robotics", "AI & Tech", 29.80, 0.024),
    ("CHIP", "Silicon Foundry Corp", "AI & Tech", 112.50, 0.016),
    ("NEUR", "NeuralSync Systems", "AI & Tech", 44.75, 0.025),
    ("SaaS", "OmniCloud Software", "AI & Tech", 78.90, 0.015),
    ("OPTC", "Photonics NanoOptics", "AI & Tech", 19.30, 0.023),

    # 2. Meme & Retail WallStreetBets Squeezes (10 stocks)
    ("MOON", "Lunar Rocket Labs", "Meme & Retail", 12.20, 0.035),
    ("APES", "Diamond Hands Retail", "Meme & Retail", 8.40, 0.038),
    ("STON", "Stonks Infinite Inc", "Meme & Retail", 4.50, 0.042),
    ("YOLO", "High Leverage Holdings", "Meme & Retail", 15.60, 0.036),
    ("DIAM", "Diamond Core Gems", "Meme & Retail", 6.80, 0.040),
    ("HODL", "Retain Capital Group", "Meme & Retail", 3.25, 0.044),
    ("TEND", "Crispy Gains Ventures", "Meme & Retail", 18.90, 0.032),
    ("MEME", "Viral Trend Network", "Meme & Retail", 7.10, 0.039),
    ("WEN", "Moon Lambo Corp", "Meme & Retail", 9.45, 0.034),
    ("DOGE", "Shiba Retail Stores", "Meme & Retail", 2.80, 0.045),

    # 3. Biotech, Oncology & Genomics (10 stocks)
    ("BIOX", "BioCure Genetics", "Biotech", 38.40, 0.028),
    ("DRUG", "PharmaCure Therapeutics", "Biotech", 22.10, 0.032),
    ("GENE", "Genome CRISPR Science", "Biotech", 48.70, 0.026),
    ("CRSP", "Targeted Gene Splicers", "Biotech", 62.00, 0.024),
    ("VACC", "VaxImmune Labs", "Biotech", 17.50, 0.034),
    ("CURE", "OncoCell BioPharma", "Biotech", 11.80, 0.036),
    ("PHRM", "NovaMedica Solutions", "Biotech", 85.30, 0.018),
    ("CLIN", "Clinical Trials Plus", "Biotech", 27.60, 0.027),
    ("TMRX", "TumorX Diagnostics", "Biotech", 14.90, 0.033),
    ("HEAL", "Regenerative Stem Cell", "Biotech", 9.20, 0.037),

    # 4. Crypto, Blockchain & Web3 (10 stocks)
    ("CRPT", "BlockBit Labs", "Crypto & Web3", 22.80, 0.030),
    ("BCON", "Beacon Chain Ventures", "Crypto & Web3", 34.50, 0.028),
    ("ETHX", "SmartContract Infra", "Crypto & Web3", 56.40, 0.026),
    ("BLOK", "Decentralized Ledger", "Crypto & Web3", 14.10, 0.034),
    ("DEFI", "Liquidity Pool Group", "Crypto & Web3", 8.90, 0.038),
    ("COIN", "Digital Exchange Pro", "Crypto & Web3", 125.00, 0.022),
    ("HASH", "MegaWatt Mining Co", "Crypto & Web3", 6.40, 0.041),
    ("SATX", "SatVault Treasury", "Crypto & Web3", 42.10, 0.027),
    ("LEDG", "Hardware Key Secure", "Crypto & Web3", 19.80, 0.029),
    ("MINT", "Tokenized Real Assets", "Crypto & Web3", 11.20, 0.035),

    # 5. Clean Energy, EV & Batteries (10 stocks)
    ("APEX", "Apex Green Energy", "Clean Energy", 45.10, 0.020),
    ("VOLT", "HyperVolt Motors EV", "Clean Energy", 32.70, 0.025),
    ("SOLR", "Helios Solar Power", "Clean Energy", 18.40, 0.023),
    ("WIND", "AeroTurbine Energy", "Clean Energy", 26.90, 0.021),
    ("NEXU", "Nexus Smart Grid", "Clean Energy", 39.50, 0.019),
    ("BATT", "SolidState Cell Corp", "Clean Energy", 54.20, 0.024),
    ("HYDR", "HydroFuel Clean H2", "Clean Energy", 13.80, 0.031),
    ("ATOM", "Small Modular Nuclear", "Clean Energy", 72.00, 0.022),
    ("LITH", "Lithium Brine Miners", "Clean Energy", 21.60, 0.028),
    ("ELEC", "GridCharge Infra", "Clean Energy", 16.30, 0.027),

    # 6. Defense, Space & Aerospace (10 stocks)
    ("ROCK", "Orbital Rocket Dynamics", "Aerospace & Defense", 58.60, 0.022),
    ("ORBT", "Constellation Satellite", "Aerospace & Defense", 24.30, 0.026),
    ("SPAC", "DeepSpace Exploration", "Aerospace & Defense", 16.70, 0.030),
    ("AERO", "Supersonic Aero Defense", "Aerospace & Defense", 94.20, 0.016),
    ("LOCK", "Aegis Defense Systems", "Aerospace & Defense", 180.50, 0.014),
    ("DRON", "Autonomous Drone Swarm", "Aerospace & Defense", 31.40, 0.027),
    ("DEFN", "Patriot Armaments", "Aerospace & Defense", 67.80, 0.017),
    ("STAR", "StarComm Relay Corp", "Aerospace & Defense", 41.20, 0.023),
    ("MISL", "Hypersonic Guidance Inc", "Aerospace & Defense", 118.00, 0.018),
    ("SATL", "Earth Imager MicroSats", "Aerospace & Defense", 12.90, 0.031),

    # 7. Finance, Commodities & Gold (10 stocks)
    ("GOLD", "Apex Gold Bullion Mine", "Finance & Commodities", 76.40, 0.017),
    ("SILV", "Sterling Silver Reserves", "Finance & Commodities", 28.10, 0.022),
    ("BANK", "Horizon Merchant Bank", "Finance & Commodities", 55.30, 0.015),
    ("PAYX", "InstantPay Global Net", "Finance & Commodities", 92.40, 0.018),
    ("LOAN", "PeerLend Micro Credit", "Finance & Commodities", 14.50, 0.029),
    ("COMM", "Commodities Global Desk", "Finance & Commodities", 46.80, 0.019),
    ("PRME", "Prime Brokerage Group", "Finance & Commodities", 135.00, 0.014),
    ("CAPX", "Venture Growth Equity", "Finance & Commodities", 33.20, 0.023),
    ("FINT", "AlgoTrading Software", "Finance & Commodities", 68.70, 0.020),
    ("URAN", "Yellowcake Uranium Corp", "Finance & Commodities", 23.90, 0.026),

    # 8. Consumer, Gaming & Media (10 stocks)
    ("PLAY", "NextGen Interactive", "Consumer & Media", 36.80, 0.021),
    ("VRXX", "Oasis VR Holographics", "Consumer & Media", 27.40, 0.028),
    ("GAME", "PixelStorm Studios", "Consumer & Media", 42.50, 0.024),
    ("STRM", "OmniStream Media Net", "Consumer & Media", 88.00, 0.018),
    ("BEVG", "Pulse Energy Drinks", "Consumer & Media", 51.30, 0.016),
    ("FOOD", "PlantMeat Alternative", "Consumer & Media", 15.20, 0.032),
    ("FASH", "Luxe Apparel Global", "Consumer & Media", 64.90, 0.017),
    ("CHEF", "Ghost Kitchen Franchise", "Consumer & Media", 9.80, 0.034),
    ("CASN", "Grand Mirage Gaming", "Consumer & Media", 31.10, 0.023),
    ("TOYS", "Collectibles & Hobby", "Consumer & Media", 13.60, 0.029),

    # 9. Shipping, Transport & Logistics (10 stocks)
    ("SHIP", "Oceanic Container Lines", "Logistics & Transport", 41.50, 0.022),
    ("RAIL", "CrossCountry Freight", "Logistics & Transport", 110.20, 0.013),
    ("FLYX", "AirCargo Express Jet", "Logistics & Transport", 35.80, 0.021),
    ("CARG", "Global Port Terminals", "Logistics & Transport", 29.40, 0.020),
    ("TANK", "Crude Supertankers", "Logistics & Transport", 19.50, 0.027),
    ("LOGX", "Autonomous Warehouse", "Logistics & Transport", 48.30, 0.022),
    ("PORT", "Pacific Docklands Inc", "Logistics & Transport", 57.60, 0.016),
    ("TRUK", "LongHaul Fleet EV", "Logistics & Transport", 16.80, 0.028),
    ("DELV", "LastMile Delivery Drone", "Logistics & Transport", 22.40, 0.025),
    ("RAXX", "Intermodal Container Co", "Logistics & Transport", 38.10, 0.019),

    # 10. Penny Stocks & Wildcard Scalpers (10 stocks)
    ("PUMP", "Penny Surge Holdings", "Penny Wildcard", 1.25, 0.048),
    ("PENY", "MicroCap Innovations", "Penny Wildcard", 0.85, 0.050),
    ("RISK", "High Stakes Biotech", "Penny Wildcard", 2.10, 0.045),
    ("WILD", "Volatile Asset Trust", "Penny Wildcard", 3.40, 0.042),
    ("SPEC", "Speculative Venture Co", "Penny Wildcard", 1.75, 0.046),
    ("ZERO", "Near-Zero Tech Lab", "Penny Wildcard", 0.65, 0.052),
    ("LEAP", "Moonshot Options Corp", "Penny Wildcard", 4.15, 0.041),
    ("BOOM", "Explosive Growth Inc", "Penny Wildcard", 2.85, 0.044),
    ("DUMP", "Turnaround Scrap Corp", "Penny Wildcard", 1.40, 0.047),
    ("LOTO", "Lottery Ticket Biotech", "Penny Wildcard", 0.95, 0.050),
]
