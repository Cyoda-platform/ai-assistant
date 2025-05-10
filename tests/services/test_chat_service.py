import asyncio
from types import SimpleNamespace
import pytest
import jwt
from unittest.mock import AsyncMock, MagicMock

import services.chat_service as chat_service
from services.chat_service import ChatService
from common.exception.exceptions import (
    InvalidTokenException,
    TokenExpiredException,
    GuestChatsLimitExceededException,
)
from common.config import const
from common.config.config import config


@pytest.fixture
def service_mocks():
    entity_service = MagicMock()
    entity_service.get_items_by_condition = AsyncMock()
    entity_service.add_item = AsyncMock()
    entity_service.get_item = AsyncMock()
    entity_service.delete_item = AsyncMock()

    ai_agent = MagicMock()
    ai_agent.run_agent = AsyncMock()

    cyoda_auth_service = MagicMock()
    chat_lock = asyncio.Lock()

    svc = ChatService(entity_service, cyoda_auth_service, chat_lock, ai_agent)
    return svc, entity_service, ai_agent


def make_jwt(payload: dict) -> str:
    # content doesn’t matter since we always patch jwt.decode in tests
    return "dummy.jwt.token"


@pytest.mark.parametrize("header,exc_type", [
    (None, InvalidTokenException),
    ("", InvalidTokenException),
    ("Bearer ", InvalidTokenException),
])
def test_get_user_id_no_header(header, exc_type, service_mocks):
    svc, _, _ = service_mocks
    with pytest.raises(exc_type):
        svc._get_user_id(header)


def test_get_user_id_invalid_token(monkeypatch, service_mocks):
    svc, _, _ = service_mocks
    # jwt.decode in _get_user_id should raise InvalidTokenError → method returns None
    monkeypatch.setattr(jwt, "decode", lambda *args, **kwargs: (_ for _ in ()).throw(jwt.InvalidTokenError()))
    assert svc._get_user_id("Bearer foo.bar") is None


def test_get_user_id_expired_token(monkeypatch, service_mocks):
    svc, _, _ = service_mocks
    # jwt.decode in _get_user_id should raise ExpiredSignatureError → method raises TokenExpiredException
    monkeypatch.setattr(jwt, "decode", lambda *args, **kwargs: (_ for _ in ()).throw(jwt.ExpiredSignatureError()))
    with pytest.raises(TokenExpiredException):
        svc._get_user_id("Bearer expired.token")


def test_get_user_id_success_non_guest(monkeypatch, service_mocks):
    svc, _, _ = service_mocks
    # jwt.decode returns payload with caas_org_id
    monkeypatch.setattr(jwt, "decode", lambda *args, **kwargs: {"caas_org_id": "user123"})
    user_id = svc._get_user_id(f"Bearer {make_jwt({'caas_org_id': 'user123'})}")
    assert user_id == "user123"


def test_get_user_id_success_guest(monkeypatch, service_mocks):
    svc, _, _ = service_mocks
    # jwt.decode returns a guest ID
    monkeypatch.setattr(jwt, "decode", lambda *args, **kwargs: {"caas_org_id": "guest.foo"})
    called = False

    def fake_validate(token, *args, **kwargs):
        nonlocal called
        called = True

    # patch the validate_token that chat_service imported
    monkeypatch.setattr(chat_service, "validate_token", fake_validate)

    user_id = svc._get_user_id(f"Bearer {make_jwt({'caas_org_id': 'guest.foo'})}")
    assert user_id == "guest.foo"
    assert called, "validate_token should be called for guest tokens"


def test_validate_answer_empty_no_file(service_mocks):
    svc, _, _ = service_mocks
    valid, msg = svc._validate_answer("", None)
    assert not valid
    assert msg == "Invalid entity"


def test_validate_answer_empty_with_file(service_mocks):
    svc, _, _ = service_mocks
    fake_file = SimpleNamespace()
    valid, msg = svc._validate_answer("", fake_file)
    assert valid
    assert msg == "Consider the file contents"


def test_validate_answer_nonempty(service_mocks):
    svc, _, _ = service_mocks
    valid, msg = svc._validate_answer("foo", None)
    assert valid
    assert msg == "foo"


@pytest.mark.asyncio
async def test_list_chats_invalid_token(service_mocks):
    svc, _, _ = service_mocks
    with pytest.raises(InvalidTokenException):
        await svc.list_chats("")


@pytest.mark.asyncio
async def test_list_chats_no_transfers(service_mocks):
    svc, entity_service, _ = service_mocks
    chat_obj = SimpleNamespace(
        technical_id="c1", name="N1", description="D1", date="2025-05-01"
    )
    # first: user chats; second: no transfers
    entity_service.get_items_by_condition.side_effect = [
        [chat_obj],
        [],
    ]

    result = await svc.list_chats("user1")
    assert result == [{
        "technical_id": "c1",
        "name": "N1",
        "description": "D1",
        "date": "2025-05-01",
    }]
    assert entity_service.get_items_by_condition.call_count == 2


@pytest.mark.asyncio
async def test_list_chats_with_transfers(service_mocks):
    svc, entity_service, _ = service_mocks
    chat1 = SimpleNamespace(
        technical_id="c1", name="A", description="D", date="2025-05-02"
    )
    chat2 = SimpleNamespace(
        technical_id="c2", name="B", description="E", date="2025-05-03"
    )
    # user chats, transfers entry, then guest chats
    entity_service.get_items_by_condition.side_effect = [
        [chat1],
        [{"guest_user_id": "guest.x"}],
        [chat2],
    ]

    result = await svc.list_chats("user1")
    ids = {c["technical_id"] for c in result}
    assert ids == {"c1", "c2"}


@pytest.mark.asyncio
async def test_add_chat_guest_limit_exceeded(monkeypatch, service_mocks):
    svc, entity_service, _ = service_mocks
    monkeypatch.setattr(config, "MAX_GUEST_CHATS", 1)
    entity_service.get_items_by_condition.return_value = [1]  # already has 1
    with pytest.raises(GuestChatsLimitExceededException):
        await svc.add_chat("guest.abc", {"name": "hello"})


@pytest.mark.asyncio
async def test_add_chat_name_too_large(monkeypatch, service_mocks):
    svc, entity_service, _ = service_mocks
    long_name = "x" * 100
    monkeypatch.setattr(config, "MAX_TEXT_SIZE", 10)
    out = await svc.add_chat("user1", {"name": long_name})
    assert out == {"error": "Answer size exceeds 1MB limit"}


@pytest.mark.asyncio
async def test_add_chat_success(monkeypatch, service_mocks):
    svc, entity_service, _ = service_mocks
    # only these three add_item calls now (greeting, memory, chat)
    entity_service.add_item.side_effect = ["edge123", "mem456", "chat789"]

    # patch out the real add_answer_to_finished_flow so it doesn't invoke entity_service
    monkeypatch.setattr(
        chat_service,
        "add_answer_to_finished_flow",
        AsyncMock(return_value="ans999"),
    )
    monkeypatch.setattr(
        chat_service,
        "current_timestamp",
        lambda: "T0"
    )
    monkeypatch.setattr(
        chat_service,
        "get_current_timestamp_num",
        lambda: 42
    )

    res = await svc.add_chat("user1", {"name": "hello", "description": "desc"})
    assert res == {
        "message": "Chat created",
        "technical_id": "chat789",
        "answer_technical_id": "ans999",
    }
    assert entity_service.add_item.call_count == 3


@pytest.mark.asyncio
async def test_delete_chat(monkeypatch, service_mocks):
    svc, entity_service, _ = service_mocks
    # stub owner check so no exception
    monkeypatch.setattr(svc, "_get_chat_for_user", AsyncMock(return_value=SimpleNamespace()))
    res = await svc.delete_chat("Bearer t", "tid123")

    assert res == {"message": "Chat deleted", "technical_id": "tid123"}
    entity_service.delete_item.assert_awaited_once_with(
        token=svc.cyoda_auth_service,
        entity_model=const.ModelName.CHAT_ENTITY.value,
        entity_version=config.ENTITY_VERSION,
        technical_id="tid123",
        meta={},
    )
