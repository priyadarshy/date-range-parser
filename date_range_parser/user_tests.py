
import unittest
import date_range_parser

import pytz, datetime, operator
from datetime import timedelta


class BasicTests(unittest.TestCase):

    def setUp(self):
        self.tz_name = u'America/New_York'
        self.timezone = pytz.timezone(self.tz_name)
        self.src_time = self.timezone.localize(datetime.datetime(2014, 8, 3, 10, 0, 32))

    def _compareResults(self, result, truth_dt_tuple):
        self.assertEqual((result[u'startDate'], result[u'endDate']), \
                (truth_dt_tuple[0].isoformat(), truth_dt_tuple[1].isoformat()))

    def _compareReconvertibleText(self, nltext, src_time):
        original = date_range_parser.parse(nltext, src_time)
        original_res = original.get(u'result')
        recon_text = original.get(u'parse')[0].get(u'reconvertible_text')
        recon = date_range_parser.parse(recon_text, src_time)
        recon_res = recon.get(u'result')
        self.assertEqual(original_res, recon_res)

    def test_basic_calendar_dates(self):
        # Currently on the weekend, test "this week"
        monday = self.timezone.localize(datetime.datetime(2014, 8, 4, 0, 0, 0))
        tuesday = monday + datetime.timedelta(days=1)
        wednesday = tuesday + datetime.timedelta(days=1)
        thursday = wednesday + datetime.timedelta(days=1)
        friday = thursday + datetime.timedelta(days=1)
        saturday = friday + datetime.timedelta(days=1)
        sunday = saturday + datetime.timedelta(days=1)
        next_monday = sunday + datetime.timedelta(days=1)
        last_sunday = monday + datetime.timedelta(days=-1)
        # Construct the two part of the last day in this month.
        first_day_september = monday.replace(month=9, day=1)
        last_day_august = first_day_september + datetime.timedelta(days=-1)
        first_day_october = monday.replace(month=10, day=1)
        last_day_september = first_day_october + datetime.timedelta(days=-1)



        r1 = date_range_parser.parse(u'this week', self.src_time).get(u'result')
        # Check that each day showed up.
        self._compareResults(r1[0], (monday, tuesday))
        self._compareResults(r1[1], (tuesday, wednesday))
        self._compareResults(r1[2], (wednesday, thursday))
        self._compareResults(r1[3], (thursday, friday))
        self._compareResults(r1[4], (friday, saturday))

        r1 = date_range_parser.parse(u'in two weeks', self.src_time).get(u'result')
        # Check that each day showed up.
        self._compareResults(r1[0], (monday+timedelta(days=14), tuesday+timedelta(days=14)))
        self._compareResults(r1[1], (tuesday+timedelta(days=14), wednesday+timedelta(days=14)))
        self._compareResults(r1[2], (wednesday+timedelta(days=14), thursday+timedelta(days=14)))
        self._compareResults(r1[3], (thursday+timedelta(days=14), friday+timedelta(days=14)))
        self._compareResults(r1[4], (friday+timedelta(days=14), saturday+timedelta(days=14)))

        r1 = date_range_parser.parse(u'in three weeks', self.src_time).get(u'result')
        # Check that each day showed up.
        self._compareResults(r1[0], (monday+timedelta(days=21), tuesday+timedelta(days=21)))
        self._compareResults(r1[1], (tuesday+timedelta(days=21), wednesday+timedelta(days=21)))
        self._compareResults(r1[2], (wednesday+timedelta(days=21), thursday+timedelta(days=21)))
        self._compareResults(r1[3], (thursday+timedelta(days=21), friday+timedelta(days=21)))
        self._compareResults(r1[4], (friday+timedelta(days=21), saturday+timedelta(days=21)))

        r2 = date_range_parser.parse(u'next week', self.src_time).get(u'result')
        # Still need to fix how we handle this/next weekend.
        # Since its Sunday this week and next week should be the same.
        #
        #self._compareResults(r2[0], (monday, tuesday))
        #self._compareResults(r2[1], (tuesday, wednesday))
        #self._compareResults(r2[2], (wednesday, thursday))
        #self._compareResults(r2[3], (thursday, friday))
        #self._compareResults(r2[4], (friday, saturday))

        r3 = date_range_parser.parse(u'next weekend', self.src_time).get(u'result')
        # Should give us a range of two days.
        self._compareResults(r3[0], (saturday, sunday))
        self._compareResults(r3[1], (sunday, next_monday))

        r4 = date_range_parser.parse(u'this weekend', monday).get(u'result')
        # Switch the day src time to monday so this weekend should move forward.
        self._compareResults(r4[0], (saturday, sunday))
        self._compareResults(r4[1], (sunday, next_monday))

        r5 = date_range_parser.parse(u'next weekend', monday).get(u'result')
        # With Monday as the src_time next weekend should move even further forward a week.
        self._compareResults(r5[0], (saturday+datetime.timedelta(days=7), sunday+datetime.timedelta(days=7)))
        self._compareResults(r5[1], (sunday+datetime.timedelta(days=7), next_monday+datetime.timedelta(days=7)))

        r6 = date_range_parser.parse(u'this month', self.src_time).get(u'result')
        self._compareResults(r6[-1], (last_day_august, first_day_september))
        #self.assertEqual(len(r6), first_day_september-1)

        r7 = date_range_parser.parse(u'next month', self.src_time).get(u'result')
        self._compareResults(r7[-1], (last_day_september, first_day_october))
        #self.assertEqual(len(r7), last_day_august.day-1)

        r8 = date_range_parser.parse(u'september', self.src_time).get(u'result')
        self._compareResults(r8[0], (first_day_september, first_day_september + timedelta(days=1)))
        self._compareResults(r8[-1], (last_day_september, first_day_october))
        self.assertEqual(len(r8), 30)

    def test_basic_absolute_dates(self):
        d8_18_sod = self.timezone.localize(datetime.datetime(2014, 8, 18))
        d8_18_eod = self.timezone.localize(datetime.datetime(2014, 8, 19))

        today_sod = self.timezone.localize(datetime.datetime(2014, 8,3))
        tomorrow_sod = self.timezone.localize(datetime.datetime(2014, 8, 4))
        tomorrow_eod = self.timezone.localize(datetime.datetime(2014, 8, 5))

        monday = tomorrow_sod
        tuesday = monday + datetime.timedelta(days=1)
        wednesday = tuesday + datetime.timedelta(days=1)
        thursday = wednesday + datetime.timedelta(days=1)

        next_wednesday = wednesday + datetime.timedelta(days=7)
        next_thursday = thursday + datetime.timedelta(days=7)

        r1 = date_range_parser.parse(u'8.18', self.src_time).get(u'result')
        self._compareResults(r1[0], (d8_18_sod, d8_18_eod))
        self.assertEqual(len(r1), 1)

        r1 = date_range_parser.parse(u'8/18', self.src_time).get(u'result')
        self._compareResults(r1[0], (d8_18_sod, d8_18_eod))
        self.assertEqual(len(r1), 1)

        r1 = date_range_parser.parse(u'08.18', self.src_time).get(u'result')
        self._compareResults(r1[0], (d8_18_sod, d8_18_eod))
        self.assertEqual(len(r1), 1)

        r1 = date_range_parser.parse(u'08/18', self.src_time).get(u'result')
        self._compareResults(r1[0], (d8_18_sod, d8_18_eod))
        self.assertEqual(len(r1), 1)

        r1 = date_range_parser.parse(u'8.18.14', self.src_time).get(u'result')
        self._compareResults(r1[0], (d8_18_sod, d8_18_eod))
        self.assertEqual(len(r1), 1)

        r1 = date_range_parser.parse(u'08/18/14', self.src_time).get(u'result')
        self._compareResults(r1[0], (d8_18_sod, d8_18_eod))
        self.assertEqual(len(r1), 1)

        r1 = date_range_parser.parse(u'08.18.2014', self.src_time).get(u'result')
        self._compareResults(r1[0], (d8_18_sod, d8_18_eod))
        self.assertEqual(len(r1), 1)

        r1 = date_range_parser.parse(u'08/18/2014', self.src_time).get(u'result')
        self._compareResults(r1[0], (d8_18_sod, d8_18_eod))
        self.assertEqual(len(r1), 1)

        r1 = date_range_parser.parse(u'August 18, 2014', self.src_time).get(u'result')
        self._compareResults(r1[0], (d8_18_sod, d8_18_eod))
        self.assertEqual(len(r1), 1)

        r1 = date_range_parser.parse(u'Aug 18, 2014', self.src_time).get(u'result')
        self._compareResults(r1[0], (d8_18_sod, d8_18_eod))
        self.assertEqual(len(r1), 1)

        r1 = date_range_parser.parse(u'Aug 18', self.src_time).get(u'result')
        self._compareResults(r1[0], (d8_18_sod, d8_18_eod))
        self.assertEqual(len(r1), 1)

        r1 = date_range_parser.parse(u'Aug 18th', self.src_time).get(u'result')
        self._compareResults(r1[0], (d8_18_sod, d8_18_eod))
        self.assertEqual(len(r1), 1)

        r1 = date_range_parser.parse(u'Aug 18th 2014', self.src_time).get(u'result')
        self._compareResults(r1[0], (d8_18_sod, d8_18_eod))
        self.assertEqual(len(r1), 1)

        r1 = date_range_parser.parse(u'on the 18th August 2014', self.src_time).get(u'result')
        self._compareResults(r1[0], (d8_18_sod, d8_18_eod))
        self.assertEqual(len(r1), 1)

        r1 = date_range_parser.parse(u'on the 18 August 2014', self.src_time).get(u'result')
        self._compareResults(r1[0], (d8_18_sod, d8_18_eod))
        self.assertEqual(len(r1), 1)

        r1 = date_range_parser.parse(u'on the 18 Aug 2014', self.src_time).get(u'result')
        self._compareResults(r1[0], (d8_18_sod, d8_18_eod))
        self.assertEqual(len(r1), 1)

        r1 = date_range_parser.parse(u'This is the fourth time I will say Aug 18th 2014', self.src_time).get(u'result')
        self._compareResults(r1[0], (d8_18_sod, d8_18_eod))
        self.assertEqual(len(r1), 1)

        r2 = date_range_parser.parse(u'today', self.src_time).get(u'result')
        self._compareResults(r2[0], (today_sod, tomorrow_sod))
        self.assertEqual(len(r2), 1)

        r3 = date_range_parser.parse(u'tomorrow', self.src_time).get(u'result')
        self._compareResults(r3[0], (tomorrow_sod, tomorrow_eod))
        self.assertEqual(len(r3), 1)

        r3 = date_range_parser.parse(u'wednesday', self.src_time).get(u'result')
        self._compareResults(r3[0], (wednesday, thursday))
        self.assertEqual(len(r3), 1)

        r4 = date_range_parser.parse(u'next wednesday', tomorrow_sod).get(u'result')
        self._compareResults(r4[0], (next_wednesday, next_thursday))
        self.assertEqual(len(r4), 1)

        r5 = date_range_parser.parse('monday', today_sod).get(u'result')
        self._compareResults(r5[0], (monday, tuesday ))
        self.assertEqual(len(r5), 1)

        r5 = date_range_parser.parse('monday', monday).get(u'result')
        self._compareResults(r5[0], (monday + timedelta(days=7), tuesday + timedelta(days=7)))
        self.assertEqual(len(r5), 1)

        r5 = date_range_parser.parse('next monday', tomorrow_sod).get(u'result')
        self._compareResults(r5[0], (monday + timedelta(days=7), tuesday + timedelta(days=7)))
        self.assertEqual(len(r5), 1)

    def test_absolute_inner_day_modifications(self):
        # Sunday 12:00 08/08/2014
        d8_3 = self.timezone.localize(datetime.datetime(2014, 8, 3))
        d8_4 = d8_3 + datetime.timedelta(days=1)
        td_10 = datetime.timedelta(hours=10)
        td_14 = datetime.timedelta(hours=14)

        # Test applying a date range to a single day.
        r1 = date_range_parser.parse(u'tomorrow between 10 - 2 pm', d8_3).get(u'result')
        self._compareResults(r1[0], (d8_4 + td_10, d8_4 + td_14))

        r1 = date_range_parser.parse(u'tomorrow from 9 - 11', d8_3).get(u'result')
        self._compareResults(r1[0], (d8_4 + timedelta(hours=9), d8_4 + timedelta(hours=11)))

        r1 = date_range_parser.parse(u'tomorrow from 9 - 1', d8_3).get(u'result')
        self._compareResults(r1[0], (d8_4 + timedelta(hours=9), d8_4 + timedelta(hours=13)))

        r1 = date_range_parser.parse(u'tomorrow from 12 - 3', d8_3).get(u'result')
        self._compareResults(r1[0], (d8_4 + timedelta(hours=12), d8_4 + timedelta(hours=15)))

        r1 = date_range_parser.parse(u'tomorrow from 13 - 15', d8_3).get(u'result')
        self._compareResults(r1[0], (d8_4 + timedelta(hours=13), d8_4 + timedelta(hours=15)))

        r1 = date_range_parser.parse(u'tomorrow between 10 - 2pm', d8_3).get(u'result')
        self._compareResults(r1[0], (d8_4 + td_10, d8_4 + td_14))

        r1 = date_range_parser.parse(u'tomorrow between 10 - 2PM', d8_3).get(u'result')
        self._compareResults(r1[0], (d8_4 + td_10, d8_4 + td_14))

        r1 = date_range_parser.parse(u'tomorrow between 10 - 2P.M.', d8_3).get(u'result')
        self._compareResults(r1[0], (d8_4 + td_10, d8_4 + td_14))

        r1 = date_range_parser.parse(u'tomorrow between 10AM - 2P.M.', d8_3).get(u'result')
        self._compareResults(r1[0], (d8_4 + td_10, d8_4 + td_14))

        r1 = date_range_parser.parse(u'tomorrow between 10A.M. - 2P.M.', d8_3).get(u'result')
        self._compareResults(r1[0], (d8_4 + td_10, d8_4 + td_14))

        r1 = date_range_parser.parse(u'tomorrow between 10 A.M. - 2P.M.', d8_3).get(u'result')
        self._compareResults(r1[0], (d8_4 + td_10, d8_4 + td_14))

        r1 = date_range_parser.parse(u'tomorrow between 10am - 2', d8_3).get(u'result')
        self._compareResults(r1[0], (d8_4 + td_10, d8_4 + td_14))

        # Test applying an hour range to multiple days.
        r2 = date_range_parser.parse(u'this week from 10 am - 2 pm', d8_3).get(u'result')
        self._compareResults(r2[0], (d8_4 + td_10, d8_4 + td_14))
        self._compareResults(r2[1], (d8_4 + td_10 + datetime.timedelta(days=1), d8_4 + td_14 + datetime.timedelta(days=1)))
        self._compareResults(r2[2], (d8_4 + td_10 + datetime.timedelta(days=2), d8_4 + td_14 + datetime.timedelta(days=2)))
        self._compareResults(r2[3], (d8_4 + td_10 + datetime.timedelta(days=3), d8_4 + td_14 + datetime.timedelta(days=3)))
        self._compareResults(r2[4], (d8_4 + td_10 + datetime.timedelta(days=4), d8_4 + td_14 + datetime.timedelta(days=4)))

        # Test applying an hour range to multiple that is shortened by the src_time. src_time = Friday
        r3 = date_range_parser.parse(u'this week from 10 am - 2 pm', d8_3 + datetime.timedelta(days=5)).get(u'result')
        self._compareResults(r3[0], (d8_4 + td_10 + datetime.timedelta(days=4), d8_4 + td_14 + datetime.timedelta(days=4)))
        self.assertEqual(len(r3), 1)

        r4 = date_range_parser.parse(u'this week from 10 am - 2 pm', d8_3 + datetime.timedelta(days=4)).get(u'result')
        self._compareResults(r4[0], (d8_4 + td_10 + datetime.timedelta(days=3), d8_4 + td_14 + datetime.timedelta(days=3)))
        self._compareResults(r4[1], (d8_4 + td_10 + datetime.timedelta(days=4), d8_4 + td_14 + datetime.timedelta(days=4)))
        self.assertEqual(len(r4), 2)


    def test_natural_inner_day_modifications(self):

        def construct_time(hr1, hr2):
            return (d8_4 + datetime.timedelta(hours=hr1), d8_4 + datetime.timedelta(hours=hr2))

        d8_3 = self.timezone.localize(datetime.datetime(2014, 8, 3))
        d8_4 = d8_3 + datetime.timedelta(days=1)
        td_8 = datetime.timedelta(hours=8)
        td_1030 = datetime.timedelta(hours=10.5)

        tomorrow_emorning = construct_time(5,8)
        tomorrow_morning = construct_time(8,11)
        tomorrow_lmorning = construct_time(10,11.5)
        tomorrow_brunch = construct_time(10,14)
        tomorrow_elunch = construct_time(11,12)
        tomorrow_lunch = construct_time(11,13)
        tomorrow_llunch = construct_time(13,14.5)
        tomorrow_eafternoon = construct_time(12,15)
        tomorrow_afternoon = construct_time(12, 16)
        tomorrow_lafternoon = construct_time(14.5, 16.5)
        tomorrow_eevening = construct_time(16,18)
        tomorrow_evening = construct_time(17,20)
        tomorrow_levening = construct_time(19,22)
        tomorrow_enight = construct_time(19,21)
        tomorrow_night = construct_time(19, 22.5)
        tomorrow_lnight = construct_time(22, 23.5)

        r1 = date_range_parser.parse(u'tomorrow morning', d8_3).get(u'result')
        self._compareResults(r1[0], tomorrow_morning)
        self.assertEqual(len(r1), 1)

        r1 = date_range_parser.parse(u'tomorrow early morning', d8_3).get(u'result')
        self._compareResults(r1[0], tomorrow_emorning)
        self.assertEqual(len(r1), 1)

        r1 = date_range_parser.parse(u'tomorrow late morning', d8_3).get(u'result')
        self._compareResults(r1[0], tomorrow_lmorning)
        self.assertEqual(len(r1), 1)

        r1 = date_range_parser.parse(u'tomorrow brunch', d8_3).get(u'result')
        self._compareResults(r1[0], tomorrow_brunch)
        self.assertEqual(len(r1), 1)

        r1 = date_range_parser.parse(u'tomorrow early lunch', d8_3).get(u'result')
        self._compareResults(r1[0], tomorrow_elunch)
        self.assertEqual(len(r1), 1)

        r1 = date_range_parser.parse(u'tomorrow lunch', d8_3).get(u'result')
        self._compareResults(r1[0], tomorrow_lunch)
        self.assertEqual(len(r1), 1)

        r1 = date_range_parser.parse(u'tomorrow late lunch', d8_3).get(u'result')
        self._compareResults(r1[0], tomorrow_llunch)
        self.assertEqual(len(r1), 1)

        r1 = date_range_parser.parse(u'tomorrow early afternoon', d8_3).get(u'result')
        self._compareResults(r1[0], tomorrow_eafternoon)
        self.assertEqual(len(r1), 1)

        r1 = date_range_parser.parse(u'tomorrow afternoon', d8_3).get(u'result')
        self._compareResults(r1[0], tomorrow_afternoon)
        self.assertEqual(len(r1), 1)

        r1 = date_range_parser.parse(u'tomorrow late afternoon', d8_3).get(u'result')
        self._compareResults(r1[0], tomorrow_lafternoon)
        self.assertEqual(len(r1), 1)

        r1 = date_range_parser.parse(u'tomorrow early night', d8_3).get(u'result')
        self._compareResults(r1[0], tomorrow_enight)
        self.assertEqual(len(r1), 1)

        r1 = date_range_parser.parse(u'tomorrow night', d8_3).get(u'result')
        self._compareResults(r1[0], tomorrow_night)
        self.assertEqual(len(r1), 1)

        r1 = date_range_parser.parse(u'tomorrow late night', d8_3).get(u'result')
        self._compareResults(r1[0], tomorrow_lnight)
        self.assertEqual(len(r1), 1)

        r1 = date_range_parser.parse(u'lunch this week', d8_3).get(u'result')
        self._compareResults(r1[0], tomorrow_lunch)
        self._compareResults(r1[1], (tomorrow_lunch[0] + timedelta(days=1), tomorrow_lunch[1] + timedelta(days=1)))
        self._compareResults(r1[2], (tomorrow_lunch[0] + timedelta(days=2), tomorrow_lunch[1] + timedelta(days=2)))
        self._compareResults(r1[3], (tomorrow_lunch[0] + timedelta(days=3), tomorrow_lunch[1] + timedelta(days=3)))
        self._compareResults(r1[4], (tomorrow_lunch[0] + timedelta(days=4), tomorrow_lunch[1] + timedelta(days=4)))
        self.assertEqual(len(r1), 5)

        r1 = date_range_parser.parse(u'lunch this week', d8_3 + timedelta(days=3)).get(u'result')
        self._compareResults(r1[0], (tomorrow_lunch[0] + timedelta(days=0+2), tomorrow_lunch[1] + timedelta(days=0+2)))
        self._compareResults(r1[1], (tomorrow_lunch[0] + timedelta(days=1+2), tomorrow_lunch[1] + timedelta(days=1+2)))
        self._compareResults(r1[2], (tomorrow_lunch[0] + timedelta(days=2+2), tomorrow_lunch[1] + timedelta(days=2+2)))
        self.assertEqual(len(r1), 3)


    def test_absolute_one_way_inner_day_modifications(self):

        d8_3 = self.timezone.localize(datetime.datetime(2014, 8, 3))
        d8_4 = d8_3 + timedelta(days=1) # Monday.
        tomorrow_before_10 = (d8_4, d8_4 + timedelta(hours=10))
        tomorrow_after_10 = (d8_4 + timedelta(hours=10), d8_4+timedelta(days=1))
        tomorrow_before_14 = (d8_4, d8_4 + timedelta(hours=14))
        tomorrow_after_14 = (d8_4 + timedelta(hours=14), d8_4+timedelta(days=1))


        r1 = date_range_parser.parse("tomorrow before 10 Am", d8_3).get(u'result')
        self._compareResults(r1[0], tomorrow_before_10)
        self.assertEqual(len(r1), 1)

        r1 = date_range_parser.parse("tomorrow before 10 am", d8_3).get(u'result')
        self._compareResults(r1[0], tomorrow_before_10)
        self.assertEqual(len(r1), 1)

        r1 = date_range_parser.parse("tomorrow before 10:00 AM", d8_3).get(u'result')
        self._compareResults(r1[0], tomorrow_before_10)
        self.assertEqual(len(r1), 1)

        r1 = date_range_parser.parse("tomorrow before 10:00 A.M.", d8_3).get(u'result')
        self._compareResults(r1[0], tomorrow_before_10)
        self.assertEqual(len(r1), 1)

        r1 = date_range_parser.parse("tomorrow after 10 Am", d8_3).get(u'result')
        self._compareResults(r1[0], tomorrow_after_10)
        self.assertEqual(len(r1), 1)

        r1 = date_range_parser.parse("tomorrow after 10 am", d8_3).get(u'result')
        self._compareResults(r1[0], tomorrow_after_10)
        self.assertEqual(len(r1), 1)

        r1 = date_range_parser.parse("tomorrow after 10:00 AM", d8_3).get(u'result')
        self._compareResults(r1[0], tomorrow_after_10)
        self.assertEqual(len(r1), 1)

        r1 = date_range_parser.parse("tomorrow after 10:00 A.M.", d8_3).get(u'result')
        self._compareResults(r1[0], tomorrow_after_10)
        self.assertEqual(len(r1), 1)

        r1 = date_range_parser.parse("tomorrow before 2", d8_3).get(u'result')
        self._compareResults(r1[0], tomorrow_before_14)
        self.assertEqual(len(r1), 1)

        r1 = date_range_parser.parse("tomorrow before 2 pm", d8_3).get(u'result')
        self._compareResults(r1[0], tomorrow_before_14)
        self.assertEqual(len(r1), 1)

        r1 = date_range_parser.parse("tomorrow before 14:00", d8_3).get(u'result')
        self._compareResults(r1[0], tomorrow_before_14)
        self.assertEqual(len(r1), 1)

        r1 = date_range_parser.parse("tomorrow before 14 ", d8_3).get(u'result')
        self._compareResults(r1[0], tomorrow_before_14)
        self.assertEqual(len(r1), 1)

        r1 = date_range_parser.parse("tomorrow before 14 am ", d8_3).get(u'result')
        self._compareResults(r1[0], tomorrow_before_14)
        self.assertEqual(len(r1), 1)

        r1 = date_range_parser.parse("tomorrow before 2:00 P.M.", d8_3).get(u'result')
        self._compareResults(r1[0], tomorrow_before_14)
        self.assertEqual(len(r1), 1)

        r1 = date_range_parser.parse("tomorrow after 2 Pm", d8_3).get(u'result')
        self._compareResults(r1[0], tomorrow_after_14)
        self.assertEqual(len(r1), 1)

        r1 = date_range_parser.parse("tomorrow after 2 pm", d8_3).get(u'result')
        self._compareResults(r1[0], tomorrow_after_14)
        self.assertEqual(len(r1), 1)

        r1 = date_range_parser.parse("tomorrow after 2:00 PM", d8_3).get(u'result')
        self._compareResults(r1[0], tomorrow_after_14)
        self.assertEqual(len(r1), 1)

        r1 = date_range_parser.parse("tomorrow after 2:00 P.M.", d8_3).get(u'result')
        self._compareResults(r1[0], tomorrow_after_14)
        self.assertEqual(len(r1), 1)


    def test_absolute_one_way_inner_multiday_modifications(self):

        d8_3 = self.timezone.localize(datetime.datetime(2014, 8, 3))
        monday = d8_3 + timedelta(days=1) # Monday.
        tuesday = monday + timedelta(days=1)
        wednesday = tuesday + timedelta(days=1)
        thursday = wednesday + timedelta(days=1)
        friday = thursday + timedelta(days=1)
        saturday = friday + timedelta(days=1)
        sunday = saturday + timedelta(days=1)

        r1 = date_range_parser.parse("before tuesday", monday).get(u'result')
        recon = date_range_parser.parse("before tuesday", monday).get(u'parse')[0].get(u'reconvertible_text')
        self.assertEqual(r1, date_range_parser.parse(recon, monday).get(u'result'))
        self._compareResults(r1[0], (monday, tuesday))
        self.assertEqual(len(r1), 1)

        r1 = date_range_parser.parse("before 8/11", monday).get(u'result')
        self._compareResults(r1[0], (monday, tuesday))
        self.assertEqual(len(r1), 7)

        r1 = date_range_parser.parse("before 08/11", monday).get(u'result')
        self._compareResults(r1[0], (monday, tuesday))
        self.assertEqual(len(r1), 7)

        r1 = date_range_parser.parse("before 08/11/2014", monday).get(u'result')
        self._compareResults(r1[0], (monday, tuesday))
        self.assertEqual(len(r1), 7)

        r1 = date_range_parser.parse("before 8/11/2014", monday).get(u'result')
        self._compareResults(r1[0], (monday, tuesday))
        self.assertEqual(len(r1), 7)

        r1 = date_range_parser.parse("before 8.11", monday).get(u'result')
        self._compareResults(r1[0], (monday, tuesday))
        self.assertEqual(len(r1), 7)

        r1 = date_range_parser.parse("before 8.11.2014", monday).get(u'result')
        self._compareResults(r1[0], (monday, tuesday))
        self.assertEqual(len(r1), 7)

        r1 = date_range_parser.parse("after tuesday", monday).get(u'result')
        self._compareResults(r1[0], (wednesday, wednesday+timedelta(days=1)))
        self._compareResults(r1[-1], (wednesday+timedelta(days=13), wednesday+timedelta(days=14)))
        self.assertEqual(len(r1), 14)

        # Should just give us 0 minutes on Monday.
        r1 = date_range_parser.parse("before this week", monday).get(u'result')
        self._compareResults(r1[0], (monday, monday))
        self.assertEqual(len(r1), 1)

        r1 = date_range_parser.parse("before this week", wednesday).get(u'result')
        self._compareResults(r1[0], (wednesday, wednesday))
        self.assertEqual(len(r1), 1)

        r1 = date_range_parser.parse("before next week", wednesday).get(u'result')
        self._compareResults(r1[0], (wednesday, thursday))
        self._compareResults(r1[-1], (sunday, sunday+timedelta(days=1)))
        self.assertEqual(len(r1), 5)  # wed, thur, fri, sat, sun = 5


        r1 = date_range_parser.parse("after this week", monday).get(u'result')
        self._compareResults(r1[0], (saturday, sunday))
        self._compareResults(r1[-1], (saturday + timedelta(days=13), sunday + timedelta(days=13)))
        self.assertEqual(len(r1), 14)


    def test_between(self):
        d8_3 = self.timezone.localize(datetime.datetime(2014, 8, 3))
        d8_11 = self.timezone.localize(datetime.datetime(2014, 8, 11))
        d8_15 = self.timezone.localize(datetime.datetime(2014, 8, 15))

        monday = self.timezone.localize(datetime.datetime(2014, 8, 4))
        tuesday = self.timezone.localize(datetime.datetime(2014, 8, 5))
        wednesday = self.timezone.localize(datetime.datetime(2014, 8, 6))
        thursday = self.timezone.localize(datetime.datetime(2014, 8, 7))
        friday = self.timezone.localize(datetime.datetime(2014, 8, 8))

        r1 = date_range_parser.parse("between 8/11 and 8/15", d8_3).get(u'result')
        self._compareResults(r1[0], (d8_11, d8_11+timedelta(days=1)))
        self._compareResults(r1[-1], (d8_15, d8_15 + timedelta(days=1)))
        self.assertEqual(len(r1), 5)

        r1 = date_range_parser.parse("from 8/11 to 8/15", d8_3).get(u'result')
        self._compareResults(r1[0], (d8_11, d8_11+timedelta(days=1)))
        self._compareResults(r1[-1], (d8_15, d8_15 + timedelta(days=1)))
        self.assertEqual(len(r1), 5)

        r1 = date_range_parser.parse("8/11/2014 - 8/15/2014", d8_3).get(u'result')
        self._compareResults(r1[0], (d8_11, d8_11+timedelta(days=1)))
        self._compareResults(r1[-1], (d8_15, d8_15 + timedelta(days=1)))
        self.assertEqual(len(r1), 5)

        r1 = date_range_parser.parse("8/11-8/15", d8_3).get(u'result')
        self._compareResults(r1[0], (d8_11, d8_11+timedelta(days=1)))
        self._compareResults(r1[-1], (d8_15, d8_15 + timedelta(days=1)))
        self.assertEqual(len(r1), 5)

        r1 = date_range_parser.parse("8.11-8.15", d8_3).get(u'result')
        self._compareResults(r1[0], (d8_11, d8_11+timedelta(days=1)))
        self._compareResults(r1[-1], (d8_15, d8_15 + timedelta(days=1)))
        self.assertEqual(len(r1), 5)

        r1 = date_range_parser.parse("between monday and thursday", d8_3).get(u'result')
        self._compareResults(r1[0], (monday, tuesday))
        self._compareResults(r1[-1], (thursday, friday))
        self.assertEqual(len(r1), 4)

        r1 = date_range_parser.parse("monday - thursday", d8_3).get(u'result')
        self._compareResults(r1[0], (monday, tuesday))
        self._compareResults(r1[-1], (thursday, friday))
        self.assertEqual(len(r1), 4)

        r1 = date_range_parser.parse("from monday to thursday", d8_3).get(u'result')
        self._compareResults(r1[0], (monday, tuesday))
        self._compareResults(r1[-1], (thursday, friday))
        self.assertEqual(len(r1), 4)

        #r1 = date_range_parser.parse("from monday morning to thursday evening", d8_3)
        #self._compareResults(r1[0], (monday + timedelta(hours=8), tuesday))
        #self._compareResults(r1[-1], (thursday, thursday + timedelta(hours=21)))
        ##self.assertEqual(len(r1), 4)

        r1 = date_range_parser.parse("from monday thru thursday", d8_3).get(u'result')
        self._compareResults(r1[0], (monday, tuesday))
        self._compareResults(r1[-1], (thursday, friday))
        self.assertEqual(len(r1), 4)

        #r1 = date_range_parser.parse("monday thru thursday", d8_3)
        #self._compareResults(r1[0], (monday, tuesday))
        #self._compareResults(r1[-1], (thursday, friday))
        #self.assertEqual(len(r1), 4)

        #r1 = date_range_parser.parse("8-11 - 8-15", d8_3)
        #self._compareResults(r1[0], (d8_11, d8_11+timedelta(days=1)))
        #self._compareResults(r1[-1], (d8_15, d8_15 + timedelta(days=1)))
        #self.assertEqual(len(r1), 5)


    def test_reldr(self):
        d8_3 = self.timezone.localize(datetime.datetime(2014, 8, 3))
        d9_15 = self.timezone.localize(datetime.datetime(2014, 9, 15))
        d9_19 = self.timezone.localize(datetime.datetime(2014, 9, 19))

        r1 = date_range_parser.parse("2 weeks from 9/2", d8_3).get(u'result')
        self._compareResults(r1[0], (d9_15, d9_15+timedelta(days=1)))
        self._compareResults(r1[-1], (d9_19, d9_19+timedelta(days=1)))
        self.assertEqual(len(r1), 5)

        r1 = date_range_parser.parse("in three weeks from 9/2", d8_3).get(u'result')
        self._compareResults(r1[0], (d9_15 + timedelta(days=7), d9_15+timedelta(days=1+7)))
        self._compareResults(r1[-1], (d9_19 + timedelta(days=7), d9_19+timedelta(days=1+7)))
        self.assertEqual(len(r1), 5)


    def test_and(self):
        pass

    def test_reject(self):
        d8_3 = self.timezone.localize(datetime.datetime(2014, 8, 3))

        r1 = date_range_parser.parse("set up a 20 minute meeting with ashutosh@siftcal.com", d8_3).get(u'result')
        self.assertEqual(len(r1), 0)


    def test_preprocessing(self):
        d8_3 = self.timezone.localize(datetime.datetime(2014, 8, 3))

        r1 = date_range_parser.parse("tomorrow in the morning", d8_3).get(u'result')
        self._compareResults(r1[0], (d8_3+timedelta(hours=(24+8)), d8_3+timedelta(hours=(24+11))))
        self.assertEqual(len(r1), 1)

        r2 = date_range_parser.parse("tomorrow from noon to 3 pm", d8_3).get(u'result')
        self._compareResults(r2[0], (d8_3+timedelta(hours=(24+12)), d8_3+timedelta(hours=(24+15))))
        self.assertEqual(len(r2), 1)

    def test_reconvertible_text(self):

        src_time = self.timezone.localize(datetime.datetime(2014, 8, 3))

        self._compareReconvertibleText(u"monday", src_time)
        self._compareReconvertibleText(u"next monday", src_time)
        self._compareReconvertibleText(u"in three weeks from 9/2", src_time)
        self._compareReconvertibleText(u"monday morning or sunday afternoon", src_time)
        self._compareReconvertibleText(u"between monday and wednesday", src_time)
        self._compareReconvertibleText(u"monday morning", src_time)
        self._compareReconvertibleText(u"monday afternoon", src_time)
        self._compareReconvertibleText(u"09/12", src_time)
        self._compareReconvertibleText(u"09.12.2014", src_time)
        self._compareReconvertibleText(u"09/12/2014", src_time)
        self._compareReconvertibleText(u"between 9/12/2014 and 9/13/2014", src_time)


if __name__ == '__main__':
    unittest.main()\
