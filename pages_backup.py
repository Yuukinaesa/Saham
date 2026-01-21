import streamlit as st
import json
import time

def backup_page():
    st.markdown("""
    <div style='margin-bottom: 24px;'>
        <h2 style='color: var(--text-color); margin-bottom: 8px;'>💾 Backup & Restore</h2>
        <p style='color: var(--text-color); opacity: 0.8; font-size: 1.1em;'>Simpan konfigurasi dan data Anda (daftar saham, modal, dll) ke file lokal.</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="medium")

    # --- BACKUP SECTION ---
    with col1:
        st.markdown("### 📤 Backup Configuration")
        st.info("Unduh file JSON berisi pengaturan saat ini.")
        
        # Collect State
        # We only backup specific keys to avoid bloating with large dataframes
        backup_keys = ['scraper_symbols', 'scraper_modal'] 
        backup_data = {}
        for key in backup_keys:
            if key in st.session_state:
                backup_data[key] = st.session_state[key]
        
        # Add timestamp
        backup_data['_timestamp'] = time.strftime("%Y-%m-%d %H:%M:%S")
        
        json_str = json.dumps(backup_data, indent=2)
        
        st.download_button(
            label="Download Backup (.json)",
            data=json_str,
            file_name=f"saham_idx_backup_{int(time.time())}.json",
            mime="application/json",
            type="primary"
        )

    # --- RESTORE SECTION ---
    with col2:
        st.markdown("### 📥 Restore Configuration")
        st.warning("⚠️ Restore akan MENIMPA pengaturan saat ini.")
        
        uploaded_file = st.file_uploader("Upload file backup (.json)", type=["json"])
        
        if uploaded_file is not None:
            if st.button("Restore Data", type="primary"):
                try:
                    # Progress Indicator
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    status_text.text("Membaca file...")
                    content = json.load(uploaded_file)
                    progress_bar.progress(30)
                    time.sleep(0.5) # Simulate slight delay for UX
                    
                    status_text.text("Memvalidasi data...")
                    valid_keys = ['scraper_symbols', 'scraper_modal']
                    data_to_restore = {k: v for k, v in content.items() if k in valid_keys}
                    progress_bar.progress(60)
                    time.sleep(0.5)
                    
                    status_text.text("Memulihkan sesi...")
                    # Restore REPLACE logic
                    for key, value in data_to_restore.items():
                        st.session_state[key] = value
                    
                    # Persist immediately to file
                    from state_manager import save_config
                    save_config()
                    
                    progress_bar.progress(100)
                    status_text.text("✅ Restore Berhasil!")
                    st.success("Konfigurasi berhasil dipulihkan! Silakan cek kembali halaman Scraper.")
                    
                    # Force rerun to reflect changes immediately
                    time.sleep(1)
                    st.rerun()
                    
                except json.JSONDecodeError:
                    st.error("File tidak valid (Bukan JSON).")
                except Exception as e:
                    st.error(f"Gagal restore: {str(e)}")
