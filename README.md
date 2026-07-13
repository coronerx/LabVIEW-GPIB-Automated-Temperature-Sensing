# LabVIEW/GPIB Automated Temperature Sensing (AD590 + LM741)

Physics 327, Rutgers University — automated data acquisition lab using
LabVIEW and a GPIB-connected HP 34401A multimeter.

## What this is

A LabVIEW VI drives an HP 34401A digital multimeter over GPIB to log
resistance/voltage measurements automatically (no manual reading), first
from a thermistor, then from an AD590 temperature-transducer circuit
buffered through an LM741 op-amp.

## Circuit

AD590 (constant-current temp sensor) feeds an LM741 op-amp with a 10 kΩ
feedback resistor, converting the AD590's current output into a readable
voltage on pin 6. Per the AD590 datasheet, the raw voltage should be
scaled by **-100** to recover temperature in Kelvin.

## The bug

The first pass scaled the voltage by **-300** instead of -100 — a 3x
error that pushed every reading roughly 3x too far from room temperature.
Re-deriving the scale factor from the AD590/LM741 transfer relationship
and correcting the LabVIEW scaling block fixed it: corrected output
settled at a physically sane ~300 K room temperature (see
`figures/thermistor_room_temp.png` and the writeup for before/after).

## Repo contents

```
data/         raw logged measurements (CSV)
analysis.py   loads whatever CSVs are present, fits exponential
              decay/growth (thermistor thermal response, tau),
              plots and saves figures
figures/      generated plots (gitignored input, committed output optional)
```

Only `data/thermistor_room_temp.csv` is currently populated — it's the
exact table from the lab report. The script is written to also pick up
`thermistor_hand_hold.csv`, `thermistor_release.csv`,
`ad590_temp_raw.csv`, and `ad590_temp_corrected.csv` if you drop the
original LabVIEW-exported logs into `data/`; anything missing is just
skipped, no code changes needed.

## Running it

```bash
pip install numpy scipy matplotlib pandas
python analysis.py
```

Outputs go to `figures/`. Console prints the fitted time constant
(tau) and asymptote for each dataset.

## Result (room-temperature baseline)

Thermistor resistance drifts down slightly over 10 s even at "room
temperature" (self-heating / settling), decaying exponentially toward
~862,713 Ω with tau ≈ 5.1 s.

## Notes

- LabVIEW itself isn't code in the usual sense (block-diagram, not
  text), so it isn't included here — this repo captures the data it
  produced and re-analyzes it in Python instead.
- GPIB commands used in the VI: `conf:volt:dc` and `conf:res` to switch
  the HP 34401A between DC voltage and resistance measurement modes.
