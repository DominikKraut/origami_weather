# Home dashboard

`home-dashboard.yaml` is the raw config of the "Domov" dashboard (4 views: Home, Rooms, Vacuum, System).
It is generated: edit `gen_dashboard.py`, then run `python3 dashboard/gen_dashboard.py` from the repo root.

Install: Settings → Dashboards → Add dashboard → New dashboard from scratch, open it,
✏️ → ⋮ → Raw configuration editor, paste the whole file, Save.

Needs from HACS: this fork's Origami Weather, [Pulse Cards](https://github.com/zacharatos/pulse-cards) (Dashboard)
and, for the matching look, [Pulse Theme](https://github.com/zacharatos/pulse-theme) (Theme, pick *Pulse* or *Pulse Glass* in your profile).
The room cards use the area IDs `living_room`, `bedroom`, `chodba`; check yours with `{{ areas() }}` in Developer Tools → Template.
Our two windows on the building light up while `sensor.count_all_lights` is above 0
(card `css`, keyed off a hidden `mdi:home-lightbulb` button).
