"""
Forecast Service - Supply Chain Module (MOD-13)
"""
from datetime import datetime, date
from decimal import Decimal
from typing import List, Optional, Tuple, Dict
from uuid import UUID, uuid4
import statistics

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.supply_chain import PurchaseForecast, ForecastMethod
from app.schemas.supply_chain import PurchaseForecastCreate, PurchaseForecastUpdate
from app.core.datetime_utils import utc_now


class ForecastService:
    """Service for purchase forecasting operations."""

    @staticmethod
    async def create_forecast(
        db: AsyncSession,
        company_id: UUID,
        data: PurchaseForecastCreate
    ) -> PurchaseForecast:
        """Create a purchase forecast."""
        forecast = PurchaseForecast(
            id=uuid4(),
            company_id=company_id,
            generated_at=utc_now(),
            **data.model_dump()
        )
        db.add(forecast)
        await db.commit()
        await db.refresh(forecast)
        return forecast

    @staticmethod
    async def get_forecast(
        db: AsyncSession,
        forecast_id: UUID,
        company_id: UUID
    ) -> Optional[PurchaseForecast]:
        """Get forecast by ID."""
        result = await db.execute(
            select(PurchaseForecast).where(
                and_(
                    PurchaseForecast.id == forecast_id,
                    PurchaseForecast.company_id == company_id
                )
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def list_forecasts(
        db: AsyncSession,
        company_id: UUID,
        product_id: Optional[UUID] = None,
        year: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[PurchaseForecast], int]:
        """List purchase forecasts."""
        query = select(PurchaseForecast).where(
            PurchaseForecast.company_id == company_id
        )

        if product_id:
            query = query.where(PurchaseForecast.product_id == product_id)
        if year:
            query = query.where(PurchaseForecast.forecast_year == year)

        count_query = select(func.count()).select_from(query.subquery())
        total = await db.execute(count_query)
        total_count = total.scalar()

        query = query.offset(skip).limit(limit).order_by(
            PurchaseForecast.forecast_year.desc(),
            PurchaseForecast.forecast_month.desc()
        )
        result = await db.execute(query)

        return result.scalars().all(), total_count

    @staticmethod
    async def update_forecast(
        db: AsyncSession,
        forecast: PurchaseForecast,
        data: PurchaseForecastUpdate
    ) -> PurchaseForecast:
        """Update purchase forecast."""
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(forecast, field, value)
        forecast.updated_at = utc_now()
        await db.commit()
        await db.refresh(forecast)
        return forecast

    @staticmethod
    def calculate_moving_average(
        historical_data: List[Decimal],
        periods: int = 3
    ) -> Decimal:
        """Calculate simple moving average."""
        if not historical_data or len(historical_data) < periods:
            return Decimal('0')

        recent_data = historical_data[-periods:]
        avg = sum(recent_data) / len(recent_data)
        return Decimal(str(avg)).quantize(Decimal('0.01'))

    @staticmethod
    def calculate_exponential_smoothing(
        historical_data: List[Decimal],
        alpha: float = 0.3
    ) -> Decimal:
        """Calculate exponential smoothing forecast."""
        if not historical_data:
            return Decimal('0')

        forecast = float(historical_data[0])
        for actual in historical_data[1:]:
            forecast = alpha * float(actual) + (1 - alpha) * forecast

        return Decimal(str(forecast)).quantize(Decimal('0.01'))

    @staticmethod
    def calculate_trend_forecast(
        historical_data: List[Decimal],
        periods_ahead: int = 1
    ) -> Decimal:
        """Calculate trend-based forecast using linear regression."""
        if len(historical_data) < 2:
            return historical_data[-1] if historical_data else Decimal('0')

        n = len(historical_data)
        x_values = list(range(1, n + 1))
        y_values = [float(d) for d in historical_data]

        x_mean = statistics.mean(x_values)
        y_mean = statistics.mean(y_values)

        numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, y_values))
        denominator = sum((x - x_mean) ** 2 for x in x_values)

        if denominator == 0:
            return Decimal(str(y_mean))

        slope = numerator / denominator
        intercept = y_mean - slope * x_mean

        forecast = intercept + slope * (n + periods_ahead)
        return Decimal(str(max(0, forecast))).quantize(Decimal('0.01'))

    @staticmethod
    async def generate_forecast(
        db: AsyncSession,
        company_id: UUID,
        product_id: UUID,
        historical_data: List[Decimal],
        method: ForecastMethod,
        year: int,
        month: int
    ) -> PurchaseForecast:
        """Generate and save a forecast."""
        if method == ForecastMethod.MOVING_AVERAGE:
            forecasted_qty = ForecastService.calculate_moving_average(historical_data)
        elif method == ForecastMethod.EXPONENTIAL:
            forecasted_qty = ForecastService.calculate_exponential_smoothing(historical_data)
        elif method == ForecastMethod.TREND:
            forecasted_qty = ForecastService.calculate_trend_forecast(historical_data)
        else:
            forecasted_qty = ForecastService.calculate_moving_average(historical_data)

        # Calculate confidence level based on data variance
        confidence = Decimal('0.8')  # Default
        if len(historical_data) > 3:
            try:
                std_dev = statistics.stdev([float(d) for d in historical_data])
                mean_val = statistics.mean([float(d) for d in historical_data])
                if mean_val > 0:
                    cv = std_dev / mean_val  # Coefficient of variation
                    confidence = Decimal(str(max(0.5, 1 - cv))).quantize(Decimal('0.01'))
            except:
                pass

        forecast_data = PurchaseForecastCreate(
            product_id=product_id,
            forecast_period=f"{year}-{month:02d}",
            forecast_year=year,
            forecast_month=month,
            forecast_method=method,
            forecasted_qty=forecasted_qty,
            confidence_level=confidence
        )

        return await ForecastService.create_forecast(db, company_id, forecast_data)

    @staticmethod
    async def get_forecast_accuracy(
        db: AsyncSession,
        company_id: UUID,
        product_id: UUID,
        periods: int = 6
    ) -> Dict[str, Decimal]:
        """Calculate forecast accuracy metrics."""
        result = await db.execute(
            select(PurchaseForecast).where(
                and_(
                    PurchaseForecast.company_id == company_id,
                    PurchaseForecast.product_id == product_id,
                    PurchaseForecast.actual_qty.isnot(None)
                )
            ).order_by(
                PurchaseForecast.forecast_year.desc(),
                PurchaseForecast.forecast_month.desc()
            ).limit(periods)
        )

        forecasts = result.scalars().all()

        if not forecasts:
            return {
                'mape': Decimal('0'),
                'bias': Decimal('0'),
                'accuracy': Decimal('0')
            }

        errors = []
        for f in forecasts:
            if f.actual_qty and f.actual_qty > 0:
                error = abs(float(f.forecasted_qty) - float(f.actual_qty)) / float(f.actual_qty)
                errors.append(error)

        if not errors:
            return {
                'mape': Decimal('0'),
                'bias': Decimal('0'),
                'accuracy': Decimal('100')
            }

        mape = Decimal(str(statistics.mean(errors) * 100)).quantize(Decimal('0.01'))
        accuracy = max(Decimal('0'), Decimal('100') - mape)

        return {
            'mape': mape,
            'bias': Decimal('0'),
            'accuracy': accuracy
        }
