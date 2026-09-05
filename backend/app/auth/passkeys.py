import base64
import json

from webauthn import (
    generate_authentication_options,
    generate_registration_options,
    options_to_json,
    verify_authentication_response,
    verify_registration_response,
)
from webauthn.helpers.structs import (
    AttestationConveyancePreference,
    AuthenticatorSelectionCriteria,
    ResidentKeyRequirement,
    UserVerificationRequirement,
    PublicKeyCredentialDescriptor,
)


def b64url(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def registration_options(rp_id: str, handle: str, user_id: bytes, challenge: bytes, existing_ids=()) -> dict:
    options = generate_registration_options(
        rp_id=rp_id,
        rp_name="Cadence",
        user_name=handle,
        user_display_name="Cadence learner",
        user_id=user_id,
        challenge=challenge,
        exclude_credentials=[PublicKeyCredentialDescriptor(id=base64.urlsafe_b64decode(value + '=' * (-len(value) % 4))) for value in existing_ids],
        attestation=AttestationConveyancePreference.NONE,
        authenticator_selection=AuthenticatorSelectionCriteria(
            resident_key=ResidentKeyRequirement.REQUIRED,
            require_resident_key=True,
            user_verification=UserVerificationRequirement.PREFERRED,
        ),
    )
    return json.loads(options_to_json(options))


def authentication_options(rp_id: str, challenge: bytes) -> dict:
    options = generate_authentication_options(
        rp_id=rp_id,
        challenge=challenge,
        user_verification=UserVerificationRequirement.PREFERRED,
    )
    return json.loads(options_to_json(options))


def verify_registration(credential: dict, challenge: bytes, rp_id: str, origin: str):
    return verify_registration_response(
        credential=credential,
        expected_challenge=challenge,
        expected_rp_id=rp_id,
        expected_origin=origin,
        require_user_verification=False,
    )


def verify_authentication(credential: dict, challenge: bytes, rp_id: str, origin: str, public_key: bytes, sign_count: int):
    return verify_authentication_response(
        credential=credential,
        expected_challenge=challenge,
        expected_rp_id=rp_id,
        expected_origin=origin,
        credential_public_key=public_key,
        credential_current_sign_count=sign_count,
        require_user_verification=False,
    )
