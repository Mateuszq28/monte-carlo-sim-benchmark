import os
import time

self_path = os.path.dirname(os.path.abspath(__file__))
rel_scritp = "original/small_mc.exe"
abs_script = os.path.join(self_path, rel_scritp)

start_time = time.time()
os.system(abs_script)
end_time = time.time()
exec_time = end_time - start_time
print("time elapsed: {0:.4f} seconds".format(exec_time))