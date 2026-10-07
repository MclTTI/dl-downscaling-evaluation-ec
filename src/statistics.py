def compute_grid_percentiles(
    da,
    percentiles=(5, 50, 95),
):

    quantiles = da.quantile(
        [p / 100 for p in percentiles],
        dim="time",
    )

    return {
        f"p{p}": quantiles.sel(quantile=p / 100).squeeze(drop=True)
        for p in percentiles
    }
