from enum import Enum


class ConfigProperty(str, Enum):
    ApiKey = 'ApiKey'
    ApiId = 'ApiId'
    ApiHash = 'ApiHash'
    SessionName = 'SessionName'
    BotConfig = 'BotConfig'
    ForwardMessage = 'ForwardMessage'
    LogFile = 'LogFile'
    LogLevel = 'LogLevel'
    LogName = 'LogName'
    LogFormat = 'LogFormat'


class LogLevel(Enum):
    Debug = 0
    Info = 1
    Warning = 2
    Error = 4
    Critical = 5


class Commands(str, Enum):
    Command = '/command'
    Delay = '/delay'
    GenerateImage = '/image'
