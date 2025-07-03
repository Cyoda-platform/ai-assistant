import logging

from common.config import const

logger = logging.getLogger(__name__)


class UserService:
    def __init__(self, cyoda_auth_service, entity_service, data_service, mock=False):
        self.mock = mock
        self.cyoda_auth_service = cyoda_auth_service
        self.entity_service = entity_service
        self.data_service = data_service

    async def get_entity_account(self, user_id):
        if user_id.startswith('guest'):
            transfer_chats_entities = await self.data_service.get_entities_by_guest_user_id(guest_user_id=user_id,
                                                                                        model=const.ModelName.TRANSFER_CHATS_ENTITY.value)
            if not transfer_chats_entities:
                return user_id
            if len(transfer_chats_entities) > 1:
                logger.warning(
                    f"Guest user {user_id} has multiple accounts")
            return transfer_chats_entities[0]['user_id']
        return user_id
