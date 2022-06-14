from common.auth.pkce.pkce_auth_service import generate_code_verifier, generate_code_challenge


def test_generate_code_verifier():
    verifier_1 = generate_code_verifier(length=100)
    assert len(verifier_1) == 100
    verifier_2 = generate_code_verifier(length=100)
    assert verifier_1 != verifier_2


def test_code_challenge():
    verifier = b"abcd"
    code_challenge = generate_code_challenge(verifier)
    assert code_challenge == b"iNQmb9TmM40TuEX88olXnSCciXgjuSF9o-Fhk28DFYk"
