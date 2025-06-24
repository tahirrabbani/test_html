import argparse
import sys

try:
    import numpy as np
    import plotly.graph_objects as go
    from plotly.colors import qualitative, sequential
except ModuleNotFoundError as exc:
    missing = exc.name
    print(f"Missing required module '{missing}'. Install dependencies with:")
    print("  pip install -r requirements.txt")
    sys.exit(1)

# Predefined color palettes
PALETTES = {
    'plotly': qualitative.Plotly,
    'set1': qualitative.Set1,
    'set2': qualitative.Set2,
    'viridis': sequential.Viridis,
    'plasma': sequential.Plasma,
    'coolwarm': sequential.RdBu
}


def generate_points(num_points=1000, num_groups=3, seed=None):
    """Generate random 3D points with group labels."""
    rng = np.random.default_rng(seed)
    points = rng.random((num_points, 3))
    labels = rng.integers(num_groups, size=num_points)
    return points, labels


def create_figure(points, labels, palette='plotly', dragmode='lasso'):
    """Create a Plotly figure for the point cloud."""
    palette = PALETTES.get(palette.lower(), qualitative.Plotly)
    colors = [palette[label % len(palette)] for label in labels]

    scatter = go.Scatter3d(
        x=points[:, 0],
        y=points[:, 1],
        z=points[:, 2],
        mode='markers',
        marker=dict(size=3, color=colors)
    )

    fig = go.Figure(scatter)
    fig.update_layout(
        scene=dict(xaxis_title='X', yaxis_title='Y', zaxis_title='Z'),
        margin=dict(l=0, r=0, b=0, t=0),
        width=800,
        height=600,
        dragmode=dragmode,
    )
    return fig


def main():
    parser = argparse.ArgumentParser(
        description="Interactive 3D point cloud viewer using Plotly.")
    parser.add_argument('-n', '--num-points', type=int, default=1000,
                        help='Number of random points to generate.')
    parser.add_argument('-g', '--groups', type=int, default=3,
                        help='Number of color groups.')
    parser.add_argument('-p', '--palette', default='plotly',
                        help=f"Color palette name. Options: {', '.join(PALETTES.keys())}")
    parser.add_argument('-d', '--dragmode', choices=['lasso', 'select'],
                        default='lasso', help='Initial selection mode.')
    parser.add_argument('-o', '--output', default='point_cloud.html',
                        help='Output HTML filename.')
    parser.add_argument('--no-open', action='store_true',
                        help="Don't open the HTML file after writing.")
    args = parser.parse_args()

    points, labels = generate_points(args.num_points, args.groups)
    fig = create_figure(points, labels, args.palette, args.dragmode)
    fig.write_html(args.output, auto_open=not args.no_open)
    print(f'Wrote {args.output}')


if __name__ == '__main__':
    main()
