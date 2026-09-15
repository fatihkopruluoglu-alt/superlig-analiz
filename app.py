import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# Sayfa Yapılandırması
st.set_page_config(
    page_title="Süper Lig Analiz Terminali", 
    page_icon="⚽", 
    layout="wide"
)

# Özel CSS Tasarımı
st.markdown("""
    <style>
    .stApp {
        background-color: #05070b;
        color: #f0f6fc;
        font-family: 'Inter', sans-serif;
    }
    .top-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: linear-gradient(135deg, #161b22 0%, #0d1117 100%);
        padding: 15px 25px;
        border-radius: 12px;
        border: 1px solid #30363d;
        margin-bottom: 20px;
    }
    .top-title h1 {
        color: #58a6ff;
        font-size: 22px;
        margin: 0;
    }
    .top-title p {
        color: #8b949e;
        font-size: 12px;
        margin: 0;
    }
    .subtle-clock {
        background-color: #111622;
        color: #8b949e;
        padding: 6px 12px;
        border-radius: 8px;
        font-size: 11px;
        border: 1px solid #21262d;
        text-align: right;
    }
    div[data-testid="stMetric"] {
        background-color: #111622;
        border: 1px solid #21262d;
        padding: 12px;
        border-radius: 10px;
        text-align: center;
    }
    div[data-testid="stMetric"] label {
        color: #8b949e !important;
        font-size: 12px !important;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: #3fb950 !important;
        font-size: 20px !important;
        font-weight: 700;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #238636 0%, #2ea043 100%);
        color: white;
        font-weight: 700;
        border-radius: 10px;
        height: 50px;
        font-size: 15px;
        border: 1px solid #3fb950;
        box-shadow: 0 4px 15px rgba(35, 134, 54, 0.4);
        transition: 0.3s;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #2ea043 100%, #3fb950 100%);
    }
    .market-box {
        background-color: #111622;
        border-left: 3px solid #58a6ff;
        padding: 12px 15px;
        border-radius: 6px;
        margin-bottom: 15px;
        font-size: 13px;
        color: #c9d1d9;
    }
    .card-container {
        background-color: #161b22;
        border: 1px solid #30363d;
        padding: 15px;
        border-radius: 10px;
        margin-top: 10px;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

API_KEY = "fapi_fj6UUWePBK9Q5bF2GlUiA1EigOKoBjer"
BASE_URL = "https://api.thestatsapi.com/api"
headers = {"Authorization": f"Bearer {API_KEY}"}
competition_id = "comp_9235"

simdi = datetime.now().strftime("%d.%m.%Y - %H:%M")

# Üst Bilgi Barı ve Saat
st.markdown(f"""
    <div class="top-bar">
        <div class="top-title">
            <h1>⚽ SÜPER LİG ANALİZ TERMİNALİ</h1>
            <p>Pinnacle & Bet365 • 5 Yıllık Olasılık Dağılım Motoru</p>
        </div>
        <div class="subtle-clock">
            🟢 Canlı Piyasa<br>Son Güncelleme: <b>{simdi}</b>
        </div>
    </div>
""", unsafe_allow_html=True)

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
                            h_open = match_odds.get('home', {}).get('opening', h)
                            over = totals.get('over', {}).get('last_seen')
                            btts_yes = btts.get('yes', {}).get('last_seen') if btts else "1.80"
                            
                            if h and d and a and over:
                                trend = "💡 Oranlar Dengeli / Stabil"
                                try:
                                    if float(h) < float(h_open):
                                        trend = "🔥 Favori Oranı Düşüyor (Ciddi Para Girişi Var)"
                                    elif float(h) > float(h_open):
                                        trend = "⚠️ Favori Oranı Yükseliyor (Piyasa Şüpheli/Riskli)"
                                except:
                                    pass

                                oranli_maclar.append({
                                    "id": m_id,
                                    "home": m.get('home_team', {}).get('name'),
                                    "away": m.get('away_team', {}).get('name'),
                                    "trend": trend,
                                    "odds": {"home": float(h), "draw": float(d), "away": float(a), "over_25": float(over), "btts_yes": float(btts_yes)}
                                })
                                break
        return oranli_maclar
    return []

with st.spinner("⚡ Güncel bülten taranıyor..."):
    aktif_maclar = maclari_ve_oranlari_getir()

if not aktif_maclar:
    st.warning("⚠️ Bu hafta henüz global bürolarda oran açılmış aktif maç bulunamadı.")
else:
    col_sec, col_info = st.columns([2, 1])
    with col_sec:
        st.markdown("#### 🎯 Maç Seçimi")
        mac_secenekleri = {f"{m['home']} vs {m['away']}": m for m in aktif_maclar}
        secilen_isim = st.selectbox("", list(mac_secenekleri.keys()), label_visibility="collapsed")
        secilen_mac = mac_secenekleri[secilen_isim]
    
    with col_info:
        st.markdown("#### 📊 Piyasa Trend Bilgisi")
        st.markdown(f'<div class="market-box">{secilen_mac["trend"]}</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("#### 📌 Canlı Oranlar (Pinnacle & Bet365)")
    
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("🏠 MS 1", secilen_mac['odds']['home'])
    c2.metric("🤝 MS 0", secilen_mac['odds']['draw'])
    c3.metric("✈️ MS 2", secilen_mac['odds']['away'])
    c4.metric("⚽ 2.5 ÜST", secilen_mac['odds']['over_25'])
    c5.metric("🔥 KG VAR", secilen_mac['odds']['btts_yes'])
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("🚀 5 YILLIK ARŞİV İLE BENZER MAÇLARI VE SKORLARI GETİR"):
        with st.spinner("🔍 Geçmiş sezonlar taranıyor, genişletilmiş oran toleransı (±0.65) eşleştiriliyor..."):
            tolerance = 0.65  # Havuzu genişletmek için toleransı biraz esnettik
            toplam_eslesme = 0
            istatistikler = {"MS 1": 0, "MS 0": 0, "MS 2": 0, "2.5 ÜST": 0, "2.5 ALT": 0, "KG VAR": 0, "KG YOK": 0}
            eslesen_maclar_listesi = []
            tum_arsiv_listesi = []
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
                                        totals_m = b.get('markets', {}).get('total_goals', {}).get('2.5', {})
                                        btts_m = b.get('markets', {}).get('btts', {})
                                        if m_odds:
                                            gh = m_odds.get('home', {}).get('opening')
                                            gd = m_odds.get('draw', {}).get('opening')
                                            ga = m_odds.get('away', {}).get('opening')
                                            
                                            h_team = mac.get('home_team', {}).get('name')
                                            a_team = mac.get('away_team', {}).get('name')
                                            hs = mac.get('score', {}).get('home')
                                            as_ = mac.get('score', {}).get('away')
                                            sezon_adi = sez.get('name', 'Bilinmiyor')
                                            
                                            if hs is not None and as_ is not None:
                                                # Tüm arşiv listesi için veriyi hazırlayalım
                                                toplam_gol = hs + as_
                                                ust_alt = "2.5 ÜST" if toplam_gol > 2.5 else "2.5 ALT"
                                                kg_durum = "KG VAR" if (hs > 0 and as_ > 0) else "KG YOK"
                                                 mac_sonucu = "MS 1" if hs > as_ else ("MS 0" if hs == as_ else "MS 2")
                                                
                                                tum_arsiv_listesi.append({
                                                    "Sezon": sezon_adi,
                                                    "Ev Sahibi": h_team,
                                                    "Deplasman": a_team,
                                                    "Açılış MS 1": gh if gh else "-",
                                                    "Açılış MS 0": gd if gd else "-",
                                                    "Açılış MS 2": ga if ga else "-",
                                                    "Skor": f"{hs} - {as_}",
                                                    "Maç Sonucu": mac_sonucu,
                                                    "Gol Alt/Üst": ust_alt,
                                                    "Karşılıklı Gol": kg_durum
                                                })

                                                # Seçilen maçla benzer oran arayan simülasyon kısmı
                                                if gh and gd and ga:
                                                    gh_f, gd_f, ga_f = float(gh), float(gd), float(ga)
                                                    if abs(gh_f - target['home']) <= tolerance and abs(gd_f - target['draw']) <= tolerance:
                                                        toplam_eslesme += 1
                                                        eslesen_maclar_listesi.append({
                                                            "Sezon": sezon_adi,
                                                            "Ev Sahibi": h_team,
                                                            "Deplasman": a_team,
                                                            "Açılış MS1": gh_f,
                                                            "Açılış MS0": gd_f,
                                                            "Açılış MS2": ga_f,
                                                            "Maç Skoru": f"{hs} - {as_}"
                                                        })
                                                        
                                                        if hs > as_: istatistikler["MS 1"] += 1
                                                        elif hs == as_: istatistikler["MS 0"] += 1
                                                        else: istatistikler["MS 2"] += 1
                                                        
                                                        if toplam_gol > 2.5: istatistikler["2.5 ÜST"] += 1
                                                        else: istatistikler["2.5 ALT"] += 1
                                                        
                                                        if hs > 0 and as_ > 0: istatistikler["KG VAR"] += 1
                                                        else: istatistikler["KG YOK"] += 1
                    meta = veri.get('meta', {})
                    if page >= meta.get('total_pages', 1):
                        break
                    page += 1

        st.success(f"✅ Analiz Tamamlandı! Genişletilmiş arama ile eşleşen benzer maç sayısı: {toplam_eslesme}")
        
        if toplam_eslesme > 0:
            st.markdown("### 📈 Olasılık Dağılım Raporu")
            
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown('<div class="card-container">', unsafe_allow_html=True)
                st.subheader("Maç Sonucu")
                ms1_p = istatistikler["MS 1"] / toplam_eslesme
                ms0_p = istatistikler["MS 0"] / toplam_eslesme
                ms2_p = istatistler["MS 2"] / toplam_eslesme
                st.progress(ms1_p); st.text(f"MS 1 (Ev): %{ms1_p*100:.1f}")
                st.progress(ms0_p); st.text(f"MS 0 (Beraberlik): %{ms0_p*100:.1f}")
                st.progress(ms2_p); st.text(f"MS 2 (Dep): %{ms2_p*100:.1f}")
                st.markdown('</div>', unsafe_allow_html=True)
            with c2:
                st.markdown('<div class="card-container">', unsafe_allow_html=True)
                st.subheader("2.5 Gol")
                ust_p = istatistikler["2.5 ÜST"] / toplam_eslesme
                alt_p = istatistikler["2.5 ALT"] / toplam_eslesme
                st.progress(ust_p); st.text(f"2.5 ÜST: %{ust_p*100:.1f}")
                st.progress(alt_p); st.text(f"2.5 ALT: %{alt_p*100:.1f}")
                st.markdown('</div>', unsafe_allow_html=True)
            with c3:
                st.markdown('<div class="card-container">', unsafe_allow_html=True)
                st.subheader("Karşılıklı Gol")
                kgvar_p = istatistikler["KG VAR"] / toplam_eslesme
                kgyok_p = istatistikler["KG YOK"] / toplam_eslesme
                st.progress(kgvar_p); st.text(f"KG VAR: %{kgvar_p*100:.1f}")
                st.progress(kgyok_p); st.text(f"KG YOK: %{kgyok_p*100:.1f}")
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Benzer Maçlar Arşivi
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("### 🗂️ Benzer Açılış Oranına Sahip Geçmiş Maçlar")
            df_benzer = pd.DataFrame(eslesen_maclar_listesi)
            st.dataframe(df_benzer, use_container_width=True, hide_index=True)
            
        else:
            st.warning("⚠️ Bu oran aralığında eşleşen maç bulunamadı. Toleransı biraz daha esnetebiliriz.")

        # TÜM ARŞİV EXCEL/CSV İNDİRME BÖLÜMÜ
        if tum_arsiv_listesi:
            st.markdown("<br><hr>", unsafe_allow_html=True)
            st.markdown("### 📊 Geçmiş 5 Sezonun Tam Maç ve Oran Arşivi (Excel Raporu)")
            st.markdown("Sistemdeki taranan tüm geçmiş maçların açılış oranlarını, skorlarını, Alt/Üst ve KG durumlarını içeren tam listeyi Excel formatına uygun olarak indirebilirsin:")
            
            df_tum = pd.DataFrame(tum_arsiv_listesi)
            csv_verisi = df_tum.to_csv(index=False).encode('utf-8')
            
            st.download_button(
                label="📥 Tüm 5 Yıllık Arşivi Excel (CSV) Olarak İndir",
                data=csv_verisi,
                file_name="superlig_5_yil_oran_ve_skor_arsivi.csv",
                mime="text/csv",
            )
