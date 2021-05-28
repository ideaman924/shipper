import datetime

from django.contrib.auth.models import AnonymousUser
from django.test import TestCase, RequestFactory

from api.views import parse_build_date, v1_updater_los, v2_updater_device
from shipper.tests import mock_devices_setup, mock_builds_setup


class APIGeneralTestCase(TestCase):
    def test_parse_build_date(self):
        self.assertEqual(parse_build_date("20200824"), datetime.date(2020, 8, 24))
        self.assertEqual(parse_build_date("20200824").strftime("%s"), "1598227200")


class APIV1TestCase(TestCase):
    def setUp(self):
        mock_devices_setup()
        mock_builds_setup()
        self.factory = RequestFactory()

    def test_v1_updater_los(self):
        request = self.factory.get("/api/v1/updater/los/")
        request.user = AnonymousUser()
        response = v1_updater_los(request, "bullhead", "gapps")
        expected_response = b'{"response": [{"datetime": 1591574400, "filename": ' \
                            b'"Bliss-v14-bullhead-OFFICIAL-gapps-20200608.zip", ' \
                            b'"id": "b9566ebc192a4c27c72df19eae8a6eed6ea063226792e680fa0b2ede284e19f2", ' \
                            b'"size": 857483855, "version": "v14", "variant": "gapps", ' \
                            b'"url": "https://testserver/media/bullhead/Bliss-v14-bullhead-OFFICIAL-gapps-20200608' \
                            b'.zip", "md5url": ' \
                            b'"https://testserver/media/bullhead/Bliss-v14-bullhead-OFFICIAL-gapps-20200608.zip.md5' \
                            b'"}]}'

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, expected_response)


class APIV2TestCase(TestCase):
    def setUp(self):
        mock_devices_setup()
        mock_builds_setup()
        self.factory = RequestFactory()

    def test_v2_updater(self):
        request = self.factory.get("/api/v2/updater/")
        request.user = AnonymousUser()
        response = v2_updater_device(request, "bullhead", "gapps")
        expected_response = b'{"date": 1591574400, "file_name": "Bliss-v14-bullhead-OFFICIAL-gapps-20200608.zip", ' \
                            b'"sha256": "b9566ebc192a4c27c72df19eae8a6eed6ea063226792e680fa0b2ede284e19f2", ' \
                            b'"size": 857483855, "version": "v14", "zip_download_url": ' \
                            b'"https://testserver/media/bullhead/Bliss-v14-bullhead-OFFICIAL-gapps-20200608.zip", ' \
                            b'"md5_download_url": ' \
                            b'"https://testserver/media/bullhead/Bliss-v14-bullhead-OFFICIAL-gapps-20200608.zip.md5"}'

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, expected_response)

