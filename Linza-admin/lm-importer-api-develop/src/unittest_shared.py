import unittest
from shared import define_type, define_source_url, is_uuid4, local_datetime_from_string, localize_imported_dates
import datetime


class TestIsUUID(unittest.TestCase):
    def test_is_uuid(self):
        self.assertTrue(is_uuid4("adfb01f4-e424-4cb9-bed9-a5b4466365cc"))


class TestDefineType(unittest.TestCase):

    def test_result_is_string(self):
        self.assertIsInstance(define_type("http://ya.ru"), str)

    def test_web(self):
        self.assertEqual(define_type('http://ya.ru/news'), "web")

    def test_vk(self):
        self.assertEqual(define_type(
            'http://vk.com/ohkorolev'), "socialnetworks/vk")

    def test_twitter(self):
        self.assertEqual(
            define_type(
                'https://twitter.com/tikaipo/status/1168853969843773440'),
            "socialnetworks/twitter")

    def test_facebook(self):
        self.assertEqual(
            define_type(
                'https://web.facebook.com/garmin.ru/posts/2465810703478576'),
            "socialnetworks/facebook")

    def test_instagram(self):
        self.assertEqual(define_type(
            'https://www.instagram.com/p/B02_e68Bbrc/'), "socialnetworks/instagram")

    def test_youtube(self):
        self.assertEqual(define_type(
            "https://www.youtube.com/watch?v=2kdRydMtWJg"), "socialnetworks/youtube")

    def test_livejournal(self):
        self.assertEqual(define_type(
            "https://textinthepiter.livejournal.com/62069.html"), "socialnetworks/livejournal")

    def test_telegram(self):
        self.assertEqual(define_type(
            "https://t.me/taranators/371144"), "messengers/telegram")


class TestDefineSourceUrl(unittest.TestCase):

    def test_result_is_string(self):
        self.assertIsInstance(define_source_url("https://ya.ru"), str)

    def test_web(self):
        self.assertEqual(define_source_url(
            "http://ya.ru/news"), "http://ya.ru")

    def test_twitter(self):
        self.assertEqual(
            define_source_url(
                "https://twitter.com/tikaipo/status/1168853969843773440"),
            "https://twitter.com/tikaipo")

    def test_facebook(self):
        self.assertEqual(define_source_url("https://web.facebook.com/garmin.ru/posts/2465810703478576"),
                         "https://web.facebook.com/garmin.ru")

    def test_livejournal(self):
        self.assertEqual(
            define_source_url(
                "https://textinthepiter.livejournal.com/62069.html"),
            "https://textinthepiter.livejournal.com")

    def test_telegram(self):
        self.assertEqual(
            define_source_url("https://t.me/taranators/371144"),
            "https://t.me/taranators")


class TestLocalDateTimeFromString(unittest.TestCase):

    def test_result_is_datetime_obj(self):
        date = local_datetime_from_string(date_string="09:37 05.09.2019",
                                          source_timezone="Asia/Yekaterinburg",
                                          languages=["en"],
                                          url="http://example.com/")
        self.assertIsInstance(date, datetime.datetime)

    def test_localizing_naive(self):
        date_now = datetime.datetime.utcnow()
        date = local_datetime_from_string(date_string="09:37 05.01.{}".format(date_now.year),
                                          source_timezone="Asia/Yekaterinburg",
                                          languages=["ru"],
                                          url="http://example.com")
        date_str = str(date)
        self.assertEqual(
            date_str, "{}-01-05 09:37:00+05:00".format(date_now.year))

    def test_localizing_naive_time_fails(self):
        date_now = datetime.datetime.utcnow()
        date = local_datetime_from_string(date_string="09:37 05.09.{}".format(date_now.year),
                                          source_timezone="Asia/Yekaterinburg",
                                          languages=["en"],
                                          url="http://example.com")
        date_str = str(date)
        self.assertNotEqual(
            date_str, "{}-05-09 06:37:00+03:00".format(date_now.year))

    def test_localizing_naive_tz_fails(self):
        date = local_datetime_from_string(date_string="09:37 05.09.{}".format(datetime.datetime.utcnow().year),
                                          source_timezone="Asia/Yekaterinburg",
                                          languages=["en"],
                                          url="http://example.com/")
        date_str = str(date)
        self.assertNotEqual(
            date_str, "{}-05-09 07:37:00+04:00".format(datetime.datetime.utcnow().year))

    def test_osurgut_com_correct(self):
        osurgut_date = "08:32 | 01.10.{}".format(
            datetime.datetime.utcnow().year)
        localized_date = local_datetime_from_string(date_string=osurgut_date,
                                                    source_timezone="Asia/Yekaterinburg",
                                                    languages=["ru"],
                                                    url="http://osurgut.com/ewew")
        self.assertEqual(str(
            localized_date), "{}-10-01 08:32:00+05:00".format(datetime.datetime.utcnow().year))

    def test_osurgut_com_not_us_like(self):
        """if using languages=["ru"] then date is parsed in ru format"""
        osurgut_date = "08:32 | 10.01.{}".format(
            datetime.datetime.utcnow().year)
        localized_date = local_datetime_from_string(date_string=osurgut_date,
                                                    source_timezone="Asia/Yekaterinburg",
                                                    languages=["ru"],
                                                    url="http://osurgut.com")
        self.assertEqual(str(
            localized_date), "{}-01-10 08:32:00+05:00".format(datetime.datetime.utcnow().year))

    # TODO: Repair tests -> this is the problem with MONTH <-> DAY switching
    def test_ugra_mk_ru_correct_pub_date(self):
        date_ = "{}-01-10T14:51:00+0300".format(datetime.datetime.now().year)
        localized_date = local_datetime_from_string(date_string=date_,
                                                    source_timezone="Europe/Moscow",
                                                    languages=["ru"],
                                                    url="http://ugra.mk.ru/cwe")
        self.assertEqual(str(
            localized_date), "{}-01-10 14:51:00+03:00".format(datetime.datetime.utcnow().year))

    def test_pravda_urfo_ru_correct_pub_date(self):
        date_ = "2020-12-01T23:17:45+05:00"
        localized_date = local_datetime_from_string(date_string=date_,
                                                    source_timezone="Asia/Yekaterinburg",
                                                    languages=["ru"], url="http://pravdaurfo.ru/qc")
        self.assertEqual(str(
            localized_date), "2020-12-01 23:17:45+05:00".format(datetime.datetime.utcnow().year))

    def test_2_goroda_ru_correct_pub_date(self):
        date_ = "01.09.2020 - 02:40"
        localized_date = local_datetime_from_string(date_string=date_,
                                                    source_timezone="Asia/Yekaterinburg",
                                                    languages=["ru"], url="http://2goroda.ru/112")
        self.assertEqual(str(
            localized_date), "2020-09-01 02:40:00+05:00".format(datetime.datetime.utcnow().year))

    def test_ugra_mk_ru_wrong_mongh_and_year(self):
        date_ = "2020-01-10T14:51:00+0300"
        localized_date = local_datetime_from_string(date_string=date_,
                                                    source_timezone="Europe/Moscow",
                                                    languages=["ru"],
                                                    url="http://ugra.mk.ru/12")
        self.assertEqual(str(localized_date), "2020-01-10 14:51:00+03:00")

    def test_hantimansiysk_bezformata_com_pub_dtae(self):
        date_ = "01.10.2020 14:25"
        localized_date = local_datetime_from_string(date_string=date_,
                                                    source_timezone="Asia/Yekaterinburg",
                                                    languages=["ru"],
                                                    url="https://hantimansiysk.bezformata.com/listnews/predstaviteley-starshego-pokoleniya/87639376/")
        self.assertEqual(str(localized_date), "2020-10-01 14:25:00+05:00")

    def test_ugra_aif_ru_pub_dtae(self):
        date_ = "2020-10-01T16:02"
        localized_date = local_datetime_from_string(date_string=date_,
                                                    source_timezone="Asia/Yekaterinburg",
                                                    languages=["ru"],
                                                    url="https://ugra.aif.ru/society/people/v_yugre_startuet_osennyaya_nedelya_dobra")
        self.assertEqual(str(localized_date), "2020-10-01 16:02:00+05:00")

    def test_ura_ru_correct(self):
        d = "24 января 2020 в 22:49"
        d_local = local_datetime_from_string(date_string=d,
                                             source_timezone="Europe/Moscow",
                                             languages=["ru"], url="https://ugra.ru/wcew/c"
                                             )
        self.assertEqual(str(d_local), "2020-01-24 22:49:00+03:00")

    def test_vestniksr_ru_correct(self):
        d = "2020-01-22T06:50:00+03:00"
        d_local = local_datetime_from_string(date_string=d,
                                             source_timezone="Europe/Moscow",
                                             languages=["ru"],
                                             url="http://vestniksr.ru/ffee"
                                             )
        self.assertEqual(str(d_local), "2020-01-22 06:50:00+03:00")

    def test_k_inform_ru_correct(self):
        d = "18 янв., 09:52"
        now_year = datetime.datetime.utcnow().year
        d_local = local_datetime_from_string(date_string=d,
                                             source_timezone="Europe/Moscow",
                                             languages=["ru"],
                                             url="https://k-inform.com/1440.html"
                                             )
        self.assertEqual(
            str(d_local), "{}-01-18 09:52:00+03:00".format(now_year))

    def test_newdaynews_correct(self):
        d = "2020-12-13T08:18Z"
        d_local = local_datetime_from_string(date_string=d,
                                             source_timezone="Europe/Moscow",
                                             languages=["ru"],
                                             url="https://newdaynews.ru/coronavirus-covid-19/711176.html"
                                             )
        self.assertEqual(str(d_local), "2020-12-13 08:18:00+03:00")

    def test_returns_correct_value_when_z_format_string_provided(self):
        # arrange
        parsedString = "2020-07-08T01:02:03Z"  # Z
        sourceTimezone = "Europe/Moscow"
        languages = ["ru"]
        url = "http://testurl.ru/"

        expected = datetime.datetime.fromisoformat(
            '2020-07-08 01:02:03.000+03:00')

        # act
        actual = local_datetime_from_string(
            parsedString, sourceTimezone, languages, url)

        # assert
        self.assertEqual(expected, actual)


class TestStaticPath(unittest.TestCase):
    def test_is_str(self):
        self.assertIsInstance(api.static_path, str)


class TestImportDateLocalize(unittest.TestCase):
    date = datetime.datetime(year=2019, month=12, day=12, hour=19, minute=20)

    def test_result_is_datetime_obj(self):
        loc_date = localize_imported_dates(date=self.date,
                                           dest_timezone="Europe/Moscow")
        self.assertIsInstance(loc_date, datetime.datetime)

    def test_result_has_tz(self):
        date = localize_imported_dates(date=self.date,
                                       dest_timezone="Europe/Moscow")
        self.assertEqual(str(date), "2019-12-12 19:20:00+03:00")

# TODO: Fix this
# class TestCheckVkDate(unittest.TestCase):
#
#     def test_return_correct_if_new_year(self):
#         correct_date = "2019-12-29 01:02:03"
#         correct_date = dateparser.parse(correct_date)
#         post_december = "2020-12-29 01:02:03"
#         post_december = dateparser.parse(post_december)
#         pass
#         self.assertEqual(check_vk_year(post_december), correct_date)
