import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm, Normalize

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
        ax.set_xlabel(xlab, fontsize=14)
        ax.set_ylabel(ylab, fontsize=14)

        # Rysowanie mapy ciepła z wspólną normą dla wszystkich wykresów
        im = ax.imshow(plot_arr, cmap='viridis', norm=norm, interpolation="none", extent=extent)

        # Zwiększenie rozmiaru czcionek na osiach
        ax.tick_params(axis='both', which='major', labelsize=12)

    # Dodanie wspólnego colorbara po prawej stronie
    fig.subplots_adjust(left=0.1, right=0.85, wspace=0.05, hspace=0.2)  # Minimalny odstęp między wykresami
    cbar_ax = fig.add_axes([0.88, 0.1, 0.03, 0.8])  # Zmniejszenie odstępu między wykresami a colorbar
    cb = fig.colorbar(im, cax=cbar_ax)
    cb.set_label(r'$ 1/cm^2 $', fontsize=14)  # Etykieta paska kolorów
    cb.ax.tick_params(labelsize=14)  # Zwiększenie czcionki skali na colorbar

    # Ustawienie wspólnego tytułu nad wszystkimi wykresami, wyżej, aby nie nachodził na wykresy
    if main_title is not None:
        fig.suptitle(main_title, fontsize=20, y=1.05)  # Przesunięcie tytułu wyżej

    plt.show()

def handle_plot_data(arr, bins_per_cm):
    """
    Funkcja pomocnicza do obsługi różnych przypadków osi i przekształceń
    """
    xlab = "x [cm]"
    ylab = "y [cm]"
    plot_arr = arr
    extent = [0, arr.shape[0]/bins_per_cm, 0, arr.shape[1]/bins_per_cm]
    
    return xlab, ylab, extent, plot_arr
