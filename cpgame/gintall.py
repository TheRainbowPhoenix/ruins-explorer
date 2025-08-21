import gc
from gint import *
gc.collect()
free_mem = gc.mem_free()
alloc_mem = gc.mem_alloc()
txt = "{} / {}".format(alloc_mem,free_mem)
print(txt)