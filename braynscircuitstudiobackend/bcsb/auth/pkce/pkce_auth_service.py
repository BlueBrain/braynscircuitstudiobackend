"""
const CODE_VERIFIER_LENGTH = 128
const CODE_VERIFIER_CHARACTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'

export function generateCodeChallenge(verifier: string): string {
    return base64URL(CryptoJS.SHA256(verifier))
}

export function generateCodeVerifier(): string {
    let result = ''
    const charactersLength = CODE_VERIFIER_CHARACTERS.length
    for (let i = 0; i < CODE_VERIFIER_LENGTH; i++) {
        result += CODE_VERIFIER_CHARACTERS.charAt(Math.floor(Math.random() * charactersLength))
    }
    return result
}

"""
import re
from base64 import urlsafe_b64encode
from hashlib import sha256
from os import urandom

CODE_VERIFIER_LENGTH = 128


def generate_code_challenge(verifier: bytes) -> bytes:
    sha_hash = sha256(verifier).digest()
    b64 = urlsafe_b64encode(sha_hash)
    result = re.sub(rb"=", b"", b64)
    return result


def generate_code_verifier(length: int = CODE_VERIFIER_LENGTH) -> bytes:
    return urandom(length)
