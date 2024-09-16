# --- HEAT MAPS ---

# WARNING! if arr it's a sum along axis, remmember to divide by len(of this axis)
# do it before giving it to heatmap2d function
def heatmap2d(arr: np.ndarray, bins_per_cm, title=None, norm="log"):

    # plt.tight_layout()

    # skip first tick on x axis
    # ax = plt.gca()
    # xticks = ax.xaxis.get_major_ticks()
    # xticks[0].label1.set_visible(False)
    
    title_out, xlab, ylab, extent, plot_arr = handle_plot_data(arr, title, bins_per_cm)

    plt.xlabel(xlab)
    plt.ylabel(ylab)
    plt.title(title_out)

    # wyświetlenie tablicy
    plt.imshow(plot_arr, cmap='viridis', norm=norm, interpolation="none", extent=extent) # musi być przed color bar

    # kolorowy pasek ze skalą
    # cb = plt.colorbar(fraction=0.046, pad=0.04)
    cb = plt.colorbar(pad=0.010)
    cb.set_label(r'$ 1/cm^2 $')

    # manager = plt.get_current_fig_manager()
    # manager.window.showMaximized()
    # manager.canvas.toolbar.save_figure()

    plt.show()




def handle_plot_data(arr, title, bins_per_cm):
    """
    Funkcja pomocnicza do obsługi różnych przypadków osi i przekształceń
    """
    xlab = ""
    ylab = ""
    title_out = "Współczynnik fluencji względnej"
    title_out += "\n" + title if title is not None else ""
    if "x_high" in title_out:
        xlab = "y [cm]"
        ylab = "z [cm]"
        plot_arr = np.flip(arr.transpose(), axis=(0))
        extent=[0, arr.shape[0]/bins_per_cm, 0, arr.shape[1]/bins_per_cm] # podziałka legendy
    elif "x_low" in title_out:
        xlab = "y [cm]"
        ylab = "z [cm]"
    elif "y_high" in title_out:
        xlab = "x [cm]"
        ylab = "z [cm]"
    elif "y_low" in title_out:
        xlab = "x [cm]"
        ylab = "z [cm]"
        # obracanie tablicy
        plot_arr = np.flip(arr.transpose(), axis=(0))
        extent=[0, arr.shape[0]/bins_per_cm, 0, arr.shape[1]/bins_per_cm] # podziałka legendy
    elif "z_high" in title_out:
        xlab = "y [cm]"
        ylab = "x [cm]"
        # obracanie tablicy
        # plot_arr = np.flip(arr.transpose(), axis=(0))
        plot_arr = arr
        extent=[0, arr.shape[0]/bins_per_cm, arr.shape[1]/bins_per_cm, 0] # podziałka legendy
        plt.gca().xaxis.set_label_position('top')  # Move xlabel to the top
        plt.gca().xaxis.tick_top()  # Move the ticks to the top
    elif "z_low" in title_out:
        xlab = "y [cm]"
        ylab = "x [cm]"
    else:
        plot_arr = arr
    return title_out, xlab, ylab, extent, plot_arr




def heatmap2d_grid_shared_colorbar(arr_list: list, bins_per_cm, grid_shape: tuple, main_title=None, norm="log"):
    """
    Wyświetla tablice w układzie siatki (grid) z wspólną skalą kolorów i jednym colorbar.
    
    Parametry:
    - arr_list: lista tablic numpy, które mają być wyświetlone,
    - bins_per_cm: wartość określająca ilość binów na centymetr,
    - grid_shape: krotka (rows, cols) określająca ilość wierszy i kolumn w siatce,
    - main_title: wspólny tytuł dla wszystkich wykresów, opcjonalny,
    - norm: sposób normalizacji, domyślnie "log".
    """

    # Obliczanie wspólnych minimalnych i maksymalnych wartości dla wszystkich tablic
    global_min = np.min([np.min(arr) for arr in arr_list])
    global_max = np.max([np.max(arr) for arr in arr_list])

    # Wybór normy
    if norm == "log":
        norm = LogNorm(vmin=global_min, vmax=global_max)
    else:
        norm = Normalize(vmin=global_min, vmax=global_max)

    # Inicjalizacja wykresu z określoną siatką
    rows, cols = grid_shape
    fig, axes = plt.subplots(rows, cols, figsize=(5*cols, 4*rows))

    # Zamiana jednowymiarowej tablicy axes na dwuwymiarową, jeśli siatka jest większa niż 1x1
    if rows * cols > 1:
        axes = axes.ravel()

    # Przejście przez wszystkie tablice i rysowanie ich w odpowiednich podwykresach
    for i, arr in enumerate(arr_list):
        ax = axes[i] if rows * cols > 1 else axes

        # Obsługa osi i przekształceń
        title_out, xlab, ylab, extent, plot_arr = handle_plot_data(arr, main_title, bins_per_cm)

        # Rysowanie wykresu
        ax.set_xlabel(xlab)
        ax.set_ylabel(ylab)

        # Rysowanie mapy ciepła z wspólną normą dla wszystkich wykresów
        im = ax.imshow(plot_arr, cmap='viridis', norm=norm, interpolation="none", extent=extent)

    # Dodanie wspólnego colorbara po lewej stronie
    fig.subplots_adjust(right=0.85)
    cbar_ax = fig.add_axes([0.88, 0.1, 0.03, 0.8])  # pozycjonowanie paska kolorów
    fig.colorbar(im, cax=cbar_ax).set_label(r'$ 1/cm^2 $')

    # Ustawienie wspólnego tytułu nad wszystkimi wykresami
    if title_out is not None:
        fig.suptitle(title_out, fontsize=16, y=1.02)

    # Układanie wykresów
    plt.tight_layout(rect=[0, 0, 0.85, 0.95])  # Dostosowanie layoutu do paska kolorów i tytułu
    plt.show()




















def print_all_frames(all_cubes, frame_ids=None):
    frame_ids = list(range(0,8))+list(range(11,14))+[15] if frame_ids is None else frame_ids
    for c in range(len(all_cubes)):
        for i in frame_ids:
            bins_per_cm = all_cubes[0]['bins_per_1_cm']
            title = all_cubes[0]['frame_names'][i]
            arr = all_cubes[0]['frames'][i]
            arr2 = all_cubes[c]['frames'][i]
            arr1 = arr

            # check axis
            arr1 = arr1.copy()
            arr1[0:20, 0:20] = 20 # niskie wartości, początek (0,0)
            arr1[-20:-1, -20:-1] = 60 # wysokie wartości, koniec (1.5, 2.0)

            heatmap2d(arr1, bins_per_cm, title=title)
            # plot2_heatmap2d(arr1, arr2, title1=None, title2=None)


def print_all_frames_beside_benchmark(all_cubes, benchmark_cube, frame_ids=None):
    frame_ids = list(range(0,8))+list(range(11,14))+[15] if frame_ids is None else frame_ids
    for c in range(len(all_cubes)):
        for i in frame_ids:
            bins_per_cm = all_cubes[0]['bins_per_1_cm']
            title = all_cubes[0]['frame_names'][i]
            arr = all_cubes[0]['frames'][i]
            arr2 = all_cubes[c]['frames'][i]
            arr1 = arr

            # check axis
            arr1 = arr1.copy()
            arr1[0:20, 0:20] = 20 # niskie wartości, początek (0,0)
            arr1[-20:-1, -20:-1] = 60 # wysokie wartości, koniec (1.5, 2.0)

            cube_list = [arr1, benchmark_cube['cube']]
            heatmap2d_grid_shared_colorbar(cube_list, bins_per_cm, grid_shape=(1,2), main_title=title)









# print("wykresy - zestawienie do benchmarku")
# temp_cub_list = [cube for cube in all_cubes if 'benchmark' in cube['name']]
# print_all_frames_beside_benchmark(all_cubes, temp_cub_list[0])




print("wykresy - porównanie w siatce")
frame_id = 6
arr_list = [cube['frames'][frame_id] for cube in all_cubes[0:4]]
bins_per_cm = all_cubes[0]['bins_per_1_cm']
title = all_cubes[0]['frame_names'][frame_id]
titles = [title for _ in range(len(arr_list))]
heatmap2d_grid_shared_colorbar(arr_list, bins_per_cm, grid_shape=(2,2), main_title=title, norm="log")