from enum import Enum


class ConfigProperty(str, Enum):
    ApiKey = 'ApiKey'
    ApiId = 'ApiId'
    ApiHash = 'ApiHash'
    SessionName = 'SessionName'
    RoleFile = 'RoleFile'
    ChannelsFile = 'ChannelsFile'
    ForwardMessage = 'ForwardMessage'


class LogLevel(Enum):
    Debug = 0
    Info = 1
    Warning = 2
    Error = 4
    Critical = 5
