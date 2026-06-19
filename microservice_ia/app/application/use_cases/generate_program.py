from app.domain.entities.exercise_context import ExerciseRecommendationContext
from app.domain.services.session_progression import compute_performance_history_score
from app.domain.ports.profile_repository import ProfileRepositoryPort
from app.domain.ports.program_generator import GenerateProgramInput, ProgramGeneratorPort
from app.domain.ports.program_repository import ProgramRepositoryPort


class GenerateProgramUseCase:
    def __init__(
        self,
        generator: ProgramGeneratorPort,
        programs: ProgramRepositoryPort,
        profiles: ProfileRepositoryPort,
    ) -> None:
        self._generator = generator
        self._programs = programs
        self._profiles = profiles

    def execute(self, data: GenerateProgramInput):
        profile_record = self._profiles.get(data.user_id)
        past_feedback = self._programs.list_feedback(data.user_id)
        performance_score = compute_performance_history_score(past_feedback)

        enriched = GenerateProgramInput(
            user_id=data.user_id,
            objectifs=data.objectifs,
            niveau=data.niveau,
            equipements=data.equipements,
            limitations=data.limitations or (profile_record.constraints.blessures_actives if profile_record else ()),
            disponibilite_minutes=data.disponibilite_minutes,
            seances_par_semaine=data.seances_par_semaine,
            longueur_programme_semaines=data.longueur_programme_semaines,
            profile=data.profile or (profile_record.profile if profile_record else None),
            constraints=profile_record.constraints if profile_record else data.constraints,
            performance_history_score=performance_score,
        )
        program = self._generator.generate(enriched)
        return self._programs.save_program(program)
