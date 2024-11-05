from .deye_solarassistant import DeyeSolarAssistantInverter
# from .deye_synsynk import DeyeSynsynkInverter
# from .growatt import GrowattInverter

INVERTER_CLASSES = {
    #    "Deye-Synsynk": DeyeSynsynkInverter,
    "Deye-SolarAssistant": DeyeSolarAssistantInverter,
    #    "Growatt": GrowattInverter,
}


def get_inverter_class(model_name):
    try:
        return INVERTER_CLASSES[model_name]
    except KeyError:
        raise ValueError(f"Unsupported inverter model: {model_name}")
