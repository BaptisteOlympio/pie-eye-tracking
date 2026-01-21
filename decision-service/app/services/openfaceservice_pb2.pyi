from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

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

class LandmarkTuple(_message.Message):
    __slots__ = ("x", "y")
    X_FIELD_NUMBER: _ClassVar[int]
    Y_FIELD_NUMBER: _ClassVar[int]
    x: int
    y: int
    def __init__(self, x: _Optional[int] = ..., y: _Optional[int] = ...) -> None: ...

class Landmark(_message.Message):
    __slots__ = ("landmark",)
    LANDMARK_FIELD_NUMBER: _ClassVar[int]
    landmark: _containers.RepeatedCompositeFieldContainer[LandmarkTuple]
    def __init__(self, landmark: _Optional[_Iterable[_Union[LandmarkTuple, _Mapping]]] = ...) -> None: ...
