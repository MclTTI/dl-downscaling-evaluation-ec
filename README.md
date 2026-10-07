# Evaluation of deep-learning temperature downscaling over the EURO-CORDEX domain

This repository contains the analysis code used to evaluate high-resolution near-surface temperature fields produced by deep-learning downscaling models over the EURO-CORDEX domain.

The code supports the analyses presented in:

Iotti, M. et al. _Deep-learning approaches for high-resolution downscaling of CMIP6 near-surface temperature over the EURO-CORDEX domain_ (manuscript submitted to Geophysical Research Letters).


## Repository structure

```text
DL-downscaling-evaluation-EURO-CORDEX/
├── config/
│   ├── config.yaml
│   └── plot_config.yaml
├── notebooks/
│   ├── distributions.ipynb
│   └── metric_evaluation.ipynb
├── outputs/
├── src/
│   ├── distributions.py
│   ├── io.py
│   ├── metrics.py
│   ├── plotting.py
│   └── statistics.py
└── README.md
```

## Analysis

The analysis is organized around two Jupyter notebooks.

### `metric_evaluation.ipynb`

This notebook evaluates the model outputs against the reference dataset in space and time.

The analysis includes:

* time-mean bias, mean absolute error (MAE), and root mean square error (RMSE) at each grid point;
* Pearson correlation between the model and reference time series at each grid point;
* summary statistics of the spatial distributions of the above evaluation metrics;
* 5th, 50th, and 95th percentiles of the temperature time series at each grid point.

The default analysis period is 2005–2014.

### `distributions.ipynb`

This notebook evaluates the temperature distributions produced by the models.

The analysis includes:

* kernel density estimates (KDEs) of the full temperature distributions;
* empirical cold-tail distributions based on the cumulative distribution function (CDF);
* empirical warm-tail distributions based on the complementary CDF (survival function);
* combined PDF and tail panels;
* Q–Q plots comparing model and reference quantiles.

Large random samples of valid temperature values are used for the distributional analysis to reduce the computational cost while retaining a representative sample of the full datasets.

## Source code

The `src/` directory contains the reusable functions used by the notebooks.

### `distributions.py`

Functions for distributional analysis, including:

* sampling finite values from `xarray.DataArray` objects;
* kernel density estimation;
* empirical CDF;
* empirical survival function.

### `io.py`

Functions for:

* reading YAML configuration files;
* loading multi-year datasets with `xarray`;
* checking spatial and temporal compatibility between datasets.

### `metrics.py`

Functions for computing:

* bias;
* MAE;
* RMSE;
* Pearson correlation;
* summary statistics of spatial metric distributions.

### `plotting.py`

Functions for generating the figures used in the analysis, including:

* spatial metric and percentile maps;
* metric distribution summaries;
* temperature probability density functions;
* cold and warm distribution tails;
* combined PDF/tail plots;
* Q–Q plots.

### `statistics.py`

Function for computing temporal percentiles.

## Configuration

The analysis is controlled through the YAML configuration files in `config/`.

* `config.yaml` defines the input datasets, variables, file patterns, and analysis period.
* `plot_config.yaml` defines plotting parameters such as labels, colors, and ranges used for the different metrics and datasets.

Input data are not included in this repository.

## Requirements

The analysis requires Python and the following main packages:

* NumPy
* SciPy
* pandas
* xarray
* PyYAML
* Matplotlib
* Cartopy
* Jupyter

The notebooks and source code were developed and tested using Python 3.12.9.

## Usage

After installing the required dependencies and configuring the input datasets in `config/config.yaml`, the analysis can be run from the corresponding Jupyter notebooks.

## Copyright and code availability

The source code in this repository is protected by copyright.
The code is made publicly available for inspection only.
No license for reuse, modification, or redistribution is granted.

## Data availability

The input climate datasets and model outputs are not distributed with this repository.

The data used in the analysis are described in the associated publication and should be obtained from the corresponding data sources.
