from enum import Enum


class ConfigProperty(str, Enum):
    ApiKey = 'ApiKey'
    ApiId = 'ApiId'
    ApiHash = 'ApiHash'
    MonitoredChannels = 'MonitoredChannels'
    TargetChannel = 'TargetChannel'
