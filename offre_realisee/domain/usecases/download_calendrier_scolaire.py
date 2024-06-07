from offre_realisee.domain.entities.calendrier_scolaire.filter_calendrier_scolaire import filter_calendrier_scolaire
from offre_realisee.domain.port.calendrier_scolaire_source_handler import CalendrierScolaireSourceHandler
from offre_realisee.domain.port.calendrier_scolaire_file_system_handler import CalendrierScolaireFileSystemHandler


def download_calendrier_scolaire(calendrier_scolaire_source_handler: CalendrierScolaireSourceHandler,
                                 file_system_handler: CalendrierScolaireFileSystemHandler) -> None:
    df_calendrier_scolaire = calendrier_scolaire_source_handler.get_calendrier_scolaire()
    filtered_calendrier_scolaire = filter_calendrier_scolaire(df_calendrier_scolaire)
    file_system_handler.save_calendrier_scolaire(filtered_calendrier_scolaire)
