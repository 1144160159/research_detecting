# Copyright 2020 Flower Labs GmbH. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""ProtoBuf serialization and deserialization."""

from flwr.common.logger import log
from logging import INFO, WARN,DEBUG
from typing import Any, Dict, List, MutableMapping, OrderedDict, Type, TypeVar, cast

from google.protobuf.message import Message as GrpcMessage

# pylint: disable=E0611
from flwr.proto.error_pb2 import Error as ProtoError
from flwr.proto.node_pb2 import Node
from flwr.proto.recordset_pb2 import Array as ProtoArray
from flwr.proto.recordset_pb2 import BoolList, BytesList
from flwr.proto.recordset_pb2 import ConfigsRecord as ProtoConfigsRecord
from flwr.proto.recordset_pb2 import ConfigsRecordValue as ProtoConfigsRecordValue
from flwr.proto.recordset_pb2 import DoubleList
from flwr.proto.recordset_pb2 import MetricsRecord as ProtoMetricsRecord
from flwr.proto.recordset_pb2 import MetricsRecordValue as ProtoMetricsRecordValue
from flwr.proto.recordset_pb2 import ParametersRecord as ProtoParametersRecord
from flwr.proto.recordset_pb2 import RecordSet as ProtoRecordSet
from flwr.proto.recordset_pb2 import Sint64List, StringList
from flwr.proto.task_pb2 import Task, TaskIns, TaskRes
from flwr.proto.transport_pb2 import (
    ClientMessage,
    Code,
    Parameters,
    Reason,
    Scalar,
    ServerMessage,
    Status,
)

# pylint: enable=E0611
from . import Array, ConfigsRecord, MetricsRecord, ParametersRecord, RecordSet, typing
from .message import Error, Message, Metadata
from .record.typeddict import TypedDict

#  === Parameters message ===


def parameters_to_proto(parameters: typing.Parameters) -> Parameters:
    """Serialize `Parameters` to ProtoBuf."""
   
    return Parameters(tensors=parameters.tensors, tensor_type=parameters.tensor_type)


def parameters_from_proto(msg: Parameters) -> typing.Parameters:
    """Deserialize `Parameters` from ProtoBuf."""
    tensors: List[bytes] = list(msg.tensors)
    return typing.Parameters(tensors=tensors, tensor_type=msg.tensor_type)


#  === ReconnectIns message ===


def reconnect_ins_to_proto(ins: typing.ReconnectIns) -> ServerMessage.ReconnectIns:
    """Serialize `ReconnectIns` to ProtoBuf."""
    if ins.seconds is not None:
        return ServerMessage.ReconnectIns(seconds=ins.seconds)
    return ServerMessage.ReconnectIns()


# === DisconnectRes message ===


def disconnect_res_from_proto(msg: ClientMessage.DisconnectRes) -> typing.DisconnectRes:
    """Deserialize `DisconnectRes` from ProtoBuf."""
    if msg.reason == Reason.RECONNECT:
        return typing.DisconnectRes(reason="RECONNECT")
    if msg.reason == Reason.POWER_DISCONNECTED:
        return typing.DisconnectRes(reason="POWER_DISCONNECTED")
    if msg.reason == Reason.WIFI_UNAVAILABLE:
        return typing.DisconnectRes(reason="WIFI_UNAVAILABLE")
    return typing.DisconnectRes(reason="UNKNOWN")


# === GetParameters messages ===


def get_parameters_ins_to_proto(
    ins: typing.GetParametersIns,
) -> ServerMessage.GetParametersIns:
    """Serialize `GetParametersIns` to ProtoBuf."""
    config = properties_to_proto(ins.config)
    return ServerMessage.GetParametersIns(config=config)


def get_parameters_ins_from_proto(
    msg: ServerMessage.GetParametersIns,
) -> typing.GetParametersIns:
    """Deserialize `GetParametersIns` from ProtoBuf."""
    config = properties_from_proto(msg.config)
    return typing.GetParametersIns(config=config)


def get_parameters_res_to_proto(
    res: typing.GetParametersRes,
) -> ClientMessage.GetParametersRes:
    """Serialize `GetParametersRes` to ProtoBuf."""
    status_msg = status_to_proto(res.status)
    if res.status.code == typing.Code.GET_PARAMETERS_NOT_IMPLEMENTED:
        return ClientMessage.GetParametersRes(status=status_msg)
    parameters_proto = parameters_to_proto(res.parameters)
    return ClientMessage.GetParametersRes(
        status=status_msg, parameters=parameters_proto
    )


def get_parameters_res_from_proto(
    msg: ClientMessage.GetParametersRes,
) -> typing.GetParametersRes:
    """Deserialize `GetParametersRes` from ProtoBuf."""
    status = status_from_proto(msg=msg.status)
    parameters = parameters_from_proto(msg.parameters)
    return typing.GetParametersRes(status=status, parameters=parameters)



# === Proposals messages ===
def prop_ins_to_proto(ins: typing.PropIns) -> ServerMessage.PropIns:
    """Serialize `PropIns` to ProtoBuf."""
    config_msg = dictionary_to_proto(ins.config)
    return ServerMessage.PropIns(config=config_msg)

def prop_ins_from_proto(msg: ServerMessage.PropIns) -> typing.PropIns:
    """Deserialize `PropIns` from ProtoBuf."""
    config = dictionary_from_proto(msg.config)
    return typing.PropIns(config=config)


def prop_res_to_proto(res: typing.PropRes) -> ClientMessage.PropRes:
    """Serialize `PropRes` to ProtoBuf."""
    status_msg = status_to_proto(res.status)
    proposal = None if res.proposal is None else dictionary_to_proto(res.proposal)
    return ClientMessage.PropRes(
        status=status_msg,
        proposals=proposal
    )


def prop_res_from_proto(msg: ClientMessage.PropRes) -> typing.PropRes:
    """Deserialize `PropRes` from ProtoBuf."""
    status = status_from_proto(msg=msg.status)
    proposal = None if msg.proposals is None else dictionary_from_proto(msg.proposals)
    return typing.PropRes(
        status=status,
        proposal=proposal
    )

# === architecture_fit messages ===


def architecture_fit_ins_to_proto(ins: typing.ArchitectureFitIns) -> ServerMessage.ArchitectureFitIns:
    """Serialize `ArchitectureFitIns` to ProtoBuf."""
    
    parameters_proto = parameters_to_proto(ins.parameters)
    model_architecture_proto = scalar_to_proto(ins.model_architecture)
    config_proto = dictionary_to_proto(ins.config)
    features_mapping_proto = dictionary_to_proto(ins.features_mapping)
    
    return ServerMessage.ArchitectureFitIns(
                                     parameters=parameters_proto, 
                                     features_mapping=features_mapping_proto, 
                                     config=config_proto, 
                                     model_architecture=model_architecture_proto
                                     )


def architecture_fit_ins_from_proto(msg: ServerMessage.ArchitectureFitIns) -> typing.ArchitectureFitIns:
    """Deserialize `ArchitectureFitIns` from ProtoBuf."""
    parameters = parameters_from_proto(msg.parameters)
    features_mapping = dictionary_from_proto(msg.features_mapping)
    config = dictionary_from_proto(msg.config)
    model_architecture = scalar_from_proto(msg.model_architecture)
    return typing.ArchitectureFitIns(
        parameters=parameters, 
        model_architecture=model_architecture, 
        config= config, 
        features_mapping=features_mapping)



# === Fit messages ===


def fit_ins_to_proto(ins: typing.FitIns) -> ServerMessage.FitIns:
    """Serialize `FitIns` to ProtoBuf."""
    parameters_proto = parameters_to_proto(ins.parameters)
    config_msg = dictionary_to_proto(ins.config)
    return ServerMessage.FitIns(parameters=parameters_proto, config=config_msg)


def fit_ins_from_proto(msg: ServerMessage.FitIns) -> typing.FitIns:
    """Deserialize `FitIns` from ProtoBuf."""
    parameters = parameters_from_proto(msg.parameters)
    config = dictionary_from_proto(msg.config)
    return typing.FitIns(parameters=parameters, config=config)


def fit_res_to_proto(res: typing.FitRes) -> ClientMessage.FitRes:
    """Serialize `FitIns` to ProtoBuf."""
    status_msg = status_to_proto(res.status)
    if res.status.code == typing.Code.FIT_NOT_IMPLEMENTED:
        return ClientMessage.FitRes(status=status_msg)
    parameters_proto = parameters_to_proto(res.parameters)
    metrics_msg = None if res.metrics is None else dictionary_to_proto(res.metrics)
    return ClientMessage.FitRes(
        status=status_msg,
        parameters=parameters_proto,
        num_examples=res.num_examples,
        metrics=metrics_msg,
    )


def fit_res_from_proto(msg: ClientMessage.FitRes) -> typing.FitRes:
    """Deserialize `FitRes` from ProtoBuf."""
    status = status_from_proto(msg=msg.status)
    parameters = parameters_from_proto(msg.parameters)
    metrics = None if msg.metrics is None else dictionary_from_proto(msg.metrics)
    return typing.FitRes(
        status=status,
        parameters=parameters,
        num_examples=msg.num_examples,
        metrics=metrics,
    )


# === GetProperties messages ===


def get_properties_ins_to_proto(
    ins: typing.GetPropertiesIns,
) -> ServerMessage.GetPropertiesIns:
    """Serialize `GetPropertiesIns` to ProtoBuf."""
    config = properties_to_proto(ins.config)
    return ServerMessage.GetPropertiesIns(config=config)


def get_properties_ins_from_proto(
    msg: ServerMessage.GetPropertiesIns,
) -> typing.GetPropertiesIns:
    """Deserialize `GetPropertiesIns` from ProtoBuf."""
    config = properties_from_proto(msg.config)
    return typing.GetPropertiesIns(config=config)


def get_properties_res_to_proto(
    res: typing.GetPropertiesRes,
) -> ClientMessage.GetPropertiesRes:
    """Serialize `GetPropertiesIns` to ProtoBuf."""
    status_msg = status_to_proto(res.status)
    if res.status.code == typing.Code.GET_PROPERTIES_NOT_IMPLEMENTED:
        return ClientMessage.GetPropertiesRes(status=status_msg)
    properties_msg = properties_to_proto(res.properties)
    return ClientMessage.GetPropertiesRes(status=status_msg, properties=properties_msg)


def get_properties_res_from_proto(
    msg: ClientMessage.GetPropertiesRes,
) -> typing.GetPropertiesRes:
    """Deserialize `GetPropertiesRes` from ProtoBuf."""
    status = status_from_proto(msg=msg.status)
    properties = properties_from_proto(msg.properties)
    return typing.GetPropertiesRes(status=status, properties=properties)


# === Evaluate messages ===


def evaluate_ins_to_proto(ins: typing.EvaluateIns) -> ServerMessage.EvaluateIns:
    """Serialize `EvaluateIns` to ProtoBuf."""
    parameters_proto = parameters_to_proto(ins.parameters)
    config_msg = dictionary_to_proto(ins.config)
    return ServerMessage.EvaluateIns(parameters=parameters_proto, config=config_msg)


def evaluate_ins_from_proto(msg: ServerMessage.EvaluateIns) -> typing.EvaluateIns:
    """Deserialize `EvaluateIns` from ProtoBuf."""
    parameters = parameters_from_proto(msg.parameters)
    config = dictionary_from_proto(msg.config)
    return typing.EvaluateIns(parameters=parameters, config=config)


def evaluate_res_to_proto(res: typing.EvaluateRes) -> ClientMessage.EvaluateRes:
    """Serialize `EvaluateIns` to ProtoBuf."""
    status_msg = status_to_proto(res.status)
    if res.status.code == typing.Code.EVALUATE_NOT_IMPLEMENTED:
        return ClientMessage.EvaluateRes(status=status_msg)
    metrics_msg = None if res.metrics is None else dictionary_to_proto(res.metrics)
    return ClientMessage.EvaluateRes(
        status=status_msg,
        loss=res.loss,
        num_examples=res.num_examples,
        metrics=metrics_msg,
    )


def evaluate_res_from_proto(msg: ClientMessage.EvaluateRes) -> typing.EvaluateRes:
    """Deserialize `EvaluateRes` from ProtoBuf."""
    status = status_from_proto(msg=msg.status)
    metrics = None if msg.metrics is None else dictionary_from_proto(msg.metrics)
    return typing.EvaluateRes(
        status=status,
        loss=msg.loss,
        num_examples=msg.num_examples,
        metrics=metrics,
    )


# === Status messages ===


def status_to_proto(status: typing.Status) -> Status:
    """Serialize `Status` to ProtoBuf."""
    code = Code.OK
    if status.code == typing.Code.GET_PROPERTIES_NOT_IMPLEMENTED:
        code = Code.GET_PROPERTIES_NOT_IMPLEMENTED
    if status.code == typing.Code.GET_PARAMETERS_NOT_IMPLEMENTED:
        code = Code.GET_PARAMETERS_NOT_IMPLEMENTED
    if status.code == typing.Code.FIT_NOT_IMPLEMENTED:
        code = Code.FIT_NOT_IMPLEMENTED
    if status.code == typing.Code.EVALUATE_NOT_IMPLEMENTED:
        code = Code.EVALUATE_NOT_IMPLEMENTED
    if status.code == typing.Code.ARCHITECTURE_FIT_NOT_IMPLEMENTED:
        code = Code.ARCHITECTURE_FIT_NOT_IMPLEMENTED
    if status.code == typing.Code.PROP_NOT_IMPLEMENTED:
        code = Code.PROP_NOT_IMPLEMENTED
    return Status(code=code, message=status.message)


def status_from_proto(msg: Status) -> typing.Status:
    """Deserialize `Status` from ProtoBuf."""
    code = typing.Code.OK
    if msg.code == Code.GET_PROPERTIES_NOT_IMPLEMENTED:
        code = typing.Code.GET_PROPERTIES_NOT_IMPLEMENTED
    if msg.code == Code.GET_PARAMETERS_NOT_IMPLEMENTED:
        code = typing.Code.GET_PARAMETERS_NOT_IMPLEMENTED
    if msg.code == Code.FIT_NOT_IMPLEMENTED:
        code = typing.Code.FIT_NOT_IMPLEMENTED
    if msg.code == Code.EVALUATE_NOT_IMPLEMENTED:
        code = typing.Code.EVALUATE_NOT_IMPLEMENTED
    if msg.code == Code.ARCHITECTURE_FIT_NOT_IMPLEMENTED:
        code = typing.Code.ARCHITECTURE_FIT_NOT_IMPLEMENTED
    if msg.code == Code.PROP_NOT_IMPLEMENTED:
        code = typing.Code.PROP_NOT_IMPLEMENTED
    return typing.Status(code=code, message=msg.message)


# === Properties messages ===


def properties_to_proto(properties: typing.Properties) -> Any:
    """Serialize `Properties` to ProtoBuf."""
    proto = {}
    for key in properties:
        proto[key] = scalar_to_proto(properties[key])
    return proto


def properties_from_proto(proto: Any) -> typing.Properties:
    """Deserialize `Properties` from ProtoBuf."""
    properties = {}
    for k in proto:
        properties[k] = scalar_from_proto(proto[k])
    return properties


# === Metrics messages ===


def dictionary_to_proto(dict) -> Any:
    proto = {}
    for key in dict:
        proto[key] = scalar_to_proto(dict[key])
    return proto

def dictionary_from_proto(proto: Any) -> typing.Metrics:
    """Deserialize `Metrics` from ProtoBuf."""
    dict = {}
    for k in proto:
        dict[k] = scalar_from_proto(proto[k])
    return dict





# === Scalar messages ===


def scalar_to_proto(scalar: typing.Scalar) -> Scalar:
    """Serialize `Scalar` to ProtoBuf."""
    if isinstance(scalar, bool):
        return Scalar(bool=scalar)

    if isinstance(scalar, bytes):
        return Scalar(bytes=scalar)

    if isinstance(scalar, float):
        return Scalar(double=scalar)

    if isinstance(scalar, int):
        return Scalar(sint64=scalar)

    if isinstance(scalar, str):
        return Scalar(string=scalar)

    raise ValueError(
        f"Accepted types: {bool, bytes, float, int, str} (but not {type(scalar)})"
    )


def scalar_from_proto(scalar_msg: Scalar) -> typing.Scalar:
    """Deserialize `Scalar` from ProtoBuf."""
    scalar_field = scalar_msg.WhichOneof("scalar")
    scalar = getattr(scalar_msg, cast(str, scalar_field))
    return cast(typing.Scalar, scalar)


# === Record messages ===


_type_to_field = {
    float: "double",
    int: "sint64",
    bool: "bool",
    str: "string",
    bytes: "bytes",
}
_list_type_to_class_and_field = {
    float: (DoubleList, "double_list"),
    int: (Sint64List, "sint64_list"),
    bool: (BoolList, "bool_list"),
    str: (StringList, "string_list"),
    bytes: (BytesList, "bytes_list"),
}
T = TypeVar("T")


def _record_value_to_proto(
    value: Any, allowed_types: List[type], proto_class: Type[T]
) -> T:
    """Serialize `*RecordValue` to ProtoBuf.

    Note: `bool` MUST be put in the front of allowd_types if it exists.
    """
    arg = {}
    for t in allowed_types:
        # Single element
        # Note: `isinstance(False, int) == True`.
        if isinstance(value, t):
            arg[_type_to_field[t]] = value
            return proto_class(**arg)
        # List
        if isinstance(value, list) and all(isinstance(item, t) for item in value):
            list_class, field_name = _list_type_to_class_and_field[t]
            arg[field_name] = list_class(vals=value)
            return proto_class(**arg)
    # Invalid types
    raise TypeError(
        f"The type of the following value is not allowed "
        f"in '{proto_class.__name__}':\n{value}"
    )


def _record_value_from_proto(value_proto: GrpcMessage) -> Any:
    """Deserialize `*RecordValue` from ProtoBuf."""
    value_field = cast(str, value_proto.WhichOneof("value"))
    if value_field.endswith("list"):
        value = list(getattr(value_proto, value_field).vals)
    else:
        value = getattr(value_proto, value_field)
    return value


def _record_value_dict_to_proto(
    value_dict: TypedDict[str, Any],
    allowed_types: List[type],
    value_proto_class: Type[T],
) -> Dict[str, T]:
    """Serialize the record value dict to ProtoBuf.

    Note: `bool` MUST be put in the front of allowd_types if it exists.
    """
    # Move bool to the front
    if bool in allowed_types and allowed_types[0] != bool:
        allowed_types.remove(bool)
        allowed_types.insert(0, bool)

    def proto(_v: Any) -> T:
        return _record_value_to_proto(_v, allowed_types, value_proto_class)

    return {k: proto(v) for k, v in value_dict.items()}


def _record_value_dict_from_proto(
    value_dict_proto: MutableMapping[str, Any]
) -> Dict[str, Any]:
    """Deserialize the record value dict from ProtoBuf."""
    return {k: _record_value_from_proto(v) for k, v in value_dict_proto.items()}


def array_to_proto(array: Array) -> ProtoArray:
    """Serialize Array to ProtoBuf."""
    return ProtoArray(**vars(array))


def array_from_proto(array_proto: ProtoArray) -> Array:
    """Deserialize Array from ProtoBuf."""
    return Array(
        dtype=array_proto.dtype,
        shape=list(array_proto.shape),
        stype=array_proto.stype,
        data=array_proto.data,
    )


def parameters_record_to_proto(record: ParametersRecord) -> ProtoParametersRecord:
    """Serialize ParametersRecord to ProtoBuf."""
    return ProtoParametersRecord(
        data_keys=record.keys(),
        data_values=map(array_to_proto, record.values()),
    )


def parameters_record_from_proto(
    record_proto: ProtoParametersRecord,
) -> ParametersRecord:
    """Deserialize ParametersRecord from ProtoBuf."""
    return ParametersRecord(
        array_dict=OrderedDict(
            zip(record_proto.data_keys, map(array_from_proto, record_proto.data_values))
        ),
        keep_input=False,
    )


def metrics_record_to_proto(record: MetricsRecord) -> ProtoMetricsRecord:
    """Serialize MetricsRecord to ProtoBuf."""
    return ProtoMetricsRecord(
        data=_record_value_dict_to_proto(record, [float, int], ProtoMetricsRecordValue)
    )


def metrics_record_from_proto(record_proto: ProtoMetricsRecord) -> MetricsRecord:
    """Deserialize MetricsRecord from ProtoBuf."""
    return MetricsRecord(
        metrics_dict=cast(
            Dict[str, typing.MetricsRecordValues],
            _record_value_dict_from_proto(record_proto.data),
        ),
        keep_input=False,
    )


def configs_record_to_proto(record: ConfigsRecord) -> ProtoConfigsRecord:
    """Serialize ConfigsRecord to ProtoBuf."""
    return ProtoConfigsRecord(
        data=_record_value_dict_to_proto(
            record,
            [bool, int, float, str, bytes],
            ProtoConfigsRecordValue,
        )
    )


def configs_record_from_proto(record_proto: ProtoConfigsRecord) -> ConfigsRecord:
    """Deserialize ConfigsRecord from ProtoBuf."""
    return ConfigsRecord(
        configs_dict=cast(
            Dict[str, typing.ConfigsRecordValues],
            _record_value_dict_from_proto(record_proto.data),
        ),
        keep_input=False,
    )


# === Error message ===


def error_to_proto(error: Error) -> ProtoError:
    """Serialize Error to ProtoBuf."""
    reason = error.reason if error.reason else ""
    return ProtoError(code=error.code, reason=reason)


def error_from_proto(error_proto: ProtoError) -> Error:
    """Deserialize Error from ProtoBuf."""
    reason = error_proto.reason if len(error_proto.reason) > 0 else None
    return Error(code=error_proto.code, reason=reason)


# === RecordSet message ===


def recordset_to_proto(recordset: RecordSet) -> ProtoRecordSet:
    """Serialize RecordSet to ProtoBuf."""
    return ProtoRecordSet(
        parameters={
            k: parameters_record_to_proto(v)
            for k, v in recordset.parameters_records.items()
        },
        metrics={
            k: metrics_record_to_proto(v) for k, v in recordset.metrics_records.items()
        },
        configs={
            k: configs_record_to_proto(v) for k, v in recordset.configs_records.items()
        },
    )


def recordset_from_proto(recordset_proto: ProtoRecordSet) -> RecordSet:
    """Deserialize RecordSet from ProtoBuf."""
    return RecordSet(
        parameters_records={
            k: parameters_record_from_proto(v)
            for k, v in recordset_proto.parameters.items()
        },
        metrics_records={
            k: metrics_record_from_proto(v) for k, v in recordset_proto.metrics.items()
        },
        configs_records={
            k: configs_record_from_proto(v) for k, v in recordset_proto.configs.items()
        },
    )


# === Message ===


def message_to_taskins(message: Message) -> TaskIns:
    """Create a TaskIns from the Message."""
    md = message.metadata
    return TaskIns(
        group_id=md.group_id,
        run_id=md.run_id,
        task=Task(
            producer=Node(node_id=0, anonymous=True),  # Assume driver node
            consumer=Node(node_id=md.dst_node_id, anonymous=False),
            created_at=md.created_at,
            ttl=md.ttl,
            ancestry=[md.reply_to_message] if md.reply_to_message != "" else [],
            task_type=md.message_type,
            recordset=(
                recordset_to_proto(message.content) if message.has_content() else None
            ),
            error=error_to_proto(message.error) if message.has_error() else None,
        ),
    )


def message_from_taskins(taskins: TaskIns) -> Message:
    """Create a Message from the TaskIns."""
    # Retrieve the Metadata
    metadata = Metadata(
        run_id=taskins.run_id,
        message_id=taskins.task_id,
        src_node_id=taskins.task.producer.node_id,
        dst_node_id=taskins.task.consumer.node_id,
        reply_to_message=taskins.task.ancestry[0] if taskins.task.ancestry else "",
        group_id=taskins.group_id,
        ttl=taskins.task.ttl,
        message_type=taskins.task.task_type,
    )

    # Construct Message
    message = Message(
        metadata=metadata,
        content=(
            recordset_from_proto(taskins.task.recordset)
            if taskins.task.HasField("recordset")
            else None
        ),
        error=(
            error_from_proto(taskins.task.error)
            if taskins.task.HasField("error")
            else None
        ),
    )
    message.metadata.created_at = taskins.task.created_at
    return message


def message_to_taskres(message: Message) -> TaskRes:
    """Create a TaskRes from the Message."""
    md = message.metadata
    return TaskRes(
        task_id="",  # This will be generated by the server
        group_id=md.group_id,
        run_id=md.run_id,
        task=Task(
            producer=Node(node_id=md.src_node_id, anonymous=False),
            consumer=Node(node_id=0, anonymous=True),  # Assume driver node
            created_at=md.created_at,
            ttl=md.ttl,
            ancestry=[md.reply_to_message] if md.reply_to_message != "" else [],
            task_type=md.message_type,
            recordset=(
                recordset_to_proto(message.content) if message.has_content() else None
            ),
            error=error_to_proto(message.error) if message.has_error() else None,
        ),
    )


def message_from_taskres(taskres: TaskRes) -> Message:
    """Create a Message from the TaskIns."""
    # Retrieve the MetaData
    metadata = Metadata(
        run_id=taskres.run_id,
        message_id=taskres.task_id,
        src_node_id=taskres.task.producer.node_id,
        dst_node_id=taskres.task.consumer.node_id,
        reply_to_message=taskres.task.ancestry[0] if taskres.task.ancestry else "",
        group_id=taskres.group_id,
        ttl=taskres.task.ttl,
        message_type=taskres.task.task_type,
    )

    # Construct the Message
    message = Message(
        metadata=metadata,
        content=(
            recordset_from_proto(taskres.task.recordset)
            if taskres.task.HasField("recordset")
            else None
        ),
        error=(
            error_from_proto(taskres.task.error)
            if taskres.task.HasField("error")
            else None
        ),
    )
    message.metadata.created_at = taskres.task.created_at
    return message
