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
    "AADI", "ADMR", "ADRO", "AKRA", "AMMN", "AMRT", "ANTM", "ASII", "BBCA", "BBNI", 
    "BBRI", "BBTN", "BMRI", "BREN", "BRPT", "BUMI", "CPIN", "CTRA", "DSSA", "EMTK", 
    "EXCL", "GOTO", "HEAL", "ICBP", "INCO", "INDF", "INKP", "ISAT", "ITMG", "JPFA", 
    "KLBF", "MAPI", "MBMA", "MDKA", "MEDC", "NCKL", "PGAS", "PGEO", "PTBA", "SCMA", 
    "SMGR", "TLKM", "TOWR", "UNTR", "UNVR"
]

IDX30_SYMBOLS = [
    "ADRO", "AKRA", "AMMN", "AMRT", "ANTM", "ASII", "BBCA", "BBNI", "BBRI", 
    "BMRI", "BREN", "BRPT", "BUMI", "CPIN", "EMTK", "EXCL", "GOTO", "ICBP", 
    "INCO", "INDF", "INKP", "ISAT", "KLBF", "MDKA", "MEDC", "PGAS", "PTBA", 
    "TLKM", "UNTR", "UNVR"
]

JII_SYMBOLS = [
    "AADI", "ADMR", "ADRO", "AKRA", "AMRT", "ANTM", "ASII", "BRIS", "BRPT", "CPIN",
    "EMTK", "EXCL", "HRUM", "ICBP", "INCO", "INDF", "INKP", "ISAT", "ITMG", "JPFA",
    "KLBF", "MAPI", "MDKA", "MEDC", "PGAS", "PTBA", "SCMA", "SMGR", "TLKM", "UNTR"
]

MARKET_INDICES = {
    # Indeks Utama
    "LQ45 (Top 45 Likuid)": LQ45_SYMBOLS,
    "IDX30 (Top 30 Kapitalisasi)": IDX30_SYMBOLS,
    "JII (Jakarta Islamic Index)": JII_SYMBOLS,
    "IDX80": ["AADI", "ACES", "ADMR", "ADRO", "AKRA", "AMRT", "ANTM", "ARTO", "ASII", "AUTO", "BBCA", "BBNI", "BBRI", "BBTN", "BFIN", "BMRI", "BREN", "BRIS", "BRPT", "BSDE", "BUKA", "CPIN", "CTRA", "CUAN", "DSNG", "EMTK", "ENRG", "ESSA", "EXCL", "GGRM", "GOTO", "HEAL", "HRTA", "HRUM", "ICBP", "INCO", "INDF", "INKP", "INTP", "ISAT", "ITMG", "JPFA", "KLBF", "MAPI", "MAPA", "MBMA", "MDKA", "MEDC", "MIKA", "MNCN", "MTEL", "MYOR", "NCKL", "PANI", "PGAS", "PGEO", "PNLF", "PTBA", "PWON", "RMKE", "SCMA", "SIDO", "SILO", "SMGR", "SMRA", "SRTG", "SSIA", "TAPG", "TBIG", "TKIM", "TLKM", "TOWR", "TPIA", "UNTR", "UNVR", "WIKA", "WIIM"],
    "IDXHIDIV20 (High Dividend)": ["ACES", "ADRO", "AKRA", "ANTM", "ASII", "BBCA", "BBNI", "BBRI", "BMRI", "BNGA", "HMSP", "INDF", "ITMG", "JPFA", "PGAS", "PTBA", "SIDO", "TLKM", "UNTR", "UNVR"],
    
    # Sektoral (IDX-IC)
    "IDXFinance (Keuangan)": ["BBCA", "BBRI", "BMRI", "BBNI", "BBTN", "BRIS", "BNGA", "NISP", "BDMN", "PNBN", "MEGA", "ARTO", "BBHI", "AGRO", "BBYB", "BFIN", "CFIN", "WOMF", "ADMF", "PNLF", "AMOR", "TUGU", "ASBI", "SUPA", "COIN"],
    "IDXEnergy (Energi)": ["AADI", "ADRO", "PTBA", "ITMG", "HRUM", "BUMI", "INDY", "MEDC", "PGAS", "ENRG", "BIPI", "ADMR", "TOBA", "BSSR", "KKGI", "MBAP", "ABMM", "SGER", "WINS", "ELSA", "PGEO", "CUAN", "DOID", "BREN"],
    "IDXBasic (Brg Baku)": ["AMMN", "ANTM", "INCO", "TINS", "MDKA", "MBMA", "NCKL", "PSAB", "ARCI", "BRPT", "TPIA", "SMGR", "INTP", "SMCB", "CMNT", "INKP", "TKIM", "FASW", "INRU", "KRAS", "ISSP", "GDST", "EMAS", "ASPR"],
    "IDXIndust (Perindustrian)": ["ASII", "UNTR", "HEXA", "KOBX", "IPCC", "BIRD", "ASSA", "TRJA", "TMAS", "SMDR", "PURA", "ARNA", "MLIA", "KIAS", "GJTL"],
    "IDXCyclic (Konsumer Siklikal)": ["MAPI", "MAPA", "RALS", "LPPF", "ACES", "ERAA", "MSIN", "MNCN", "SCMA", "FILM", "PANR", "BAYU", "PJAA", "AUTO"],
    "IDXNonCyc (Konsumer Non-Siklikal)": ["ICBP", "INDF", "UNVR", "MYOR", "CMRY", "GOOD", "AMRT", "MIDI", "CLEO", "CAMP", "ROTI", "ULTJ", "CPIN", "JPFA", "MAIN", "WMUU", "SSMS", "AALI", "LSIP", "GZCO", "TAPG", "DSNG", "BWPT", "RLCO", "MERI", "PMUI"],
    "IDXHealth (Kesehatan)": ["KLBF", "SIDO", "MIKA", "SILO", "HEAL", "PRDA", "PEHA", "KAEF", "INAF", "OMED", "CARE", "SAME", "BMHS", "IRRA", "CHEK"],
    "IDXProp (Properti & Real Estat)": ["PWON", "BSDE", "CTRA", "SMRA", "ASRI", "DILD", "KIJA", "SSIA", "DMAS", "PANI", "LPCK", "LPKR", "APLN", "BKSL", "BEST", "NZIA", "OMRE", "MMLP"],
    "IDXTech (Teknologi)": ["GOTO", "BUKA", "BELI", "WIFI", "EMTK", "MLPT", "DMMX", "GLVA", "NINE", "AWAN", "WIRG", "KREN", "MCAS"],
    "IDXInfra (Infrastruktur)": ["TLKM", "ISAT", "EXCL", "MTEL", "TOWR", "TBIG", "JSMR", "CMNP", "META", "WIKA", "PTPP", "ADHI", "WSKT", "WEGE", "TOTL", "CASS", "BREN", "CDIA"],
    "IDXTrans (Transportasi & Logistik)": ["BIRD", "ASSA", "SMDR", "TMAS", "BPTR", "GIAA", "HAIS", "TCPI", "TRUK", "SAPX", "TNCA", "DEAL", "JARR", "KJEN", "LRNA", "NELY", "SDMU", "TAXI", "TRJA", "PJHB", "BLOG", "PSAT"],

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
    "Grup Emtek (Sariaatmadja)": ["EMTK", "SCMA", "BUKA", "RSGK", "SIDO", "OMED", "CASS", "SAME", "BBYB", "SUPA"],
    "Grup Adaro (Thohir)": ["ADRO", "AADI", "ADMR", "MDKA", "MBMA", "BSSR", "ESSA", "TRIM", "GOTO", "ABMM", "EMAS"],
    "Grup Saratoga (Sandiaga/Soeryadjaya)": ["SRTG", "ADRO", "MDKA", "MBMA", "MPMX", "TBIG", "PALM", "AGII", "EMAS"],
    "Grup Agung Sedayu (Aguan)": ["PANI", "HOPE"],
    "Grup Panin (Mukmin Ali)": ["PNBN", "PNLF", "PNIN", "CFIN", "AMAG"],
    "Grup Mayapada (Tahir)": ["MAYA", "SONA", "SRAJ", "BBYB"],
    "Grup Arsari (Hashim Djojohadikusumo)": ["WIFI", "COIN"],
}
