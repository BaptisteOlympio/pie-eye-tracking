from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class ArrayRequest(_message.Message):
    __slots__ = ("image", "dtype", "shape")
    IMAGE_FIELD_NUMBER: _ClassVar[int]
    DTYPE_FIELD_NUMBER: _ClassVar[int]
    SHAPE_FIELD_NUMBER: _ClassVar[int]
    image: bytes
    dtype: bytes
    shape: bytes
    def __init__(self, image: _Optional[bytes] = ..., dtype: _Optional[bytes] = ..., shape: _Optional[bytes] = ...) -> None: ...

class MessageResponse(_message.Message):
    __slots__ = ("message",)
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    message: bytes
    def __init__(self, message: _Optional[bytes] = ...) -> None: ...
