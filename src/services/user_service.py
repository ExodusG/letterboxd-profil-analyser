from src.db.queries.qr_user import *

class UserService:

    def get_all_mean(self):
        return get_global_stats()
    
    def get_all_means(self) :
        # Récupère les données de la feuille "profiles_stats" au format DataFrame pandas
        extraction = self.get_all_mean()

        res = {}
        res["Consommateur"] = round(extraction["nb_films_vus"])
        res["Explorateur"] = round(extraction["ratio_peu_vus"], 2)*100
        res["Consensuel"] = round(extraction["moyenne_diff_rating"], 3)

        # Pour la colonne "ratio_par_genre", on récupère le JSON de la première ligne
        ratio_dict = extraction["ratio_par_genre"]
        # Extraire uniquement le nom du premier genre (première clé) apparaissant dans le JSON
        res["Éclectique"] = next(iter(ratio_dict.keys()))

        res["Actif"] = round(extraction["nb_interactions"])

        return res

    def add_profiles_to_db(self, profile, radar_stats):
            """ Ajoute ou met à jour les scores d'un profil dans la base de données"""
            add_profile_to_stats(profile, radar_stats)

    def get_all_user_stats(self):
        return get_user_stats()