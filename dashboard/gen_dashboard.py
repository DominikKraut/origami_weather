"""Generate dashboard/home-dashboard.yaml (raw config for a sections dashboard).

Run from the repo root: python3 dashboard/gen_dashboard.py
Needs node (reads the Home preset from layout-presets.js) and PyYAML.
"""
import json, pathlib, subprocess, yaml

root = pathlib.Path(__file__).resolve().parent.parent
WEATHER = "weather.home"
LIGHTS_ON = "mdi:home-lightbulb"   # icon of the "lights on" button; the card CSS keys off it

# --- entities -------------------------------------------------------------
LIGHTS = [  # (entity, name, icon)
    ("light.living_room_lampa_tretakt_smart_plug_1_obyvak", "Lampa", "mdi:floor-lamp"),
    ("light.chodba_svetlo_chodba", "Lampa 2", "mdi:floor-lamp-outline"),
    ("light.svetlo_obyvak_koule", "Koule", "mdi:globe-light"),
    ("light.svetlo_loznice", "Ložnice", "mdi:ceiling-light"),
    ("light.led_strip_lights", "LED pásek", "mdi:led-strip-variant"),
    ("light.chodba_svetlo_chodba_2", "Chodba", "mdi:ceiling-light-outline"),
]
DOOR = "binary_sensor.moes_door_senzor_luminance"
VAC = "vacuum.vysafac"
AUTOMATIONS = [
    "automation.living_room_lights_evening_schedule",
    "automation.flash_lights_at_21_50_if_on",
    "automation.turn_off_all_lights_when_away_for_10_minutes",
    "automation.rozsvitit_lampu_a_kouli_switch_obyvak",
    "automation.lampa_2_obyvak_toggle",
    "automation.svetlo_chodba_switch",
    "automation.reset_lights_obyvak",
    "automation.smart_vacuum_when_away",
    "automation.vacuum_started_notifications",
]
MAINT = [  # (entity, name)
    ("sensor.vysafac_main_brush_time_left", "Main brush"),
    ("sensor.vysafac_side_brush_time_left", "Side brush"),
    ("sensor.vysafac_filter_time_left", "Filter"),
    ("sensor.vysafac_sensor_time_left", "Sensors"),
]
BATTERIES = [
    ("sensor.chodba_switch_chodba_battery", "Switch chodba"),
    ("sensor.living_room_switch_obyvak_battery", "Switch obývák"),
    ("sensor.moes_door_senzor_luminance_battery", "Door sensor"),
]


def tile(entity, name=None, icon=None, cols=6, **kw):
    c = {"type": "tile", "entity": entity}
    if name: c["name"] = name
    if icon: c["icon"] = icon
    c.update(kw)
    c["grid_options"] = {"columns": cols}
    return c


def heading(text, icon=None, badges=None, style="title"):
    c = {"type": "heading", "heading": text, "heading_style": style}
    if icon: c["icon"] = icon
    if badges: c["badges"] = badges
    return c


def light_tile(e, name, icon):
    return tile(e, name, icon, tap_action={"action": "toggle"},
                hold_action={"action": "more-info"}, vertical=False)


# --- Origami Weather card --------------------------------------------------
preset = json.loads(subprocess.check_output(
    ["node", "--input-type=module", "-e",
     f"const m = await import('{(root / 'layout-presets.js').as_uri()}');"
     f"console.log(JSON.stringify(m.instantiatePreset(m.LAYOUT_PRESETS.find(p => p.id === 'home'), '{WEATHER}')))"]))

def txt(extra, size="12px", weight="500"):
    return {"type": "text", "size": size, "weight": weight, "color": "var(--primary-text-color)", **extra}

def label(text):
    return txt({"text": text, "color": "var(--secondary-text-color)"})

def stat(entity, name, value_el, **kw):
    return {"entity": entity, "style": "vertical", "align": "start",
            "elements": [label(name), value_el], **kw}

on = [{"condition": "numeric_state", "entity": "sensor.count_all_lights", "above": 0}]
off = [{"condition": "numeric_state", "entity": "sensor.count_all_lights", "below": 1}]
lights_on = stat("sensor.count_all_lights", "Lights", txt({"format": " on"}, "16px", "300"), visibility=on,
                 tap_action={"action": "navigate", "navigation_path": "rooms"})
# invisible marker, only rendered while a light is on (see css below)
marker = {"entity": "sensor.count_all_lights", "visibility": on, "position": "custom", "position_anchor": "top-left",
          "background": False, "elements": [{"type": "icon", "icon": LIGHTS_ON, "icon_size": "1px", "color": "transparent"}]}
lights_off = stat("sensor.count_all_lights", "Lights", txt({"text": "Off"}, "16px", "300"), visibility=off)

rooms = next(c for c in preset["button_containers"] if c.get("position_anchor") == "bottom-right")
rooms["buttons"] = [
    lights_on, lights_off, marker,
    stat(DOOR, "Door", txt({}, "16px", "300")),
    stat(WEATHER, "Humidity", txt({"attribute": "humidity", "precision": 0, "format": "%"}, "16px", "300")),
]

# Our two windows (class omy in the building SVG) light up only while any light is on.
# The "lights on" button above is only rendered then, so :has() on its icon is the switch.
LIT = f'#card-root:has(ha-icon[icon="{LIGHTS_ON}"])'
css = (
    "#card-root.scheme-dark .omy{fill:#18191b}"
    "#card-root.scheme-dark .ogl{display:none}"
    f"{LIT}.scheme-dark .omy{{fill:#ffc56e}}"
    f"{LIT}.scheme-dark .ogl{{display:inline}}"
    f"{LIT}.scheme-light .omy{{fill:#e9b872}}"
)

# The Home preset switches the sky off; we want it back: animated sky that follows the real sun
# (day, dusk, night with stars), clouds, rain/snow, sun and moon, birds, planes and balloons.
for k in ["sun_enabled", "moon_enabled", "cloud_effects", "night_sky_effects", "bird_effects",
          "balloon_effects", "plane_effects", "background_mode", "background_threshold_entity",
          "background_thresholds"]:
    preset.pop(k, None)
# Written out explicitly (all of them are on by default) so they are easy to find and switch off.
effects = {"background_mode": "default", "sun_enabled": True, "moon_enabled": True, "sun_moon_x": "dynamic",
           "sun_moon_size": "64px", "cloud_effects": True, "precipitation_effects": True,
           "night_sky_effects": True, "bird_effects": True, "bird_density": 0.5, "plane_effects": True,
           "plane_density": 0.5, "balloon_effects": True, "balloon_density": 0.5}
origami = {"type": "custom:origami-weather", "weather_entity": WEATHER, "color_mode": "sun",
           **effects, **preset, "css": css}
origami["grid_options"] = {"columns": "full", "rows": "auto"}

# --- views ------------------------------------------------------------------
warn_vis = [{"condition": "or", "conditions":
             [{"condition": "numeric_state", "entity": e, "below": 0} for e, _ in MAINT] +
             [{"condition": "numeric_state", "entity": e, "below": 20} for e, _ in BATTERIES]}]
warnings = {
    "type": "markdown",
    "visibility": warn_vis,
    "content": (
        "{% set ns = namespace(w=[]) %}"
        + "".join(f"{{% if states('{e}') | float(1) < 0 %}}{{% set ns.w = ns.w + ['🧹 Vacuum: {n.lower()} overdue'] %}}{{% endif %}}" for e, n in MAINT)
        + "".join(f"{{% if states('{e}') | float(100) < 20 %}}{{% set ns.w = ns.w + ['🔋 {n} battery ' ~ states('{e}') ~ '%'] %}}{{% endif %}}" for e, n in BATTERIES)
        + "{% for w in ns.w %}{{ w }}\n{% endfor %}"
    ),
    "grid_options": {"columns": "full"},
}

# Area IDs as HA created them from the area names; check with {{ areas() }} in Developer Tools > Template.
AREA_LIVING, AREA_BED, AREA_HALL = "living_room", "bedroom", "chodba"
ROOM_CLEAN = "button.vysafac_kuchyne_chodba_obyva"

def area_card(area, name, icon, actions, **kw):
    return {"type": "custom:area-pulse-card", "area": area, "name": name, "icon": icon,
            "max_chips": 3, "actions": actions, "grid_options": {"columns": "full"}, **kw}

home_pulse = {
    "type": "custom:home-pulse-card",
    "title": "{greeting}, {name}",
    "sections": ["greeting", "status", "alerts", "nudges"],
    "persons": ["person.dominik", "person.lenicka"],
    "weather_entity": WEATHER,
    "alarm_entity": "none",
    "mode_entity": "none",
    "today": False,
    "grid_options": {"columns": "full"},
}
shortcuts = {
    "type": "custom:home-pulse-shortcuts-card",
    "columns": 4,
    "shortcuts": [
        {"name": "Rooms", "icon": "mdi:floor-plan", "navigation_path": "rooms", "badge": "lights"},
        {"name": "Vacuum", "icon": "mdi:robot-vacuum", "navigation_path": "vacuum", "entity": VAC},
        {"name": "Media", "icon": "mdi:television-play", "navigation_path": "rooms", "badge": "media"},
        {"name": "System", "icon": "mdi:cog-outline", "navigation_path": "system", "badge": "batteries"},
    ],
    "grid_options": {"columns": "full"},
}

home = {
    "title": "Home", "path": "home", "icon": "mdi:home-outline", "type": "sections", "max_columns": 2,
    "sections": [
        {"type": "grid", "cards": [home_pulse, origami, shortcuts, warnings]},
        {"type": "grid", "cards": [
            heading("Rooms", style="title"),
            area_card(AREA_LIVING, "Obývák", "mdi:sofa-outline", [
                {"preset": "lights_toggle", "name": "Lights"},
                {"entity": "media_player.jabko_tv", "name": "Apple TV", "icon": "mdi:apple"},
                {"entity": ROOM_CLEAN, "name": "Vacuum", "icon": "mdi:robot-vacuum"},
                {"preset": "lights_off", "name": "All off", "icon": "mdi:power"},
            ], main_light="light.svetlo_obyvak_koule", exclude_entities=["light.smart_zasuvka_obyvak_1_socket",
                "switch.smart_zasuvka_obyvak_1_socket", "switch.ikea_of_sweden_tretakt_smart_plug",
                "switch.living_room_svetlo_chodba"]),
            area_card(AREA_BED, "Ložnice", "mdi:bed-outline", [
                {"preset": "lights_on", "name": "Lights on"},
                {"preset": "lights_off", "name": "Lights off"},
            ]),
            area_card(AREA_HALL, "Chodba", "mdi:door-open", [
                {"preset": "lights_toggle", "name": "Light"},
            ], sensor_classes=["illuminance"], show_inactive=True),
            {"type": "weather-forecast", "entity": WEATHER, "show_current": False, "show_forecast": True,
             "forecast_type": "daily", "grid_options": {"columns": "full"}},
        ]},
    ],
}

rooms_view = {
    "title": "Rooms", "path": "rooms", "icon": "mdi:floor-plan", "type": "sections", "max_columns": 3,
    "sections": [
        {"type": "grid", "cards": [
            heading("Obývák", "mdi:sofa-outline"),
            *[light_tile(*l) for l in LIGHTS[:3]],
            tile("sensor.living_room_svetlo_chodba_power", "Lampa 2 power", cols=6),
            tile("media_player.jabko_tv", "Apple TV", cols=6),
            tile("media_player.homepod_obyvak", "HomePod", cols=6),
            tile("sensor.living_room_switch_obyvak_battery", "Switch battery", cols=6),
        ]},
        {"type": "grid", "cards": [
            heading("Ložnice", "mdi:bed-outline"),
            *[light_tile(*l) for l in LIGHTS[3:5]],
        ]},
        {"type": "grid", "cards": [
            heading("Chodba", "mdi:door-open"),
            light_tile(*LIGHTS[5]),
            tile(DOOR, "Door", "mdi:door"),
            tile("sensor.moes_door_senzor_luminance_illuminance", "Light level"),
            tile("sensor.chodba_switch_chodba_battery", "Switch battery"),
        ]},
        {"type": "grid", "cards": [
            heading("Outside", "mdi:weather-partly-cloudy"),
            tile("sensor.home_temperature", "Temperature", cols=6),
            tile("sensor.home_humidity", "Humidity", cols=6),
            tile("sensor.home_wind_speed", "Wind", cols=6),
            tile("sensor.home_atmospheric_pressure", "Pressure", cols=6),
            {"type": "weather-forecast", "entity": WEATHER, "forecast_type": "hourly", "show_current": False,
             "grid_options": {"columns": "full"}},
        ]},
    ],
}

select = lambda e, n: tile(e, n, cols=12, features=[{"type": "select-options"}])
vacuum_view = {
    "title": "Vacuum", "path": "vacuum", "icon": "mdi:robot-vacuum", "type": "sections", "max_columns": 3,
    "sections": [
        {"type": "grid", "cards": [
            heading("Vysavač", "mdi:robot-vacuum"),
            {"type": "picture-entity", "entity": "image.vysafac_byt", "show_name": False, "show_state": False,
             "grid_options": {"columns": "full"}},
            tile(VAC, "Vysavač", cols=12, state_content=["state", "battery_level"],
                 features=[{"type": "vacuum-commands",
                            "commands": ["start_pause", "stop", "clean_spot", "locate", "return_home"]}]),
            tile("button.vysafac_kuchyne_chodba_obyva", "Clean kitchen, hall & living", "mdi:broom", cols=12,
                 tap_action={"action": "perform-action", "perform_action": "button.press",
                             "target": {"entity_id": "button.vysafac_kuchyne_chodba_obyva"}},
                 state_content="name"),
            tile("sensor.vysafac_status", "Status"),
            tile("sensor.vysafac_current_room", "Room"),
            tile("sensor.vysafac_cleaning_progress", "Progress"),
            tile("sensor.vysafac_last_clean_end", "Last clean"),
        ]},
        {"type": "grid", "cards": [
            heading("Settings", "mdi:tune-variant"),
            select("select.living_room_vysafac_cleaning_mode", "Cleaning mode"),
            select("select.vysafac_mop_mode", "Mop mode"),
            select("select.vysafac_mop_intensity", "Mop intensity"),
            select("select.vysafac_dock_empty_mode", "Dock empty mode"),
            tile("switch.vysafac_do_not_disturb", "Do not disturb", tap_action={"action": "toggle"}),
            tile("switch.living_room_vysafac_dock_dust_emptying", "Dust emptying", tap_action={"action": "toggle"}),
        ]},
        {"type": "grid", "cards": [
            heading("Maintenance", "mdi:wrench-clock", style="subtitle"),
            *[tile(e, n, "mdi:timer-sand") for e, n in MAINT],
            tile("binary_sensor.vysafac_water_shortage", "Water"),
            tile("sensor.vysafac_vacuum_error", "Error"),
            tile("sensor.vysafac_total_cleaning_count", "Cleanings"),
            tile("sensor.vysafac_total_cleaning_area", "Total area"),
        ]},
    ],
}

system_view = {
    "title": "System", "path": "system", "icon": "mdi:cog-outline", "type": "sections", "max_columns": 3,
    "sections": [
        {"type": "grid", "cards": [
            heading("Batteries", "mdi:battery-heart-variant"),
            tile("sensor.dominik_iphone_battery", "Dominik iPhone"),
            tile("sensor.lenkas_iphone_battery", "Lenka iPhone"),
            tile("sensor.sidephone_battery_level", "Sidephone"),
            tile("sensor.vysafac_battery", "Vysavač"),
            *[tile(e, n) for e, n in BATTERIES],
        ]},
        {"type": "grid", "cards": [
            heading("Health", "mdi:heart-pulse"),
            tile("sensor.icloud3_alerts", "iCloud3", "mdi:apple-icloud", cols=12),
            tile("sensor.backup_last_successful_automatic_backup", "Last backup", cols=12),
            tile("sensor.backup_next_scheduled_automatic_backup", "Next backup", cols=12),
            tile("binary_sensor.rpi_power_status", "Raspberry Pi power", cols=12),
        ]},
        {"type": "grid", "cards": [
            heading("Automations", "mdi:robot-outline"),
            *[tile(a, cols=12, tap_action={"action": "toggle"}, hold_action={"action": "more-info"}) for a in AUTOMATIONS],
        ]},
    ],
}

dash = {"title": "Domov", "views": [home, rooms_view, vacuum_view, system_view]}

out = root / "dashboard" / "home-dashboard.yaml"
out.write_text("# Generated by dashboard/gen_dashboard.py - edit the generator, not this file.\n"
               + yaml.safe_dump(dash, allow_unicode=True, sort_keys=False, width=1000), encoding="utf-8")
print("wrote", out)
