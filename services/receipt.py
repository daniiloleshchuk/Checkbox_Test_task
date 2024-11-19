from typing import List, Optional

from dto import ReceiptCreate, Receipt, ReceiptFilters
from repositories import ReceiptRepository


class ReceiptService:
    @classmethod
    def _validate(cls, receipt: ReceiptCreate) -> None:
        amount_paid = receipt["payment"]["amount"]
        total = sum([p["price"] * p.get("quantity", 1) for p in receipt["products"]])
        if amount_paid < total:
            raise ValueError("Not enough money. Total is bigger than amount paid")

    @classmethod
    def _format_number(cls, number: float) -> str:
        return f"{number:,.2f}".replace(",", " ")

    @classmethod
    async def create(cls, receipt: ReceiptCreate, user_id: int) -> Receipt:
        cls._validate(receipt)
        return await ReceiptRepository.save(receipt, user_id)

    @classmethod
    async def get(cls, filters: Optional[ReceiptFilters]) -> List[Receipt]:
        return await ReceiptRepository.get(filters)

    @classmethod
    def format_receipt(cls, receipt: dict, line_width: int) -> str:
        seller = "ФОП Джонсонюк Борис"
        header = seller.center(line_width)
        separator = "=" * line_width
        footer = "Дякуємо за покупку!".center(line_width)
        date_time = receipt["created_at"].strftime("%d.%m.%Y %H:%M").center(line_width)

        product_lines = []
        for product in receipt["products"]:
            quantity_price = (
                f"{cls._format_number(product['quantity'])} x {cls._format_number(product['price'])}"
            )
            product_total = cls._format_number(product["total"])
            product_name = product["name"]

            product_lines.append(quantity_price)

            if len(product_name) + len(product_total) + 1 > line_width:
                chunks = [
                    product_name[i:i + (line_width - 1)]
                    for i in range(0, len(product_name), line_width - 1)
                ]

                product_lines.extend(chunks[:-1])

                product_lines.append(
                    f"{chunks[-1].ljust(line_width - len(product_total))}{product_total}"
                )
            else:
                product_lines.append(
                    f"{product_name.ljust(line_width - len(product_total))}{product_total}"
                )

        total = float(receipt["total"])
        amount_paid = float(receipt["payment"]["amount"])
        rest = float(receipt["rest"])

        total_line = f"СУМА".ljust(line_width // 2) + cls._format_number(total).rjust(line_width // 2)
        payment_line = f"{receipt['payment']['type']}".ljust(line_width // 2) + cls._format_number(amount_paid).rjust(
            line_width // 2)
        change_line = f"Решта".ljust(line_width // 2) + cls._format_number(rest).rjust(line_width // 2)

        return "\n".join([
            header,
            separator,
            *product_lines,
            separator,
            total_line,
            payment_line,
            change_line,
            separator,
            date_time,
            footer,
        ])
