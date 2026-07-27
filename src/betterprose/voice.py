from __future__ import annotations

from importlib.resources import files

import yaml

from betterprose.models import VoiceProfile, VoiceRegister

AUTO_REGISTER = "auto"


def voice_names() -> list[str]:
    voice_dir = files("betterprose").joinpath("voices")
    return sorted(
        item.name.removesuffix(".yaml")
        for item in voice_dir.iterdir()
        if item.name.endswith(".yaml")
    )


def load_voice_profile(name: str) -> VoiceProfile:
    resource = files("betterprose").joinpath("voices", f"{name}.yaml")
    if not resource.is_file():
        available = ", ".join(voice_names())
        raise ValueError(f"Unknown voice '{name}'. Available voices: {available}")
    profile = VoiceProfile.model_validate(yaml.safe_load(resource.read_text(encoding="utf-8")))
    validate_voice_profile(profile)
    return profile


def register_names(profile: VoiceProfile, *, include_auto: bool = True) -> list[str]:
    names = [register.id for register in profile.registers]
    return [AUTO_REGISTER, *names] if include_auto else names


def resolve_register(profile: VoiceProfile, name: str) -> VoiceRegister | None:
    if name == AUTO_REGISTER:
        return None
    for register in profile.registers:
        if register.id == name:
            return register
    available = ", ".join(register_names(profile))
    raise ValueError(
        f"Unknown register '{name}' for voice '{profile.name}'. Available registers: {available}"
    )


def render_voice_instructions(profile: VoiceProfile, register_name: str) -> str:
    selected = resolve_register(profile, register_name)
    if selected is None:
        register_text = "\n\n".join(
            _render_register(register) for register in profile.registers
        )
        selection = (
            "Select the register that best fits the supplied genre, audience, and purpose. "
            "Do not mix their visible formatting conventions without a rhetorical reason."
        )
    else:
        register_text = _render_register(selected)
        selection = f"Use only the {selected.label} register unless the user directs otherwise."

    return (
        f"Voice profile: {profile.label} v{profile.version}\n"
        f"Description: {profile.description}\n"
        f"Persona and stance: {profile.persona}\n"
        f"Register selection: {selection}\n\n"
        f"Registers:\n{register_text}\n\n"
        f"Shared principles:\n{_bullets(profile.shared_principles)}\n\n"
        f"Sentence, paragraph, and presentation mechanics:\n{_bullets(profile.mechanics)}\n\n"
        f"Spelling:\n{_bullets(profile.spelling)}\n\n"
        f"Preferred vocabulary fields:\n{_bullets(profile.vocabulary.prefer)}\n\n"
        f"Avoid:\n{_bullets(profile.vocabulary.avoid)}\n\n"
        f"Non-negotiable safeguards:\n{_bullets(profile.safeguards)}\n\n"
        "Calibration examples:\n"
        + "\n\n".join(
            f"Not this voice: {example.not_voice}\n"
            f"In this voice: {example.in_voice}"
            for example in profile.calibration_examples
        )
    )


def validate_voice_profile(profile: VoiceProfile) -> None:
    if not profile.registers:
        raise ValueError(f"Voice '{profile.name}' must define at least one register.")
    register_ids = [register.id for register in profile.registers]
    if AUTO_REGISTER in register_ids:
        raise ValueError(f"Voice '{profile.name}' cannot define '{AUTO_REGISTER}' as a register.")
    if len(register_ids) != len(set(register_ids)):
        raise ValueError(f"Voice '{profile.name}' contains duplicate register IDs.")
    if not profile.shared_principles or not profile.safeguards:
        raise ValueError(
            f"Voice '{profile.name}' must define shared principles and safeguards."
        )


def _render_register(register: VoiceRegister) -> str:
    return (
        f"{register.id} — {register.label}\n"
        f"Use when: {register.use_when}\n"
        f"{_bullets(register.instructions)}"
    )


def _bullets(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)
