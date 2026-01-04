# TempCalc  
Advanced Climate Calculation Engine for Home Assistant  
(English below • Deutsch unten)

---

# 🇬🇧 English

## Overview
TempCalc is a powerful climate calculation engine for Home Assistant.  
It generates advanced climate metrics based on your indoor and optional outdoor sensors:

- Absolute humidity (g/m³)  
- Dew point (°C)  
- Enthalpy (kJ/kg)  
- Mold index (0–6, dynamic)  
- Ventilation recommendation  
- Ventilation duration (minutes)

TempCalc supports **automatic outdoor sensor detection**, **manual selection**, and **custom sensor IDs**.

Compatible with **Home Assistant 2025.12+**.

---

## Features

### ✔ Automatic outdoor sensor detection
TempCalc automatically detects outdoor sensors using:
- Device class  
- Area assignment  
- Integration metadata  
- Name patterns (balcony, garden, outdoor, etc.)

### ✔ Manual selection + custom IDs
You can override everything and enter your own sensor IDs.

### ✔ Advanced climate calculations
- **Absolute humidity** using Magnus formula  
- **Dew point**  
- **Enthalpy**  
- **Mold index** with accumulation  
- **Ventilation recommendation** based on humidity differential  
- **Ventilation duration** based on humidity delta

### ✔ Auto‑reload
Changing options reloads all sensors instantly.

---

## Installation

### HACS (recommended)
1. Add this repository as a custom integration  
2. Search for **TempCalc**  
3. Install  
4. Restart Home Assistant

### Manual installation
Copy the folder:

```
custom_components/tempcalc/
```

into your Home Assistant configuration directory.

Restart Home Assistant.

---

## Configuration

### Step 1: Add integration
Go to:

**Settings → Devices & Services → Add Integration → TempCalc**

### Step 2: Select sensors
You must select:
- Indoor temperature  
- Indoor humidity  

Optional:
- Outdoor temperature  
- Outdoor humidity  

### Step 3: Enable/disable calculated sensors
You can enable:
- Absolute humidity  
- Dew point  
- Enthalpy  
- Mold index  
- Ventilation recommendation  
- Ventilation duration  

---

## Entities created

| Entity | Description |
|--------|-------------|
| `sensor.<name>_absolute_humidity` | Absolute humidity in g/m³ |
| `sensor.<name>_dew_point` | Dew point temperature |
| `sensor.<name>_enthalpy` | Moist air enthalpy |
| `sensor.<name>_mold_index` | Mold growth risk (0–6) |
| `sensor.<name>_ventilation_recommendation` | "ventilate_now" / "do_not_ventilate" |
| `sensor.<name>_ventilation_duration` | Recommended ventilation time in minutes |

---

## Ventilation logic

### Ventilation recommendation
TempCalc compares indoor and outdoor **absolute humidity**:

- If outdoor < indoor → `ventilate_now`  
- Otherwise → `do_not_ventilate`

### Ventilation duration
Based on humidity delta:

```
duration = 5 + (delta / 2)
```

Rounded to full minutes.

---

## Troubleshooting

### No sensors detected
Make sure:
- Entities have numeric values  
- Device class is set correctly  
- Plant sensors are excluded automatically  

### Mold index stuck at 0
The mold index increases only when:
- Humidity > 70%  
- Temperature > 15°C  

---

# 🇩🇪 Deutsch

## Übersicht
TempCalc ist eine leistungsstarke Klima‑Berechnungs‑Engine für Home Assistant.  
Sie erzeugt erweiterte Klimawerte basierend auf Innen‑ und optionalen Außensensoren:

- Absolute Feuchte (g/m³)  
- Taupunkt (°C)  
- Enthalpie (kJ/kg)  
- Schimmelindex (0–6, dynamisch)  
- Lüftungsempfehlung  
- Lüftungsdauer (Minuten)

TempCalc unterstützt **automatische Außensensor‑Erkennung**, **manuelle Auswahl** und **freie Eingabe eigener Sensor‑IDs**.

Kompatibel mit **Home Assistant 2025.12+**.

---

## Funktionen

### ✔ Automatische Erkennung von Außensensoren
TempCalc erkennt Außensensoren anhand von:
- Device Class  
- Bereich „Außen“  
- Integrations‑Metadaten  
- Namensmustern (Balkon, Garten, Outdoor, etc.)

### ✔ Manuelle Auswahl + freie Eingabe
Du kannst alles überschreiben und eigene Sensor‑IDs eintragen.

### ✔ Erweiterte Klima‑Berechnungen
- **Absolute Feuchte** (Magnus‑Formel)  
- **Taupunkt**  
- **Enthalpie**  
- **Schimmelindex** mit Akkumulation  
- **Lüftungsempfehlung** basierend auf Feuchte‑Differenz  
- **Lüftungsdauer** basierend auf Feuchte‑Delta

### ✔ Auto‑Reload
Änderungen in den Optionen werden sofort übernommen.

---

## Installation

### HACS (empfohlen)
1. Repository als benutzerdefinierte Integration hinzufügen  
2. Nach **TempCalc** suchen  
3. Installieren  
4. Home Assistant neu starten

### Manuelle Installation
Ordner:

```
custom_components/tempcalc/
```

in das Home Assistant Konfigurationsverzeichnis kopieren.

Home Assistant neu starten.

---

## Konfiguration

### Schritt 1: Integration hinzufügen
**Einstellungen → Geräte & Dienste → Integration hinzufügen → TempCalc**

### Schritt 2: Sensoren auswählen
Pflicht:
- Innentemperatur  
- Innenfeuchte  

Optional:
- Außentemperatur  
- Außenfeuchte  

### Schritt 3: Berechnete Sensoren aktivieren/deaktivieren
Aktivierbar:
- Absolute Feuchte  
- Taupunkt  
- Enthalpie  
- Schimmelindex  
- Lüftungsempfehlung  
- Lüftungsdauer  

---

## Erzeugte Entitäten

| Entität | Beschreibung |
|--------|--------------|
| `sensor.<name>_absolute_humidity` | Absolute Feuchte in g/m³ |
| `sensor.<name>_dew_point` | Taupunkt |
| `sensor.<name>_enthalpy` | Enthalpie der feuchten Luft |
| `sensor.<name>_mold_index` | Schimmelrisiko (0–6) |
| `sensor.<name>_ventilation_recommendation` | „ventilate_now“ / „do_not_ventilate“ |
| `sensor.<name>_ventilation_duration` | Empfohlene Lüftungsdauer in Minuten |

---

## Lüftungslogik

### Lüftungsempfehlung
Vergleich der absoluten Feuchte:

- Außen < Innen → `ventilate_now`  
- Sonst → `do_not_ventilate`

### Lüftungsdauer
Basierend auf Feuchte‑Delta:

```
dauer = 5 + (delta / 2)
```

Gerundet auf volle Minuten.

---

## Fehlerbehebung

### Keine Sensoren gefunden
Bitte prüfen:
- Entitäten haben numerische Werte  
- Device Class korrekt gesetzt  
- Pflanzensensoren werden automatisch ausgeschlossen  

### Schimmelindex bleibt bei 0
Der Index steigt nur, wenn:
- Feuchte > 70%  
- Temperatur > 15°C  

---

# License
MIT License

