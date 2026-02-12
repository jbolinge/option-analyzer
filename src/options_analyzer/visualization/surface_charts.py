"""3D surface chart functions — Greeks vs price x vol/time."""

import numpy as np
import plotly.graph_objects as go

from options_analyzer.visualization.theme import SURFACE_COLORSCALE, apply_theme


def plot_greek_surface(
    x_range: np.ndarray,
    y_range: np.ndarray,
    z_surface: np.ndarray,
    x_label: str,
    y_label: str,
    z_label: str,
    title: str = "Greek Surface",
) -> go.Figure:
    """Generic 3D surface for any Greek combination."""
    fig = go.Figure(
        data=[
            go.Surface(
                x=x_range,
                y=y_range,
                z=z_surface,
                colorscale=SURFACE_COLORSCALE,
            )
        ]
    )

    fig.update_layout(
        title=title,
        scene=dict(
            xaxis_title=x_label,
            yaxis_title=y_label,
            zaxis_title=z_label,
        ),
    )

    return apply_theme(fig)


def plot_delta_surface(
    price_range: np.ndarray,
    vol_range: np.ndarray,
    delta_surface: np.ndarray,
    title: str = "Delta Surface",
) -> go.Figure:
    """Delta vs price x implied volatility."""
    return plot_greek_surface(
        price_range,
        vol_range,
        delta_surface,
        x_label="Underlying Price",
        y_label="Implied Volatility",
        z_label="Delta",
        title=title,
    )


def plot_gamma_surface(
    price_range: np.ndarray,
    dte_range: np.ndarray,
    gamma_surface: np.ndarray,
    title: str = "Gamma Surface",
) -> go.Figure:
    """Gamma vs price x time — shows gamma concentration near ATM."""
    return plot_greek_surface(
        price_range,
        dte_range,
        gamma_surface,
        x_label="Underlying Price",
        y_label="Days to Expiration",
        z_label="Gamma",
        title=title,
    )
