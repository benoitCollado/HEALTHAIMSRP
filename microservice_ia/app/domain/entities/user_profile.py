from dataclasses import dataclass


@dataclass(frozen=True)
class UserProfile:
    age: int
    sexe: str
    taille_cm: float
    poids_kg: float
    niveau_activite: int
    perte_de_poids: bool = False
    performance: bool = False
    endurance: bool = False
    force: bool = False

    def is_complete_for_calories(self) -> bool:
        return self.age > 0 and self.taille_cm > 0 and self.poids_kg > 0
