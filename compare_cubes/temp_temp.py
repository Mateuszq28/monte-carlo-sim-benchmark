def detect_and_split_image_with_vertical_trim(image_path, output_path, gap_threshold=20, pixel_threshold=220):
    """
    Funkcja wczytuje obraz, wykrywa poziome przerwy szersze niż gap_threshold, a w dolnej części
    obrazu wykrywa białe kolumny pionowe powyżej pixel_threshold i zmniejsza je do 10% ich pierwotnej szerokości.
    Następnie łączy górną i dolną część w jeden obraz.

    Parametry:
    - image_path: ścieżka do pliku wejściowego .png
    - output_path: ścieżka do zapisu wynikowego obrazu
    - gap_threshold: minimalna szerokość przerwy, aby została uznana za "przerwę"
    - pixel_threshold: próg jasności dla wykrywania białych pikseli (im mniejsza wartość, tym większa czułość)
    """
    
    # Wczytanie obrazu
    img = Image.open(image_path)
    img_color = img.copy()  # Zachowanie oryginalnego obrazu w kolorze
    img_gray = img.convert("L")  # Konwersja do skali szarości tylko dla operacji detekcji
    img_array = np.array(img_gray)  # Konwersja do tablicy numpy

    # Szukamy poziomych przerw (obszarów, gdzie piksele są "białe" lub bardzo jasne na całej szerokości)
    horizontal_sum = np.sum(img_array > pixel_threshold, axis=1)  # Liczymy piksele jaśniejsze niż pixel_threshold
    img_width = img_array.shape[1]

    # Zwiększamy dokładność wykrywania przerw
    gaps = np.where(horizontal_sum == img_width)[0]  # Wiersze, gdzie cała szerokość wiersza jest biała

    # Szukamy linii, gdzie przerwa jest większa niż gap_threshold
    large_gaps = []
    current_gap = []
    for i in range(1, len(gaps)):
        if gaps[i] - gaps[i-1] > 1:  # Kiedy przerwa między kolejnymi białymi liniami jest większa niż 1
            if len(current_gap) > gap_threshold:  # Jeśli przerwa ma odpowiednią szerokość
                large_gaps.append(current_gap)
            current_gap = []  # Resetujemy przerwę
        current_gap.append(gaps[i])

    if len(current_gap) > gap_threshold:
        large_gaps.append(current_gap)

    if not large_gaps:
        raise ValueError("Nie znaleziono żadnej przerwy większej niż threshold.")

    # Wybieramy pierwszą dużą przerwę
    first_large_gap = large_gaps[0]
    gap_start = first_large_gap[0]
    gap_end = first_large_gap[-1]

    # Dzielimy obraz na górną i dolną część
    top_part = img_color.crop((0, 0, img.width, gap_start))
    bottom_part = img_color.crop((0, gap_end, img.width, img.height))
    bottom_array = np.array(bottom_part.convert("L"))  # Skala szarości dla dolnej części

    # Szukamy pionowych białych kolumn TYLKO w dolnej części obrazu
    vertical_sum = np.sum(bottom_array > pixel_threshold, axis=0)  # Sumujemy piksele jaśniejsze niż próg w każdej kolumnie
    white_columns = np.where(vertical_sum >= bottom_part.height * 1.0)[0]  # Kolumny, które mają powyżej 95% białych pikseli

    # Tworzymy nową listę kolumn, gdzie białe kolumny zostaną zmniejszone do 10% szerokości
    reduced_columns = []
    i = 0
    while i < bottom_part.width:
        if i in white_columns:
            # Zmniejszamy szerokość białych kolumn do 10%
            col_start = i
            col_end = i
            while col_end < bottom_part.width and col_end in white_columns:
                col_end += 1
            # Zostawiamy tylko 10% szerokości
            reduced_width = max(1, int(0.1 * (col_end - col_start)))
            reduced_columns.append(bottom_part.crop((col_start, 0, col_start + reduced_width, bottom_part.height)))
            i = col_end  # Przeskakujemy białe kolumny
        else:
            # Normalna kolumna
            reduced_columns.append(bottom_part.crop((i, 0, i + 1, bottom_part.height)))
            i += 1

    # Łączymy wszystkie kolumny w nowy obraz dla dolnej części
    new_bottom_width = sum([col.width for col in reduced_columns])
    reduced_bottom_part = Image.new('RGB', (new_bottom_width, bottom_part.height))
    
    x_offset = 0
    for col in reduced_columns:
        reduced_bottom_part.paste(col, (x_offset, 0))
        x_offset += col.width

    # Dopasowanie szerokości górnej części do szerokości dolnej części
    top_part_width = top_part.width
    width_diff = top_part_width - new_bottom_width

    if width_diff > 0:
        # Przycinamy górną część po bokach, aby dopasować do dolnej części
        left_crop = width_diff // 2
        right_crop = width_diff - left_crop
        new_top_part = top_part.crop((left_crop, 0, top_part_width - right_crop, top_part.height))
    else:
        # Jeśli szerokość górnej części jest mniejsza lub równa, nie przycinamy
        new_top_part = top_part

    # Łączenie górnej i dolnej części
    final_img = Image.new('RGB', (new_bottom_width, new_top_part.height + reduced_bottom_part.height))
    final_img.paste(new_top_part, (0, 0))
    final_img.paste(reduced_bottom_part, (0, new_top_part.height))

    # Wyświetlanie i zapisywanie obrazu
    final_img.show()
    final_img.save(output_path)
    print(f"Wynikowy obraz zapisany do {output_path}")




# Przykład użycia
detect_and_split_image_with_vertical_trim('chart4_img/chart4.png', 'chart4_img/output_combined.png', gap_threshold=16, pixel_threshold=220)
