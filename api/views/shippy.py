import os

from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login

from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from drf_chunked_upload.serializers import ChunkedUploadSerializer
from drf_chunked_upload.views import ChunkedUploadView
from rest_framework.authtoken.models import Token
from rest_framework.decorators import permission_classes, api_view
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_401_UNAUTHORIZED, HTTP_400_BAD_REQUEST, HTTP_200_OK, HTTP_404_NOT_FOUND

from config.settings import SHIPPER_VERSION
from shipper.exceptions import UploadException
from shipper.handler import handle_chunked_build
from shipper.models import Device, Build


from config import settings

# Serializer for overriding success url
class V1MaintainersChunkedUploadSerializer(ChunkedUploadSerializer):
    # noinspection SpellCheckingInspection
    viewname = 'v1_maintainers_chunked_upload_detail'


class V1MaintainersChunkedUpload(ChunkedUploadView):
    serializer_class = V1MaintainersChunkedUploadSerializer

    def on_completion(self, chunked_upload, request) -> Response:
        """
        Validates chunked upload and transfers to handler
        """
        device_codename = get_codename_from_filename(chunked_upload.filename)
        device = get_object_or_404(Device, codename=device_codename)

        # Check if maintainer is in device's approved maintainers list
        if self.request.user not in device.maintainers.all():
            chunked_upload.delete()
            return Response(
                {
                    'error': 'insufficient_permissions',
                    'message': 'You are not authorized to upload for this device!'
                },
                status=HTTP_401_UNAUTHORIZED
            )

        try:
            build_id = handle_chunked_build(device, chunked_upload, request.POST.get('md5'))
        except UploadException as exception:
            chunked_upload.delete()
            return Response(
                {
                    'error': str(exception),
                    'message': exception_to_message(exception)
                },
                status=HTTP_400_BAD_REQUEST
            )

        # Upload was successful, update user's last login timestamp
        update_last_login(None, self.request.user)

        return Response(
            {
                'message': 'Build has been uploaded for device {}!'.format(device),
                'build_id': build_id
            },
            status=HTTP_200_OK
        )


def get_codename_from_filename(filename):
    fields = os.path.splitext(filename)[0].split(settings.SHIPPER_FILE_NAME_FORMAT_DELIMITER)
    # Check field count
    if len(fields) != 6:
        return None
    return fields[2]  # Codename


@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
def v1_maintainers_login(request):
    username = request.data.get("username")
    password = request.data.get("password")
    if username is None or password is None:
        return Response(
            {
                'error': 'blank_username_or_password',
                'message': 'Username or password cannot be blank!'
            },
            status=HTTP_400_BAD_REQUEST
        )
    user = authenticate(username=username, password=password)
    if not user:
        return Response({
            'error': 'invalid_credential',
            'message': 'Invalid credentials. Please try again.'
        },
            status=HTTP_404_NOT_FOUND
        )

    # Update login timestamp
    update_last_login(None, user)

    # Generate and return token
    token, _ = Token.objects.get_or_create(user=user)
    return Response(
        {
            'token': token.key,
            'message': 'Successfully logged in!'
        },
        status=HTTP_200_OK
    )


@csrf_exempt
@api_view(["GET"])
@permission_classes((AllowAny,))
def v1_system_info(_):
    return Response(
        {
            'version': SHIPPER_VERSION
        }
    )


@csrf_exempt
@api_view(["GET"])
def v1_maintainers_token_check(request):
    # Update login timestamp
    update_last_login(None, request.user)

    return Response(
        {
            'username': request.user.username
        },
        status=HTTP_200_OK
    )


@csrf_exempt
@api_view(["POST"])
def v1_maintainers_build_enabled_status_modify(request):
    build_id = request.data.get("build_id")
    enable = request.data.get("enable")
    if build_id is None or enable is None:
        return Response(
            {
                'error': 'missing_parameters',
                'message': 'One or more of the required parameters is blank! Required parameters: build ID, '
                           'enabled flag'
            },
            status=HTTP_400_BAD_REQUEST
        )

    build = get_object_or_404(Build, pk=build_id)
    enable = enable.lower() == "true"

    # Check if maintainer has permission to modify this build/device
    if request.user not in build.device.maintainers.all():
        return Response(
            {
                'error': 'insufficient_permissions',
                'message': 'You are not authorized to modify builds associated with this device!'
            },
            status=HTTP_401_UNAUTHORIZED
        )

    # Switch build status
    build.enabled = enable
    build.save()

    # Update login timestamp
    update_last_login(None, request.user)

    if enable:
        return Response(
            {
                'message': 'Successfully enabled the build!'
            },
            status=HTTP_200_OK
        )
    else:
        return Response(
            {
                'message': 'Successfully disabled the build!'
            },
            status=HTTP_200_OK
        )


def exception_to_message(e):
    e = str(e)
    if e == 'file_name_mismatch':
        return "The file name does not match the checksum file name!"
    if e == 'invalid_file_name':
        return "The file name was malformed. Please do not edit the file name!"
    if e == 'not_official':
        return "Only official builds are allowed."
    if e == 'codename_mismatch':
        return "The codename does not match the file!"
    if e == 'duplicate_build':
        return "The build already exists in the system!"
    return "An unknown error occurred."
