import rasterio
import ctypes
import math
import numpy as np
import tkinter as tk
from PIL import Image, ImageTk
import networkx as nx
import matplotlib
import geopandas as gpd
from random import randint
from rasterio.transform import from_bounds
from rasterio.features import rasterize


def bitmap(epis):
    global pper, max_val, gp
    matrix = [[G[i*m+j] for j in range(m)] for i in range(n)]
    gr = nx.Graph()
    for i in range(n):
        gr.add_edges_from([((i*m+j, matrix[i][j]), (i*m+j+1, matrix[i][j+1])) for j in range(m-1) if abs(matrix[i][j] - matrix[i][j+1]) < epis])
    for j in range(m):
        gr.add_edges_from([((i * m + j, matrix[i][j]), (i * m + j + m, matrix[i+1][j])) for i in range(n - 1) if abs(matrix[i][j] - matrix[i+1][j]) < epis])
    conex_list = list(nx.connected_components(gr))
    max_val = 0
    average = []
    colors_dict = {i*m+j : 0 for i in range(n) for j in range(m)}
    for conex in conex_list:
        sum_temp = sum(a[1] for a in conex)
        average.append(sum_temp)
        for a in conex:
            colors_dict[a[0]] = sum_temp
        max_val = max(max_val, sum_temp)
    gp = abs(math.log((max_val - sum(average)/len(conex_list)) / max_val))
    max_label.config(text="Maximum value of connected component: " + str(max_val))
    gp_label.config(text="Degree of polycentrism: " + str(gp))
    imi = Image.new(mode="RGB", size=(m, n), color="white")
    pixels = imi.load()
    for i in range(n):
        for j in range(m):
            color = 255 - int((colors_dict[i*m+j]/max_val) * 255)
            pixels[j, i] = (color, color, color)
    return imi


def on_slider_move(epis):
    try:
        val = math.log(1+float(epis)/(100*float(vanish_entry.get()))) * maxi/math.log(2)
    except:
        val = math.log(1+float(epis)/100) * maxi/math.log(2)
    pil_image = bitmap(val)
    pil_image = pil_image.resize((int(m*size),int(n*size)))
    tk_photo = ImageTk.PhotoImage(pil_image)
    image_display.config(image=tk_photo)
    image_display.image = tk_photo


compression = 10
vanish = 100
file_path = "data/gridpoblacio01012025.shp"
pop_column = "TOTAL"
resolution = 250

gdf = gpd.read_file(file_path).to_crs("EPSG:25831")
bounds = gdf.total_bounds

n_in = int((bounds[3] - bounds[1]) / resolution)
m_in = int((bounds[2] - bounds[0]) / resolution)

n = math.ceil(n_in / compression)
m = math.ceil(m_in / compression)
print(n_in, m_in)
print(n, m)
size = min(800 / n, 1400 / m)
transform = from_bounds(*bounds, width=m_in, height=n_in)

shapes = (
    (geom, value)
    for geom, value in zip(gdf.geometry, gdf[pop_column])
    if value is not None and not np.isnan(float(value))
)

full_raster = rasterize(
    shapes=shapes,
    out_shape=(n_in, m_in),
    transform=transform,
    fill=np.nan,
    dtype="float64"
)

G = (ctypes.c_double * (n * m))()
for k in range(n * m):
    G[k] = 0.0

for i in range(n):
    for j in range(m):
        row_start = i * compression
        row_stop = min((i + 1) * compression, n_in)
        col_start = j * compression
        col_stop = min((j + 1) * compression, m_in)

        block = full_raster[row_start:row_stop, col_start:col_stop]

        if np.isnan(block).all():
            block_mean = 0.0
        else:
            block_mean = np.nanmean(block)

        G[i * m + j] = block_mean

class_lib = ctypes.CDLL("./class_lib.dll")

class_lib.max_search.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_double)]
class_lib.max_search.restype = ctypes.c_double

class_lib.slice_graph.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_double, ctypes.POINTER(ctypes.c_double),
                                  ctypes.POINTER(ctypes.c_int)]
class_lib.slice_graph.restype = ctypes.c_int

maxi = class_lib.max_search(n,m,G)
pper=100
max_val = maxi
gp = 0

miau = (ctypes.c_int * (int(2 * n * m * 2)))()
miau_len = class_lib.slice_graph(n, m, 0, G, miau)
miau_to_py = [(miau[2 * i], miau[2 * i + 1]) for i in range(miau_len)]
inipi = len(set([x for y in miau_to_py for x in y]))

root = tk.Tk()
root.title("Policentrinator")
root.geometry("2000x960")
root.resizable(width = True, height = True)

max_label = tk.Label(root, text = "Maximum value of connected component: " + str(max_val), font=("Arial", 20))
max_label.grid(row=1, column = 1, pady = 20, padx=20)
gp_label = tk.Label(root, text = "Degree of polycentrism: " + str(gp), font=("Arial", 20))
gp_label.grid(row=2, column = 1, pady = 20, padx=20)


image_display = tk.Label(root)
image_display.grid(row=0, column=0, padx=20, pady=20, rowspan = 19)

slider=tk.Scale(root,from_=0, to = 100, orient="horizontal", length = size*m, command=on_slider_move)
slider.grid(row=20, column=0,pady=20,padx=20)

vanish_entry = tk.Entry(root)
vanish_entry.grid(row=4, column = 1, pady=20, padx=20)

on_slider_move(0.5)


root.mainloop()

