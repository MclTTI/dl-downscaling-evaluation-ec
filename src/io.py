from pathlib import Path
import yaml

import numpy as np
import xarray as xr



def load_config(path):
    with open(path) as f:
        config = yaml.safe_load(f)

    return config



def load_dataset_series(cfg, years, lazy=True):

    files = [
        Path(cfg["directory"]) /
        cfg["pattern"].format(year=year)
        for year in years
    ]

    print("[INFO] Files:")
    for f in files:
        print(f"  - {f}")

    ds = xr.open_mfdataset(
        files,
        combine="by_coords",
        chunks={} if lazy else None
    )

    da = ds[cfg["variable"]]

    # Add rotated pole information if available
    if "rotated_pole" in ds:
        da.attrs["_rotated_pole"] = ds["rotated_pole"].attrs

    if not lazy:
        da = da.load()
        ds.close()

    return da 



def check_spatiotemporal_compatibility(a, b):

    checks = {
        "time": np.array_equal(a.time.values, b.time.values),
        "lat": np.array_equal(a.lat.values, b.lat.values),
        "lon": np.array_equal(a.lon.values, b.lon.values),
    }

    print(f"  time: {checks['time']}")
    print(f"  lat:  {checks['lat']}")
    print(f"  lon:  {checks['lon']}")

    return checks