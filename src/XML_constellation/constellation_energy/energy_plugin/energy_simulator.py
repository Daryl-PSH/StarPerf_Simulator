import h5py
import numpy as np
from skyfield.api import load
import os
import json

def energy_simulation(constellation, rechargable_battery_capacity_Wh=60, idle_energy_consumption_W=40, 
                      solar_panel_energy_generation_W=120):  

    constellation_name = constellation.constellation_name
    shells = constellation.shells
    num_shells = len(shells)
    cycle = 5792
    dT = 1
    
    data = load('de421.bsp')

    # Use same timescale as orbit configuration
    ts = load.timescale()
    t_ts = ts.utc(2023, 10, 1, 0, 0, range(0 , cycle , dT))

    constellation_energy = {}

    for i in range(num_shells):
        current_shell = constellation.shells[i]
        num_orbits = len(current_shell.orbits)
        constellation_energy["shell" + str(i)] = {}

        for j in range(num_orbits):
            current_orbit = current_shell.orbits[j]
            num_satellites = len(current_orbit.satellites)
            constellation_energy["shell" + str(i)]["orbit" + str(j)] = {}

            for k in range(num_satellites):
                current_satellite = current_orbit.satellites[k]
                satellite_obj = current_satellite.true_satellite

                time_interval = int(cycle / (cycle / dT))
                is_sunlit_arr = satellite_obj.at(t_ts).is_sunlit(data)
                battery_capacity = rechargable_battery_capacity_Wh
                constellation_energy["shell" + str(i)]["orbit" + str(j)]["satellite" + str(k)] = []

                for sunlit in is_sunlit_arr:
                    energy_consumed = idle_energy_consumption_W * time_interval / 3600
                    if sunlit:
                        energy_generated = solar_panel_energy_generation_W * time_interval / 3600
                        surplus_energy = energy_generated - energy_consumed
                        battery_capacity = min(battery_capacity + surplus_energy, rechargable_battery_capacity_Wh)
                    else:
                        battery_capacity = battery_capacity - energy_consumed # Add check if fall below 0
                    constellation_energy["shell" + str(i)]["orbit" + str(j)]["satellite" + str(k)].append([int(sunlit), battery_capacity])

    output_path = os.path.join("data", f"{constellation_name}_energy_simulation")
    os.makedirs(output_path, exist_ok=True)
    with open(os.path.join(output_path, "energy_consumption.json"), "w") as f:
        json.dump(constellation_energy, f)