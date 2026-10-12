# Home dashboard

`home-dashboard.yaml` is the raw config of the "Domov" dashboard (4 views: Home, Rooms, Vacuum, System).
It is generated: edit `gen_dashboard.py`, then run `python3 dashboard/gen_dashboard.py` from the repo root.

Install: Settings → Dashboards → Add dashboard → New dashboard from scratch, open it,
✏️ → ⋮ → Raw configuration editor, paste the whole file, Save.

Only built-in cards plus this fork's Origami Weather card are used.
Our two windows on the building light up while `sensor.count_all_lights` is above 0
(card `css`, keyed off a hidden `mdi:home-lightbulb` button).
