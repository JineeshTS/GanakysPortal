"""
Mobile Sync Service - Mobile Apps API Module (MOD-18)
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.mobile import (
    MobileSyncRequest, MobileSyncResponse, SyncDataItem,
    OfflineActionCreate, OfflineActionBatchCreate, OfflineActionBatchResponse,
    SyncEntityType, OfflineActionType
)


class MobileSyncService:
    """Service for mobile data synchronization."""

    @staticmethod
    async def sync_data(
        db: AsyncSession,
        company_id: UUID,
        user_id: UUID,
        request: MobileSyncRequest
    ) -> MobileSyncResponse:
        """Sync data for mobile app."""
        sync_id = uuid4()
        items = []
        has_more = False

        for entity_type in request.entity_types:
            entity_items = await MobileSyncService._get_entity_changes(
                db, company_id, user_id, entity_type,
                request.last_sync_at, request.include_deleted
            )
            items.extend(entity_items)

        # Limit items and set has_more
        if len(items) > 100:
            items = items[:100]
            has_more = True

        return MobileSyncResponse(
            sync_id=sync_id,
            device_id=request.device_id,
            sync_timestamp=datetime.utcnow(),
            items=items,
            has_more=has_more,
            next_cursor=str(sync_id) if has_more else None
        )

    @staticmethod
    async def _get_entity_changes(
        db: AsyncSession,
        company_id: UUID,
        user_id: UUID,
        entity_type: SyncEntityType,
        last_sync: Optional[datetime],
        include_deleted: bool
    ) -> List[SyncDataItem]:
        """Get changes for an entity type since last sync."""
        items = []

        # This would query the appropriate tables based on entity_type
        # For now, return empty list as placeholder
        # In real implementation, would query:
        # - employees table for EMPLOYEE
        # - attendance_records for ATTENDANCE
        # - leave_requests for LEAVE
        # - expense_claims for EXPENSE
        # - etc.

        return items

    @staticmethod
    async def process_offline_actions(
        db: AsyncSession,
        company_id: UUID,
        user_id: UUID,
        batch: OfflineActionBatchCreate
    ) -> OfflineActionBatchResponse:
        """Process offline actions from mobile app."""
        batch_id = uuid4()
        results = []
        success_count = 0
        failed_count = 0

        for action in batch.actions:
            try:
                result = await MobileSyncService._process_single_action(
                    db, company_id, user_id, action
                )
                if result.get('success'):
                    success_count += 1
                else:
                    failed_count += 1
                results.append(result)
            except Exception as e:
                failed_count += 1
                results.append({
                    'id': uuid4(),
                    'client_action_id': action.client_action_id,
                    'status': 'failed',
                    'error_message': str(e),
                    'processed_at': datetime.utcnow()
                })

        return OfflineActionBatchResponse(
            batch_id=batch_id,
            processed_count=len(batch.actions),
            success_count=success_count,
            failed_count=failed_count,
            results=results
        )

    @staticmethod
    async def _process_single_action(
        db: AsyncSession,
        company_id: UUID,
        user_id: UUID,
        action: OfflineActionCreate
    ) -> Dict[str, Any]:
        """Process a single offline action."""
        result = {
            'id': uuid4(),
            'client_action_id': action.client_action_id,
            'entity_type': action.entity_type,
            'action_type': action.action_type,
            'status': 'success',
            'processed_at': datetime.utcnow(),
            'success': True
        }

        try:
            if action.action_type == OfflineActionType.CREATE:
                # Create entity
                server_id = await MobileSyncService._create_entity(
                    db, company_id, user_id, action.entity_type, action.payload
                )
                result['server_entity_id'] = server_id
            elif action.action_type == OfflineActionType.UPDATE:
                # Update entity
                await MobileSyncService._update_entity(
                    db, action.entity_id, action.entity_type, action.payload
                )
                result['server_entity_id'] = action.entity_id
            elif action.action_type == OfflineActionType.DELETE:
                # Delete entity
                await MobileSyncService._delete_entity(
                    db, action.entity_id, action.entity_type
                )

        except Exception as e:
            result['status'] = 'failed'
            result['error_message'] = str(e)
            result['success'] = False

        return result

    @staticmethod
    async def _create_entity(
        db: AsyncSession,
        company_id: UUID,
        user_id: UUID,
        entity_type: SyncEntityType,
        payload: Dict[str, Any]
    ) -> UUID:
        """Create an entity from offline action."""
        # Placeholder - would create the appropriate entity
        return uuid4()

    @staticmethod
    async def _update_entity(
        db: AsyncSession,
        entity_id: UUID,
        entity_type: SyncEntityType,
        payload: Dict[str, Any]
    ) -> None:
        """Update an entity from offline action."""
        # Placeholder - would update the appropriate entity
        pass

    @staticmethod
    async def _delete_entity(
        db: AsyncSession,
        entity_id: UUID,
        entity_type: SyncEntityType
    ) -> None:
        """Delete an entity from offline action."""
        # Placeholder - would delete the appropriate entity
        pass

    @staticmethod
    async def get_sync_status(
        db: AsyncSession,
        device_id: UUID,
        company_id: UUID
    ) -> Dict[str, Any]:
        """Get sync status for a device."""
        return {
            'device_id': device_id,
            'last_sync_at': None,
            'pending_uploads': 0,
            'pending_downloads': 0,
            'sync_in_progress': False
        }
