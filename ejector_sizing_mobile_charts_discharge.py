
import streamlit as st
import math
import matplotlib.pyplot as plt

st.set_page_config(page_title="Ejector Sizing Tool", layout="centered")
st.title("📱 Ejector Sizing Tool with Charts + Discharge Pressure")

st.markdown("Multi-stream tool with auto-sizing, flow/velocity charting, and discharge pressure input.")

stream_data = []

def get_density(fluid, pressure, api=None):
    R = 10.73
    T = 520
    MW = 18
    if fluid == "Gas":
        return (pressure * MW) / (R * T)
    elif fluid == "Water":
        return 62.4
    elif fluid == "Oil":
        return (141.5 / (api + 131.5)) * 62.4 if api else 53
    return 0

def convert_mass_flow(fluid, flow, rho):
    R = 10.73
    T = 520
    MW = 18
    if fluid == "Gas":
        lbmol = (flow * 1e6) / (R * T)
        return lbmol * MW
    else:
        ft3 = flow * 5.615  # Convert BPD to ft³
        return ft3 * rho

num_motive = st.number_input("Number of Motive Streams", min_value=1, max_value=5, value=1)
num_suction = st.number_input("Number of Suction Streams", min_value=1, max_value=5, value=1)

st.subheader("🔵 Motive Streams")
for i in range(int(num_motive)):
    st.markdown(f"**Motive Stream {i+1}**")
    fluid = st.selectbox(f"Fluid Type (Motive {i+1})", ["Gas", "Oil", "Water"], key=f"motive_fluid_{i}")
    flow = st.number_input(f"Flow ({'MMSCFD' if fluid == 'Gas' else 'BPD'})", key=f"motive_flow_{i}")
    pressure = st.number_input("Pressure (psi)", key=f"motive_pressure_{i}")
    api = None
    if fluid == "Oil":
        api = st.number_input("API Gravity (optional)", key=f"motive_api_{i}")
    stream_data.append({"type": fluid, "flow": flow, "pressure": pressure, "api": api})

st.subheader("🟢 Suction Streams")
for i in range(int(num_suction)):
    st.markdown(f"**Suction Stream {i+1}**")
    fluid = st.selectbox(f"Fluid Type (Suction {i+1})", ["Gas", "Oil", "Water"], key=f"suction_fluid_{i}")
    flow = st.number_input(f"Flow ({'MMSCFD' if fluid == 'Gas' else 'BPD'})", key=f"suction_flow_{i}")
    pressure = st.number_input("Pressure (psi)", key=f"suction_pressure_{i}")
    api = None
    if fluid == "Oil":
        api = st.number_input("API Gravity (optional)", key=f"suction_api_{i}")
    stream_data.append({"type": fluid, "flow": flow, "pressure": pressure, "api": api})

# New discharge pressure input
st.subheader("📤 Discharge Conditions")
discharge_pressure = st.number_input("Discharge Pressure (psi)", min_value=0.0, value=200.0, step=10.0)

if st.button("Calculate and Show Charts"):
    total_mass_flow = 0
    rho_list = []
    flows = []

    for stream in stream_data:
        if stream["flow"] <= 0:
            continue
        rho = get_density(stream["type"], stream["pressure"], stream["api"])
        mass_flow = convert_mass_flow(stream["type"], stream["flow"], rho)
        total_mass_flow += mass_flow
        rho_list.append(rho)
        flows.append(stream["flow"])

    if total_mass_flow > 0 and rho_list:
        avg_rho = sum(rho_list) / len(rho_list)
        avg_velocity = 125
        mass_flow_rate = total_mass_flow / 86400
        area_throat = mass_flow_rate / (avg_rho * avg_velocity)
        diameter_throat = 2 * math.sqrt(area_throat / math.pi)
        diameter_throat_in = diameter_throat * 12
        diameter_mixing_in = 2 * diameter_throat_in

        st.success("✅ Calculation Complete!")
        st.metric("Total Mass Flow", f"{total_mass_flow:.2f} lbm/day")
        st.metric("Average Density", f"{avg_rho:.2f} lb/ft³")
        st.metric("Nozzle Throat Diameter", f"{diameter_throat_in:.2f} in")
        st.metric("Mixing Chamber Diameter", f"{diameter_mixing_in:.2f} in")
        st.metric("Discharge Pressure", f"{discharge_pressure:.2f} psi")

        # Charts
        st.subheader("📊 Charts")
        fig, ax = plt.subplots()
        ax.plot(flows, [avg_velocity] * len(flows), label="Velocity (ft/s)", marker='o')
        ax.plot(flows, [diameter_throat_in] * len(flows), label="Throat Diameter (in)", marker='s')
        ax.set_xlabel("Flow")
        ax.set_ylabel("Value")
        ax.set_title("Flow vs Velocity & Diameter")
        ax.legend()
        st.pyplot(fig)
    else:
        st.warning("Please enter valid flow and pressure values.")
