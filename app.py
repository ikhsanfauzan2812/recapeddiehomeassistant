import streamlit as st
from home_assistant_api import HomeAssistantAPI
from ui import DashboardUI, PlotPV
import datetime

def main():
    ui = DashboardUI()
    
    instances = ["Eddie02", "Mawar7", "HajiNawi", "Mawar8"]
    ha_apis = {instance: HomeAssistantAPI(instance) for instance in instances}

    # Date input for start and end date
    col_start, col_end = st.columns(2)
    with col_start:
        start_date = st.date_input(
            "Start date",
            value=datetime.datetime.now().date(),
            format="DD/MM/YYYY",
            key="start_date_picker"
        )
    with col_end:
        end_date = st.date_input(
            "End date",
            value=datetime.datetime.now().date(),
            format="DD/MM/YYYY",
            key="end_date_picker"
        )

    # Set time to 00:00 and 23:59
    start_time = datetime.time(0, 0)
    end_time = datetime.time(23, 59)

    # Combine date and time and convert to UTC
    local_tz = datetime.timezone(datetime.timedelta(hours=7))  # WIB = UTC+7

    # Start datetime
    local_start = datetime.datetime.combine(start_date, start_time)
    start_datetime = local_start.replace(tzinfo=local_tz)

    # End datetime
    local_end = datetime.datetime.combine(end_date, end_time)
    end_datetime = local_end.replace(tzinfo=local_tz)

    # Iterate over each instance and fetch data
    col1, col2, col3, col4 = st.columns(4)

    for instance, col in zip(instances, [col1, col2, col3, col4]):
        with col:
            st.markdown(f"### 🔆 {instance} PV Production")
            import_plts_entity = "sensor.pv_energy_total" if instance == "Eddie02" else "sensor.import_energy_plts"
            solar_data = ha_apis[instance].get_pv_statistics(start_datetime, end_datetime, import_plts_entity)
            if solar_data:
                df_solar = PlotPV.process_pv_data(solar_data, start_datetime, end_datetime)
                if df_solar is not None:
                    PlotPV.render_solar_production(df_solar)

            st.markdown(f"### ⚡ {instance} Energy Usage")
            if instance == "Eddie02":
                import_plts_entity = "sensor.pv_energy_total"
                import_pln_entity = "sensor.victron_grid_energy_forward_total_32"
                export_pln_entity = "sensor.victron_grid_energy_reverse_total_32"
                energy_from_battery_entity = "sensor.energy_from_battery"
                energy_to_battery_entity = "sensor.energy_to_battery"
            else:
                import_plts_entity = "sensor.import_energy_plts"
                import_pln_entity = "sensor.import_energy_pln"
                export_pln_entity = "sensor.export_energy_pln"
                energy_from_battery_entity = None
                energy_to_battery_entity = None

            import_plts_data = ha_apis[instance].get_pv_statistics(start_datetime, end_datetime, import_plts_entity)
            import_pln_data = ha_apis[instance].get_pv_statistics(start_datetime, end_datetime, import_pln_entity)
            export_pln_data = ha_apis[instance].get_pv_statistics(start_datetime, end_datetime, export_pln_entity)

            if energy_from_battery_entity and energy_to_battery_entity:
                energy_from_battery_data = ha_apis[instance].get_pv_statistics(start_datetime, end_datetime, energy_from_battery_entity)
                energy_to_battery_data = ha_apis[instance].get_pv_statistics(start_datetime, end_datetime, energy_to_battery_entity)
            else:
                energy_from_battery_data = None
                energy_to_battery_data = None

            if import_plts_data and import_pln_data:
                df_import_plts = PlotPV.process_pv_data(import_plts_data, start_datetime, end_datetime)
                df_import_pln = PlotPV.process_pv_data(import_pln_data, start_datetime, end_datetime)
                
                # Initialize df_export_pln as None
                df_export_pln = None
                df_consumed_solar = None

                # Process export PLN data if available
                if export_pln_data:
                    df_export_pln = PlotPV.process_pv_data(export_pln_data, start_datetime, end_datetime)

                # Calculate consumed solar - always create it if we have import_plts data
                if df_import_plts is not None:
                    df_consumed_solar = df_import_plts.copy()
                    if df_export_pln is not None and not df_export_pln.empty:
                        # Subtract export only if we have valid export data
                        df_consumed_solar["value"] = df_import_plts["value"] - df_export_pln["value"]
                    # else use import_plts as consumed_solar (assume all production is consumed)

                if energy_from_battery_data and energy_to_battery_data:
                    df_energy_from_battery = PlotPV.process_pv_data(energy_from_battery_data, start_datetime, end_datetime)
                    df_energy_to_battery = PlotPV.process_pv_data(energy_to_battery_data, start_datetime, end_datetime)
                else:
                    df_energy_from_battery = None
                    df_energy_to_battery = None

                # # Debug logging
                # st.write(f"Debug - {instance}:")
                # st.write(f"df_import_plts: {df_import_plts is not None}")
                # st.write(f"df_import_pln: {df_import_pln is not None}")
                # st.write(f"df_export_pln: {df_export_pln is not None}")
                # st.write(f"df_consumed_solar: {df_consumed_solar is not None}")

                if df_import_plts is not None and df_import_pln is not None and df_consumed_solar is not None:
                    PlotPV.render_energy_usage(df_consumed_solar, df_import_pln, df_export_pln, df_energy_from_battery, df_energy_to_battery)

if __name__ == "__main__":
    main()
