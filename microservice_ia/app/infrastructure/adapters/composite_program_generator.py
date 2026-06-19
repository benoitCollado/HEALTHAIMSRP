from app.domain.entities.exercise_context import ExerciseRecommendationContext
from app.domain.entities.program import SessionExercise, WorkoutProgram, WorkoutSession
from app.domain.entities.user_profile import UserProfile
from app.domain.ports.calorie_recommender import CalorieRecommenderPort
from app.domain.ports.exercise_recommender import ExerciseRecommenderPort
from app.domain.ports.program_generator import AdjustSessionInput, GenerateProgramInput, ProgramGeneratorPort


class CompositeProgramGenerator(ProgramGeneratorPort):
    """Génère un programme en combinant recommandations caloriques et exercices."""

    def __init__(
        self,
        calorie_recommender: CalorieRecommenderPort,
        exercise_recommender: ExerciseRecommenderPort,
    ) -> None:
        self._calorie_recommender = calorie_recommender
        self._exercise_recommender = exercise_recommender

    def generate(self, data: GenerateProgramInput) -> WorkoutProgram:
        profile = self._build_profile(data)
        calories = None
        detail_calorique = "Profil biométrique incomplet — calories non calculées."

        if profile.is_complete_for_calories():
            calorie_result = self._calorie_recommender.recommend(profile)
            calories = calorie_result.calories
            detail_calorique = calorie_result.detail

        exercise_result = self._exercise_recommender.recommend(
            profile,
            limit=4,
            context=self._context_from_input(data),
        )
        sessions = self._build_sessions(
            data.longueur_programme_semaines,
            data.seances_par_semaine,
            data.disponibilite_minutes,
            exercise_result.exercices,
            data.limitations,
        )
        current_id = sessions[0].id if sessions else None

        return WorkoutProgram(
            id=WorkoutProgram.new_id(),
            user_id=data.user_id,
            objectifs=data.objectifs,
            longueur_programme_semaines=data.longueur_programme_semaines,
            seances_par_semaine=data.seances_par_semaine,
            calories_recommandees=calories,
            detail_calorique=detail_calorique,
            sessions=tuple(sessions),
            session_courante_id=current_id,
        )

    def adjust(self, program: WorkoutProgram, data: AdjustSessionInput) -> WorkoutProgram:
        if not program.session_courante_id:
            return program

        updated_sessions: list[WorkoutSession] = []
        for session in program.sessions:
            if session.id != program.session_courante_id:
                updated_sessions.append(session)
                continue

            ajustements: list[str] = []
            duree = session.duree_minutes
            exercices = list(session.exercices)

            if data.temps_partiel_minutes and data.temps_partiel_minutes < duree:
                duree = data.temps_partiel_minutes
                ajustements.append(f"Durée réduite à {duree} min (temps partiel).")

            if data.fatigue >= 7:
                duree = max(15, int(duree * 0.7))
                exercices = exercices[: max(1, len(exercices) - 1)]
                ajustements.append("Volume réduit (fatigue élevée).")

            if data.douleur:
                exercices = [
                    ex
                    for ex in exercices
                    if ex.type_exercice in {"souplesse", "cardio"} or "étirement" in ex.nom_exercice.lower()
                ] or [
                    SessionExercise(
                        nom_exercice="Étirements doux",
                        type_exercice="souplesse",
                        duree_minutes=min(duree, 20),
                    )
                ]
                ajustements.append("Exercices adaptés (signalement de douleur).")

            updated_sessions.append(
                WorkoutSession(
                    id=session.id,
                    titre=f"{session.titre} (ajustée)",
                    duree_minutes=duree,
                    exercices=tuple(exercices),
                    statut="ajustee",
                    ajustements=tuple(ajustements),
                )
            )

        return WorkoutProgram(
            id=program.id,
            user_id=program.user_id,
            objectifs=program.objectifs,
            longueur_programme_semaines=program.longueur_programme_semaines,
            seances_par_semaine=program.seances_par_semaine,
            calories_recommandees=program.calories_recommandees,
            detail_calorique=program.detail_calorique,
            sessions=tuple(updated_sessions),
            session_courante_id=program.session_courante_id,
            created_at=program.created_at,
        )

    @staticmethod
    def _build_profile(data: GenerateProgramInput) -> UserProfile:
        if data.profile:
            return data.profile

        objectifs = set(data.objectifs)
        return UserProfile(
            age=30,
            sexe="H",
            taille_cm=175,
            poids_kg=70,
            niveau_activite=data.niveau,
            perte_de_poids="perte_de_poids" in objectifs or "perte" in objectifs,
            endurance="endurance" in objectifs,
            force="force" in objectifs,
            performance="performance" in objectifs,
        )

    @staticmethod
    def _build_sessions(
        longueur_semaines: int,
        seances_par_semaine: int,
        minutes: int,
        exercises,
        limitations: tuple[str, ...],
    ) -> list[WorkoutSession]:
        sessions: list[WorkoutSession] = []
        per_session = max(1, minutes // max(1, len(exercises)))

        for week in range(1, longueur_semaines + 1):
            for session_in_week in range(1, seances_par_semaine + 1):
                session_exercises = []
                for ex in exercises:
                    if limitations and ex.equipement and any(
                        lim.lower() in (ex.equipement or "").lower() for lim in limitations
                    ):
                        continue
                    session_exercises.append(
                        SessionExercise(
                            nom_exercice=ex.nom_exercice,
                            type_exercice=ex.type_exercice,
                            duree_minutes=per_session,
                            series=ex.recommended_sets or (3 if ex.type_exercice == "musculation" else None),
                            repetitions=12 if ex.type_exercice == "musculation" else None,
                        )
                    )
                if not session_exercises:
                    session_exercises.append(
                        SessionExercise(
                            nom_exercice="Marche rapide",
                            type_exercice="cardio",
                            duree_minutes=minutes,
                        )
                    )

                sessions.append(
                    WorkoutSession(
                        id=WorkoutSession.new_id(),
                        titre=f"Semaine {week} — Séance {session_in_week}",
                        duree_minutes=minutes,
                        exercices=tuple(session_exercises),
                    )
                )
        return sessions

    @staticmethod
    def _context_from_input(data: GenerateProgramInput) -> ExerciseRecommendationContext:
        limitation = "aucune"
        if data.limitations:
            limitation = data.limitations[0].lower().replace(" ", "_")

        preferred = "musculation"
        objectifs = set(data.objectifs)
        if "endurance" in objectifs:
            preferred = "running"
        elif "perte_de_poids" in objectifs or "perte" in objectifs:
            preferred = "hiit"
        elif "force" in objectifs or "performance" in objectifs:
            preferred = "musculation"

        return ExerciseRecommendationContext(
            desired_duration_min=data.disponibilite_minutes,
            equipment_available=data.equipements,
            physical_limitation=limitation,
            preferred_activity=preferred,
            performance_history_score=data.performance_history_score,
        )
