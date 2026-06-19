from datetime import datetime

from bson import ObjectId
from pymongo.database import Database

from app.domain.entities.profile_record import ProfileConstraints, UserProfileRecord
from app.domain.entities.program import SessionFeedbackRecord, WorkoutProgram, WorkoutSession
from app.domain.entities.user_profile import UserProfile
from app.domain.ports.profile_repository import ProfileRepositoryPort
from app.domain.ports.program_repository import ProgramRepositoryPort
from app.domain.services.session_progression import apply_session_completion
from app.infrastructure.persistence.mongodb.client import COLLECTION_SESSION_LOGS, COLLECTION_USERS, COLLECTION_WORKOUT_PLANS
from app.infrastructure.persistence.mongodb.mappers import (
    constraints_to_document,
    document_to_program,
    document_to_user_profile_record,
    feedback_to_session_log,
    program_to_document,
    session_log_to_feedback,
    user_profile_to_document,
)


class MongoProfileRepository(ProfileRepositoryPort):
    def __init__(self, db: Database) -> None:
        self._users = db[COLLECTION_USERS]
        self._users.create_index("user_ref", unique=True)

    def get(self, user_id: int) -> UserProfileRecord | None:
        doc = self._users.find_one({"user_ref": user_id})
        if doc is None:
            return None
        return document_to_user_profile_record(doc)

    def upsert_profile(self, user_id: int, profile: UserProfile) -> UserProfileRecord:
        existing = self._users.find_one({"user_ref": user_id})
        constraints = ProfileConstraints()
        if existing:
            constraints = ProfileConstraints(
                equipements_dispo=tuple(existing.get("constraints", {}).get("equipment_available", [])),
                blessures_actives=tuple(existing.get("constraints", {}).get("physical_limitations", [])),
            )

        payload = user_profile_to_document(user_id, profile, constraints)
        if existing is None:
            payload["created_at"] = payload["updated_at"]

        self._users.update_one({"user_ref": user_id}, {"$set": payload}, upsert=True)
        record = self.get(user_id)
        assert record is not None
        return record

    def update_constraints(self, user_id: int, constraints: ProfileConstraints) -> UserProfileRecord:
        existing = self._users.find_one({"user_ref": user_id})
        payload = constraints_to_document(constraints)
        if existing is None:
            payload["user_ref"] = user_id
            payload["created_at"] = payload["updated_at"]
        self._users.update_one({"user_ref": user_id}, {"$set": payload}, upsert=True)
        record = self.get(user_id)
        if record is None:
            return UserProfileRecord(user_id=user_id, constraints=constraints, updated_at=payload["updated_at"])
        return UserProfileRecord(
            user_id=user_id,
            profile=record.profile,
            constraints=constraints,
            updated_at=payload["updated_at"],
        )

    def get_user_oid(self, user_id: int) -> ObjectId | None:
        doc = self._users.find_one({"user_ref": user_id}, {"_id": 1})
        return doc["_id"] if doc else None

    def ensure_user_oid(self, user_id: int) -> ObjectId:
        oid = self.get_user_oid(user_id)
        if oid:
            return oid
        result = self._users.insert_one({"user_ref": user_id, "created_at": datetime.utcnow()})
        return result.inserted_id


class MongoProgramRepository(ProgramRepositoryPort):
    def __init__(self, db: Database, profiles: MongoProfileRepository) -> None:
        self._plans = db[COLLECTION_WORKOUT_PLANS]
        self._logs = db[COLLECTION_SESSION_LOGS]
        self._profiles = profiles
        self._plans.create_index([("user_ref", 1), ("status", 1)])
        self._logs.create_index([("user_ref", 1), ("session_date", -1)])

    def save_program(self, program: WorkoutProgram) -> WorkoutProgram:
        user_oid = self._profiles.ensure_user_oid(program.user_id)
        self._plans.update_many(
            {"user_ref": program.user_id, "status": "active"},
            {"$set": {"status": "archived"}},
        )
        doc = program_to_document(program, user_oid)
        self._plans.update_one({"plan_ref": program.id}, {"$set": doc}, upsert=True)
        return program

    def get_active_program(self, user_id: int) -> WorkoutProgram | None:
        doc = self._plans.find_one({"user_ref": user_id, "status": "active"}, sort=[("generated_at", -1)])
        if doc is None:
            return None
        return document_to_program(doc)

    def get_session(self, session_id: str) -> WorkoutProgram | None:
        doc = self._plans.find_one({"sessions.session_id": session_id})
        if doc is None:
            return None
        return document_to_program(doc)

    def update_program(self, program: WorkoutProgram) -> WorkoutProgram:
        return self.save_program(program)

    def save_feedback(self, feedback: SessionFeedbackRecord) -> SessionFeedbackRecord:
        program = self.get_session(feedback.session_id)
        if program is None:
            return feedback

        plan_doc = self._plans.find_one({"plan_ref": program.id})
        user_oid = plan_doc["user_id"] if plan_doc else self._profiles.ensure_user_oid(feedback.user_id)
        plan_oid = plan_doc["_id"] if plan_doc else ObjectId()

        session = next((s for s in program.sessions if s.id == feedback.session_id), None)
        total_exercises = len(session.exercices) if session else 0
        log_doc = feedback_to_session_log(feedback, user_oid, plan_oid, total_exercises)
        self._logs.insert_one(log_doc)

        updated_program = apply_session_completion(program, feedback.session_id)
        self.save_program(updated_program)
        return feedback

    def list_feedback(self, user_id: int, date_from=None, date_to=None) -> list[SessionFeedbackRecord]:
        query: dict = {"user_ref": user_id}
        if date_from or date_to:
            query["session_date"] = {}
            if date_from:
                query["session_date"]["$gte"] = date_from
            if date_to:
                query["session_date"]["$lte"] = date_to

        docs = self._logs.find(query).sort("session_date", -1)
        return [session_log_to_feedback(doc) for doc in docs]
