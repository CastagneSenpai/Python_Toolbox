# ====================================================================================================
# Développeur : Romain Castagné
# Société : CGI
#
# Version : 1
# Date : 2 juillet 2024
#
# Description :
# Ce module contient la fonction print_progress_bar, qui affiche une barre de progression textuelle dans la console.
# Elle prend en charge les paramètres suivants :
#
#     - iteration : Nombre d'itérations complétées jusqu'à présent.
#     - total : Nombre total d'itérations prévues.
#     - prefix (optionnel) : Préfixe affiché avant la barre de progression.
#     - prefix_width (optionnel) : Largeur maximale du préfixe.
#     - length (optionnel) : Longueur totale de la barre de progression en caractères.
#
# Exemple d'utilisation :
#
#     print_progress_bar(50, 100, prefix='Progress', prefix_width=15, length=40)
#
#     Cela affichera :
#     Progress |██████████------| 50.0%
# ====================================================================================================


def print_progress_bar(iteration, total, prefix='Progress...', prefix_width=50, length=100):
    percent = f"{100 * (iteration / float(total)):.1f}"
    filled_length = int(length * iteration // total)
    bar = '█' * filled_length + '-' * (length - filled_length)
    truncated_prefix = (prefix[:prefix_width - 3] + '...') if len(prefix) > prefix_width else prefix.ljust(prefix_width)
    print(f'\r{truncated_prefix} |{bar}| {percent}%', end='\r')
    if iteration == total:
        print()
