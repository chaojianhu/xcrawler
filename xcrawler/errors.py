"""
    exceptions
    ~~~~~~~~~~~~~~
    
    :copyright: (c) 2017 by 0xE8551CCB.
    :license: MIT, see LICENSE for more details.
"""


class Error(Exception):
    pass


class InvalidURLError(Error):
    pass


class InvalidPipelineError(Error):
    pass


class InvalidExtensionError(Error):
    pass


class DroppedItem(Error):
    pass


class DroppedRequest(Error):
    pass


class DroppedResponse(Error):
    pass
