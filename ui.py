import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import datetime

# Function to load global CSS styling
def load_css():
    return """
    <style>
        /* Global Styles */
        [data-testid="stAppViewContainer"] {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #E5E7EB;
        }

        /* Hide Streamlit Branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}

        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background: rgba(22, 33, 62, 0.95);
            backdrop-filter: blur(10px);
            border-right: 1px solid rgba(255, 255, 255, 0.1);
        }

        /* Header Styling */
        h1 {
            background: linear-gradient(90deg, #00F5A0, #00D9F5);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 2.5rem !important;
            font-weight: 700 !important;
            text-align: center;
            margin-bottom: 2rem !important;
        }

        /* Sensor Card Styling */
        .card {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            padding: 1.5rem;
            text-align: center;
            transition: all 0.3s ease;
            margin: 10px 0;
            height: 160px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
        }

        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
        }

        .sensor-label {
            font-size: 1.2rem;
            font-weight: bold;
            color: #FFFFFF;
            margin-bottom: 1rem;
            word-break: break-word;
            max-width: 100%;
            overflow: hidden;
            text-overflow: ellipsis;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
        }

        .metric {
            font-size: 1.8rem;
            font-weight: 700;
            margin: 0;
            background: linear-gradient(90deg, #00F5A0, #00D9F5);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .metric.warning {
            background: linear-gradient(90deg, #FFB75E, #ED8F03);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .metric.danger {
            background: linear-gradient(90deg, #FF512F, #DD2476);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        /* Fix untuk container Streamlit */
        [data-testid="column"] {
            padding: 0 5px !important;
        }

        /* Metrik Styling */
        .metric-container {
            display: flex;
            justify-content: flex-end;
            align-items: center;
            flex-direction: column;
            margin-top: 20px;
        }

        .metric-title {
            font-size: 3rem;
            font-weight: bold;
            color: #FFFFFF;
            margin-bottom: 0.5rem;
        }

        .metric-value {
            font-size: 5rem;
            font-weight: 700;
            color: #00F5A0;
        }

        .metric-change {
            font-size: 1.8rem;
            color: #00D9F5;
        }
    </style>
    """

class SensorCard:
    """Class untuk menampilkan sensor dalam bentuk card"""

    @staticmethod
    def get_sensor_emoji(sensor_name):
        """Fungsi untuk menentukan emoji berdasarkan jenis sensor"""
        sensor_name = sensor_name.lower()
        emoji_map = {
            "power": "⚡", "energy": "⚡", "battery": "🔋", 
            "temperature": "🌡️", "humidity": "💧", "co2": "🌬️",
            "motion": "👤", "light": "💡", "network": "🌐", 
            "cost": "💰"
        }
        return next((emoji for key, emoji in emoji_map.items() if key in sensor_name), "📊")

    @staticmethod
    def render(sensor_name, sensor_value):
        """Fungsi untuk merender card sensor di Streamlit"""
        emoji = SensorCard.get_sensor_emoji(sensor_name)
        metric_class = "metric"

        try:
            value_float = float(sensor_value)
            if value_float >= 70:
                metric_class = "metric danger"
            elif value_float >= 30:
                metric_class = "metric warning"
        except ValueError:
            pass

        st.markdown(
            f"""
            <div class="card">
                <div class="sensor-label">
                    <span class="emoji">{emoji}</span>
                    {sensor_name}
                </div>
                <p class="{metric_class}">{sensor_value}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

class DashboardUI:
    """Class untuk menghandle UI utama di Streamlit"""

    def __init__(self):
        self.config_ui()

    def config_ui(self):
        """Konfigurasi tampilan utama"""
        st.set_page_config(page_title="Recap Eddie Home Assistant Graphic", layout="wide")
        st.markdown(load_css(), unsafe_allow_html=True)  # Load Styling
        st.markdown(
            "<h1 style='color: white; text-align: center;'>Recap Eddie Home Assistant Graphic</h1>",
            unsafe_allow_html=True
        )

    def render_sidebar(self):
        """Render sidebar buat pilih instance"""
        with st.sidebar:
            st.title("🏠 Home Assistant")
            return st.selectbox("Instance", options=["Eddie02", "EddieMawar7", "EddieHajiNawi", "EddieMawar8"], key="ha_instance")

    def render_sensors(self, sensors):
        """Render tampilan sensor dalam bentuk grid 3 kolom"""
        if sensors:
            cols = st.columns(3)
            for i, sensor in enumerate(sensors):
                with cols[i % 3]:
                    SensorCard.render(sensor["entity_id"], sensor["state"])
        else:
            st.warning("⚠️ No sensors detected.")

class PlotPV:
    """Class untuk menampilkan grafik PV Energy Production"""

    @staticmethod
    def process_pv_data(raw_data, requested_start, requested_end):
        """Extract timestamp dan nilai PV energy total"""
        if not raw_data or len(raw_data) == 0:
            st.warning("⚠️ Tidak ada data historis yang ditemukan.")
            return None
        
        try:
            entity_data = raw_data[0]  # Ambil data sensor pertama
            
            # Format data sesuai dengan response yang diterima
            data_points = []
            for entry in entity_data:
                timestamp = entry.get('last_updated') or entry.get('last_changed')
                state = entry.get('state')
                
                if timestamp and state:
                    try:
                        value = float(state)
                        ts = pd.to_datetime(timestamp).tz_convert('Asia/Jakarta')  # Convert to local timezone
                        data_points.append({
                            'timestamp': ts,
                            'value': value
                        })
                    except (ValueError, TypeError):
                        continue
            
            if not data_points:
                st.warning("⚠️ Tidak ada data valid yang dapat diproses")
                return None
            
            # Convert ke DataFrame dan sort
            df = pd.DataFrame(data_points)
            df.set_index('timestamp', inplace=True)
            df = df.sort_index()
            
            # Remove duplicates
            df = df[~df.index.duplicated(keep='first')]
            
            # Convert requested timestamps to pandas datetime for comparison
            req_start = pd.to_datetime(requested_start).tz_convert('Asia/Jakarta')
            req_end = pd.to_datetime(requested_end).tz_convert('Asia/Jakarta')
            
            # Filter data to match requested time range
            df_filtered = df[(df.index >= req_start) & (df.index <= req_end)]
            
            # Calculate hourly differences
            df_hourly = df_filtered.resample('H').ffill().diff().dropna()
            
            return df_hourly
            
        except Exception as e:
            st.error(f"Error saat memproses data: {str(e)}")
            import traceback
            st.error(traceback.format_exc())
            return None

    @staticmethod
    def render(df, entity_name="Daily Energy"):
        """Render grafik produksi PV dengan tampilan modern"""
        try:
            # Container untuk kontrol dan grafik
            with st.container():
                # Persiapkan data untuk plotting
                chart_data = df.copy()
                chart_data.index = chart_data.index.tz_localize(None)  # Remove timezone
                
                # Tentukan format tanggal berdasarkan range data
                date_range = (chart_data.index.max() - chart_data.index.min()).days if not df.empty else 0
                if date_range > 1:
                    tick_format = "%d/%m %H:%M"  # Format untuk multiple days
                    hover_format = "%d %b %Y %H:%M"  # Format lengkap untuk hover
                else:
                    tick_format = "%H:%M"  # Format untuk single day
                    hover_format = "%d %b %Y %H:%M"  # Format lengkap untuk hover
                
                # Konfigurasi plot
                fig = {
                    "data": [{
                        "x": chart_data.index,
                        "y": chart_data["value"],
                        "type": "bar",  # Change to bar chart
                        "marker": {
                            "color": "#FFD700",  # Change color to yellow
                        },
                        "hovertemplate": f"<b>%{{y:.2f}} kWh</b><br>%{{x|{hover_format}}}<extra></extra>",
                    }],
                    "layout": {
                        "plot_bgcolor": "#1a1a2e",
                        "paper_bgcolor": "#1a1a2e",
                        "font": {"color": "#ffffff"},
                        "xaxis": {
                            "showgrid": True,
                            "gridcolor": "#2a2a4a",
                            "title": None,
                            "tickformat": tick_format,
                            "hoverformat": hover_format,
                            "range": [
                                chart_data.index.min().replace(hour=0, minute=0),
                                chart_data.index.max().replace(hour=23, minute=59)
                            ] if not df.empty else [0, 0]
                        },
                        "yaxis": {
                            "showgrid": True,
                            "gridcolor": "#2a2a4a",
                            "title": "kWh",
                            "tickformat": ",.0f",
                        },
                        "margin": {"t": 5, "l": 5, "r": 5, "b": 5},  # Further reduced margins
                        "height": 220,  # Further reduced height
                        "hovermode": "x unified",
                    }
                }
                
                # Render plot
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        except Exception as e:
            st.error(f"Error saat plotting data: {str(e)}")

    @staticmethod
    def render_energy_usage(df_consumed_solar, df_import_pln, df_export_pln, df_energy_from_battery=None, df_energy_to_battery=None):
        """Render grafik penggunaan energi dengan tampilan modern"""
        try:
            # Container untuk kontrol dan grafik
            with st.container():
                # Persiapkan data untuk plotting
                chart_data = pd.DataFrame({
                    "Consumed Solar": df_consumed_solar["value"],
                    "Import PLN": df_import_pln["value"],
                })

                # Buat traces terpisah untuk nilai positif dan negatif
                traces = [
                    {
                        "x": chart_data.index,
                        "y": chart_data["Consumed Solar"],
                        "type": "bar",
                        "name": "Consumed Solar",
                        "marker": {"color": "rgba(255, 193, 7, 0.6)"},
                        "hovertemplate": "<b>Consumed Solar</b><br>%{y:.2f} kWh<extra></extra>",
                    },
                    {
                        "x": chart_data.index,
                        "y": chart_data["Import PLN"],
                        "type": "bar",
                        "name": "Import PLN",
                        "marker": {"color": "rgba(0, 123, 255, 0.6)"},
                        "hovertemplate": "<b>Import PLN</b><br>%{y:.2f} kWh<extra></extra>",
                    },
                    {
                        "x": df_export_pln.index,
                        "y": -df_export_pln["value"],  # Negative values for export
                        "type": "bar",
                        "name": "Export PLN",
                        "marker": {"color": "rgba(123, 0, 255, 0.6)"},
                        "hovertemplate": "<b>Export PLN</b><br>%{y:.2f} kWh<extra></extra>",
                    }
                ]

                if df_energy_from_battery is not None and df_energy_to_battery is not None:
                    traces.extend([
                        {
                            "x": df_energy_from_battery.index,
                            "y": df_energy_from_battery["value"],
                            "type": "bar",
                            "name": "Energy from Battery",
                            "marker": {"color": "rgba(0, 255, 0, 0.6)"},
                            "hovertemplate": "<b>Energy from Battery</b><br>%{y:.2f} kWh<extra></extra>",
                        },
                        {
                            "x": df_energy_to_battery.index,
                            "y": -df_energy_to_battery["value"],  # Negative values for energy to battery
                            "type": "bar",
                            "name": "Energy to Battery",
                            "marker": {"color": "rgba(255, 0, 255, 0.6)"},
                            "hovertemplate": "<b>Energy to Battery</b><br>%{y:.2f} kWh<extra></extra>",
                        }
                    ])

                # Tentukan format tanggal berdasarkan range data
                date_range = (chart_data.index.max() - chart_data.index.min()).days if not chart_data.empty else 0
                if date_range > 1:
                    tick_format = "%d/%m %H:%M"
                    hover_format = "%d %b %Y %H:%M"
                else:
                    tick_format = "%H:%M"
                    hover_format = "%d %b %Y %H:%M"
                
                # Konfigurasi plot
                fig = {
                    "data": traces,
                    "layout": {
                        "barmode": "relative",  # Change to relative to allow negative values
                        "plot_bgcolor": "#1a1a2e",
                        "paper_bgcolor": "#1a1a2e",
                        "font": {"color": "#ffffff"},
                        "xaxis": {
                            "showgrid": True,
                            "gridcolor": "#2a2a4a",
                            "title": None,
                            "tickformat": tick_format,
                            "hoverformat": hover_format,
                            "range": [
                                chart_data.index.min().replace(hour=0, minute=0),
                                chart_data.index.max().replace(hour=23, minute=59)
                            ] if not chart_data.empty else [0, 0]
                        },
                        "yaxis": {
                            "showgrid": True,
                            "gridcolor": "#2a2a4a",
                            "title": "kWh",
                            "tickformat": ",.0f",
                        },
                        "margin": {"t": 5, "l": 5, "r": 5, "b": 5},
                        "height": 220,
                        "hovermode": "x unified",
                    }
                }
                
                # Render plot
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        except Exception as e:
            st.error(f"Error saat plotting data: {str(e)}")

    @staticmethod
    def render_solar_production(df):
        """Render grafik produksi solar dengan tampilan modern"""
        try:
            # Container untuk kontrol dan grafik
            with st.container():
                # Persiapkan data untuk plotting
                chart_data = df.copy()
                chart_data.index = chart_data.index.tz_localize(None)  # Remove timezone
                
                # Tentukan format tanggal berdasarkan range data
                date_range = (chart_data.index.max() - chart_data.index.min()).days if not df.empty else 0
                if date_range > 1:
                    tick_format = "%d/%m %H:%M"  # Format untuk multiple days
                    hover_format = "%d %b %Y %H:%M"  # Format lengkap untuk hover
                else:
                    tick_format = "%H:%M"  # Format untuk single day
                    hover_format = "%d %b %Y %H:%M"  # Format lengkap untuk hover
                
                # Konfigurasi plot
                fig = {
                    "data": [{
                        "x": chart_data.index,
                        "y": chart_data["value"],
                        "type": "bar",
                        "name": "Solar Production",
                        "marker": {"color": "rgba(255, 193, 7, 0.6)"},
                        "hovertemplate": "<b>Solar Production</b><br>%{y:.2f} kWh<br>%{x|"+hover_format+"}<extra></extra>",
                    }],
                    "layout": {
                        "plot_bgcolor": "#1a1a2e",
                        "paper_bgcolor": "#1a1a2e",
                        "font": {"color": "#ffffff"},
                        "xaxis": {
                            "showgrid": True,
                            "gridcolor": "#2a2a4a",
                            "title": None,
                            "tickformat": tick_format,
                            "hoverformat": hover_format,
                            "range": [
                                chart_data.index.min().replace(hour=0, minute=0),
                                chart_data.index.max().replace(hour=23, minute=59)
                            ] if not df.empty else [0, 0]
                        },
                        "yaxis": {
                            "showgrid": True,
                            "gridcolor": "#2a2a4a",
                            "title": "kWh",
                            "tickformat": ",.0f",
                        },
                        "margin": {"t": 5, "l": 5, "r": 5, "b": 5},  # Further reduced margins
                        "height": 220,  # Further reduced height
                        "hovermode": "x unified",
                    }
                }
                
                # Render plot
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        except Exception as e:
            st.error(f"Error saat plotting data: {str(e)}")