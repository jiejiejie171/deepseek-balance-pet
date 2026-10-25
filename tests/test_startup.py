import sys

from deepseek_pet import startup


def test_startup_command_frozen(monkeypatch):
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "executable", r"C:\Apps\DeepSeekPet\DeepSeekPet.exe")
    assert startup.startup_command() == r'"C:\Apps\DeepSeekPet\DeepSeekPet.exe"'


def test_startup_command_source(monkeypatch):
    monkeypatch.delattr(sys, "frozen", raising=False)
    monkeypatch.setattr(sys, "executable", r"D:\Python\python.exe")
    assert startup.startup_command().endswith("-m deepseek_pet")
