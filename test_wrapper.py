import os
import re
import json
import time
from datetime import datetime

t1 = { # example
    "sim_c_filename": "mc456_mc.c",
    "params_type": "original_params",
    "n_photons": 10_000,

    "out_log_default_name": "mc456_log.txt",
    "out_cube_default_name": "mc456_mc_cube.json",
    "out_log_change_name": "mc456_log_10k_original_params.txt",
    "out_cube_change_name": "mc456_mc_10k_original_params_cube.json",

    "script_dir": "original_params",
    "time_wrapper_Dir_id": 1,
    "time_wrapper_Sim_id": 3
}

num_decoder = {
    0: "0",
    1: "1",
    10: "10",
    100: "100",
    1_000: "1k",
    10_000: "10k",
    100_000: "100k",
    1_000_000: "1mln",
    10_000_000: "10mln",
    100_000_000: "100mln",
    1_000_000_000: "1mld",
    10_000_000_000: "10mld",
    100_000_000_000: "100mld",
}


g_decoder = {
    "0": "0",
    "0.0": "0",
    "0.1": "0_1",
    "0.2": "0_2",
    "0.3": "0_3",
    "0.4": "0_4",
    "0.5": "0_5",
    "0.6": "0_6",
    "0.7": "0_7",
    "0.8": "0_8",
    "0.9": "0_9",
    "1.0": "1",
    "1": "1"
}


tissue_properties = {
    "-2": {"mu_a": 5, "mu_s": 95, "n": 1.0, "name": "ignore label", "print color": "#AACB23"},
    "-1": {"mu_a": None, "mu_s": None, "n": None, "name": "light source", "print color": "#FFE800"},
    "0": {"mu_a": 0, "mu_s": 0, "n": 1.0, "name": "vacuum", "print color": "#FF00F7"},

    "1": {"mu_a": 0.0000019, "mu_s": 0.0000006, "n": 1.000293, "name": "air", "print color": "#E4F6FF"},
    "2": {"mu_a": 0.001019, "mu_s": 0.029813, "n": 1.333, "name": "salt water", "print color": "#5091CE"},
    "3": {"mu_a": 0.0835, "mu_s": 11.71, "n": 1.36, "name": "epidermis", "print color": "#FFF99A"},
    "4": {"mu_a": 0.37, "mu_s": 23.8888943003376, "n": 1.36, "name": "dermis", "print color": "#FFCB9A"},
    "5": {"mu_a": 1.1, "mu_s": 12.8426992965418, "n": 1.36, "name": "fatty subcutaneous tissue", "print color": "#F3FF33"},
    "6": {"mu_a": 2.8, "mu_s": 12.3086801371514, "n": 1.36, "name": "mucous tissue", "print color": "#A9FFBF"},
    "7": {"mu_a": 6.14, "mu_s": 17.07, "n": 1.36, "name": "vein", "print color": "#F3794B"},
    "8": {"mu_a": 2.1, "mu_s": 773, "n": 1.37, "name": "blood", "print color": "#FF1414"}
}


def make_test_dict(sim_c_filename, params_type, n_photon, tiss, g, light_source):
    out_log_default_name = sim_c_filename[:-4] + "log.txt"
    num = num_decoder[n_photon]
    g_str = g_decoder[str(g)]
    out_log_change_name = sim_c_filename[:-4] + "log" + "_" + num + "_" + params_type + "_tiss_id_"+str(tiss)+ "_g_"+g_str+"_" + "ls_"+light_source+ ".txt"

    if sim_c_filename == "mc456_mc.c":
        out_cube_default_name = sim_c_filename[:-2] + "_cube.json"
        out_cube_change_name = sim_c_filename[:-2] + "_" + num + "_" + params_type + "_tiss_id_"+str(tiss)+ "_g_"+g_str+"_" + "ls_"+light_source + "_cube.json"
    else:
        out_cube_default_name = None
        out_cube_change_name = None

    script_dir = "benchmark_sims" if params_type == "my_params" else params_type

    time_wrapper_Sim_id = ["tiny", "small", "mc321", "mc456"].index(sim_c_filename[:-5])
    time_wrapper_Dir_id = ["benchmark_sims", "original_params"].index(script_dir)

    d = {
        "sim_c_filename": sim_c_filename,
        "params_type": params_type,
        "n_photons": n_photon,

        "out_log_default_name": out_log_default_name,
        "out_cube_default_name": out_cube_default_name,
        "out_log_change_name": out_log_change_name,
        "out_cube_change_name": out_cube_change_name,

        # --- from time wrapper: ---
        # sim_names_list = ["tiny", "small", "mc321", "mc456"]
        # sim_name = sim_names_list[3]
        # dirs = ["benchmark_sims", "original_params"]
        # rel_scritpt_dir = dirs[1]

        "script_dir": script_dir,
        "time_wrapper_Dir_id": time_wrapper_Dir_id,
        "time_wrapper_Sim_id": time_wrapper_Sim_id,

        "tiss_id": tiss,
        "tiss_name": tissue_properties[str(tiss)]['name'],
        "tiss_mu_a": tissue_properties[str(tiss)]['mu_a'],
        "tiss_mu_s": tissue_properties[str(tiss)]['mu_s'],
        "tiss_n": tissue_properties[str(tiss)]['n'],

        "anisotropy_g": g,
        "light_source": light_source
    }

    return d



# Function to find and replace a line in a file based on a regex pattern
def replace_line_in_file(file_path, regex_pattern, new_sentence):
    # Open the file and read all lines
    with open(file_path, 'r') as file:
        lines = file.readlines()
    
    # Open the file in write mode to replace the content
    with open(file_path, 'w') as file:
        for line in lines:
            # If the line matches the regex pattern, replace it with the new sentence
            if re.search(regex_pattern, line):
                if new_sentence is not None:
                    file.write(new_sentence + '\n')
            else:
                file.write(line)



def test_log(data_dict, filename, iter_start_time, all_runs_start_time):
    datetime_log = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    end_time = time.time()
    iter_time = str(end_time - iter_start_time) + " seconds"
    all_runs_time_time = str(end_time - all_runs_start_time) + " seconds"
    # add to log file
    data_dict['datetime_log'] = datetime_log
    data_dict['iter_time'] = iter_time
    data_dict['all_runs_time_time'] = all_runs_time_time
    # print
    print('datetime_log', datetime_log)
    print('iter_time', iter_time)
    print('all_runs_time_time', all_runs_time_time)
    with open(filename, 'w') as f:
        json.dump(data_dict, f)



def run():
    # small test
    # sim_c_filenames = ["tiny_mc.c"]
    # params_types = ["original_params"]
    # n_photons = [10_000]

    # duży test na ilość fotonów
    sim_c_filenames = ["mc456_mc.c", "tiny_mc.c", "small_mc.c"]
    params_types = ["original_params", "my_params"]
    n_photons = [10**n for n in range(8,9)]

    # test na różne warstwy skóry
    sim_c_filenames = ["mc456_mc.c"]
    params_types = ["my_params"]
    n_photons = [10**8]
    tissue_material_id = list(range(2,9))

    # test na różne g
    sim_c_filenames = ["mc456_mc.c"]
    params_types = ["my_params"]
    n_photons = [10**7]
    tissue_material_id = [4] # domyślna skóra
    g_list = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]

    # test na różne źródła światła
    sim_c_filenames = ["mc456_mc.c"]
    params_types = ["my_params"]
    n_photons = [10**8]
    tissue_material_id = [4] # domyślna skóra
    g_list = [0.9]
    light_source_list = ["down", "up", "isotropic", "coll_gauss", "foc_gauss"]



    all_runs_start_time = time.time()
    for light_source in light_source_list:
        for g in g_list:
            for tiss in tissue_material_id:
                for n_photon in n_photons:
                    for sim_c_filename in sim_c_filenames:
                        for params_type in params_types:

                            print("iter start")
                            iter_start_time = time.time()
                            # setup dict that describes all features of the test
                            print("make_test_dict")
                            test_dict = make_test_dict(sim_c_filename, params_type, n_photon, tiss, g, light_source)
                            print()
                            print("===============================================")
                            print(test_dict['n_photons'])
                            print(num_decoder[ test_dict['n_photons'] ] + " photons")
                            print(test_dict)
                            # path to dir with script
                            print()
                            print("set paths")
                            self_path = os.path.dirname(os.path.abspath(__file__))
                            script_dir = os.path.join(self_path, test_dict['script_dir'])
                            # change nphotons in c source code
                            print("edit n photons in c source code")
                            cfile_path = os.path.join(script_dir, sim_c_filename)
                            exefile_path = os.path.join(script_dir, sim_c_filename[:-1] + "exe")
                            objfile_path = os.path.join(script_dir, sim_c_filename[:-1] + "obj")
                            if sim_c_filename == "tiny_mc.c":
                                regex_pattern = r".*ID_EDIT_1_1.*"
                                new_sentence = f"long   i, shell, photons = {n_photon}; /*ID_EDIT_1_1*/"
                            elif sim_c_filename == "small_mc.c":
                                regex_pattern = r".*ID_EDIT_1_2.*"
                                new_sentence = f"long   i, photons = {n_photon}; /*ID_EDIT_1_2*/"
                            elif sim_c_filename == "mc456_mc.c":
                                regex_pattern = r".*ID_EDIT_1_3.*"
                                new_sentence = f"Nphotons    = {n_photon}; /* set number of photons in simulation */ /*ID_EDIT_1_3*/"
                            else:
                                print("break!")
                                print(test_dict)
                                break
                            replace_line_in_file(cfile_path, regex_pattern, new_sentence)
                            # change tissue
                            if sim_c_filename == "mc456_mc.c":
                                cfile_path = os.path.join(script_dir, sim_c_filename)
                                # mu_a
                                regex_pattern = r".*ID_EDIT_4_1.*"
                                new_sentence = f"mua         = {test_dict['tiss_mu_a']};     /* cm^-1 */ /*ID_EDIT_4_1*/"
                                replace_line_in_file(cfile_path, regex_pattern, new_sentence)
                                # mu_s
                                regex_pattern = r".*ID_EDIT_4_2.*"
                                new_sentence = f"mus         = {test_dict['tiss_mu_s']};  /* cm^-1 */ /*ID_EDIT_4_2*/"
                                replace_line_in_file(cfile_path, regex_pattern, new_sentence)
                                # n
                                regex_pattern = r".*ID_EDIT_4_3.*"
                                new_sentence = f"nt          = {test_dict['tiss_n']};  /*ID_EDIT_4_3*/"
                                replace_line_in_file(cfile_path, regex_pattern, new_sentence)
                            else:
                                raise NotImplementedError
                            # change g
                            if sim_c_filename == "mc456_mc.c":
                                cfile_path = os.path.join(script_dir, sim_c_filename)
                                # g
                                regex_pattern = r".*ID_EDIT_5.*"
                                new_sentence = f"g           = {test_dict['anisotropy_g']};  /*ID_EDIT_5*/"
                                replace_line_in_file(cfile_path, regex_pattern, new_sentence)
                            else:
                                raise NotImplementedError
                            # change light source type
                            if sim_c_filename == "mc456_mc.c":
                                cfile_path = os.path.join(script_dir, sim_c_filename)
                                # del all but first edit line
                                regex_pattern = r".*ID_EDIT_6_DEL.*"
                                new_sentence = None
                                replace_line_in_file(cfile_path, regex_pattern, new_sentence)
                                # replace first edit line
                                regex_pattern = r".*ID_EDIT_6_FIXED.*"
                                ls = test_dict['light_source']
                                if ls == "down":
                                    new_sentence = "x = x_start;    /* Set photon position to origin. */ /*ID_EDIT_6_FIXED*/" + "\n"
                                    new_sentence += "y = y_start; /*ID_EDIT_6_DEL*/" + "\n"
                                    new_sentence += "z = z_start; /*ID_EDIT_6_DEL*/" + "\n"
                                    new_sentence += "/*ID_EDIT_6_DEL*/" + "\n"
                                    new_sentence += "/* source - vartical down [0,0,-1] */ /*ID_EDIT_6_DEL*/" + "\n"
                                    new_sentence += "ux = 0; /*ID_EDIT_6_DEL*/" + "\n"
                                    new_sentence += "uy = 0; /*ID_EDIT_6_DEL*/" + "\n"
                                    new_sentence += "uz = -1; /*ID_EDIT_6_DEL*/"
                                elif ls == "up":
                                    new_sentence = "x = x_start;    /* Set photon position to origin. */ /*ID_EDIT_6_FIXED*/" + "\n"
                                    new_sentence += "y = y_start; /*ID_EDIT_6_DEL*/" + "\n"
                                    new_sentence += "z = z_start; /*ID_EDIT_6_DEL*/" + "\n"
                                    new_sentence += "/*ID_EDIT_6_DEL*/" + "\n"
                                    new_sentence += "/* source - vartical up [0,0,1] */ /*ID_EDIT_6_DEL*/" + "\n"
                                    new_sentence += "ux = 0; /*ID_EDIT_6_DEL*/" + "\n"
                                    new_sentence += "uy = 0; /*ID_EDIT_6_DEL*/" + "\n"
                                    new_sentence += "uz = 1; /*ID_EDIT_6_DEL*/"
                                elif ls == "isotropic":
                                    new_sentence = "x = x_start;    /* Set photon position to origin. */ /*ID_EDIT_6_FIXED*/" + "\n"
                                    new_sentence += "y = y_start; /*ID_EDIT_6_DEL*/" + "\n"
                                    new_sentence += "z = z_start - 120 * dr; /*ID_EDIT_6_DEL*/" + "\n"
                                    new_sentence += "/*ID_EDIT_6_DEL*/" + "\n"
                                    new_sentence += "/* Randomly set photon trajectory to yield an isotropic source. */ /*ID_EDIT_6_DEL*/" + "\n"
                                    new_sentence += "costheta = 2.0*RandomNum - 1.0; /*ID_EDIT_6_DEL*/" + "\n"
                                    new_sentence += "sintheta = sqrt(1.0 - costheta*costheta);	/* sintheta is always positive */ /*ID_EDIT_6_DEL*/" + "\n"
                                    new_sentence += "psi = 2.0*PI*RandomNum; /*ID_EDIT_6_DEL*/" + "\n"
                                    new_sentence += "ux = sintheta*cos(psi); /*ID_EDIT_6_DEL*/" + "\n"
                                    new_sentence += "uy = sintheta*sin(psi); /*ID_EDIT_6_DEL*/" + "\n"
                                    new_sentence += "uz = costheta; /*ID_EDIT_6_DEL*/"
                                elif ls == "coll_gauss":
                                    # Collimated Gaussian Beam
                                    new_sentence = "b_rad = 20 * SIGN(2*RandomNum-1) * dr;    /* Set photon position to origin. */ /*ID_EDIT_6_FIXED*/" + "\n"
                                    new_sentence += "x = x_start + b_rad * sqrt(-log(RandomNum)); /* log is e base */ /*ID_EDIT_6_DEL*/" + "\n"
                                    new_sentence += "y = y_start; /*ID_EDIT_6_DEL*/" + "\n"
                                    new_sentence += "z = z_start; /*ID_EDIT_6_DEL*/" + "\n"
                                    new_sentence += "ux = 0; /*ID_EDIT_6_DEL*/" + "\n"
                                    new_sentence += "uy = 0; /*ID_EDIT_6_DEL*/" + "\n"
                                    new_sentence += "uz = -1; /*ID_EDIT_6_DEL*/"
                                elif ls == "foc_gauss":
                                    # Focused Gaussian Beam
                                    new_sentence = "w_rad = 20 * SIGN(2*RandomNum-1) * dr;    /* Set photon position to origin. */ /*ID_EDIT_6_FIXED*/" + "\n"
                                    new_sentence += "x = x_start + w_rad * sqrt(-log(RandomNum)); /* log is e base */ /*ID_EDIT_6_DEL*/" + "\n"
                                    new_sentence += "y = y_start; /*ID_EDIT_6_DEL*/" + "\n"
                                    new_sentence += "z = z_start; /*ID_EDIT_6_DEL*/" + "\n"
                                    new_sentence += "z_focus = 60 * dr; /*ID_EDIT_6_DEL*/" + "\n"
                                    new_sentence += "x_focus = w_rad * sqrt(-log(RandomNum)) * SIGN(2*RandomNum-1); /*ID_EDIT_6_DEL*/" + "\n"
                                    new_sentence += "temp = sqrt(pow((x-x_focus),2) + pow(z_focus,2)); /*ID_EDIT_6_DEL*/" + "\n"
                                    new_sentence += "sintheta = -(x-x_focus)/temp; /*ID_EDIT_6_DEL*/" + "\n"
                                    new_sentence += "costheta = z_focus/temp; /*ID_EDIT_6_DEL*/" + "\n"
                                    new_sentence += "ux = sintheta; /*ID_EDIT_6_DEL*/" + "\n"
                                    new_sentence += "uy = 0; /*ID_EDIT_6_DEL*/" + "\n"
                                    new_sentence += "uz = costheta; /*ID_EDIT_6_DEL*/"
                                else:
                                    raise NotImplementedError
                                replace_line_in_file(cfile_path, regex_pattern, new_sentence)
                            else:
                                raise NotImplementedError
                            # compile
                            print("compile")
                            print()
                            # /Fe - flag to tell where put .exe output file
                            # /Fo - flag to tell where put .obj output file
                            # /O2 - maximum optimization for speed
                            os.system(f"cl {cfile_path} /Fe{exefile_path} /Fo{objfile_path} /O2")
                            print()
                            # change source code in time wrapper
                            print("change time_wrapper.py")
                            pywrap_path = os.path.join(self_path, "time_wrapper.py")
                            regex_pattern1 = r".*ID_EDIT_2.*"
                            regex_pattern2 = r".*ID_EDIT_3.*"
                            new_sentence1 = f"sim_name = sim_names_list[{ test_dict['time_wrapper_Sim_id'] }] # ID_EDIT_2"
                            new_sentence2 = f"rel_scritpt_dir = dirs[{ test_dict['time_wrapper_Dir_id'] }] # ID_EDIT_3"
                            replace_line_in_file(pywrap_path, regex_pattern1, new_sentence1)
                            replace_line_in_file(pywrap_path, regex_pattern2, new_sentence2)
                            # run using time wrapper
                            print("run in time wrapper")
                            os.system(f"python {pywrap_path}")
                            # rename
                            print("rename")
                            # rename cube.json
                            old_name = test_dict["out_cube_default_name"]
                            new_name = test_dict["out_cube_change_name"]
                            if old_name is not None:
                                old_name = os.path.join(script_dir, old_name)
                                new_name = os.path.join(script_dir, new_name)
                                os.replace(old_name, new_name)
                            # rename log.txt
                            old_name = test_dict["out_log_default_name"]
                            old_name = os.path.join(script_dir, old_name)
                            new_name = test_dict["out_log_change_name"]
                            new_name = os.path.join(script_dir, new_name)
                            os.replace(old_name, new_name)
                            # save state log
                            print("log")
                            test_log(test_dict, "test_wrapper_log.txt", iter_start_time, all_runs_start_time)
                            print("iter done")
                    


if __name__ == '__main__':
    run()