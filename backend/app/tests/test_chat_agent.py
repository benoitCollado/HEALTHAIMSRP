from app.chat_agent import should_call_microservice_ia


def test_should_call_microservice_for_calories():
    assert should_call_microservice_ia("Combien de calories par jour ?")


def test_should_call_microservice_for_exercises():
    assert should_call_microservice_ia("Quels exercices pour la musculation ?")


def test_should_not_call_microservice_for_generic_question():
    assert not should_call_microservice_ia("A quoi sert HealthAI MSPR ?")
