import rasterio
import ctypes
import math
import numpy as np
import tkinter as tk
from PIL import Image, ImageTk
import networkx as nx
import matplotlib
import geopandas as gpd


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


def bitmap(epis):
    global pper, max_val, gp
    gr = nx.Graph()
    gr_con = (ctypes.c_int * (int(2 * n * m * 2)))()
    gr_con_len = class_lib.slice_graph(n, m, epis, G, gr_con)
    gr_con_to_py = [(gr_con[2 * i], gr_con[2 * i + 1]) for i in range(gr_con_len)]
    edges_list = [((x[0], G[x[0]]), (x[1], G[x[1]])) for x in gr_con_to_py]
    gr.add_edges_from(edges_list)
    conex_list = list(nx.connected_components(gr))
    max_val = 0
    average = []
    max_indexes = []
    for conex in conex_list:
        sum_temp = sum(a[1] for a in conex)
        average.append(sum_temp)
        if max_val < sum_temp:
            max_indexes = {a[0] for a in conex}
            max_val = sum_temp
    gp = (max_val - sum(average)/len(conex_list)) / max_val
    pixel_set = {x for y in gr_con_to_py for x in y}
    imi = Image.new(mode="RGB", size=(m, n), color="white")
    pixels = imi.load()
    temp = 0
    for i in range(n):
        for j in range(m):
            if i*m + j in max_indexes:
                temp += 1
                pixels[j, i] = (136, 8, 8)
            elif i * m + j in pixel_set:
                temp += 1
                pixels[j, i] = (0, 0, 0)
            else:
                pixels[j, i] = (255, 255, 255)
    pper = temp / inipi * 100
    global pper_label
    max_label.config(text="Maximum value of connected component: " + str(max_val))
    pper_label.config(text="Percentage of points: " + str(pper))
    gp_label.config(text="Degree of polycentrism: " + str(gp))
    return imi


file_path = "data/GHS_POP_E2030_GLOBE_R2023A_54009_100_V1_0_R5_C19.tif"
compression = 25
vanish = 100

with rasterio.open(file_path) as src:
    n_in, m_in = src.height, src.width
    n = math.ceil(n_in / compression)
    m = math.ceil(m_in / compression)
print(n_in,m_in)
print(n,m)
size = min(800/n, 1400/m)
G = (ctypes.c_double * (n * m))()
for k in range(n * m):
    G[k] = 0.0
with rasterio.open(file_path) as src:
    for i in range(n):
        for j in range(m):
            row_start = i * compression
            row_stop  = min((i + 1) * compression, n_in)
            col_start = j * compression
            col_stop  = min((j + 1) * compression, m_in)
            window = ((row_start, row_stop), (col_start, col_stop))

            block = src.read(int(1), window=window).astype('float64')
            if src.nodata is not None:
                block = np.where(block == src.nodata, np.nan, block)
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

pper_label = tk.Label(root, text = "Percentage of points: " + str(pper) + "%", font=("Arial", 20))
pper_label.grid(row=0, column = 1, pady = 20, padx=20)
max_label = tk.Label(root, text = "Maximum value of connected component: " + str(max_val), font=("Arial", 20))
max_label.grid(row=1, column = 1, pady = 20, padx=20)
gp_label = tk.Label(root, text = "Degree of polycentrism: " + str(gp), font=("Arial", 20))
gp_label.grid(row=2, column = 1, pady = 20, padx=20)


image_display = tk.Label(root)
image_display.grid(row=0, column=0, padx=20, pady=20, rowspan = 19)

slider=tk.Scale(root,from_=0, to = 100, orient="horizontal", length = size*m, command=on_slider_move)
slider.grid(row=20, column=0,pady=20,padx=20)

vanish_label = tk.Label(root, text = "Vanish Factor")
vanish_label.grid(row=4, column = 1, pady = 20, padx=20)

vanish_entry = tk.Entry(root)
vanish_entry.grid(row=5, column = 1, pady=20, padx=20)

on_slider_move(0)


root.mainloop()

