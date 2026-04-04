from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

if TYPE_CHECKING:
    from ..models.channel import Channel


T = TypeVar("T", bound="Message")


@_attrs_define
class Message:
    """
    Attributes:
        id (str):
        channel (Channel):
        sender (str):
        content (str):
        timestamp (datetime.datetime):
    """

    id: str
    channel: Channel
    sender: str
    content: str
    timestamp: datetime.datetime
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        channel = self.channel.to_dict()

        sender = self.sender

        content = self.content

        timestamp = self.timestamp.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "channel": channel,
                "sender": sender,
                "content": content,
                "timestamp": timestamp,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.channel import Channel

        d = dict(src_dict)
        id = d.pop("id")

        channel = Channel.from_dict(d.pop("channel"))

        sender = d.pop("sender")

        content = d.pop("content")

        timestamp = isoparse(d.pop("timestamp"))

        message = cls(
            id=id,
            channel=channel,
            sender=sender,
            content=content,
            timestamp=timestamp,
        )

        message.additional_properties = d
        return message

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
