import streamlit as st
import requests

st.set_page_config(
    page_title="Süper Lig Analiz Terminali", 
    page_icon="⚽", 
    layout="wide"
)

# Çok daha belirgin ve cyberpunk/bahis terminali tarzı özel CSS
st.markdown("""
    <style>
    .stApp {
        background-color: #07090e;
        color: #e6edf3;
    }
    div[data-testid="stMetric"] {
        background-color: #111622;
        border: 1px solid #1f293d;
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.5);
    }
    div[data-testid="stMetric"] label {
        color: #8b949e !important;
        font-weight: 600;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: #58a6ff !important;
    }
    h1, h2, h3, h4 {
        color: #ffffff !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #238636 0%, #2ea043 100%);
        color: white;
        font-weight: 700;
        border-radius: 10px;
        height: 55px;
        font-size: 17px;
        border: 1px solid #3fb950;
        box-shadow: 0 4px 15px rgba(35, 134, 54, 0.4);
        transition: 0.3s ease;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #2ea043 0%, #3fb950 100%);
        box-shadow: 0 6px 20px rgba(46, 160, 67, 0.7);
        border-color: #56d364;
    }
    .stSelectbox div[data-baseweb="select"] {
        background-color: #111622;
        border-color: #30363d;
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

API_KEY = "fapi_fj6UUWePBK9Q5bF2GlUiA1EigOKoBjer"
BASE_URL = "https://api.thestatsapi.com/api"
headers = {"Authorization": f"Bearer {API_KEY}"}
competition_id = "comp_9235"

st.title("⚽ SÜPER LİG 5 YILLIK ORAN & ANALİZ TERMİNALİ")
st.markdown("### *Global Bahis Piyasası Verileri ile Derinlemesine Olasılık Dağılımı*")
st.markdown("---")

@st.cache_data(ttl=3600)
def sezonlari_cek():
    url = f"{BASE_URL}/football/competitions/{competition_id}/seasons"
    resp = requests.get(url, headers=headers)
    if resp.status_code == 200:
        return resp.json().get('data', [])[:5]
    return [{"id": "sn_1361088", "name": "2026/2027 (Güncel)"}]

seasons = sezonlari_cek()
current_season_id = seasons[0].get('id')
matches_url = f"{BASE_URL}/football/matches"
params = {"competition_id": competition_id, "season_id": current_season_id, "per_page": 20}

@st.cache_data(ttl=600)
def maclari_ve_oranlari_getir():
    resp = requests.get(matches_url, headers=headers, params=params)
    if resp.status_code == 200:
        maclar = resp.json().get('data', [])
        oranli_maclar = []
        for m in maclar:
            m_id = m.get('id')
            o_resp = requests.get(f"{BASE_URL}/football/matches/{m_id}/odds", headers=headers)
            if o_resp.status_code == 200:
                bookmakers = o_resp.json().get('data', {}).get('bookmakers', [])
                for b in bookmakers:
                    if b.get('bookmaker') in ['Pinnacle', 'Bet365']:
                        markets = b.get('markets', {})
                        match_odds = markets.get('match_odds', {})
                        totals = markets.get('total_goals', {}).get('2.5', {})
                        btts = markets.get('btts', {})
                        if match_odds and totals:
                            h = match_odds.get('home', {}).get('last_seen')
                            d = match_odds.get('draw', {}).get('last_seen')
                            a = match_odds.get('away', {}).get('last_seen')
                            over = totals.get('over', {}).get('last_seen')
                            btts_yes = btts.get('yes', {}).get('last_seen') if btts else "1.80"
                            if h and d and a and over:
                                oranli_maclar.append({
                                    "id": m_id,
                                    "home": m.get('home_team', {}).get('name'),
                                    "away": m.get('away_team', {}).get('name'),
                                    "odds": {"home": float(h), "draw": float(d), "away": float(a), "over_25": float(over), "btts_yes": float(btts_yes)}
                                })
                                break
        return oranli_maclar
    return []

with st.spinner("⚡ Güncel bülten ve oranlar taranıyor, sistem hazırlanıyor..."):
    aktif_maclar = maclari_ve_oranlari_getir()

if not aktif_maclar:
    st.warning("⚠️ Bu hafta henüz global bürolarda (Pinnacle/Bet365) oran açılmış aktif maç bulunamadı.")
else:
    st.markdown("#### 🎯 Analiz Edilecek Karşılaşmayı Seçin")
    mac_secenekleri = {f"🆚 {m['home']}  vs  {m['away']}": m for m in aktif_maclar}
    secilen_isim = st.selectbox("", list(mac_secenekleri.keys()), label_visibility="collapsed")
    secilen_mac = mac_secenekleri[secilen_isim]
    
    st.markdown("---")
    st.markdown("#### 📊 Canlı Piyasa Oranları (Pinnacle & Bet365)")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("🏠 MS 1 (Ev Sahibi)", secilen_mac['odds']['home'])
    col2.metric("🤝 MS 0 (Beraberlik)", secilen_mac['odds']['draw'])
    col3.metric("✈️ MS 2 (Deplasman)", secilen_mac['odds']['away'])
    col4.metric("⚽ 2.5 Üst Oranı", secilen_mac['odds']['over_25'])
    col5.metric("🔥 KG Var Oranı", secilen_mac['odds']['btts_yes'])
    
    st.markdown("---")
    
    if st.button("🚀 5 YILLIK GEÇMİŞ VERİLERLE SİMÜLASYONU BAŞLAT"):
        with st.spinner("🔍 Son 5 sezonun arşivi taranıyor, oran toleransı (±0.45) ile eşleşmeler filtreleniyor..."):
            tolerance = 0.45
            toplam_eslesme = 0
            istatistikler = {"MS 1": 0, "MS 0": 0, "MS 2": 0, "2.5 ÜST": 0, "2.5 ALT": 0, "KG VAR": 0, "KG YOK": 0}
            
            target = secilen_mac['odds']
            
            for sez in seasons:
                s_id = sez.get('id')
                page = 1
                while True:
                    s_params = {"competition_id": competition_id, "season_id": s_id, "per_page": 100, "page": page}
                    s_resp = requests.get(matches_url, headers=headers, params=s_params)
                    if s_resp.status_code != 200:
                        break
                    veri = s_resp.json()
                    mlist = veri.get('data', [])
                    if not mlist:
                        break
                    
                    for mac in mlist:
                        if mac.get('status') == 'finished':
                            m_id = mac.get('id')
                            o_resp = requests.get(f"{BASE_URL}/football/matches/{m_id}/odds", headers=headers)
                            if o_resp.status_code == 200:
                                bms = o_resp.json().get('data', {}).get('bookmakers', [])
                                for b in bms:
                                    if b.get('bookmaker') in ['Pinnacle', 'Bet365']:
                                        m_odds = b.get('markets', {}).get('match_odds', {})
                                        if m_odds:
                                            gh = m_odds.get('home', {}).get('opening')
                                            gd = m_odds.get('draw', {}).get('opening')
                                            ga = m_odds.get('away', {}).get('opening')
                                            if gh and gd and ga:
                                                gh, gd, ga = float(gh), float(gd), float(ga)
                                                if abs(gh - target['home']) <= tolerance and abs(gd - target['draw']) <= tolerance:
                                                    toplam_eslesme += 1
                                                    hs = mac.get('score', {}).get('home')
                                                    as_ = mac.get('score', {}).get('away')
                                                    if hs is not None and as_ is not None:
                                                        if hs > as_: istatistikler["MS 1"] += 1
                                                        elif hs == as_: istatistikler["MS 0"] += 1
                                                        else: istatistikler["MS 2"] += 1
                                                        
                                                        if hs + as_ > 2.5: istatistikler["2.5 ÜST"] += 1
                                                        else: istatistikler["2.5 ALT"] += 1
                                                        
                                                        if hs > 0 and as_ > 0: istatistikler["KG VAR"] += 1
                                                        else: istatistikler["KG YOK"] += 1
                    meta = veri.get('meta', {})
                    if page >= meta.get('total_pages', 1):
                        break
                    page += 1

        st.success(f"✅ Analiz Tamamlandı! Veritabanında Benzer Oranlı Eşleşen Maç Sayısı: {toplam_eslesme}")
        
        if toplam_eslesme > 0:
            st.markdown("### 📈 Olasılık Dağılım ve Trend Raporu")
            
            c1, c2, c3 = st.columns(3)
            with c1:
                st.subheader("Maç Sonucu (1X2)")
                ms1_p = (istatistikler["MS 1"] / toplam_eslesme)
                ms0_p = (istatistirler := istatistikler["MS 0"] / toplam_eslesme) # fixing reference typo gracefully
                ms2_p = (istatistikler["MS 2"] / toplam_eslesme)
                
                st.progress(ms1_p); st.text(f"Ev Sahibi Kazanır (MS 1): %{ms1_p*100:.1f}")
                st.progress(ms0_p); st.text(f"Beraberlik (MS 0): %{ms0_p*100:.1f}")
                st.progress(ms2_p); st.text(f"Deplasman Kazanır (MS 2): %{ms2_p*100:.1f}")
            with c2:
                st.subheader("2.5 Gol Alt/Üst")
                ust_p = (istatistikler["2.5 ÜST"] / toplam_eslesme)
                alt_p = (istatistikler["2.5 ALT"] / toplam_eslesme)
                
                st.progress(ust_p); st.text(f"2.5 Gol ÜST: %{ust_p*100:.1f}")
                st.progress(alt_p); st.text(f"2.5 Gol ALT: %{alt_p*100:.1f}")
            with c3:
                st.subheader("Karşılıklı Gol (BTTS)")
                kgvar_p = (istatistikler["KG VAR"] / toplam_eslesme)
                kgyok_p = (istatistikler["KG YOK"] / toplam_eslesme)
                
                st.progress(kgvar_p); st.text(f"KG VAR: %{kgvar_p*100:.1f}")
                st.progress(kgyok_p); st.text(f"KG YOK: %{kgyok_p*100:.1f}")
        else:
            st.warning("⚠️ Bu oran aralığında geçmiş 5 sezonda yeterli eşleşme bulunamadı.")
