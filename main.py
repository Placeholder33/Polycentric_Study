import rasterio
import ctypes
import math

##%%time CPU times: user 7.03 s, sys: 254 ms, total: 7.29 s;  Wall time: 11.2 s

file_path = "data/ciesen_nasa_gpw_v4_population_density_2020.tif"

compression = 1000  # size of blocks

with rasterio.open(file_path) as src:
    n_in, m_in = src.height, src.width
    n = math.ceil(n_in / compression)
    m = math.ceil(m_in / compression)
print(n_in,m_in)
# create the ctypes array
G = (ctypes.c_double * (n * m))()
for k in range(n * m):
    G[k] = 0.0

with rasterio.open(file_path) as src:
    for i in range(n):
        for j in range(m):
            # compute actual window bounds
            row_start = i * compression
            row_stop  = min((i + 1) * compression, n_in)
            col_start = j * compression
            col_stop  = min((j + 1) * compression, m_in)

            window = ((row_start, row_stop), (col_start, col_stop))
            block = src.read(int(1), window=window).astype('float64')
            if src.nodata is not None:
                block = np.where(block == src.nodata, np.nan, block)
            if np.isnan(block).all():
                block_mean = 0.0  # or np.nan, depending on your use case
            else:
                block_mean = np.nanmean(block)
            # store directly into ctypes array
            G[i * m_out + j] = block_mean
#%%
