import cv2
import os
from concurrent.futures import ThreadPoolExecutor
import csv
import argparse


def parse_args():
    """
    Parse les arguments de la ligne de commande.
    """
    parser = argparse.ArgumentParser(description="Analyse la netteté des images dans un répertoire et exporte les résultats.")
    parser.add_argument('dir_path', type=str, help='Chemin du répertoire à analyser.')
    return parser.parse_args()


def to_csv(data, dir_path, filename="image_analysis_results.csv"):
    """
    Exporte les données vers un fichier CSV dans le sous-dossier spécifié.

    :param data: Liste de tuples contenant les données à écrire (chemin complet, nom du fichier, flou ou non, variance Laplacienne).
    :param dir_path: Chemin du sous-dossier où le fichier CSV sera créé.
    :param filename: Nom du fichier CSV à créer.
    """
    file_path = os.path.join(dir_path, filename)
    headers = ['Full Path', 'File Name', 'Is Blurry', 'Laplacian Variance']
    with open(file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        writer.writerows(data)
    print(f"Data successfully exported to {file_path}")


def get_fullpath_images_from_directory(dir_path, file_types=[".jpg", ".jpeg", ".png", ".tiff", ".NEF"]):
    """
    Liste tous les fichiers dans le répertoire donné avec les extensions spécifiées.

    :param dir_path: Chemin du répertoire à fouiller.
    :param file_types: Liste des extensions de fichiers à inclure (ex: ['.jpg', '.txt']).
    :return: Liste des chemins complets des fichiers correspondants.
    """
    file_list = []
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            if os.path.splitext(file)[1] in file_types:
                full_path = os.path.join(root, file)
                file_list.append(full_path)
    return file_list
def is_blurry(image_path, threshold=100.0, verbose=False):
    # Charger l'image en niveaux de gris
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    # Calculer la matrice Laplacienne
    laplacian_var = cv2.Laplacian(image, cv2.CV_64F).var()

    # Si la variance de la Laplacienne est inférieure au seuil, l'image est considérée comme floue
    if laplacian_var < threshold:
        if verbose:
            print(f"L'image est floue. Variance Laplacienne: {laplacian_var:.2f}")
        return True, laplacian_var
    else:
        if verbose:
            print(f"L'image est nette. Variance Laplacienne: {laplacian_var:.2f}")
        return False, laplacian_var


def analyze_images_blurriness(dir_path, file_types=[".jpg", ".jpeg", ".png", ".tiff", ".NEF"], threshold=100.0, sort=True, export_to_csv=True):
    """
    Analyse les images pour la netteté dans tous les sous-dossiers du répertoire donné et
    exporte les résultats en CSV dans chaque sous-dossier si nécessaire.

    :param dir_path: Chemin du répertoire principal.
    :param file_types: Types de fichiers à analyser.
    :param threshold: Seuil pour la détermination de l'état flou.
    :param sort: Booléen pour trier les résultats du plus flou au moins flou.
    :param export_to_csv: Booléen pour exporter les résultats en CSV.
    """
    for root, dirs, files in os.walk(dir_path):
        results = []
        images = [os.path.join(root, file) for file in files if os.path.splitext(file)[1] in file_types]
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = {executor.submit(is_blurry, img, threshold): img for img in images}
            for future in futures:
                image_path = futures[future]
                blurry, laplacian = future.result()
                file_name = os.path.basename(image_path)
                results.append((image_path, file_name, blurry, laplacian))
        if sort:
            results.sort(key=lambda x: x[3], reverse=False)
        if export_to_csv and results:
            to_csv(results, root)

if __name__ == "__main__":
    args = parse_args()  # Récupérer les arguments de la ligne de commande
    file_types = [".jpg", ".jpeg", ".png", ".tiff", ".NEF"]
    analyze_images_blurriness(args.dir_path, file_types)
    input("Appuyez sur Entrée pour fermer...")

