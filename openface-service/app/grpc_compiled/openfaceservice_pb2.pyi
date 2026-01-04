from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class Frame(_message.Message):
    __slots__ = ("frame", "dtype", "shape")
    FRAME_FIELD_NUMBER: _ClassVar[int]
    DTYPE_FIELD_NUMBER: _ClassVar[int]
    SHAPE_FIELD_NUMBER: _ClassVar[int]
    frame: bytes
    dtype: bytes
    shape: bytes
    def __init__(self, frame: _Optional[bytes] = ..., dtype: _Optional[bytes] = ..., shape: _Optional[bytes] = ...) -> None: ...

class Landmark(_message.Message):
    __slots__ = ("landmark",)
    LANDMARK_FIELD_NUMBER: _ClassVar[int]
    landmark: bytes
    def __init__(self, landmark: _Optional[bytes] = ...) -> None: ...
