$(document).ready(function () {
    // Test 'parse_querystring()'
    test('test_parse_querystring_empty', function() {
        same(awstatic.parse_querystring(''), {});
    });
    test('test_parse_querystring_basics', function() {
        same(awstatic.parse_querystring('foo=1&bar=2'),
             {'foo': '1', 'bar': '2'});
    });
    test('test_parse_querystring_trailing_ampersand', function() {
        same(awstatic.parse_querystring('foo=1&bar=2&'),
             {'foo': '1', 'bar': '2'});
    });
    test('test_parse_querystring_empty_value', function() {
        same(awstatic.parse_querystring('foo=1&bar='),
             {'foo': '1', 'bar': ''});
    });

    // Test 'to_querystring()'
    test('test_to_querystring_empty', function() {
        same(awstatic.to_querystring({}), '');
    });
    test('test_to_querystring_basics', function() {
        same(awstatic.to_querystring({'foo': '1', 'bar': '2'}), 'foo=1&bar=2');
    });
    test('test_to_querystring_empty_value', function() {
        same(awstatic.to_querystring({'foo': '1', 'bar': ''}), 'foo=1&bar=');
    });

    // Test 'get_period_label()'
    test('test_get_period_label_month_and_year', function() {
        same(awstatic.get_period_label('201201'), 'January 2012');
        same(awstatic.get_period_label('201202'), 'February 2012');
        same(awstatic.get_period_label('201203'), 'March 2012');
        same(awstatic.get_period_label('201204'), 'April 2012');
        same(awstatic.get_period_label('201205'), 'May 2012');
        same(awstatic.get_period_label('201206'), 'June 2012');
        same(awstatic.get_period_label('201207'), 'July 2012');
        same(awstatic.get_period_label('201208'), 'August 2012');
        same(awstatic.get_period_label('201209'), 'September 2012');
        same(awstatic.get_period_label('201210'), 'October 2012');
        same(awstatic.get_period_label('201211'), 'November 2012');
        same(awstatic.get_period_label('201212'), 'December 2012');
    });
    test('test_get_period_label_year_only', function() {
        same(awstatic.get_period_label('2012'), '2012');
    });

    // Test 'get_sorted_properties()'
    test('test_get_sorted_properties_basics', function() {
        same(awstatic.get_sorted_properties({'foo': 3, 'bar': 1, 'baz': 2}),
             [['bar', 1], ['baz', 2], ['foo', 3]]);
    });
    test('test_get_sorted_properties_empty_object', function() {
        same(awstatic.get_sorted_properties({}), []);
    });

    // Test 'is_leap_year()'
    test('test_is_leap_year', function() {
        ok(awstatic.is_leap_year(2012));
        ok(!awstatic.is_leap_year(2011));
        ok(awstatic.is_leap_year(1600));
        ok(!awstatic.is_leap_year(1700));
    });

    // Test 'get_month_ticks()'
    test('test_get_month_ticks', function() {
        same(awstatic.get_month_ticks('201201'),
             [[0, '1'], [1, '2'], [2, '3'], [3, '4'], [4, '5'], [5, '6'],
              [6, '7'], [7, '8'], [8, '9'], [9, '10'], [10, '11'], [11, '12'],
              [12, '13'], [13, '14'], [14, '15'], [15, '16'], [16, '17'],
              [17, '18'], [18, '19'], [19, '20'], [20, '21'], [21, '22'],
              [22, '23'], [23, '24'], [24, '25'], [25, '26'], [26, '27'],
              [27, '28'], [28, '29'], [29, '30'], [30, '31']]);
        same(awstatic.get_month_ticks('201202'),
             [[0, '1'], [1, '2'], [2, '3'], [3, '4'], [4, '5'], [5, '6'],
              [6, '7'], [7, '8'], [8, '9'], [9, '10'], [10, '11'], [11, '12'],
              [12, '13'], [13, '14'], [14, '15'], [15, '16'], [16, '17'],
              [17, '18'], [18, '19'], [19, '20'], [20, '21'], [21, '22'],
              [22, '23'], [23, '24'], [24, '25'], [25, '26'], [26, '27'],
              [27, '28'], [28, '29']]);
        same(awstatic.get_month_ticks('201102'),
             [[0, '1'], [1, '2'], [2, '3'], [3, '4'], [4, '5'], [5, '6'],
              [6, '7'], [7, '8'], [8, '9'], [9, '10'], [10, '11'], [11, '12'],
              [12, '13'], [13, '14'], [14, '15'], [15, '16'], [16, '17'],
              [17, '18'], [18, '19'], [19, '20'], [20, '21'], [21, '22'],
              [22, '23'], [23, '24'], [24, '25'], [25, '26'], [26, '27'],
              [27, '28']]);
    });

    // Test 'format_bandwidth()'
    test('test_format_bandwidth', function() {
        same(awstatic.format_bandwidth(undefined), '0');
        same(awstatic.format_bandwidth(0), '0');
        same(awstatic.format_bandwidth(1), '1 b');
        same(awstatic.format_bandwidth(1024), '1 Kb');
        same(awstatic.format_bandwidth(1132), '1.11 Kb');
        same(awstatic.format_bandwidth(2048 + 512), '2.5 Kb');
        same(awstatic.format_bandwidth(1024 * 1024), '1 Mb');
        same(awstatic.format_bandwidth(1024 * 1024 + 512 * 1024), '1.5 Mb');
        same(awstatic.format_bandwidth(1024 * 1024 * 1024), '1024 Mb');
    });
});