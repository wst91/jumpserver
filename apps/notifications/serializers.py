from rest_framework import serializers

from .models import Subscription


class SubscriptionSerializer(serializers.ModelSerializer):
    receive_backends = serializers.ListField(child=serializers.CharField())

    class Meta:
        model = Subscription
        fields = ('users', 'groups', 'app_name', 'message', 'receive_backends')
