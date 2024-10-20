# version for python scripts

import os
import time

# choose sim
sims_that_saves_output_itself = ["mc321_p", "mc456_p"]
sim_names_list = ["mc321_p", "mc456_p"]
sim_name = sim_names_list[1] # ID_EDIT_2
dirs = ["benchmark_sims", "original_params"]
rel_scritpt_dir = dirs[0] # ID_EDIT_3

# filenames
sim_exe = "{}.py".format(sim_name)
sim_out = "{}_out.txt".format(sim_name)
sim_c = "{}.py".format(sim_name)
sim_log = "{}_log.txt".format(sim_name)

# absolute paths
self_path = os.path.dirname(os.path.abspath(__file__))
abs_script_dir = os.path.join(self_path, rel_scritpt_dir)
path_sim_exe = os.path.join(abs_script_dir, sim_exe)
path_sim_out = os.path.join(abs_script_dir, sim_out)
path_sim_c = os.path.join(abs_script_dir, sim_c)
path_sim_log = os.path.join(abs_script_dir, sim_log)

# do simulation
start_time = time.time()
if sim_name not in sims_that_saves_output_itself:
    os.system("python {} > {}".format(path_sim_exe, path_sim_out))
else:
    os.system("cd {} && python {}".format(abs_script_dir, sim_exe))
end_time = time.time()

# print time
exec_time = end_time - start_time
time_text = "time elapsed: {0:.4f} seconds".format(exec_time)
print(time_text)

# save simulation log
f = open(path_sim_log, "w")
f.write(time_text)
f.write("\n\n")
f.write("=================================")
f.write("\n\n")
f.write("sim results:")
f.write("\n\n")
with open(path_sim_out, "r") as f_out:
    f_out_text = f_out.read()
    f.write(f_out_text)
f.write("\n\n")
f.write("=================================")
f.write("\n\n")
f.write("code that generated this simulation:")
f.write("\n\n")
with open(path_sim_c, "r") as f_code:
    f_code_text = f_code.read()
    f.write(f_code_text)
f.close()

