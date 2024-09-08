import os
import time

# choose sim
sim_names_list = ["tiny", "small", "mc321"]
sim_name = sim_names_list[0]

# open script location
self_path = os.path.dirname(os.path.abspath(__file__))
rel_scritpt_dir = "benchmark_sims"
abs_script = os.path.join(self_path, rel_scritpt_dir)
os.system("cd {}".format(abs_script))

# do simulation
start_time = time.time()
if sim_name != "mc321":
    os.system("{}_mc.exe > {}_out.txt".format(sim_name, sim_name))
else:
    os.system("{}_mc.exe".format(sim_name))
end_time = time.time()

# print time
exec_time = end_time - start_time
time_text = "time elapsed: {0:.4f} seconds".format(exec_time)
print(time_text)

# save simulation log
f = open("{}_log.txt", "w")
f.write(time_text)
f.write("\n\n")
f.wite("sim results:")
f.write("\n\n")
with open("{}_out.txt".format(sim_name), "r") as f_out:
    f_out_text = f_out.read()
    f.write(f_out_text)
f.write("\n\n")
f.write("code that generated this simulation:")
f.write("\n\n")
with open("{}_mc.c".format(sim_name), "r") as f_code:
    f_code_text = f_code.read()
    f.write(f_code_text)
f.close()



