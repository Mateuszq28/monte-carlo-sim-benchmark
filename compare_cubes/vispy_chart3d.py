import numpy as np
from vispy import scene
from vispy.color import Colormap
from matplotlib import cm
from func4chart3d import *
import os

def chart3d_vispy(data1=None, data2=None, data3=None, min_heat=None, max_heat=None):

    # Przykładowe dane
    # data1 = np.random.rand(18, 18)  # Tablica 180x180 na płaszczyznę XY
    data1 = np.full((180, 180), 128) if data1 is None else data1.copy() # Tablica 180x180 na płaszczyznę XY
    # data2 = np.random.rand(24, 18)  # Tablica 240x180 na płaszczyznę ZX
    data2 = np.full((240, 180), 128) if data2 is None else data2.copy()  # Tablica 240x180 na płaszczyznę ZX
    # data3 = np.random.rand(18, 24)  # Tablica 240x180 na płaszczyznę ZY
    data3 = np.full((180, 240), 128) if data3 is None else data3.copy()  # Tablica 240x180 na płaszczyznę ZY

    # Definicja minimalnych i maksymalnych wartości
    if min_heat is None:
        min_heat = np.min([np.min(data1), np.min(data2), np.min(data3)])
    if max_heat is None:
        max_heat = np.max([np.max(data1), np.max(data2), np.max(data3)])

    # markery na rogach
    # min_marker = min_heat + 0.01 * max_heat
    # max_marker = max_heat
    # data1[0:40, 0:40] = min_marker
    # data1[-40:-1, -40:-1] = max_marker
    # data2[0:40, 0:40] = min_marker
    # data2[-40:-1, -40:-1] = max_marker
    # data3[0:40, 0:40] = min_marker
    # data3[-40:-1, -40:-1] = max_marker

    # Współrzędne środka przecięcia [90, 90, 120]
    x_center, y_center, z_center = 90, 90, 120

    # Tworzenie kanwy
    canvas = scene.SceneCanvas(keys='interactive', show=True)
    view = canvas.central_widget.add_view()
    view.camera = 'arcball'  # Interaktywny widok 3D

    # Ustawienie zakresów osi
    view.camera.scale_factor = 300

    # Ustawienie centralnego punktu obrotu kamery
    view.camera.center = (90, 90, 120)

    # Tworzenie map ciepła
    # colormap1 = Colormap('viridis')
    # colormap2 = Colormap('viridis')
    # colormap3 = Colormap('viridis')
    colormap1 = 'viridis'
    colormap2 = 'viridis'
    colormap3 = 'viridis'

    # Mapy ciepła

    # Płaszczyzna XY (180x180)
    heatmap1 = scene.visuals.Image(data1, cmap=colormap1, clim=(min_heat, max_heat), method='auto', parent=view.scene)
    heatmap1.transform = scene.transforms.MatrixTransform()
    heatmap1.transform.translate([0, 0, z_center])  # Wstawienie na płaszczyznę XY na wysokości z = 120

    # Płaszczyzna ZX (240x180)
    heatmap2 = scene.visuals.Image(data2, cmap=colormap2, clim=(min_heat, max_heat), method='auto', parent=view.scene)
    heatmap2.transform = scene.transforms.MatrixTransform()
    heatmap2.transform.rotate(90, (1, 0, 0))  # Obrót wokół osi X, aby umieścić na ZX
    heatmap2.transform.translate([0, y_center, 0])  # Przesunięcie na płaszczyznę ZX na wysokości y = 90

    # Płaszczyzna ZY (240x180)
    heatmap3 = scene.visuals.Image(data3, cmap=colormap3, clim=(min_heat, max_heat), method='auto', parent=view.scene)
    heatmap3.transform = scene.transforms.MatrixTransform()
    heatmap3.transform.rotate(-90, (0, 1, 0))  # Obrót wokół osi Y, aby umieścić na ZY
    heatmap3.transform.translate([x_center, 0, 0])  # Przesunięcie na płaszczyznę ZY na wysokości x = 90

    # Dodanie osi XYZ przeskalowanych do 180x180x180
    axis = scene.visuals.XYZAxis(parent=view.scene)

    # Przeskalowanie osi XYZ do 180x180x180
    axis.transform = scene.transforms.MatrixTransform()
    axis.transform.scale([180, 180, 180])
    axis.transform.translate([0, 0, 0])  # Przesunięcie na środek danych

    # Uruchomienie interaktywnego wyświetlania
    canvas.app.run()




def get_frame(filename, name):
    cube = load_from_file(filename)
    cube['mu_a'] = 0.37
    cube['name'] = name
    cube['photon_weight'] = 1.0
    cube['normalized_already'] = False

    cube_list2array(cube)

    normalization(cube)

    make_frames([cube])

    # XY
    arr1 = cube['frames'][4]
    # ZX
    arr2 = cube['frames'][1].transpose()
    # ZY
    arr3 = cube['frames'][12]

    # skala logarytmiczna
    # Upewnij się, że wszystkie wartości są większe od 0 (logarytm wymaga wartości > 0)
    out = [arr1, arr2, arr3]
    for i in range(len(out)):
        out[i][out[i] == 0] = np.min(out[i][out[i] > 0])  # Zastąp 0 minimalną dodatnią wartością
        out[i] = np.log10(out[i])

    return out


def show3d_cube(arr_list, min_heat=None, max_heat=None):
    chart3d_vispy(arr_list[0], arr_list[1], arr_list[2], min_heat=min_heat, max_heat=max_heat)


def get_min_max_heat(arr_lists):
    min_heat = np.min([np.min([np.min(al[0]), np.min(al[1]), np.min(al[2])]) for al in arr_lists])
    max_heat = np.max([np.max([np.max(al[0]), np.max(al[1]), np.max(al[2])]) for al in arr_lists])
    print('min_heat', min_heat)
    print('max_heat', max_heat)
    return min_heat, max_heat



class experiment():
    def __init__(self, category, experiment_name, benchmark_path, folders):
        self.category = category #
        self.experiment_name = experiment_name #

        self.folders = folders #
        self.filenames = [] #
        self.benchmark_path = benchmark_path #
        self.mu_a = [] #
        self.all_cubes_names = [] #
        self.params_types = [] #

        self.cubes_path = 'CUBES'

        self.file_paths = []


    def get_all_cubes_names_from_filenames(self):
        self.all_cubes_names = []
        for f_list in self.filenames:
            this_dir_cube_names = []
            for fn in f_list:
                cube_name = fn[:-5]
                this_dir_cube_names.append(cube_name)
            self.all_cubes_names.append(this_dir_cube_names)


    def file_paths_from_filenames(self):
        self.file_paths = []
        for dir_id in range(len(self.folders)):
            this_folder_paths = []
            for fn_id in range(len(self.filenames[dir_id])):
                # path = '/'.join([self.cubes_path, self.folders[dir_id], self.filenames[dir_id][fn_id]])
                path = os.path.join(self.cubes_path, self.folders[dir_id], self.filenames[dir_id][fn_id])
                this_folder_paths.append(path)
            self.file_paths.append(this_folder_paths)


    def make_folders_long(self):
        self.folders_long = []
        for dir_id in range(len(self.folders)):
            this_folder = []
            for _ in range(len(self.filenames[dir_id])):
                this_folder.append(self.folders[dir_id])
            self.folders_long.append(this_folder)


    def get_filenames_from_folders(self):
        self.filenames = []
        for f in self.folders:
            path = os.path.join(self.cubes_path, f)
            file_list = os.listdir(path)
            self.filenames.append(file_list)
        self.file_paths_from_filenames()
        self.make_folders_long()


    def mua_per_dir(self, mua_list):
        self.mu_a = []
        for mua, fn in zip(mua_list, self.filenames):
            self.mu_a.append([mua] * len(fn)) # łączenie tablic


    def params_types_per_dir(self, params_types):
        self.params_types = []
        for pt, fn in zip(params_types, self.filenames):
            self.params_types.append([pt] * len(fn))
        # print(self.params_types)


    def mua_from_file(self):
        self.mu_a = []
        for dir_id in range(len(self.folders)):
            this_folder_mua = []
            for p in self.file_paths[dir_id]:
                with open(p, 'r') as f:
                    cub = json.load(f)
                mua = cub['mu_a']
                this_folder_mua.append(mua)
            self.mu_a.append(this_folder_mua)


    def run(self):

        # przypisz właściwości podstawowe
        all_cubes_names = sum(self.all_cubes_names, []) # łączenie tablic
        all_mu_a = sum(self.mu_a, [])
        all_filename_list = sum(self.file_paths, [])
        all_dir_list = sum(self.folders_long, [])
        all_path_list = sum(self.file_paths, [])
        params_types = sum(self.params_types, [])

        arr_lists = []
        for path, name in zip(all_path_list, all_cubes_names):
            arr_lists.append(get_frame(path, name))

        # min_heat, max_heat = get_min_max_heat(arr_lists)
        min_heat, max_heat = None, None

        for al in arr_lists:
            show3d_cube(al, min_heat=min_heat, max_heat=max_heat)

        





if __name__ == '__main__':





    test = experiment(category = 'specjalistyczne mc456 my-params light-sources',
                  experiment_name = '',
                  benchmark_path = ['CUBES', 'mc456 my-params light-sources', 'mc456_mc_100mln_my_params_tiss_id_4_g_0_9_ls_down_cube.json'],
                  folders = ['mc456 my-params light-sources'],
                  )
    test.get_filenames_from_folders()
    test.get_all_cubes_names_from_filenames()
    test.mua_per_dir([0.37])
    test.params_types_per_dir(['my'])
    test.run()

    # mc456 my-params light-sources




    # test = experiment(category = 'specjalistyczne mc456 rozne_skóry_z_tabeli (8 rodzajów) 100mln',
    #               experiment_name = '',
    #               benchmark_path = ['CUBES', 'mc456 rozne_skóry_z_tabeli (8 rodzajów) 100mln', 'mc456_mc_100mln_my_params_tiss_id_4_cube.json'],
    #               folders = ['mc456 rozne_skóry_z_tabeli (8 rodzajów) 100mln'],
    #               )
    # test.get_filenames_from_folders()
    # test.get_all_cubes_names_from_filenames()
    # test.mua_from_file()
    # test.params_types_per_dir(['my'])
    # test.run()

    # mc456 rozne_skóry_z_tabeli (8 rodzajów) 100mln










