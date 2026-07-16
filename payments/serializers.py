# Import serializer classes used to convert model instances to and from JSON.
from rest_framework import serializers

# Import the Payment model to be serialized.
from .models import Payment


# Serializer for Payment model instances.
class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        # Specify the model this serializer is based on.
        model = Payment

        # Define the fields included in the serialized representation.
        fields = [
            "id",
            "user",
            "order",
            "method",
            "status",
            "amount",
            "currency",
            "transaction_id",
            "created_at",
            "updated_at",
        ]
