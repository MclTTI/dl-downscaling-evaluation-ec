import numpy as np
import xarray as xr

import pandas as pd



def bias(pred, ref):
    return (pred - ref).mean(dim="time")


def mae(pred, ref):
    return np.abs(pred - ref).mean(dim="time")


def rmse(pred, ref):
    diff = pred - ref
    return np.sqrt((diff ** 2).mean(dim="time"))


def correlation(pred, ref):
    return xr.corr(pred, ref, dim="time")



def compute_grid_metrics(
    pred,
    ref,
    metrics,
    start_date=None,
    end_date=None,
    verbose=True
):

    if start_date is not None or end_date is not None:
        pred = pred.sel(time=slice(start_date, end_date))
        ref = ref.sel(time=slice(start_date, end_date))

    if pred.time.size == 0:
        raise ValueError(
            "Selected period contains no time steps"
        )

    results = {}

    for metric in metrics:
        results[metric.__name__] = metric(pred, ref)

    if verbose:

        print("\n" + "=" * 60)
        print(f"Summary:\n")

        for metric_name, da in results.items():

            print(
                f"{metric_name:12s}  "
                f"mean={float(da.mean()):+8.4f}   "
                f"min={float(da.min()):+8.4f}   "
                f"max={float(da.max()):+8.4f}"
            )

        print("\n" + "=" * 60)

    return results



def summarize_metric_distributions(
    metrics,
    percentiles=(1,5,50,95,99)
):

    rows = []

    for model, model_metrics in metrics.items():

        for metric, da in model_metrics.items():

            values = da.values.ravel()

            row = {
                "model": model,
                "metric": metric,
                "min": np.nanmin(values),
                "max": np.nanmax(values),
            }

            for p in percentiles:

                row[f"p{p}"] = np.nanpercentile(
                    values,
                    p
                )

            rows.append(row)

    return pd.DataFrame(rows)