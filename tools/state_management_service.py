from typing import Any

from common.config.config import config
from entity.chat.chat import ChatEntity
from entity.model import AgenticFlowEntity
from tools.base_service import BaseWorkflowService


class StateManagementService(BaseWorkflowService):
    """
    Service responsible for managing chat state, stage completion,
    locking/unlocking, and transition management.
    """

    async def finish_discussion(self, technical_id: str, entity: AgenticFlowEntity, **params: Any) -> None:
        """
        Mark a discussion as finished for a specific transition.
        
        Args:
            technical_id: Technical identifier
            entity: Agentic flow entity
            **params: Parameters including transition
            
        Raises:
            ValueError: If transition parameter is missing
        """
        transition = params.get("transition")
        if transition is None:
            raise ValueError("Missing required parameter: 'transition'")

        additional_flag = False

        # Ensure the nested dictionary for conditions exists
        conditions = entity.transitions_memory.conditions

        # Set the flag for the specified transition
        conditions.setdefault(transition, {})["require_additional_question"] = additional_flag

    async def is_stage_completed(self, technical_id: str, entity: ChatEntity, **params: Any) -> bool:
        """
        Check if a specific stage/transition is completed.
        
        Args:
            technical_id: Technical identifier
            entity: Chat entity
            **params: Parameters including transition
            
        Returns:
            True if stage is completed, False otherwise
        """
        if params.get('params'):
            self.logger.warning("Wrong value for params")
            params = params.get('params')
            
        transition = params.get("transition")
        if transition is None:
            self.logger.exception("Missing required parameter: 'transition'")
            return False

        transitions = entity.transitions_memory
        current_iteration = transitions.current_iteration
        max_iteration = transitions.max_iteration

        # Check if maximum iterations exceeded
        if transition in current_iteration:
            allowed_max = max_iteration.get(transition, config.MAX_ITERATION)
            if current_iteration[transition] > allowed_max:
                return True

        conditions = transitions.conditions
        # If the condition for the transition does not exist, assume stage is not completed
        if transition not in conditions:
            return False

        # Return the inverse of the require_additional_question flag
        return not conditions[transition].get("require_additional_question", True)

    async def not_stage_completed(self, technical_id: str, entity: ChatEntity, **params: Any) -> bool:
        """
        Check if a specific stage/transition is NOT completed.
        
        Args:
            technical_id: Technical identifier
            entity: Chat entity
            **params: Parameters including transition
            
        Returns:
            True if stage is NOT completed, False if it is completed
        """
        completed = await self.is_stage_completed(technical_id=technical_id, entity=entity, params=params)
        return not completed

    async def is_chat_locked(self, technical_id: str, entity: ChatEntity, **params: Any) -> bool:
        """
        Check if the chat is currently locked.
        
        Args:
            technical_id: Technical identifier
            entity: Chat entity
            **params: Additional parameters (unused)
            
        Returns:
            True if chat is locked, False otherwise
        """
        return entity.locked

    async def is_chat_unlocked(self, technical_id: str, entity: ChatEntity, **params: Any) -> bool:
        """
        Check if the chat is currently unlocked.
        
        Args:
            technical_id: Technical identifier
            entity: Chat entity
            **params: Additional parameters (unused)
            
        Returns:
            True if chat is unlocked, False otherwise
        """
        return not entity.locked

    async def lock_chat(self, technical_id: str, entity: ChatEntity, **params: Any) -> None:
        """
        Lock the chat to prevent further interactions.
        
        Args:
            technical_id: Technical identifier
            entity: Chat entity
            **params: Additional parameters (unused)
        """
        entity.locked = True

    async def unlock_chat(self, technical_id: str, entity: ChatEntity, **params: Any) -> None:
        """
        Unlock the chat to allow interactions.
        
        Args:
            technical_id: Technical identifier
            entity: Chat entity
            **params: Additional parameters (unused)
        """
        entity.locked = False

    async def reset_failed_entity(self, technical_id: str, entity: AgenticFlowEntity, **params: Any) -> str:
        """
        Reset the failed state of an entity to allow retry.
        
        Args:
            technical_id: Technical identifier
            entity: Agentic flow entity
            **params: Additional parameters (unused)
            
        Returns:
            Success message
        """
        entity.failed = False
        return "Retrying last step"
