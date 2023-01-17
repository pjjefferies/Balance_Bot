#! /usr/bin/python3

import pyttsx3

SPEED_MIN = 25
SPEED_MAX = 300
VOLUME_MIN = 0
VOLUME_MAX = 1.0


class RobotVoice:
    def __init__(self, sex: str = "male", rate: int = 200, volume: float = 1.0):
        self._voice = pyttsx3.init()
        self.sex = sex if sex in ["male", "female"] else "male"
        self.rate = rate if rate >= SPEED_MIN and rate <= SPEED_MAX else 200
        self.volume = (
            volume if volume >= VOLUME_MIN and volume <= VOLUME_MAX else VOLUME_MAX
        )

    @property
    def sex(self) -> str:
        for voice in self._voice.getProperty("voices"):
            if self._voice.getProperty("voice") == voice.id:
                break
        return voice.gender if voice.gender is not None else "None"

    @sex.setter
    def sex(self, value: str) -> None:
        if value == "male":
            self._voice.setProperty("voice", self._voice.getProperty("voices")[0].id)
        elif value == "female":
            self._voice.setProperty("voice", self._voice.getProperty("voices")[1].id)

    @property
    def rate(self) -> int:
        return self._voice.getProperty("rate")

    @rate.setter
    def rate(self, value: int) -> None:
        value = max(value, SPEED_MIN)
        value = min(value, SPEED_MAX)
        self._voice.setProperty("rate", value)

    @property
    def volume(self) -> int:
        return self._voice.getProperty("volume")

    @volume.setter
    def volume(self, value: float) -> None:
        value = max(value, VOLUME_MIN)
        value = min(value, VOLUME_MAX)
        self._voice.setProperty("volume", value)

    def say(self, text: str = "Hello, world!"):
        self._voice.say(text)
        self._voice.runAndWait()
