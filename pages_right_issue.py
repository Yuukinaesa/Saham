import streamlit as st
from config import PLATFORM_CONFIG
from utils import format_rupiah

def right_issue_calculator_page():
    st.info("Kalkulator untuk menghitung harga teoritis dan potensi keuntungan/kerugian dari aksi korporasi Right Issue.")
    
    col_input1, col_input2 = st.columns(2, gap="medium")
    
    with col_input1:
        st.markdown("""<div style='margin-bottom: 12px;'><h3 style='color: var(--text-color); margin-bottom: 12px;'>Data Saham Induk</h3></div>""", unsafe_allow_html=True)
        harga_cum = st.number_input("Harga Cum Date (Closing)", min_value=0, value=1000, step=5, help="Harga saham induk pada penutupan Cum Date.")
        rasio_lama = st.number_input("Rasio Saham Lama", min_value=1, value=100, step=1, help="Setiap X saham lama...")
        rasio_baru = st.number_input("Rasio Saham Baru (HMETD)", min_value=1, value=20, step=1, help="...Mendapatkan Y saham baru (HMETD).")
        harga_tebus = st.number_input("Harga Tebus (Exercise Price)", min_value=0, value=800, step=5, help="Harga penebusan Right Issue.")
        
    with col_input2:
        st.markdown("""<div style='margin-bottom: 12px;'><h3 style='color: var(--text-color); margin-bottom: 12px;'>Simulasi Kepemilikan</h3></div>""", unsafe_allow_html=True)
        modal_lot = st.number_input("Jumlah Lot Dimiliki", min_value=1, value=100, step=1)
        
        # Broker Selection for Fees
        broker = st.selectbox("Pilih Sekuritas (Fee Jual)", list(PLATFORM_CONFIG.keys()), index=0, key='ri_broker')
        _, fee_jual = PLATFORM_CONFIG[broker]


    st.markdown("---")
    
    if st.button("Hitung Simulasi", type="primary"):
        # 1. Theoretical Ex-Price Calculation
        # Formula: ((Harga Cum * Rasio Lama) + (Harga Tebus * Rasio Baru)) / (Rasio Lama + Rasio Baru)
        total_rasio = rasio_lama + rasio_baru
        harga_teoritis = ((harga_cum * rasio_lama) + (harga_tebus * rasio_baru)) / total_rasio
        
        # 2. Rights Calculation
        total_saham_induk = modal_lot * 100
        # HMETD Received = (Saham Induk / Rasio Lama) * Rasio Baru
        jumlah_hmetd_lembar = (total_saham_induk / rasio_lama) * rasio_baru
        jumlah_hmetd_lot = jumlah_hmetd_lembar / 100 # Can be fractional
        
        # 3. Cost to Exercise
        biaya_tebus = jumlah_hmetd_lembar * harga_tebus
        
        # 4. Theoretical Value of Right (Harga Wajar Right Issue)
        # Usually: Harga Induk Ex Date - Harga Tebus (min 0)
        # But closer estimate is: Harga Teoritis - Harga Tebus
        harga_wajar_right = max(0, harga_teoritis - harga_tebus)
        
        # 5. Dilution if not exercised
        dilusi_persen = (rasio_baru / total_rasio) * 100
        
        # --- DISPLAY ---
        
        st.markdown("""
        <div style='margin-bottom: 20px; text-align: center;'>
            <h3 style='color: var(--text-color); margin-bottom: 5px; font-size: 1.25rem;'>📉 Analisa Right Issue</h3>
        </div>
        """, unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns(3)
        with c1:
             st.metric("Harga Teoritis (Ex-Date)", format_rupiah(harga_teoritis))
        with c2:
             st.metric("Harga Wajar Right", format_rupiah(harga_wajar_right))
        with c3:
             st.metric("Potensi Dilusi", f"{dilusi_persen:.2f}%")
             
        st.markdown("### 💼 Skenario Aksi")
        
        # Skenario 1: Tebus Semua
        st.markdown("""
        <div class='premium-card'>
            <h4 style='color: #3b82f6; margin-top:0;'>✅ Skenario 1: Tebus Semua (Exercise)</h4>
            <p>Anda menggunakan hak anda untuk membeli saham baru di harga tebus.</p>
        """, unsafe_allow_html=True)
        
        col_s1_a, col_s1_b = st.columns(2)
        with col_s1_a:
            st.write(f"**Hak HMETD:** {jumlah_hmetd_lot:,.2f} Lot ({jumlah_hmetd_lembar:,.0f} lembar)")
            st.write(f"**Modal Penebusan:** {format_rupiah(biaya_tebus)}")
        with col_s1_b:
            # Est Value after exercise
            # New Avg Price usually = Harga Teoritis (assuming bought at Cum Price)
            # Total Asset = (Lot Awal + Lot HMETD) * Harga Teoritis
            total_lot_akhir = modal_lot + jumlah_hmetd_lot
            estimasi_aset = total_lot_akhir * 100 * harga_teoritis
            st.write(f"**Total Lot Akhir:** {total_lot_akhir:,.2f} Lot")
            st.write(f"**Estimasi Nilai Aset:** {format_rupiah(estimasi_aset)}")
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Skenario 2: Jual Rights
        st.markdown("""
        <div class='premium-card'>
            <h4 style='color: #ef4444; margin-top:0;'>❌ Skenario 2: Tidak Tebus (Jual Right)</h4>
            <p>Anda menjual HMETD anda di pasar saat periode perdagangan (Asumsi jual di Harga Wajar Teoritis).</p>
        """, unsafe_allow_html=True)
        
        col_s2_a, col_s2_b = st.columns(2)
        with col_s2_a:
            # Sell rights
            # Proceeds = HMETD * Harga Wajar * (1 - Fee)
            # Note: Fee sell applies to Right trading too usually
            proceeds = jumlah_hmetd_lembar * harga_wajar_right * (1 - fee_jual)
            st.write(f"**Hak HMETD Dijual:** {jumlah_hmetd_lot:,.2f} Lot")
            st.write(f"**Estimasi Uang Tunai Diterima:** {format_rupiah(proceeds)}")
        with col_s2_b:
            # Holding remains same, price drops to Theoretical
            aset_saham = modal_lot * 100 * harga_teoritis
            total_wealth = aset_saham + proceeds
            st.write(f"**Sisa Aset Saham:** {format_rupiah(aset_saham)}")
            st.write(f"**Total Kekayaan:** {format_rupiah(total_wealth)}")
            st.write(f"*(Aset Saham + Tunai Jual Right)*")
        st.markdown("</div>", unsafe_allow_html=True)
