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
    data1[0:40, 0:40] = 40
    data1[-40:-1, -40:-1] = 255
    # data2 = np.random.rand(24, 18)  # Tablica 240x180 na płaszczyznę ZX
    data2 = np.full((240, 180), 128) if data2 is None else data2.copy()  # Tablica 240x180 na płaszczyznę ZX
    data2[0:40, 0:40] = 40
    data2[-40:-1, -40:-1] = 255
    # data3 = np.random.rand(18, 24)  # Tablica 240x180 na płaszczyznę ZY
    data3 = np.full((180, 240), 128) if data3 is None else data3.copy()  # Tablica 240x180 na płaszczyznę ZY
    data3[0:40, 0:40] = 40
    data3[-40:-1, -40:-1] = 255

    # Definicja minimalnych i maksymalnych wartości
    if min_heat is None:
        min_heat = np.min([np.min(data1), np.min(data2), np.min(data3)])
    if max_heat is None:
        max_heat = np.max([np.max(data1), np.max(data2), np.max(data3)])

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
    filename = os.path.join('compare_cubes', filename)
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
    return [arr1, arr2, arr3]


def show3d_cube(arr_list, min_heat=None, max_heat=None):
    chart3d_vispy(arr_list[0], arr_list[1], arr_list[2], min_heat=min_heat, max_heat=max_heat)


def get_min_max_heat(arr_lists):
    min_heat = np.min([np.min([np.min(al[0]), np.min(al[1]), np.min(al[2])]) for al in arr_lists])
    max_heat = np.max([np.max([np.max(al[0]), np.max(al[1]), np.max(al[2])]) for al in arr_lists])
    print('min_heat', min_heat)
    print('max_heat', max_heat)
    return min_heat, max_heat



if __name__ == '__main__':
    # chart3d_vispy()

    arr_lists = []
    arr_lists.append(get_frame("mati_1mln_cube.json", "mati_1mln_cube"))
    # arr_lists.append(get_frame("mc456_mc_100mln_my_params_cube.json", "benchmark_my_100mln_cube"))

    min_heat, max_heat = get_min_max_heat(arr_lists)

    for al in arr_lists:
        show3d_cube(al, min_heat=min_heat, max_heat=max_heat)
