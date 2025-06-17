from setuptools import setup, find_packages

setup(
    name="voice_agent",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'flask>=3.0.0',
        'openai>=1.0.0',
        'python-dotenv>=1.0.0',
        'SpeechRecognition>=3.10.0',
        'pyaudio>=0.2.13',
        'gTTS>=2.3.2',
        'playsound>=1.3.0'
    ],
) 