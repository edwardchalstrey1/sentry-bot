"""Configuration via environment variables."""
from enum import Enum

from pydantic import BaseSettings


class CameraLibrary(str, Enum):
    """Supported camera libraries."""

    PICAMERA = "picamera"
    OPENCV = "opencv"


class Settings(BaseSettings):
    """Environment variable settings."""

    camera_library: CameraLibrary
    control_turret: bool
    do_aiming: bool
    minimum_hue_target: int
    maximum_hue_target: int
    streaming_source: int
