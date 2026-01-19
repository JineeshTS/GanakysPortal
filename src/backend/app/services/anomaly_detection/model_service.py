"""
Anomaly Model Service
Handles ML model management for anomaly detection
"""
from datetime import datetime, date
from typing import Optional, List, Tuple, Dict, Any
from uuid import UUID

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.datetime_utils import utc_now
from app.models.anomaly_detection import AnomalyModel, ModelStatus
from app.schemas.anomaly_detection import (
    AnomalyModelCreate, AnomalyModelUpdate, TrainModelRequest
)


class ModelService:
    """Service for managing anomaly detection ML models"""

    async def list_models(
        self,
        db: AsyncSession,
        company_id: UUID,
        model_type: Optional[str] = None,
        status: Optional[ModelStatus] = None,
        data_source: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> Tuple[List[AnomalyModel], int]:
        """List models with filters"""
        conditions = []
        # Include company-specific and global models (company_id is NULL)
        conditions.append(
            (AnomalyModel.company_id == company_id) | (AnomalyModel.company_id.is_(None))
        )

        if model_type:
            conditions.append(AnomalyModel.model_type == model_type)
        if status:
            conditions.append(AnomalyModel.status == status)
        if data_source:
            conditions.append(AnomalyModel.data_source == data_source)

        # Get total count
        count_query = select(func.count()).select_from(AnomalyModel).where(and_(*conditions))
        total = await db.scalar(count_query) or 0

        # Get items
        query = (
            select(AnomalyModel)
            .where(and_(*conditions))
            .order_by(AnomalyModel.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        models = result.scalars().all()

        return list(models), total

    async def create_model(
        self,
        db: AsyncSession,
        company_id: UUID,
        model_data: AnomalyModelCreate
    ) -> AnomalyModel:
        """Create a new model"""
        # Generate version
        version = f"1.0.{utc_now().strftime('%Y%m%d%H%M%S')}"

        model = AnomalyModel(
            company_id=company_id,
            name=model_data.name,
            description=model_data.description,
            model_type=model_data.model_type,
            version=model_data.version or version,
            config=model_data.config,
            feature_columns=model_data.feature_columns,
            target_column=model_data.target_column,
            data_source=model_data.data_source,
            status=ModelStatus.draft
        )

        db.add(model)
        await db.commit()
        await db.refresh(model)
        return model

    async def get_model(
        self,
        db: AsyncSession,
        model_id: UUID,
        company_id: UUID
    ) -> Optional[AnomalyModel]:
        """Get a specific model"""
        query = select(AnomalyModel).where(
            and_(
                AnomalyModel.id == model_id,
                (AnomalyModel.company_id == company_id) | (AnomalyModel.company_id.is_(None))
            )
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def update_model(
        self,
        db: AsyncSession,
        model_id: UUID,
        company_id: UUID,
        model_data: AnomalyModelUpdate
    ) -> Optional[AnomalyModel]:
        """Update a model"""
        model = await self.get_model(db, model_id, company_id)
        if not model:
            return None

        # Don't allow updating global models
        if model.company_id is None:
            return None

        update_data = model_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(model, field, value)

        model.updated_at = utc_now()
        await db.commit()
        await db.refresh(model)
        return model

    async def delete_model(
        self,
        db: AsyncSession,
        model_id: UUID,
        company_id: UUID
    ) -> bool:
        """Delete a model"""
        model = await self.get_model(db, model_id, company_id)
        if not model or model.company_id is None:
            return False

        await db.delete(model)
        await db.commit()
        return True

    async def train_model(
        self,
        db: AsyncSession,
        model_id: UUID,
        company_id: UUID,
        training_start_date: Optional[date] = None,
        training_end_date: Optional[date] = None
    ) -> Optional[AnomalyModel]:
        """Train a model"""
        model = await self.get_model(db, model_id, company_id)
        if not model or model.company_id is None:
            return None

        # Set training status
        model.status = ModelStatus.training
        model.training_start_date = training_start_date
        model.training_end_date = training_end_date
        await db.commit()

        started_at = utc_now()

        # In production, this would:
        # 1. Fetch training data from the data source
        # 2. Preprocess and feature engineer
        # 3. Train the model based on model_type:
        #    - isolation_forest: sklearn.ensemble.IsolationForest
        #    - autoencoder: tensorflow/keras autoencoder
        #    - lstm: tensorflow/keras LSTM
        #    - statistical: scipy statistical models
        # 4. Evaluate model performance
        # 5. Save model to storage (S3, local, etc.)

        # Placeholder: Simulate training
        training_duration = 1  # seconds

        # Update model with training results
        model.status = ModelStatus.trained
        model.trained_at = utc_now()
        model.training_duration_seconds = training_duration
        model.training_samples = 1000  # Placeholder

        # Placeholder metrics
        model.accuracy = 0.95
        model.precision = 0.92
        model.recall = 0.89
        model.f1_score = 0.90
        model.auc_roc = 0.94

        model.updated_at = utc_now()
        await db.commit()
        await db.refresh(model)
        return model

    async def create_and_train_model(
        self,
        db: AsyncSession,
        company_id: UUID,
        request: TrainModelRequest
    ) -> AnomalyModel:
        """Create and train a new model"""
        # Create the model
        model_create = AnomalyModelCreate(
            name=request.name,
            model_type=request.model_type,
            version=f"1.0.{utc_now().strftime('%Y%m%d%H%M%S')}",
            feature_columns=request.feature_columns,
            target_column=request.target_column,
            data_source=request.data_source,
            config=request.config
        )

        model = await self.create_model(db, company_id, model_create)

        # Train the model
        model = await self.train_model(
            db, model.id, company_id,
            training_start_date=request.training_start_date,
            training_end_date=request.training_end_date
        )

        return model

    async def predict(
        self,
        db: AsyncSession,
        model_id: UUID,
        company_id: UUID,
        features: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Make prediction using a model"""
        model = await self.get_model(db, model_id, company_id)
        if not model or model.status != ModelStatus.deployed:
            return None

        # In production, this would:
        # 1. Load the trained model from storage
        # 2. Preprocess input features
        # 3. Run inference
        # 4. Return prediction with confidence

        # Update inference stats
        model.inference_count += 1
        model.last_inference_at = utc_now()
        await db.commit()

        # Placeholder prediction
        return {
            "is_anomaly": False,
            "anomaly_score": 0.1,
            "confidence": 0.95,
            "model_id": str(model.id),
            "model_version": model.version
        }

    async def deploy_model(
        self,
        db: AsyncSession,
        model_id: UUID,
        company_id: UUID
    ) -> Optional[AnomalyModel]:
        """Deploy a trained model"""
        model = await self.get_model(db, model_id, company_id)
        if not model or model.status != ModelStatus.trained:
            return None

        model.status = ModelStatus.deployed
        model.updated_at = utc_now()
        await db.commit()
        await db.refresh(model)
        return model

    async def retire_model(
        self,
        db: AsyncSession,
        model_id: UUID,
        company_id: UUID
    ) -> Optional[AnomalyModel]:
        """Retire a deployed model"""
        model = await self.get_model(db, model_id, company_id)
        if not model:
            return None

        model.status = ModelStatus.retired
        model.updated_at = utc_now()
        await db.commit()
        await db.refresh(model)
        return model

    async def get_model_performance(
        self,
        db: AsyncSession,
        model_id: UUID,
        company_id: UUID
    ) -> Optional[Dict[str, Any]]:
        """Get model performance metrics"""
        model = await self.get_model(db, model_id, company_id)
        if not model:
            return None

        return {
            "model_id": str(model.id),
            "model_name": model.name,
            "model_type": model.model_type,
            "version": model.version,
            "status": model.status.value,
            "metrics": {
                "accuracy": model.accuracy,
                "precision": model.precision,
                "recall": model.recall,
                "f1_score": model.f1_score,
                "auc_roc": model.auc_roc
            },
            "training": {
                "samples": model.training_samples,
                "duration_seconds": model.training_duration_seconds,
                "trained_at": model.trained_at.isoformat() if model.trained_at else None
            },
            "inference": {
                "count": model.inference_count,
                "avg_time_ms": model.avg_inference_time_ms,
                "last_inference": model.last_inference_at.isoformat() if model.last_inference_at else None
            }
        }


model_service = ModelService()
