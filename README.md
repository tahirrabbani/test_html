# test_html
Basic testing

## Point Cloud Viewer

`point_cloud_viewer.py` generates an interactive 3D scatter plot of a point cloud using Plotly.
The viewer supports rotation, zooming, rectangle and lasso selection and lets you choose
between several color palettes.

### Usage

```bash
python point_cloud_viewer.py
```

Options include the number of points, groups and the palette:

```bash
python point_cloud_viewer.py -n 2000 -g 4 -p viridis -d select -o viewer.html
```
You can skip automatically opening the file with `--no-open`.
The script writes an HTML file. Install the required dependencies with:

```bash
pip install -r requirements.txt
```
