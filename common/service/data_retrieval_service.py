from common.config.config import config


class DataRetrievalService:
    def __init__(self, cyoda_auth_service, entity_service, mock=False):
        self.mock = mock
        self.cyoda_auth_service = cyoda_auth_service
        self.entity_service = entity_service

    # =============================

    async def get_entities_by_guest_user_id(self, guest_user_id, model):
        return await self.entity_service.get_items_by_condition(
            token=self.cyoda_auth_service,
            entity_model=model,
            entity_version=config.ENTITY_VERSION,
            condition={
                "cyoda": {
                    "operator": "AND",
                    "conditions": [
                        {
                            "jsonPath": "$.guest_user_id", "operatorType": "EQUALS",
                            "value": guest_user_id, "type": "simple"
                        },
                        {
                            "field": "state", "operatorType": "INOT_EQUAL",
                            "value": "deleted", "type": "lifecycle"
                        }
                    ],
                    "type": "group"
                },
                "local": {"key": "guest_user_id", "value": guest_user_id}
            }
        )

    async def get_entities_by_user_name(self, user_id, model):
        return await self.entity_service.get_items_by_condition(
            token=self.cyoda_auth_service,
            entity_model=model,
            entity_version=config.ENTITY_VERSION,
            condition={
                "cyoda": {
                    "operator": "AND",
                    "conditions": [
                        {
                            "jsonPath": "$.user_id", "operatorType": "EQUALS",
                            "value": user_id, "type": "simple"
                        },
                        {
                            "field": "state", "operatorType": "INOT_EQUAL",
                            "value": "deleted", "type": "lifecycle"
                        }
                    ],
                    "type": "group"
                },
                "local": {"key": "user_id", "value": user_id}
            }
        )

    async def get_entities_by_user_name_and_workflow_name(self, user_id, model, workflow_name):
        return await self.entity_service.get_items_by_condition(
            token=self.cyoda_auth_service,
            entity_model=model,
            entity_version=config.ENTITY_VERSION,
            condition={
                "cyoda": {
                    "operator": "AND",
                    "conditions": [
                        {"jsonPath": "$.user_id", "operatorType": "IEQUALS", "value": user_id, "type": "simple"},
                        {"jsonPath": "$.workflow_name", "operatorType": "IEQUALS",
                         "value": workflow_name, "type": "simple"},
                        {
                            "field": "state",
                            "operatorType": "INOT_EQUAL",
                            "value": "deleted",
                            "type": "lifecycle"
                        }
                    ],
                    "type": "group"
                },
                "local": {"key": "user_id", "value": user_id}
            }
        )