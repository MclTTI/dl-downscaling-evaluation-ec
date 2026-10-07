import numpy as np

import matplotlib.pyplot as plt
import cartopy.feature as cfeature
import cartopy.crs as ccrs



def add_gridlines(
    ax,
    draw_labels=False,
    linewidth=0.5,
    linestyle="-",
    color="gray",
    alpha=0.6
):

    gl = ax.gridlines(
        crs=ccrs.PlateCarree(),
        draw_labels=draw_labels,
        linewidth=linewidth,
        linestyle=linestyle,
        color=color,
        alpha=alpha
    )

    if draw_labels:

        gl.top_labels = False
        gl.right_labels = False

        gl.left_labels = True
        gl.bottom_labels = True

        gl.xlabel_style = {
            "size": 8,
            "rotation": 0,
            "ha": "center"
        }

        gl.ylabel_style = {
            "size": 8,
            "rotation": 0,
            "va": "center"
        }

    return gl



def get_projection(da):

    rot = da.attrs.get("_rotated_pole")

    if rot is not None:

        return ccrs.RotatedPole(
            pole_latitude=rot["grid_north_pole_latitude"],
            pole_longitude=rot["grid_north_pole_longitude"]
        )

    return ccrs.PlateCarree()



def plot_metric_field(
    ax,
    da,
    field_type,
    plot_config
):

    if field_type in plot_config["metrics"]:

        cfg = plot_config["metrics"][field_type]

    else:

        cfg = plot_config["percentiles"]["temperature"]

    cmap = cfg["cmap"]

    vmin = cfg["default"]["vmin"]
    vmax = cfg["default"]["vmax"]

    extend = cfg.get(
        "extend",
        "neither"
    )

    im = ax.pcolormesh(
        da.lon,
        da.lat,
        da,
        cmap=cmap,
        vmin=vmin,
        vmax=vmax,
        shading="auto",
        transform=ccrs.PlateCarree()
    )


    ax.add_feature(
        cfeature.COASTLINE
    )

    ax.add_feature(
        cfeature.BORDERS,
        linestyle=":"
    )


    add_gridlines(
        ax,
        draw_labels=False
    )


    return im



def plot_metrics_panel(
    metrics,
    percentiles,
    plot_config,
    add_suptitle=False,
    analysis_period=None
):

    # Define panel rows and corresponding data keys
    rows = [
    ("Reference", "reference")
] + [
    (model, model)
    for model in percentiles
    if model != "reference"
]
    
    # Define panel columns and titles
    columns = {
        "p5": "5th percentile",
        "p50": "Median",
        "p95": "95th percentile",
        "bias": "Bias",
        "mae": "MAE",
        "rmse": "RMSE",
        "correlation": "Pearson"
    }

    column_names = list(columns)


    fig = plt.figure(figsize=(32, 18))

    axes = []
    images = {}

    gs = fig.add_gridspec(
        nrows=len(rows)+1,
        ncols=len(column_names),
        height_ratios=[1]*len(rows) + [0.04],
        wspace=0.0,
        hspace=0.08)


    for i, (row_name, model) in enumerate(rows):

        row_axes = []

        for j, column in enumerate(columns):

            # Get dataarray
            if column in ["bias","mae","rmse","correlation"]:

                if model == "reference":
                    ax = fig.add_subplot(gs[i,j])
                    ax.axis("off")
        
                    if i == 0:
                        ax.set_title(
                            columns[column],
                            fontsize=15,
                            fontweight="bold",
                            pad=12
                        )

                    continue

                da = metrics[model][column]

            else:

                da = percentiles[model][column]

            # Get projection from dataarray metadata
            proj = get_projection(da)
            
            # Set axes
            if da is None:
                ax = fig.add_subplot(gs[i,j])
                ax.axis("off")
                continue

            else:

                ax = fig.add_subplot(gs[i, j],projection=proj)
                

            # Plot field
            im = plot_metric_field(
                ax,
                da,
                column,
                plot_config
            )

            images[(model, column)] = im

            row_axes.append(ax)


            # Column title
            if i == 0:
                ax.set_title(
                    columns[column],
                    fontsize=15,
                    fontweight="bold",
                    pad=12
                )


            # Row label
            if j == 0:
                ax.text(
                    -0.10,
                    0.5,
                    row_name,
                    transform=ax.transAxes,
                    rotation=90,
                    va="center",
                    ha="center",
                    fontsize=14,
                    fontweight="bold"
                )


        axes.append(row_axes)


    # -------------------------
    # Colorbars
    # -------------------------
    
    # Column groups
    colorbar_groups = [
        ["p5", "p50", "p95"],
        ["bias"],
        ["mae"],
        ["rmse"],
        ["correlation"]
    ]
    

    for group in colorbar_groups:
    
        cols = [
            column_names.index(c)
            for c in group
        ]
    
        # Set a position spanning multiple columns
        cax = fig.add_subplot(
            gs[-1, cols[0]:cols[-1]+1]
        )
    
        pos = cax.get_position()
    
        cax.set_position([
            pos.x0 + 0.02,
            pos.y0,
            pos.width - 0.04,
            pos.height
        ])
    
    
        column = group[0]
    
        if column in ["p5","p50","p95"]:
            im = images[("reference", column)]
            metric_cfg = plot_config["percentiles"]["temperature"]
    
        else:
            
            model = next(
                model
                for model in percentiles
                if model != "reference"
            ) 
            
            im = images[(model, column)]
            metric_cfg = plot_config["metrics"][column]
    
    
        cbar = fig.colorbar(
            im,
            cax=cax,
            orientation="horizontal",
            extend=metric_cfg.get(
                "extend",
                "neither"
            )
        )
    
    
        cbar.set_label("(K)",fontsize=12)

    if add_suptitle:

        if analysis_period is None:
            raise ValueError(
                "analysis_period must be provided when suptitle=True"
            )

        fig.suptitle(
            "Ensemble mean spatial evaluation | "
            f"Analysis period: {analysis_period['start_date']} - {analysis_period['end_date']}",
            fontsize=16,
            fontweight="bold",
            y=0.94
        )


    return fig, axes, images



def plot_single_metric_range(
    ax,
    df_summary,
    metric
):
    
    sub = df_summary[df_summary["metric"] == metric]

    y_positions = []
    labels = []
    
    y = 0.25
    
    for _, row in sub.iterrows():
    
        # min-max
        ax.hlines(
            y,
            row["min"],
            row["max"],
            linewidth=1,
            color="black"
        )

        # p1-p99
        ax.hlines(
            y,
            row["p1"],
            row["p99"],
            linewidth=8,
            color="0.25",
        )

        # p5-p95
        ax.hlines(
            y,
            row["p5"],
            row["p95"],
            linewidth=16,
            color="0.65"
        )

        # median
        ax.vlines(
            row["p50"],
            y-0.045,
            y+0.045,
            linewidth=1.5,
            color="red"
        )

        labels.append(f"{row['model']}")

        y_positions.append(y)

        y += 0.25

    ax.set_ylim(0.1,0.9)

    ax.set_yticks(y_positions)

    ax.set_yticklabels(
        labels,
        fontsize=10
    )

    ax.invert_yaxis()

    ax.grid(
        axis="x",
        linestyle=":",
        alpha=0.5
    )



def plot_metric_summary(
    df_summary,
    figsize=(10,10),
    add_suptitle=False,
    analysis_period=None
):

    fig, axes = plt.subplots(4, 1, figsize=figsize)

    metrics = [
        ("bias", "Bias", "(K)"),
        ("mae", "MAE", "(K)"),
        ("rmse", "RMSE", "(K)"),
        ("correlation", "Pearson", "")
    ]


    for ax, (metric, title, xlabel) in zip(axes, metrics):

        plot_single_metric_range(ax, df_summary, metric)

        ax.set_xlabel(xlabel)
        ax.set_title(title, fontweight="bold")


    # specific ranges and lines
    axes[0].axvline(0, color="black", linestyle="--")

    axes[3].set_xlim(0.5, 1)

    if add_suptitle:
    
        if analysis_period is None:
           raise ValueError(
                "analysis_period must be provided when suptitle=True"
            )
    
        fig.suptitle(
            "Distribution of ensemble mean evaluation metrics\n"
            f"Analysis period: {analysis_period['start_date']} - {analysis_period['end_date']}",
            fontsize=16,
            fontweight="bold"
            )

    fig.tight_layout()

    return fig, axes



def set_temperature_axis(
    ax,
    major_step=10,
    minor_step=5,
    limits = (228, 320),
    y_axis=False
):
    
    from matplotlib.ticker import MultipleLocator

    ax.set_xlim(limits)

    ax.xaxis.set_major_locator(
        MultipleLocator(major_step)
    )

    ax.xaxis.set_minor_locator(
        MultipleLocator(minor_step)
    )

    if y_axis:

        ax.set_ylim(limits)

        ax.yaxis.set_major_locator(
            MultipleLocator(major_step)
        )

        ax.yaxis.set_minor_locator(
            MultipleLocator(minor_step)
        )

    ax.grid(
        which="major",
        linestyle="-",
        linewidth=0.75,
        alpha=0.75
    )

    ax.grid(
        which="minor",
        linestyle="-",
        linewidth=0.5,
        alpha=0.5
    )



def plot_temperature_distributions(
    datasets,
    n_samples=300000,
    config=None,
    title_string=None,
    ax=None,
    show_legend=True
):
    
    from src.distributions import sample_valid_values, compute_kde

    data = {}

    # reference
    data["reference"] = sample_valid_values(
        datasets["reference"],
        n_samples=n_samples
    )


    # models
    for name, da in datasets["models"].items():

        data[name] = sample_valid_values(
            da,
            n_samples=n_samples
        )


    # common data range
    xmin = min(
        values.min()
        for values in data.values()
    )

    xmax = max(
        values.max()
        for values in data.values()
    )


    xgrid = np.linspace(
        xmin,
        xmax,
        500
    )


    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 8))
    else:
        fig = ax.figure


    for name, values in data.items():

        y = compute_kde(
            values,
            xgrid
        )

        ax.plot(
            xgrid,
            y,
            linewidth=2,
            color=config["distributions"][name]["color"],
            label=config["distributions"][name]["label"]
        )

    set_temperature_axis(ax)

    ax.set_xlabel("(K)")
    ax.set_ylabel("Probability density")

    if show_legend:
        ax.legend()

    if title_string:
    
        ax.set_title(
            f"{title_string}",
            fontsize=14,
            fontweight="bold"
            )

    plt.tight_layout()

    return fig, ax



def plot_temperature_tails(
    datasets,
    n_samples=None,
    figsize=(8,5),
    config=None,
    title_string=None,
    ax=None,
    show_legend=True
):

    from src.distributions import sample_valid_values, empirical_cdf, empirical_survival

    if ax is None:
        fig, ax_cold = plt.subplots(figsize=figsize)
    else:
        fig = ax.figure
        ax_cold = ax

    ax_warm = ax_cold.twinx()


    # --------------------
    # Reference
    # --------------------

    ref = sample_valid_values(
        datasets["reference"],
        n_samples=n_samples
    )


    # cold tail
    x_cold, y_cold = empirical_cdf(ref)

    ax_cold.plot(
        x_cold,
        y_cold,
        linewidth=2,
        color=config["distributions"]["reference"]["color"],
        label=config["distributions"]["reference"]["label"],
    )


    # warm tail
    x_warm, y_warm = empirical_survival(ref)

    ax_warm.plot(
        x_warm[:-1],
        y_warm[:-1],
        color=config["distributions"]["reference"]["color"],
        linewidth=2
    )


    # --------------------
    # Models
    # --------------------

    for name, da in datasets["models"].items():

        values = sample_valid_values(
            da,
            n_samples=n_samples
        )


        # cold tail
        x_cold, y_cold = empirical_cdf(values)

        ax_cold.plot(
            x_cold,
            y_cold,
            linewidth=2,
            color=config["distributions"][name]["color"],
            label=config["distributions"][name]["label"],
        )


        # warm tail
        x_warm, y_warm = empirical_survival(values)

        ax_warm.plot(
            x_warm[:-1],
            y_warm[:-1],
            linewidth=2,
            color=config["distributions"][name]["color"],
        )


    # --------------------
    # Log scales
    # --------------------

    ax_cold.set_yscale("log")
    ax_cold.set_ylim(1e-7, 1.5)

    ax_warm.set_yscale("log")
    ax_warm.set_ylim(1e-7, 1.5)


    # --------------------
    # Labels
    # --------------------

    set_temperature_axis(ax_cold)

    
    ax_cold.set_xlabel("(K)")
    ax_cold.set_ylabel("CDF (cold tail)")
    ax_warm.set_ylabel("1 - CDF (warm tail)")

    if show_legend:
        ax_cold.legend(
            loc="upper left",
            bbox_to_anchor=(0.05, 0.95)
        )

    if title_string:
        
        ax_cold.set_title(
            f"{title_string}",
            fontsize=14,
            fontweight="bold"
            )


    return fig, (ax_cold, ax_warm)



def plot_temperature_distribution_tails(
    datasets,
    n_samples=3000,
    figsize=(10, 7),
    config=None,
    title_string=None
):
    
    from src.distributions import (
        sample_valid_values,
        compute_kde,
        empirical_cdf,
        empirical_survival
    )

    # --------------------------------------------------
    # Sample data
    # --------------------------------------------------

    data = {}

    data["reference"] = sample_valid_values(
        datasets["reference"],
        n_samples=n_samples
    )

    for name, da in datasets["models"].items():

        data[name] = sample_valid_values(
            da,
            n_samples=n_samples
        )


    # --------------------------------------------------
    # Reference thresholds
    # --------------------------------------------------

    reference = data["reference"]

    p5 = np.percentile(reference, 5)
    p95 = np.percentile(reference, 95)


    # --------------------------------------------------
    # X grid
    # --------------------------------------------------

    xmin = min(
        values.min()
        for values in data.values()
    )

    xmax = max(
        values.max()
        for values in data.values()
    )

    xgrid = np.linspace(
        xmin,
        xmax,
        500
    )


    # --------------------------------------------------
    # Figure and axes
    # --------------------------------------------------

    fig, ax = plt.subplots(
        figsize=figsize
    )

    ax_density = ax.twinx()
    ax.set_zorder(2)
    ax_density.set_zorder(1)
    ax.patch.set_visible(False)


    # --------------------------------------------------
    # Plot distributions
    # --------------------------------------------------

    for name, values in data.items():

        cfg = config["distributions"][name]

        color = cfg["color"]
        label = cfg["label"]


        # ----------------------------------------------
        # PDF
        # ----------------------------------------------

        kde = compute_kde(
            values,
            xgrid
        )

        mask_pdf = (
            (xgrid >= p5) &
            (xgrid <= p95)
        )

        ax_density.plot(
            xgrid,#[mask_pdf],
            kde,#[mask_pdf],
            linewidth=2,
            color=color,
            label=label,
            zorder=2
        )


        # ----------------------------------------------
        # CDF -- cold tail
        # ----------------------------------------------

        x_cold, y_cold = empirical_cdf(values)

        mask_cold = x_cold <= p5

        ax.plot(
            x_cold[mask_cold],
            y_cold[mask_cold],
            linewidth=2,
            color=color,
            zorder=2
        )


        # ----------------------------------------------
        # Survival -- warm tail
        # ----------------------------------------------

        x_warm, y_warm = empirical_survival(values)

        mask_warm = x_warm >= p95

        ax.plot(
            x_warm[mask_warm],
            y_warm[mask_warm],
            linewidth=2,
            color=color,
            zorder=2
        )


    # --------------------------------------------------
    # x-axis
    # --------------------------------------------------

    xrange = xmax - xmin
    padding = 2
    
    ax.set_xlim(
        xmin - padding,
        xmax + padding
        )
    
    ax.set_xlabel("Temperature (K)")

    ax_density.axvline(p5,
               linestyle="-",
               color="black",
               linewidth=1,
               alpha=0.75,
               zorder=1
               )
                
    ax_density.axvline(p95,
               linestyle="-",
               color="black",
               linewidth=1,
               alpha=0.75,
               zorder=1
               )
                    
    ax_density.annotate(
        "Ref p5",
        xy=(p5, 1),
        xycoords=("data", "axes fraction"),
        xytext=(-1, -5),
        textcoords="offset points",
        rotation=90,
        va="top",
        ha="right",
        fontsize=10,
        zorder=3
    )

    ax_density.annotate(
        "Ref p95",
        xy=(p95, 1),
        xycoords=("data", "axes fraction"),
        xytext=(-1, -5),
        textcoords="offset points",
        rotation=90,
        va="top",
        ha="right",
        fontsize=10,
        zorder=3
    )


    # --------------------------------------------------
    # density axis
    # --------------------------------------------------
    
    density_grid_color = "#008C95"
    
    ax_density.set_ylim(bottom=0)


    ax_density.tick_params(axis="y", colors=density_grid_color)
    ax_density.set_ylabel("Probability density",color=density_grid_color)

    ax_density.grid(
            which="major",
            axis="y",
            linestyle="-",
            linewidth=0.75,
            color=density_grid_color,
            zorder=0
        )

    # --------------------------------------------------
    # log axis
    # --------------------------------------------------

    log_grid_color = "#555555"
    
    ax.set_yscale("log")
    ax.set_ylim(1e-7, 1.5)

    ax.tick_params(axis="y", colors=log_grid_color)
    ax.set_ylabel("CDF / 1 − CDF", color=log_grid_color)

    for decade in range(-7, 0):

        # Major line 
        y_major = 10.0 ** decade

        for x0, x1 in [(xmin - padding, p5), (p95, xmax + padding)]:
            ax.plot(
                [x0, x1],
                [y_major, y_major],
                linestyle="-",
                linewidth=0.75,
                alpha=0.75,
                color=log_grid_color,
                zorder=0
                )

            # Minor lines
            for m in range(2, 10):

                y_minor = m * 10.0 ** decade

                ax.plot(
                    [x0, x1],
                    [y_minor, y_minor],
                    linestyle="-",
                    linewidth=0.5,
                    alpha=0.5,
                    color=log_grid_color,
                    zorder=0
                    )

    # --------------------------------------------------
    # Legend
    # --------------------------------------------------

    ax_density.legend(
        loc="upper left",
        framealpha=0.9
    )


    # --------------------------------------------------
    # Title
    # --------------------------------------------------

    if title_string:

        ax.set_title(
            title_string,
            fontsize=14,
            fontweight="bold"
        )


    fig.tight_layout()

    return fig, (ax, ax_density)



def add_percentile_lines(
    ax,
    values,
    percentiles=(5, 95),
    labels=None,
    zorder_line=1,
    zorder_text=3
):

    if labels is None:
        labels = [
            f"p{p:g}"
            for p in percentiles
        ]

    for p, label in zip(percentiles, labels):

        value = np.percentile(values, p)

        ax.axvline(
            value,
            linestyle="-",
            color="black",
            linewidth=1,
            alpha=0.75,
            zorder=zorder_line
        )

        ax.annotate(
            label,
            xy=(value, 1),
            xycoords=("data", "axes fraction"),
            xytext=(-1, -10),
            textcoords="offset points",
            rotation=90,
            va="top",
            ha="right",
            fontsize=10,
            zorder=zorder_text
        )



def plot_temperature_qq(
    datasets,
    n_samples=300000,
    config=None,
    title_string=None
):

    from src.distributions import sample_valid_values 

    reference = datasets["reference"]

    ref_values = sample_valid_values(
        reference,
        n_samples=n_samples
    )


    fig, ax = plt.subplots(figsize=(10,10))

    set_temperature_axis(ax,y_axis=True)
        
    ax.set_xlabel("Reference quantiles (K)")
    ax.set_ylabel("Model quantiles (K)")
    
    
    p5 = np.percentile(ref_values, 5)
    p95 = np.percentile(ref_values, 95)
    
    
    ax.axvline(
        p5,
        linestyle="-",
        color="black",
        linewidth=1,
        alpha=0.75,
        zorder=1
        )
        
    ax.axvline(
        p95,
        linestyle="-",
        color="black",
        linewidth=1,
        alpha=0.75,
        zorder=1
        )
            
    ax.annotate(
        "Ref p5",
        xy=(p5, ax.get_ylim()[0]),
        xytext=(-1, 10),
        textcoords="offset points",
        rotation=90,
        va="bottom",
        ha="right",
        fontsize=10)
    
    ax.annotate(
        "Ref p95",
        xy=(p95, ax.get_ylim()[0]),
        xytext=(-1, 10),
        textcoords="offset points",
        rotation=90,
        va="bottom",
        ha="right",
        fontsize=10)
    
    
    # 1:1 reference line 
    lims = [
        min(ax.get_xlim()[0], ax.get_ylim()[0]),
        max(ax.get_xlim()[1], ax.get_ylim()[1])
        ]
    
    ax.plot(
        lims,
        lims,
        "--",
        color="black",
        linewidth=1,
        alpha=0.75,
        zorder=1
        )


    # quantile levels, increased resolution in the tails
    percentile_levels = np.concatenate([
        np.linspace(0, 5, 50),
        np.linspace(5, 95, 100),
        np.linspace(95, 99.9, 50)
        ])

    ref_q = np.percentile(
        ref_values,
        percentile_levels
    )


    for name, da in datasets["models"].items():

        values = sample_valid_values(
            da,
            n_samples=n_samples
        )

        model_q = np.percentile(
            values,
            percentile_levels
        )


        ax.scatter(
            ref_q,
            model_q,
            marker="o",
            s=32,
            alpha=0.75,
            linewidths=0.5,
            edgecolor=config["distributions"][name]["color"],
            color=config["distributions"][name]["color"],
            label=config["distributions"][name]["label"],
            zorder=2
        )

    
    ax.legend()

    if title_string:

        ax.set_title(
            f"{title_string}",
            fontsize=14,
            fontweight="bold"
            )


    return fig, ax