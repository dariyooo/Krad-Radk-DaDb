# Krad-Radk-DaDb

Repackage KRADFILE/RADKFILE into a DaKanji DaDb radical archive.

Produces `out/krad-radk-dadb.zip` — an archive DaKanji imports through its normal
dictionary pipeline (an `index.json` plus the data files). Run `uv run main.py`
(or `python main.py`); CI rebuilds on a schedule and publishes the archive as
`releases/latest`, which the app checks for updates.
