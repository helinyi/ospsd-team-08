from chat_client_api import Channel, Message
from openai_ai_client_impl import OpenAIAIClient


class FakeChatClient:
    def get_channels(self) -> list[Channel]:
        return [
            Channel(
                channel_id="123",
                name="general",
                is_private=False,
                channel_type="group",
            )
        ]

    def get_channel(self, channel_id: str) -> Channel:
        return Channel(
            channel_id=channel_id,
            name="general",
            is_private=False,
            channel_type="group",
        )

    def get_messages(
        self,
        channel_id: str,
        limit: int = 10,
        cursor: str | None = None,
    ) -> list[Message]:
        return [
            Message(
                message_id="m1",
                channel=channel_id,
                text="hello",
                sender="bot",
                timestamp="2026-04-17T21:00:00Z",
            )
        ]

    def get_message(self, message_id: str) -> Message:
        return Message(
            message_id=message_id,
            channel="123",
            text="hello",
            sender="bot",
            timestamp="2026-04-17T21:00:00Z",
        )

    def delete_message(self, message_id: str) -> None:
        return None

    def send_message(self, channel_id: str, text: str) -> Message:
        return Message(
            message_id="m2",
            channel=channel_id,
            text=text,
            sender="me",
            timestamp="2026-04-17T21:01:00Z",
        )


def main() -> None:
    ai_client = OpenAIAIClient(chat_client=FakeChatClient())

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in {"exit", "quit"}:
            break

        response = ai_client.run(user_input)
        print("AI:", response)


if __name__ == "__main__":
    main()