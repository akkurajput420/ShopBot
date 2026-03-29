import re
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional, Annotated
# Python 3.10 compatibility ke liye ye zaroori hai
from typing_extensions import Self 
from pydantic import BaseModel, Field, StringConstraints, field_validator, model_validator

# --- YEH CLASS ADD KI GAYI HAI ---
class CategoryRequest(BaseModel):
    """Validate Product Categories"""
    name: Annotated[str, StringConstraints(min_length=2, max_length=50, strip_whitespace=True)]
    description: Optional[str] = Field(None, max_length=200)
    is_active: bool = Field(True)

    @field_validator('name')
    @classmethod
    def validate_category_name(cls, v: str) -> str:
        # Sirf alphanumeric aur spaces allow karne ke liye
        if not re.match(r'^[a-zA-Z0-9\s]+$', v):
            raise ValueError('Category name mein sirf letters, numbers aur spaces allowed hain')
        return v
# --------------------------------

class PaymentRequest(BaseModel):
    """Store Bot Payment Validation (INR Focus)"""
    amount: Decimal = Field(..., gt=0, le=50000)
    currency: str = Field("INR", min_length=3, max_length=3)
    provider: str = Field(..., pattern="^(telegram|stars|cryptopay|fiat)$")

    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v: Decimal) -> Decimal:
        if v < Decimal("10"):
            raise ValueError('Minimum payment ₹10 honi chahiye')
        if abs(v.as_tuple().exponent) > 2:
            raise ValueError('Amount mein 2 se zyada decimal places nahi ho sakte')
        return v

class ItemPurchaseRequest(BaseModel):
    """Validate TG Account / Digital Item Purchase"""
    item_name: Annotated[str, StringConstraints(min_length=1, max_length=100, strip_whitespace=True)]
    user_id: int = Field(..., gt=0)

    @field_validator('item_name')
    @classmethod
    def validate_item_name(cls, v: str) -> str:
        if re.search(r'[\x00-\x1f\x7f<>]', v):
            raise ValueError('Item name mein invalid characters hain')
        return v

class UserDataUpdate(BaseModel):
    """Update User Balance and Stats"""
    telegram_id: int = Field(..., gt=0)
    balance: Optional[Decimal] = Field(None, ge=0, le=1000000)

    @field_validator('balance')
    @classmethod
    def validate_balance(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        if v is not None:
            return v.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return v

class BroadcastMessage(BaseModel):
    """Validate HTML Broadcasts for Channel/Users"""
    text: Annotated[str, StringConstraints(min_length=1, max_length=4096)]
    parse_mode: Optional[str] = Field("HTML", pattern="^(HTML|Markdown|MarkdownV2)$")

    @model_validator(mode='after')
    def validate_html_tags(self) -> Self:
        if self.parse_mode == 'HTML':
            allowed_tags = ['b', 'i', 'u', 's', 'code', 'pre', 'a']
            for tag in allowed_tags:
                opened = len(re.findall(f'<{tag}(?:\s+[^>]*)?>', self.text))
                closed = self.text.count(f'</{tag}>')
                if opened != closed:
                    raise ValueError(f'HTML Tag "{tag}" sahi se close nahi kiya gaya hai')
        return self

class PromoCodeRequest(BaseModel):
    """Validate Store Promo Codes"""
    code: Annotated[str, StringConstraints(min_length=3, max_length=20, strip_whitespace=True)]

    @field_validator('code')
    @classmethod
    def validate_code(cls, v: str) -> str:
        v = v.upper()
        if not re.match(r'^[A-Z0-9_]+$', v):
            raise ValueError('Promo code mein sirf A-Z, 0-9 aur Underscore allowed hai')
        return v

# --- Utility Functions ---
def validate_telegram_id(telegram_id) -> int:
    try:
        tid = int(telegram_id)
        if 10000 <= tid <= 9999999999:
            return tid
        raise ValueError
    except (ValueError, TypeError):
        raise ValueError("Invalid Telegram ID format")

def validate_money_amount(amount) -> Decimal:
    try:
        d = Decimal(str(amount)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        if d < Decimal("0.01"):
            raise ValueError("Amount too small")
        return d
    except Exception:
        raise ValueError("Invalid amount format")
