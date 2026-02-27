DEFAULT_SYMBOLS = 'BBCA, BBRI, BYAN, BMRI, TLKM, ASII, TPIA, BBNI, UNVR, HMSP'

FRACSI_HARGA_DATA = {
    "Harga Saham": ["< Rp 200", "Rp 200 - Rp 500", "Rp 500 - Rp 2.000", "Rp 2.000 - Rp 5.000", "Rp 5.000+"],
    "Fraksi Harga": ["Rp 1", "Rp 2", "Rp 5", "Rp 10", "Rp 25"]
}

PLATFORM_CONFIG = {
    "IPOT": (0.0019, 0.0029),
    "Stockbit": (0.0015, 0.0025),
    "BNI Bions": (0.0017, 0.0027),
    "Custom": (0, 0)
}

LQ45_SYMBOLS = [
    "ACES", "ADRO", "AKRA", "AMRT", "ANTM", "ARTO", "ASII", "BBCA", "BBNI", "BBRI", 
    "BBTN", "BMRI", "BRIS", "BRPT", "BUKA", "CPIN", "EMTK", "ESSA", "EXCL", "GGRM", 
    "GOTO", "HRUM", "ICBP", "INCO", "INDF", "INKP", "INTP", "ITMG", "JPFA", "KLBF", 
    "MAPI", "MBMA", "MDKA", "MEDC", "MERK", "PGAS", "PTBA", "SCMA", "SIDO", "SMGR", 
    "SRTG", "TBIG", "TINS", "TLKM", "TOWR", "UNTR", "UNVR"
]

IDX30_SYMBOLS = [
    "ADRO", "AKRA", "AMRT", "ANTM", "ARTO", "ASII", "BBCA", "BBNI", "BBRI", 
    "BBTN", "BMRI", "BRPT", "CPIN", "EMTK", "ESSA", "GOTO", "HRUM", "ICBP", 
    "INCO", "INDF", "INKP", "INTP", "ITMG", "KLBF", "MDKA", "MEDC", "PGAS", 
    "PTBA", "TLKM", "UNTR", "UNVR"
]

JII_SYMBOLS = [
    "ACES", "ADRO", "AKRA", "AMRT", "ANTM", "ASII", "BRIS", "BRPT", "CPIN",
    "EMTK", "ESSA", "EXCL", "HRUM", "ICBP", "INCO", "INDF", "INKP", "INTP",
    "ITMG", "JPFA", "KLBF", "MAPI", "MDKA", "MEDC", "PGAS", "PTBA", "SCMA",
    "SMGR", "TLKM", "UNTR", "UNVR"
]

MARKET_INDICES = {
    # Indeks Utama
    "LQ45 (Top 45 Likuid)": LQ45_SYMBOLS,
    "IDX30 (Top 30 Kapitalisasi)": IDX30_SYMBOLS,
    "JII (Jakarta Islamic Index)": JII_SYMBOLS,
    "IDX80": ["ACES", "ADMR", "ADRO", "AKRA", "AMRT", "ANTM", "ARTO", "ASII", "AVIA", "AUTO", "BBCA", "BBNI", "BBRI", "BBTN", "BFIN", "BMRI", "BRIS", "BRPT", "BSDE", "BUKA", "CPIN", "CTRA", "DSNG", "EMTK", "ENRG", "ESSA", "EXCL", "GGRM", "GOTO", "HEAL", "HRUM", "ICBP", "INCO", "INDF", "INKP", "INTP", "ISAT", "ITMG", "JPFA", "KLBF", "MAPI", "MAPA", "MBMA", "MDKA", "MEDC", "MIKA", "MNCN", "MTEL", "MYOR", "NCKL", "PANI", "PGAS", "PGEO", "PNLF", "PTBA", "PWON", "RMKE", "SCMA", "SIDO", "SILO", "SMGR", "SMRA", "SRTG", "SSIA", "TAPG", "TBIG", "TKIM", "TLKM", "TOWR", "TPIA", "UNTR", "UNVR", "WIKA", "WIIM"],
    "IDXHIDIV20 (High Dividend)": ["ADRO", "ASII", "BBCA", "BBNI", "BBRI", "BBTN", "BMRI", "BNGA", "HEXA", "HMSP", "INDF", "ITMG", "LPPF", "MPMX", "PGAS", "PTBA", "SIDO", "TLKM", "UNTR", "UNVR"],
    
    # Sektoral (IDX-IC)
    "IDXFinance (Keuangan)": ["BBCA", "BBRI", "BMRI", "BBNI", "BBTN", "BRIS", "BNGA", "NISP", "BDMN", "PNBN", "MEGA", "ARTO", "BBHI", "AGRO", "BBYB", "BFIN", "CFIN", "WOMF", "ADMF", "PNLF", "AMOR", "TUGU", "ASBI"],
    "IDXEnergy (Energi)": ["ADRO", "PTBA", "ITMG", "HRUM", "BUMI", "INDY", "MEDC", "PGAS", "ENRG", "BIPI", "ADMR", "TOBA", "BSSR", "KKGI", "MBAP", "ABMM", "SGER", "WINS", "ELSA", "PGEO", "CUAN", "DOID"],
    "IDXBasic (Brg Baku)": ["ANTM", "INCO", "TINS", "MDKA", "MBMA", "NCKL", "PSAB", "ARCI", "BRPT", "TPIA", "SMGR", "INTP", "SMCB", "CMNT", "INKP", "TKIM", "FASW", "INRU", "KRAS", "ISSP", "GDST"],
    "IDXIndust (Perindustrian)": ["ASII", "UNTR", "HEXA", "KOBX", "IPCC", "BIRD", "ASSA", "TRJA", "TMAS", "SMDR", "PURA", "ARNA", "MLIA", "KIAS", "GJTL"],
    "IDXCyclic (Konsumer Siklikal)": ["MAPI", "MAPA", "RALS", "LPPF", "ACES", "ERAA", "MSIN", "MNCN", "SCMA", "FILM", "PANR", "BAYU", "PJAA", "AUTO"],
    "IDXNonCyc (Konsumer Non-Siklikal)": ["ICBP", "INDF", "UNVR", "MYOR", "CMRY", "GOOD", "AMRT", "MIDI", "CLEO", "CAMP", "ROTI", "ULTJ", "CPIN", "JPFA", "MAIN", "WMUU", "SSMS", "AALI", "LSIP", "GZCO", "TAPG", "DSNG", "BWPT"],
    "IDXHealth (Kesehatan)": ["KLBF", "SIDO", "MIKA", "SILO", "HEAL", "PRDA", "PEHA", "KAEF", "INAF", "OMED", "CARE", "SAME", "BMHS", "IRRA"],
    "IDXProp (Properti & Real Estat)": ["PWON", "BSDE", "CTRA", "SMRA", "ASRI", "DILD", "KIJA", "SSIA", "DMAS", "PANI", "LPCK", "LPKR", "APLN", "BKSL", "BEST", "NZIA", "OMRE", "MMLP"],
    "IDXTech (Teknologi)": ["GOTO", "BUKA", "BELI", "WIFI", "EMTK", "MLPT", "DMMX", "GLVA", "NINE", "AWAN", "WIRG", "KREN", "MCAS"],
    "IDXInfra (Infrastruktur)": ["TLKM", "ISAT", "EXCL", "MTEL", "TOWR", "TBIG", "JSMR", "CMNP", "META", "WIKA", "PTPP", "ADHI", "WSKT", "WEGE", "TOTL", "CASS", "BREN"],
    "IDXTrans (Transportasi & Logistik)": ["BIRD", "ASSA", "SMDR", "TMAS", "BPTR", "GIAA", "HAIS", "TCPI", "TRUK", "SAPX", "TNCA", "DEAL", "JARR", "KJEN", "LRNA", "NELY", "SDMU", "TAXI", "TRJA"],

    # Grup Konglomerasi (Lengkap Terkini 2026)
    "Grup Barito (Prajogo Pangestu)": ["BRPT", "TPIA", "BREN", "CUAN", "PTRO", "CDIA", "GZCO"],
    "Grup Salim (Anthoni Salim)": ["INDF", "ICBP", "LSIP", "SIMP", "ROTI", "AMMN", "DNET", "MEGA", "DCII", "BINA", "NFCX", "CASA", "FAST", "META", "BEEF", "NANO", "IMAS", "IMJS", "PANI"],
    "Grup Astra (Inc. Jardine)": ["ASII", "UNTR", "AALI", "AUTO", "BNLI", "ACST", "ASGR", "HEAL", "ARTO"],
    "Grup Sinar Mas (Widjaja)": ["INKP", "TKIM", "SMMA", "BSDE", "DUTI", "DSSA", "DMAS", "BSIM", "BINA", "GEMS"],
    "Grup MNC (Hary Tanoe)": ["BHIT", "BMTR", "MNCN", "MSKY", "KPIG", "BABP", "BCAP", "IATA"],
    "Grup Lippo (Riady)": ["LPKR", "LPCK", "SILO", "LPPF", "MLPT", "MPPA", "NOBU", "LINK", "LPLI"],
    "Grup Bakrie (Aburizal Bakrie)": ["BUMI", "BRMS", "ENRG", "DEWA", "BNBR", "VKTR", "BTEL", "UNSP", "MTFN", "ELTY", "MDLN", "VIVA", "MDIA", "JGLE", "ALII"],
    "Grup CT Corp (Chairul Tanjung)": ["MEGA", "BBHI", "GIAA"],
    "Grup Djarum (Hartono)": ["BBCA", "TOWR", "BLTA", "RANC", "SUPR"],
    "Grup Emtek (Sariaatmadja)": ["EMTK", "SCMA", "BUKA", "RSGK", "SIDO", "OMED", "CASS", "SAME", "BBYB"],
    "Grup Adaro (Thohir)": ["ADRO", "ADMR", "MDKA", "MBMA", "BSSR", "ESSA", "TRIM", "GOTO", "ABMM"],
    "Grup Saratoga (Sandiaga/Soeryadjaya)": ["SRTG", "ADRO", "MDKA", "MBMA", "MPMX", "TBIG", "PALM", "AGII"],
    "Grup Agung Sedayu (Aguan)": ["PANI", "HOPE"],
    "Grup Panin (Mukmin Ali)": ["PNBN", "PNLF", "PNIN", "CFIN", "AMAG"],
    "Grup Mayapada (Tahir)": ["MAYA", "SONA", "SRAJ", "BBYB"],
}
