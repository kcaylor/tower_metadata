"""Settings used in the Metadata program."""
from datetime import datetime

# The following list defines all sensors that have been deployed on the Mpala
# tower. It must be updated when sensors are altered on the tower.
sensors = [
    {
        'name': 'li-7500',
        'description': 'open path infrared gas analyzer (CO2 and H2O)',
        'serial_number': '',
        'manufacturor': 'LiCor',
        'supplier': 'Campbell Scientific, Inc.',
        'purchase_date': datetime(year=2009, month=1, day=1),
        'installation_date': datetime(year=2009, month=1, day=1),
        'calibration_certificate': '',
        'invoice': '',
        'manual': '',
        'notes': '',
        'last_calibrated': datetime(year=2009, month=1, day=1),
    },
    {
        'name': 'csat3',
        'description': 'three dimensional sonic anemometer',
        'serial_number': '',
        'manufacturor': 'Campbell Scientific, Inc.',
        'supplier': 'Campbell Scientific, Inc.',
        'purchase_date': datetime(year=2009, month=1, day=1),
        'installation_date': datetime(year=2009, month=1, day=1),
        'calibration_certificate': '',
        'invoice': '',
        'manual': '',
        'notes': '',
        'last_calibrated': datetime(year=2009, month=1, day=1),
    },
    {
        'name': 'wvia',
        'description': 'water vapor isotope analyzer',
        'serial_number': '',
        'manufacturor': 'Los Gatos, Inc.',
        'supplier': 'Los Gatos, Inc.',
        'purchase_date': datetime(year=2009, month=1, day=1),
        'installation_date': datetime(year=2009, month=1, day=1),
        'calibration_certificate': '',
        'invoice': '',
        'manual': '',
        'notes': '',
        'last_calibrated': datetime(year=2009, month=1, day=1),
    },
]

# The following dict specifies variable definitions for the Mpala tower
# The QA/QC code will check for variable definitions first when cleaning data
# It will also use these variable definitions to specify sensors deployed on
# each day. This dictionary has to be maintained to include any new variables
# added to the tower datafiles.
# TODO: Figure out how to harvest variable names from program files.
variables = {
}

# TODO:
# This isn't really by variable. It's by units. We should probably
# think about how to set limits by _either_ variable or units, with
# variable-specific limits taking precedence over unit-specifc ones
units = {
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
