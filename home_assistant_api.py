import requests
import streamlit as st
import datetime
import urllib.parse

class HomeAssistantAPI:
    def __init__(self, instance):
        ha_config = st.secrets[instance]
        self.url = ha_config["url"].rstrip('/')
        self.token = ha_config["token"]
        # Pastikan token tidak include 'Bearer' prefix
        if self.token.startswith('Bearer '):
            self.token = self.token[7:]
        
        self.headers = {
            "Authorization": f"Bearer {self.token}",  # Tambahkan 'Bearer ' prefix
            "Content-Type": "application/json"
        }

    def get_data(self):
        """Ambil semua data dari Home Assistant"""
        base_url = self.url.rstrip('/api').rstrip('/')
        response = requests.get(f"{base_url}/api/states", headers=self.headers)
        return response.json() if response.status_code == 200 else None

    def get_pv_statistics(self, start_datetime, end_datetime, entity_id="sensor.pv_energy_daily"):
        """Ambil data histori produksi PV energy berdasarkan range tanggal"""
        try:
            # Format timestamp dengan format yang benar untuk URL
            start_timestamp = start_datetime.isoformat()
            end_timestamp = end_datetime.isoformat()
            
            # URL yang benar sesuai dokumentasi
            base_url = self.url.rstrip('/api').rstrip('/')
            
            # Encode timestamp untuk URL
            encoded_start = urllib.parse.quote(start_timestamp)
            encoded_end = urllib.parse.quote(end_timestamp)
            
            api_url = f"{base_url}/api/history/period/{encoded_start}"
            
            params = {
                "filter_entity_id": entity_id,
                "end_time": end_timestamp,
                "minimal_response": "false",
                "significant_changes_only": "false"
            }
            
            # # Debug: Print timestamps, API URL, and parameters
            # st.write(f"Debug - Start Timestamp: {start_timestamp}")
            # st.write(f"Debug - End Timestamp: {end_timestamp}")
            # st.write(f"Debug - API URL: {api_url}")
            # st.write(f"Debug - Parameters: {params}")
            
            response = requests.get(api_url, headers=self.headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                # # Debug: Print JSON output
                # st.write("Debug - JSON Output:", data)
                
                if not data or len(data) == 0:
                    st.warning("⚠️ Tidak ada data PV yang ditemukan untuk periode tersebut")
                    return None
                
                return data
            else:
                st.error(f"⚠️ Gagal mengambil data PV: {response.status_code}")
                st.error(f"Response: {response.text}")
                return None
            
        except Exception as e:
            st.error(f"⚠️ Error saat mengambil data PV: {str(e)}")
            import traceback
            st.error(traceback.format_exc())
            return None