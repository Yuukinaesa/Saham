import streamlit as st
import json
import base64

def inject_pwa_support():
    """
    Injects PWA manifest and meta tags to verify 'Install to Home Screen' functionality.
    Note: Requires https or localhost.
    """
    manifest = {
        "name": "Saham IDX",
        "short_name": "Saham IDX",
        "start_url": ".",
        "display": "standalone",
        "background_color": "#111827",
        "theme_color": "#2563eb",
        "description": "Aplikasi Analisa dan Kalkulator Saham Indonesia",
        "icons": [
            {
                "src": "https://cdn-icons-png.flaticon.com/512/2454/2454269.png",
                "sizes": "192x192",
                "type": "image/png"
            },
            {
                "src": "https://cdn-icons-png.flaticon.com/512/2454/2454269.png",
                "sizes": "512x512",
                "type": "image/png"
            }
        ]
    }
    
    manifest_json = json.dumps(manifest)
    b64_manifest = base64.b64encode(manifest_json.encode()).decode()
    manifest_href = f"data:application/manifest+json;base64,{b64_manifest}"
    
    pwa_html = f"""
    <head>
        <link rel="manifest" href="{manifest_href}" crossorigin="use-credentials" />
        <meta name="theme-color" content="#2563eb" />
        <meta name="apple-mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />
        <meta name="apple-mobile-web-app-title" content="Saham IDX" />
    </head>
    <div id="pwa-install-container"></div>
    <script>
        // Check if service worker is supported
        if ('serviceWorker' in navigator) {{
            console.log("PWA support injected");
        }}

        // Listen for the beforeinstallprompt event
        window.addEventListener('beforeinstallprompt', (e) => {{
            // Prevent the mini-infobar from appearing on mobile
            e.preventDefault();
            // Stash the event so it can be triggered later.
            window.deferredPrompt = e;
            
            // Create Install Button
            const container = document.getElementById('pwa-install-container');
            if (container) {{
                const btn = document.createElement('button');
                btn.innerText = '📲 Install App';
                btn.style.position = 'fixed';
                btn.style.bottom = '20px';
                btn.style.right = '20px';
                btn.style.zIndex = '9999';
                btn.style.backgroundColor = '#2563eb';
                btn.style.color = 'white';
                btn.style.border = 'none';
                btn.style.borderRadius = '8px';
                btn.style.padding = '10px 16px';
                btn.style.fontWeight = '600';
                btn.style.cursor = 'pointer';
                btn.style.boxShadow = '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)';
                
                btn.addEventListener('click', async () => {{
                    const promptEvent = window.deferredPrompt;
                    if (!promptEvent) return;
                    // Show the install prompt
                    promptEvent.prompt();
                    // Wait for the user to respond to the prompt
                    const {{ outcome }} = await promptEvent.userChoice;
                    console.log(`User response to the install prompt: ${{outcome}}`);
                    // We've used the prompt, and can't use it again, throw it away
                    window.deferredPrompt = null;
                    // Hide the button
                    btn.style.display = 'none';
                }});
                
                container.appendChild(btn);
            }}
        }});

        // If app is already installed, hide button
        window.addEventListener('appinstalled', () => {{
            const container = document.getElementById('pwa-install-container');
            if (container) container.style.display = 'none';
            console.log('PWA was installed');
        }});
    </script>
    """
    
    st.markdown(pwa_html, unsafe_allow_html=True)
