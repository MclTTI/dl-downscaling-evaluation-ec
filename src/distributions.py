import numpy as np
from scipy.stats import gaussian_kde



def sample_valid_values(
    da,
    n_samples=None,
    seed=42
):

    values = da.values.ravel()

    values = values[np.isfinite(values)]

    if n_samples is not None and values.size > n_samples:

        rng = np.random.default_rng(seed)

        idx = rng.choice(
            values.size,
            size=n_samples,
            replace=False
        )

        values = values[idx]

    return values



def compute_kde(values, xgrid):

    kde = gaussian_kde(values)

    return kde(xgrid)



def empirical_cdf(values):

    values = np.sort(values)

    n = len(values)

    cdf = np.arange(1, n + 1) / n

    return values, cdf



def empirical_survival(values):

    values = np.sort(values)

    n = len(values)

    cdf = np.arange(1, n + 1) / n

    survival = 1 - cdf

    # Avoid zero values for logarithmic plotting
    #survival = np.maximum(
    #    survival,
    #    1 / n
    #)

    return values, survival
