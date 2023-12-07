from utils.yml_utils import load_yaml
from pathlib import Path

import floris
from floris.tools import FlorisInterface


def yml2TurbineType(yml):
    wt = load_yaml(yml)
    power = wt['performance']

    if 'Cp_curve' not in power or 'Ct_curve' not in power:
        raise NotImplementedError()
    
    turbine = dict()
    turbine['turbine_type'] = wt['name']
    turbine['generator_efficiency'] = 1.0
    turbine['hub_height'] = wt['hub_height']
    turbine['pP'] = 1.88
    turbine['pT'] = 1.88
    turbine['rotor_diameter'] = wt['rotor_diameter']
    turbine['TSR'] = 8.0
    turbine['ref_density_cp_ct'] = 1.225
    turbine['ref_tilt_cp_ct'] = 6.0
    turbine['power_thrust_table'] = {
        'power': wt['performance']['Cp_curve']['Cp_values'],
        'thrust': wt['performance']['Ct_curve']['Ct_values'],
        'wind_speed': wt['performance']['Cp_curve']['Cp_wind_speeds'],
    }

    return turbine


def ymlSystem2Floris(wind_energy_system_yml):
    floris_input_filepath = Path(floris.__file__).parent.parent / "examples" / "inputs" / "gch.yaml"
    floris_config = load_yaml(floris_input_filepath)
    wes = load_yaml(wind_energy_system_yml)
    wf = wes['wind_farm']
    x, y = [wf['layouts']['initial_layout']['coordinates'][xy] for xy in 'xy']

    turbine = yml2TurbineType(wf['turbines'])

    wind_directions = wes["site"]["energy_resource"]["wind_resource"]["wind_direction"]
    wind_speeds = wes["site"]["energy_resource"]["wind_resource"]["wind_speed"]
    TI = wes["site"]["energy_resource"]["wind_resource"]["turbulence_intensity"]["data"]

    floris_config["farm"]["layout_x"] = x
    floris_config["farm"]["layout_y"] = y
    floris_config["farm"]["turbine_type"] = [turbine]
    floris_config["flow_field"]["turbulence_intensity"] = TI
    floris_config["flow_field"]["wind_directions"] = wind_directions
    floris_config["flow_field"]["wind_speeds"] = wind_speeds
    
    return FlorisInterface(floris_config)


if __name__ == '__main__':
    examples_data_path = Path(__file__).parent.parent / "examples" / "plant"

    fi = ymlSystem2Floris(examples_data_path / "wind_energy_system" / "IEA37_case_study_4_wind_energy_system.yaml")

    fi.calculate_wake()
    print(fi.get_turbine_powers())
