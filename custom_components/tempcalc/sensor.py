from __future__ import annotations

import math
from datetime import timedelta

from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.const import (
    UnitOfTemperature,
    UnitOfPressure,
    UnitOfEnergy,
    UnitOfMassDensity,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_state_change_event

from homeassistant.config_entries import ConfigEntry

from .const import (
    DOMAIN,
    PLANT_KEYWORDS,
    OUTDOOR_KEYWORDS,
    DEFAULT_ENABLE_ABSOLUTE_HUMIDITY,
    DEFAULT_ENABLE_MOLD_INDEX,
    DEFAULT_ENABLE_DEW_POINT,
    DEFAULT_ENABLE_ENTHALPY,
    DEFAULT_ENABLE_VENTILATION_RECOMMENDATION,
    DEFAULT_ENABLE_VENTILATION_DURATION,
    MIN_INDOOR_TEMP,
    MAX_TEMP_DROP,
    MOLD_INDEX_MIN,
    MOLD_INDEX_MAX,
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
):
    """Set up TempCalc sensors."""

    config = entry.options

    enable_absolute_humidity = config.get(
        "enable_absolute_humidity", DEFAULT_ENABLE_ABSOLUTE_HUMIDITY
    )
    enable_mold_index = config.get(
        "enable_mold_index", DEFAULT_ENABLE_MOLD_INDEX
    )
    enable_dew_point = config.get(
        "enable_dew_point", DEFAULT_ENABLE_DEW_POINT
    )
    enable_enthalpy = config.get(
        "enable_enthalpy", DEFAULT_ENABLE_ENTHALPY
    )
    enable_ventilation_recommendation = config.get(
        "enable_ventilation_recommendation",
        DEFAULT_ENABLE_VENTILATION_RECOMMENDATION,
    )
    enable_ventilation_duration = config.get(
        "enable_ventilation_duration",
        DEFAULT_ENABLE_VENTILATION_DURATION,
    )

    indoor_temp = config.get("indoor_temperature_sensor")
    indoor_humidity = config.get("indoor_humidity_sensor")

    outdoor_temp = config.get("outdoor_temperature_sensor")
    outdoor_humidity = config.get("outdoor_humidity_sensor")

    entities = []

    # Base sensors
    if enable_absolute_humidity:
        entities.append(
            AbsoluteHumiditySensor(
                hass,
                entry,
                indoor_temp,
                indoor_humidity,
                outdoor_temp,
                outdoor_humidity,
            )
        )

    if enable_dew_point:
        entities.append(
            DewPointSensor(
                hass,
                entry,
                indoor_temp,
                indoor_humidity,
            )
        )

    if enable_enthalpy:
        entities.append(
            EnthalpySensor(
                hass,
                entry,
                indoor_temp,
                indoor_humidity,
            )
        )

    if enable_mold_index:
        entities.append(
            MoldIndexSensor(
                hass,
                entry,
                indoor_temp,
                indoor_humidity,
            )
        )

    if enable_ventilation_recommendation:
        entities.append(
            VentilationRecommendationSensor(
                hass,
                entry,
                indoor_temp,
                indoor_humidity,
                outdoor_temp,
                outdoor_humidity,
            )
        )

    if enable_ventilation_duration:
        entities.append(
            VentilationDurationSensor(
                hass,
                entry,
                indoor_temp,
                indoor_humidity,
                outdoor_temp,
                outdoor_humidity,
            )
        )

    async_add_entities(entities)


# ---------------------------------------------------------
# Helper functions
# ---------------------------------------------------------

def calc_absolute_humidity(temp_c: float, rel_humidity: float) -> float:
    """Calculate absolute humidity (g/m³) using Magnus formula."""
    if temp_c is None or rel_humidity is None:
        return None

    saturation_pressure = 6.112 * math.exp((17.67 * temp_c) / (temp_c + 243.5))
    vapor_pressure = rel_humidity / 100 * saturation_pressure
    abs_humidity = 2.1674 * vapor_pressure / (273.15 + temp_c)
    return round(abs_humidity * 1000, 2)


def calc_dew_point(temp_c: float, rel_humidity: float) -> float:
    """Calculate dew point using Magnus formula."""
    if temp_c is None or rel_humidity is None:
        return None

    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(rel_humidity / 100)
    dew_point = (b * alpha) / (a - alpha)
    return round(dew_point, 2)


def calc_enthalpy(temp_c: float, rel_humidity: float) -> float:
    """Calculate enthalpy (kJ/kg)."""
    if temp_c is None or rel_humidity is None:
        return None

    abs_h = calc_absolute_humidity(temp_c, rel_humidity) / 1000
    enthalpy = 1.006 * temp_c + abs_h * (2501 + 1.86 * temp_c)
    return round(enthalpy, 2)


# ---------------------------------------------------------
# Base class
# ---------------------------------------------------------

class TempCalcBaseSensor(SensorEntity):
    """Base class for all TempCalc sensors."""

    _attr_has_entity_name = True
    _attr_should_poll = False
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        indoor_temp: str,
        indoor_humidity: str,
        outdoor_temp: str | None = None,
        outdoor_humidity: str | None = None,
    ):
        self.hass = hass
        self.entry = entry

        self.indoor_temp = indoor_temp
        self.indoor_humidity = indoor_humidity
        self.outdoor_temp = outdoor_temp
        self.outdoor_humidity = outdoor_humidity

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="TempCalc",
            manufacturer="TempCalc",
            model="Climate Calculation Engine",
        )

    async def async_added_to_hass(self):
        """Register state listeners."""

        sensors = [self.indoor_temp, self.indoor_humidity]

        if self.outdoor_temp:
            sensors.append(self.outdoor_temp)
        if self.outdoor_humidity:
            sensors.append(self.outdoor_humidity)

        async_track_state_change_event(
            self.hass,
            sensors,
            self._async_state_changed,
        )

    @callback
    async def _async_state_changed(self, event):
        """Update when any linked sensor changes."""
        self.async_write_ha_state()


# ---------------------------------------------------------
# Absolute Humidity
# ---------------------------------------------------------

class AbsoluteHumiditySensor(TempCalcBaseSensor):
    _attr_name = "Absolute Humidity"
    _attr_native_unit_of_measurement = UnitOfMassDensity.GRAMS_PER_CUBIC_METER
    _attr_device_class = SensorDeviceClass.HUMIDITY

    @property
    def native_value(self):
        temp = self._get_state(self.indoor_temp)
        hum = self._get_state(self.indoor_humidity)
        return calc_absolute_humidity(temp, hum)

    def _get_state(self, entity_id):
        state = self.hass.states.get(entity_id)
        if state is None:
            return None
        try:
            return float(state.state)
        except:
            return None


# ---------------------------------------------------------
# Dew Point
# ---------------------------------------------------------

class DewPointSensor(TempCalcBaseSensor):
    _attr_name = "Dew Point"
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_device_class = SensorDeviceClass.TEMPERATURE

    @property
    def native_value(self):
        temp = self._get_state(self.indoor_temp)
        hum = self._get_state(self.indoor_humidity)
        return calc_dew_point(temp, hum)

    def _get_state(self, entity_id):
        state = self.hass.states.get(entity_id)
        if state is None:
            return None
        try:
            return float(state.state)
        except:
            return None


# ---------------------------------------------------------
# Enthalpy
# ---------------------------------------------------------

class EnthalpySensor(TempCalcBaseSensor):
    _attr_name = "Enthalpy"
    _attr_native_unit_of_measurement = "kJ/kg"

    @property
    def native_value(self):
        temp = self._get_state(self.indoor_temp)
        hum = self._get_state(self.indoor_humidity)
        return calc_enthalpy(temp, hum)

    def _get_state(self, entity_id):
        state = self.hass.states.get(entity_id)
        if state is None:
            return None
        try:
            return float(state.state)
        except:
            return None


# ---------------------------------------------------------
# Mold Index (0–6)
# ---------------------------------------------------------

class MoldIndexSensor(TempCalcBaseSensor):
    _attr_name = "Mold Index"
    _attr_native_unit_of_measurement = None

    _mold_value = 0.0

    @property
    def native_value(self):
        temp = self._get_state(self.indoor_temp)
        hum = self._get_state(self.indoor_humidity)

        if temp is None or hum is None:
            return None

        # Simple mold risk model
        if hum > 70 and temp > 15:
            self._mold_value = min(self._mold_value + 0.05, MOLD_INDEX_MAX)
        else:
            self._mold_value = max(self._mold_value - 0.02, MOLD_INDEX_MIN)

        return round(self._mold_value, 2)

    def _get_state(self, entity_id):
        state = self.hass.states.get(entity_id)
        if state is None:
            return None
        try:
            return float(state.state)
        except:
            return None


# ---------------------------------------------------------
# Ventilation Recommendation
# ---------------------------------------------------------

class VentilationRecommendationSensor(TempCalcBaseSensor):
    _attr_name = "Ventilation Recommendation"

    @property
    def native_value(self):
        indoor_temp = self._get_state(self.indoor_temp)
        indoor_hum = self._get_state(self.indoor_humidity)
        outdoor_temp = self._get_state(self.outdoor_temp)
        outdoor_hum = self._get_state(self.outdoor_humidity)

        if None in (indoor_temp, indoor_hum, outdoor_temp, outdoor_hum):
            return "unknown"

        ah_in = calc_absolute_humidity(indoor_temp, indoor_hum)
        ah_out = calc_absolute_humidity(outdoor_temp, outdoor_hum)

        if ah_out < ah_in:
            return "ventilate_now"
        else:
            return "do_not_ventilate"

    def _get_state(self, entity_id):
        state = self.hass.states.get(entity_id)
        if state is None:
            return None
        try:
            return float(state.state)
        except:
            return None


# ---------------------------------------------------------
# Ventilation Duration
# ---------------------------------------------------------

class VentilationDurationSensor(TempCalcBaseSensor):
    _attr_name = "Ventilation Duration"
    _attr_native_unit_of_measurement = "min"

    @property
    def native_value(self):
        indoor_temp = self._get_state(self.indoor_temp)
        indoor_hum = self._get_state(self.indoor_humidity)
        outdoor_temp = self._get_state(self.outdoor_temp)
        outdoor_hum = self._get_state(self.outdoor_humidity)

        if None in (indoor_temp, indoor_hum, outdoor_temp, outdoor_hum):
            return None

        ah_in = calc_absolute_humidity(indoor_temp, indoor_hum)
        ah_out = calc_absolute_humidity(outdoor_temp, outdoor_hum)

        delta = ah_in - ah_out

        if delta <= 0:
            return 0

        duration = 5 + (delta / 2)
        return round(duration, 0)

    def _get_state(self, entity_id):
        state = self.hass.states.get(entity_id)
        if state is None:
            return None
        try:
            return float(state.state)
        except:
            return None
