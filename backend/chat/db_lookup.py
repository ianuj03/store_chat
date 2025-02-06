import json
from datetime import datetime
from channels.db import database_sync_to_async
from django.core.exceptions import FieldError, ValidationError

from orders.models import Order, OrderItem
from customers.models import Customer
from products.models import Product

MODEL_MAPPING = {
    "Order": Order,
    "Customer": Customer,
    "Product": Product,
    "OrderItem": OrderItem
}

OPERATOR_MAPPING = {
    ">=": "gte",
    "<=": "lte",
    ">": "gt",
    "<": "lt",
    "!=": "ne",
    "=": "exact"
}

def convert_filter_key(key):
    for operator, lookup in OPERATOR_MAPPING.items():
        if operator in key:
            field = key.split(operator)[0].strip()
            return f"{field}__{lookup}"
    return key

def parse_date(value):
    if isinstance(value, str):
        for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%m/%d/%Y"):
            try:
                return datetime.strptime(value, fmt).date().isoformat()
            except ValueError:
                continue
    return value

@database_sync_to_async
def get_filtered_queryset(ModelClass, filters, fields):
    print(f"Running DB Query on Model: {ModelClass.__name__}")
    print(f"Filters: {filters}")
    print(f"Fields: {fields}")

    for key, value in filters.items():
        if 'date' in key or 'created_at' in key:
            filters[key] = parse_date(value)

    try:
        queryset = ModelClass.objects.filter(**filters)
        result = list(queryset.values(*fields)) if fields else list(queryset.values())
        print(f"DB Query Result: {result}")
        return result
    except (FieldError, ValidationError) as e:
        print(f"Validation Error: {e}")
        return {"error": f"Invalid filter: {str(e)}"}
    except Exception as e:
        print(f"Unexpected Error: {e}")
        return {"error": f"Unexpected error: {str(e)}"}

async def perform_db_lookup(lookup_spec: dict):
    model_name = lookup_spec.get("model")
    filters = lookup_spec.get("filters", {})
    fields = lookup_spec.get("fields", [])

    if not model_name or model_name not in MODEL_MAPPING:
        return {"error": "Invalid model name"}

    ModelClass = MODEL_MAPPING[model_name]
    converted_filters = {convert_filter_key(k): v for k, v in filters.items()}
    results = await get_filtered_queryset(ModelClass, converted_filters, fields)
    return results

