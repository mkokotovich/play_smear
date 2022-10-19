from apps.user.serializers import UserSummarySerializer


def jwt_response_payload_handler(token, user=None, request=None, issued_at=None):
    return {
        'token': token,
        'user': UserSummarySerializer(user, context={'request': request}).data
    }
