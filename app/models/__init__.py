from flask.ext.mongoengine import MongoEngine

db = MongoEngine()

non_static_attrs = ['source', 'program', 'logger']

static_attrs = ['station_name', 'lat', 'lon', 'elevation',
                'Year', 'Month', 'DOM', 'Minute', 'Hour',
                'Day_of_Year', 'Second', 'uSecond', 'WeekDay']

# Setting expected ranges for units. It is ok to include multiple ways of
# writing the same unit, just put all the units in a list
flag_by_units = {}

# TODO:
# This isn't really by variable. It's by units. We should probably
# think about how to set limits by _either_ variable or units, with
# variable-specific limits taking precedence over unit-specifc ones
variables = {
    'temp': {
        'min': -40,
        'max': 120,
        'units': ['Deg C', 'C', 'degC']
    },
    'percent': {
        'min': 0,
        'max': 0,
        'units': ['percent', '%']
    },
    'energy_flux': {
        'min': -800,
        'max': 1400,
        'units': ['W/m^2', 'W/meter^2']
    },
    'soil heat flux calibration': {  # NOT SURE ABOUT THESE MAX/MIN
        'min': 0,  # Must be postivie
        'max': 100,
        'units': ['W/(m^2 mV)']
    },
    'battery voltage': {
        'min': 11,
        'max': 15,
        'units': ['Volts', 'V']
    },
    'CS616 Period (uS)': {  # NOT SURE ABOUT THESE MAX/MIN
        'min': 0,
        'max': 2000,
        'units': ['uSec']

    },
    'Kelvin temperature': {
        'min': 233,  # About -40 degrees C. Seems safe.
        'max': 350,  # About 120 degrees C. Toasty.
        'units': ['K', 'Kelvin']
    },
    'pressure, kPa': {
        'min': 0,  # Pressure has to be postive (in the atmosphere)
        'max': 100,  # One atmosphere is 83kPa or something.
        'units': ['kPa']
    },
    'millivolts': {
        'min': 0,
        'max': 5000,
        'units': ['mV']
    },
    'wind speed': {
        'min': -40,  # Seems a little outrageous, but neg for sonic
        'max': 40,  # Again, higher than reasonable.
        'units': ['m/s']
    },
    'molar fluxes': {
        'min': -100,  # Can be negative (uptake of CO2)
        'max': 100,
        'units': ['umol/s/m2']
    },
    'nan': {
        'min': -9999,
        'max': 9999,
        'units': ['nan']
    }
}

for variable in variables:
    for unit in variables[variable]['units']:
        flag_by_units.update({
            unit: {
                'min': variables[variable]['min'],
                'max': variables[variable]['max']}
        })
