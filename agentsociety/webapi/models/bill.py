"""
账户系统模型，包含用户账户、消费记录、充值记录等
"""

from datetime import datetime
from typing import Optional
import uuid
from decimal import Decimal
from enum import Enum
from pydantic import AwareDatetime, BaseModel
from sqlalchemy import Index
from sqlalchemy.orm import Mapped, mapped_column

from ._base import TABLE_PREFIX, Base, BillDecimal

__all__ = ["Bill", "ApiBill", "Account", "ApiAccount", "ItemEnum"]


class ItemEnum(str, Enum):
    """账单项目枚举"""
    RECHARGE = "recharge"
    LLM_INPUT_TOKEN = "llm_input_token"
    LLM_OUTPUT_TOKEN = "llm_output_token"
    RUNTIME = "run_time"


class Account(Base):
    """账户记录"""

    __tablename__ = f"{TABLE_PREFIX}account"

    tenant_id: Mapped[str] = mapped_column(primary_key=True)
    """租户ID"""
    balance: Mapped[BillDecimal] = mapped_column(default=Decimal(0))
    """余额，单位：元，保留6位小数"""
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    """创建时间"""
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.now, onupdate=datetime.now
    )


class Bill(Base):
    """账单记录，未完成支付的充值不进入账单"""

    __tablename__ = f"{TABLE_PREFIX}bill"

    tenant_id: Mapped[str] = mapped_column(primary_key=True)
    """租户ID"""
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    """账单ID"""
    related_exp_id: Mapped[uuid.UUID] = mapped_column(nullable=True)
    """关联实验ID"""
    item: Mapped[str] = mapped_column(primary_key=True)
    """项目类型ID"""
    amount: Mapped[BillDecimal] = mapped_column()
    """账单金额，单位：元，保留6位小数，负值为消费，正值为充值"""
    unit_price: Mapped[BillDecimal] = mapped_column()
    """单价，单位：元，保留6位小数"""
    quantity: Mapped[float] = mapped_column()
    """数量"""
    description: Mapped[str] = mapped_column()
    """账单描述"""
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    """创建时间"""

    __table_args__ = (
        Index("idx_tenant_id_related_exp_id", "tenant_id", "related_exp_id"),
    )


class ApiAccount(BaseModel):
    """账户记录"""

    balance: Decimal
    """余额，单位：元，保留2位小数"""
    created_at: AwareDatetime
    """创建时间"""
    updated_at: AwareDatetime
    """更新时间"""

    class Config:
        from_attributes = True


class ApiBill(BaseModel):
    """账单记录，未完成支付的充值不进入账单"""

    id: uuid.UUID
    """账单ID"""
    related_exp_id: Optional[uuid.UUID]
    """关联实验ID"""
    item: str
    """项目"""
    amount: Decimal
    """账单金额，单位：元，保留6位小数，负值为消费，正值为充值"""
    unit_price: Decimal
    """单价，单位：元，保留6位小数"""
    quantity: float
    """数量"""
    description: str
    """账单描述"""
    created_at: AwareDatetime
    """创建时间"""

    class Config:
        from_attributes = True
