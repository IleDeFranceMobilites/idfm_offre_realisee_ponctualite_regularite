import abc


class MesureType:
    ponctualite = "ponctualite"
    regularite = "regularite"


class Mesure(abc.ABC):
    @abc.abstractproperty
    def ligne(self) -> str:
        pass

    @abc.abstractproperty
    def nombre_theorique(self) -> str:
        pass

    @abc.abstractproperty
    def nombre_reel(self) -> str:
        pass

    @abc.abstractproperty
    def score_de_conformite(self) -> str:
        pass

    @abc.abstractproperty
    def taux_de_conformite(self) -> str:
        pass

    @abc.abstractproperty
    def taux_absence_de_donnees(self) -> str:
        pass

    @abc.abstractproperty
    def situation_inacceptable_types(self) -> list:
        pass

    @abc.abstractproperty
    def column_order(self) -> list:
        pass


class MesurePonctualite(Mesure):
    ligne = 'LIGNE'
    tag_frequence = 'TAG_FREQUENCE'
    arret = 'ARRET'
    sens = 'SENS'
    heure_theorique = 'HEURE_THEORIQUE'
    heure_reelle = 'HEURE_REELLE'
    is_terminus = 'IS_TERMINUS'
    frequence = 'FREQUENCE'
    difference_theorique = 'DIFFERENCE_THEORIQUE'
    resultat = 'RESULTAT'
    nombre_theorique = 'NOMBRE_PASSAGES_THEORIQUES'
    nombre_reel = 'NOMBRE_PASSAGES_REELS'
    score_de_conformite = 'SCORE_DE_CONFORMITE'
    situation_inacceptable_retard = 'SITUATION_INACCEPTABLE_RETARD'
    situation_inacceptable_avance = 'SITUATION_INACCEPTABLE_AVANCE'
    situation_inacceptable_sans_horaire_reel_attribue = 'SITUATION_INACCEPTABLE_THEORIQUE_SANS_HORAIRE_REEL_ATTRIBUE'
    situation_inacceptable_total = 'SITUATION_INACCEPTABLE_TOTAL'
    taux_de_conformite = 'TAUX_DE_CONFORMITE'
    taux_absence_de_donnees = 'TAUX_ABSENCE_DE_DONNEES'
    situation_inacceptable_types = [
        situation_inacceptable_retard,
        situation_inacceptable_avance,
        situation_inacceptable_sans_horaire_reel_attribue,
        situation_inacceptable_total,
    ]
    column_order = [
        ligne,
        nombre_theorique,
        nombre_reel,
        score_de_conformite,
        situation_inacceptable_retard,
        situation_inacceptable_avance,
        situation_inacceptable_sans_horaire_reel_attribue,
        situation_inacceptable_total,
        taux_de_conformite,
        taux_absence_de_donnees,
    ]


class Borne:
    inf = '_INF'
    sup = '_SUP'


class MesureRegularite(Mesure):
    ligne = 'LIGNE'
    arret = 'ARRET'
    sens = 'SENS'
    nombre_theorique = 'NOMBRE_PASSAGES_THEORIQUES'
    nombre_reel = 'NOMBRE_PASSAGES_REELS'
    heure_theorique = 'HEURE_THEORIQUE'
    heure_reelle = 'HEURE_REELLE'
    heure_theorique_inf = 'HEURE_THEORIQUE' + Borne.inf
    heure_theorique_sup = 'HEURE_THEORIQUE' + Borne.sup
    frequence = 'FREQUENCE'
    difference_theorique = 'DIFFERENCE_THEORIQUE'
    difference_reelle = 'DIFFERENCE_REELLE'
    difference_theorique_inf = 'DIFFERENCE_THEORIQUE' + Borne.inf
    difference_theorique_sup = 'DIFFERENCE_THEORIQUE' + Borne.sup
    resultat = 'RESULTAT'
    resultat_inf = 'RESULTAT' + Borne.inf
    resultat_sup = 'RESULTAT' + Borne.sup
    score_de_conformite = 'SCORE_DE_CONFORMITE'
    situation_inacceptable_train_de_bus = 'SITUATION_INACCEPTABLE_TRAIN_DE_BUS'
    situation_inacceptable_ecart_important = 'SITUATION_INACCEPTABLE_ECART_IMPORTANT'
    situation_inacceptable_total = 'SITUATION_INACCEPTABLE_TOTAL'
    taux_de_conformite = 'TAUX_DE_CONFORMITE'
    taux_absence_de_donnees = 'TAUX_ABSENCE_DE_DONNEES'
    situation_inacceptable_types = [
        situation_inacceptable_train_de_bus,
        situation_inacceptable_ecart_important,
        situation_inacceptable_total,
    ]
    column_order = [
        ligne,
        nombre_theorique,
        nombre_reel,
        score_de_conformite,
        situation_inacceptable_train_de_bus,
        situation_inacceptable_ecart_important,
        situation_inacceptable_total,
        taux_de_conformite,
        taux_absence_de_donnees,
    ]


MESURE_TYPE: dict[MesureType, Mesure] = {
    MesureType.ponctualite: MesurePonctualite,
    MesureType.regularite: MesureRegularite,
}


class FrequenceType:
    basse_frequence = 'BF'
    haute_frequence = 'HF'


class ComplianceType:
    compliant = 1.
    semi_compliant = {
        MesureType.ponctualite: {
            FrequenceType.haute_frequence: 0.75,
            FrequenceType.basse_frequence: 0.5,
        },
        MesureType.regularite: 0.65,
    }
    not_compliant = {
        MesureType.ponctualite: {
            FrequenceType.haute_frequence: 0.25,
            FrequenceType.basse_frequence: 0.,
        },
        MesureType.regularite: 0.,
    }

    # Ponctualité
    situation_inacceptable_retard = -1000000. - 0      # Un retard est le SI le moins pénalisant
    situation_inacceptable_avance = -1000000. - 100    # Un passage en avance est plus pénalisant qu'un retard
    situation_inacceptable_absence = -1000000. - 1000  # On cherche à assigner le plus de passages possible

    # Régularité
    situation_inacceptable_train_de_bus = -1.      # SI de trains de bus
    situation_inacceptable_faible_frequence = -2.  # SI d'interval trop important
