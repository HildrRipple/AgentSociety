from datetime import datetime
from typing import Any
from decimal import Decimal
from sqlalchemy import Text, TIMESTAMP, DECIMAL
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base

__all__ = ["Base", "TABLE_PREFIX"]


# Define decimal types for type annotations
class BillDecimal(Decimal):
    pass  # 6 decimal places for bills


class AccountDecimal(Decimal):
    pass  # 2 decimal places for accounts


# The base class of sqlalchemy models
Base = declarative_base(
    type_annotation_map={
        Any: JSONB,
        str: Text,
        datetime: TIMESTAMP(timezone=True),
        Decimal: DECIMAL,
        BillDecimal: DECIMAL(precision=18, scale=6),
        AccountDecimal: DECIMAL(precision=18, scale=2),
    }
)

TABLE_PREFIX = "as_"
