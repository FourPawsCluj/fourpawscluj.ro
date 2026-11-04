#!/usr/bin/env bash
# Downloads Cluj map layers from OpenStreetMap (Overpass API) into tools/map/osm/.
# Overpass often answers "at capacity"; small queries with retries get through.
set -u
cd "$(dirname "$0")" && mkdir -p osm
B='(46.700,23.50,46.80,23.68)'
q() {
  echo "[out:json][timeout:60];($2);out geom;" > "osm/$1.q"
  for w in 5 10 20 30 40; do
    curl -s -m 90 -A 'fourpawscluj-map-build' --data-urlencode "data@osm/$1.q" https://overpass-api.de/api/interpreter -o "osm/$1.json"
    grep -q '"elements"' "osm/$1.json" && { echo "$1 ok"; return; }
    sleep "$w"
  done
  echo "$1 FAILED"; return 1
}
q river "way[\"waterway\"=\"river\"]$B;"
q parks "way[\"leisure\"=\"park\"][\"name\"]$B;relation[\"leisure\"=\"park\"][\"name\"]$B;"
q woods "way[\"natural\"=\"wood\"]$B;relation[\"natural\"=\"wood\"]$B;way[\"landuse\"=\"forest\"]$B;relation[\"landuse\"=\"forest\"]$B;"
q water "way[\"natural\"=\"water\"]$B;"
q roads "way[\"highway\"~\"^(trunk|primary|secondary)\$\"]$B;"
q tert "way[\"highway\"=\"tertiary\"]$B;"
