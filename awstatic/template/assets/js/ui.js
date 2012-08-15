var awstatic = (function(window, $, undefined) {

"use strict";

/* ******************************************************************
** Utilities
** *********/
// Synchronous version of '$.getJSON()'.
function get_json(url) {
    return $.parseJSON(
        $.ajax({
            url: url,
            async: false,
            dataType: 'json',
            error: function (jqXHR, textStatus, errorThrown) {
                window.alert('Could not load "' + url + '": ' + errorThrown);
            }
        }).responseText);
}

// Parse the given query string and return an associative array with
// the key/values of the given hash. We use it here only to parse the
// hash part of the URL.
function parse_querystring(str) {
    if (!str) {
        return {};
    }
    var values = {};
    var groups = str.split('&');
    for (var i = 0; i < groups.length; i++) {
        var key_value = groups[i].split('=');
        if (!key_value[0].length) {
            continue;
        }
        values[key_value[0]] = key_value[1];
    }
    return values;
}

// Given an associate array, return the corresponding query string
// (without the leading '?').
function to_querystring(hash) {
    var values = [];
    for (var key in hash) {
        if (hash.hasOwnProperty(key)) {
            values.push(key + '=' + hash[key]);
        }
    }
    return values.join('&');
}

// Given a date formatted as 'YYYYMM' or 'YYYY', return a proper label
// such as 'month YYYY' or 'YYYY' (respectively).
var MONTHS = ['January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'];
function get_period_label(date) {
    if (date.length === 4) {
        return date;
    }
    return MONTHS[parseInt(date.slice(4), 10) - 1] +
        ' ' +
        date.slice(0, 4);
}

// Return the name and value (as an array of 2-element of arrays) of
// all properties of the given object, sorted by the property name.
function get_sorted_properties(obj) {
    var items = [];
    for (var prop in obj) {
        if (obj.hasOwnProperty(prop)) {
            items.push([prop, obj[prop]]);
        }
    }
    return items.sort();
}

// Return whether the given year is a leap year.
function is_leap_year(year) {
    if (year % 4 !== 0) {
        return false;
    }
    if (year % 400 === 0) {
        return true;
    }
    return (year % 100 !== 0);
}

// Return an array to be used as ticks in the graph, i.e. basically
// the list of days of the month.
// 'yyyymm' must be the month formatted as 'YYYYMM'. Duh.
var DAYS_IN_MONTH = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
function get_month_ticks(yyyymm) {
    var month = parseInt(yyyymm.slice(4), 10);
    var year = parseInt(yyyymm.slice(0, 4), 10);
    var n_days = DAYS_IN_MONTH[month - 1];
    if (month === 2 && is_leap_year(year)) {
        n_days += 1;
    }
    var ticks = [];
    for (var i = 0; i < n_days; i++) {
        ticks.push([i, String(1 + i)]);
    }
    return ticks;
}

// Given a numeric (or undefined value), return a string with the
// proper unit.
function format_bandwidth(bandwidth) {
    if (!bandwidth) {
        return '0';
    }
    var units = ['b', 'Kb', 'Mb'];
    var i = 1;
    for (; i < units.length; i++) {
        if (bandwidth < 1024) {
            break;
        }
        bandwidth = bandwidth / 1024;
    }
    // keep only 2 significant digits
    bandwidth = bandwidth.toFixed(2).toString();
    // remove trailing 0's.
    while (bandwidth.slice(bandwidth.length - 1) === '0') {
        bandwidth = bandwidth.slice(0, bandwidth.length - 1);
    }
    // remove dot if the 2 significant digits were 0's.
    if (bandwidth.slice(bandwidth.length - 1) === '.') {
        bandwidth = bandwidth.slice(0, bandwidth.length - 1);
    }
    return bandwidth + ' ' + units[i - 1];
}
/* *****************************************************************/


/* ******************************************************************
** Main 'UI' class
**
** The 'UI' class loads reports, generates diagrams and responds to
** user commands.
** *************************/
function UI(site, period, page) {
    this.init_templates();
    this.select_site(site, period);
    this.show_page(page || 'overview');
}

// Return the mode which we are in: 'month' or 'year'.
UI.prototype.get_period_mode = function() {
    if (this.period.length === 4) {
        return 'year';
    }
    return 'month';
};

// Compile templates.
UI.prototype.init_templates = function() {
    this._templates = {};
    var that = this;
    $('script[type="text/html"]').each(function(index, tag) {
        var template_id = tag.id.slice('tmpl-'.length);
        that._templates[template_id] = Handlebars.compile(
            $('#' + tag.id).html());
    });
};

// Render a template.
UI.prototype.render = function(template_id, data) {
    return this._templates[template_id](data);
};

// Select a site, load data, update reports and interface.
UI.prototype.select_site = function(new_site, new_period) {
    var old_site = this.site;
    var old_period = this.period;
    if ((new_site === old_site) && (new_period === old_period)) {
        return false;
    }
    $('#page-loading').show();
    if (new_site !== old_site) {
        this.site = new_site;
        this.data = get_json('data/' + this.site + '.json');
        this.url = this.data['url'];
        $('.domain-selector').find('.placeholder').html(new_site);
    }
    if (old_period !== new_period || old_period === undefined) {
        // If no particular period is provided, use the latest one.
        new_period = new_period || this.data['periods'][0];
        this.period = new_period;
        this.update_period_selector(this.data['periods']);
        var label = get_period_label(new_period);
        $('.period-selector').find('.placeholder').text(label);
    }
    this.update_reports();
    if (old_site === undefined) {
        // When the page is first loaded (and no site has been
        // selected yet), the header is empty. We want everything to
        // appear (text, content 'after:' and borders) at the same
        // time so the whole header has been set invisible. Here we
        // make it visible again.
        $('.header').children('li').toggleClass('invisible', false);
    }
    $('#page-loading').hide();
    this.update_hash();
};

// Select a period, update reports and interface.
UI.prototype.select_period = function(new_period) {
    if (new_period !== this.period) {
        this.select_site(this.site, new_period);
    }
};

// Update URL hash so that we can bookmark (deep-link) the page.
UI.prototype.update_hash = function() {
    window.location.hash = to_querystring({'site': this.site,
                                           'period': this.period,
                                           'page': this.page});
};

// Show one of the report pages.
UI.prototype.show_page = function(new_page) {
    if (this.page === new_page) {
        return;
    }
    $('#page-' + new_page).show();
    $('#nav-' + new_page).toggleClass('current', true);
    if (this.page !== undefined) {
        $('#page-' + this.page).hide();
        $('#nav-' + this.page).toggleClass('current', false);
    }
    this.page = new_page;
    this.update_hash();
};

// Update period dropdown selector.
UI.prototype.update_period_selector = function(periods, selected_label) {
    var hashes = [];
    for (var i = 0; i < periods.length; i++) {
        hashes.push({'key': periods[i], 'label': get_period_label(periods[i])});
    }
    $('#period-menu').html(this.render('period-menu', {'periods': hashes}));
};

// Update all reports.
UI.prototype.update_reports = function() {
    this.update_report_overview();
    this.update_report_top10();
    this.update_report_downloads();
    this.update_report_referrers();
    this.update_report_keywords();
    this.update_report_phrases();
};

// FIXME: review this. Probably rename.
// Return series for the selected period.
// - 'what' is the key in the JSON file. It may be either 'visits' or
//   'visits_by_day'. FIXME: not true anymore
// - 'mode' may be either 'month' or 'year'.
UI.prototype.get_series = function(what, mode) {
    var data = get_sorted_properties(this.data[what]);
    // 'idx' is the position of the varying component of the keys of
    // the 'data' object. The varying component is the day when in
    // 'month' mode, and the month when in 'year' mode.
    var idx = mode === 'year' ? 4 : 6;
    // 'expected_length' is the length of the keys that are
    // relevant. In 'year' mode, we look for YYYYMM keys (6 chars
    // long); in 'month' mode, we look for YYYYMMDD keys (8 chars
    // long).
    var expected_length = mode === 'year' ? 6 : 8;
    // We may not have data for the first days of the month (or the
    // first months of the year). Here we find out the first day (or
    // month) for which we have data.
    var i = 0;
    for (; i < data.length; i++) {
        if ((data[i][0].length === expected_length) &&
            (data[i][0].slice(0, idx) === this.period)) {
            break;
        }
    }
    var series = [];
    // We provide a value of 0 for missing days/months.
    var x = 0;
    var first = parseInt(data[i][0].slice(1 + idx), 10) - 1;
    for (; x < first; x++) {
        series.push([x, {}]);
    }
    // ... and add data that we do know.
    for (; i < data.length; i++) {
        if ((data[i][0].length === expected_length) &&
            (data[i][0].slice(0, idx) === this.period)) {
            series.push([x++, data[i][1]]);
        }
    }
    return series;
};

var YEAR_TICKS = [[0, 'jan'], [1, 'feb'], [2, 'mar'], [3, 'apr'], [4, 'may'],
    [5, 'jun'], [6, 'jul'], [7, 'aug'], [8, 'sep'], [9, 'oct'], [10, 'nov'],
    [11, 'dec']];
// Update overview page.
UI.prototype.update_report_overview = function() {
    var data = [];
    var options = {'series':
                   {'lines':
                    {'show': true,
                     'fill': 0.8},
                    'color': '#f6dd93',
                    'points': {'show': true}},
                   'yaxis': {'ticks': 2}}; // FIXME: really?
    // FIXME: add tooltips
    // (see http://people.iola.dk/olau/flot/examples/interacting.html)
    if (this.get_period_mode() === 'year') {
        data = this.get_series('overview', 'year');
        options['xaxis'] = {'ticks': YEAR_TICKS};
    }
    else { // mode === 'month'
        data = this.get_series('overview', 'month');
        options['xaxis'] = {'ticks': get_month_ticks(this.period)};
    }
    var series = [];
    for (var i = 0; i < data.length; i++) {
        series.push([data[i][0], data[i][1]['pages']]);
    }
    $.plot($("#overview-graph"), [series], options);

    // Update overview table.
    var table = [];
    for (var i = 0; i < data.length; i++) {
        var label = '';
        if (this.get_period_mode() === 'month') {
            label = String(1 + series[i][0]);
        } else {
            label = MONTHS[series[i][0]];
        }
        var bandwidth = format_bandwidth(data[i][1]['bandwidth']);
        table.push({'label': label,
                    'hits': data[i][1]['hits'],
                    'pages': data[i][1]['pages'],
                    'visits': data[i][1]['visits'],
                    'visitors': data[i][1]['visitors'],
                    'bandwidth': bandwidth});
    }
    var view = {'table': table};
    $('.overview').children('tbody').html(this.render('overview-table', view));
};

// Update "Top 10" report.
UI.prototype.update_report_top10 = function() {
    var pages = this.data['top10'][this.period] || [];
    var view = {'base_url': this.url,
                'pages': pages,
                'format_bandwidth': format_bandwidth};
    $('.top10').children('tbody').html(this.render('top10-table', view));
};

// Update "Downloads" report.
UI.prototype.update_report_downloads = function() {
    var files = this.data['downloads'][this.period] || [];
    var view = {'base_url': this.url,
                'files': files,
                'format_bandwidth': format_bandwidth};
    $('.downloads').children('tbody').html(
        this.render('downloads-table', view));
};

// Update "Referrers" report.
UI.prototype.update_report_referrers = function() {
    var referrers = this.data['referrers'][this.period] || [];
    var view = {'referrers': referrers};
    $('.referrers').children('tbody').html(
        this.render('referrers-table', view));
};

// Update "Search keywords" report.
UI.prototype.update_report_keywords = function() {
    var keywords = this.data['keywords'][this.period] || [];
    var view = {'keywords': keywords};
    $('.keywords').children('tbody').html(this.render('keywords-table', view));
};


// Update "Search phrases" report.
UI.prototype.update_report_phrases = function() {
    var phrases = this.data['phrases'][this.period] || [];
    var view = {'phrases': phrases};
    $('.phrases').children('tbody').html(this.render('phrases-table', view));
};


var ui = undefined; // will be set in 'init_ui()'

// Initialize the user interface (to be called when the document is
// ready): this sets up dropdown menus, generates graphs, etc.
function init_ui() {
    $('.dropdown-toggle').dropdown();
    var sites = get_json('data/sites.json');
    var qs = parse_querystring(window.location.hash);
    var site = qs.site;
    if (!site) {
        site = sites[0];
    }
    // Set 'window.ui'
    // 'qs.period' and 'qs.page' may be undefined but the constructor
    // can deal with that.
    window.ui = ui = new UI(site, qs.period, qs.page);
    $('#site-menu').html(ui.render('site-menu', {'sites': sites}));
}

// public symbols of the module
return {
    format_bandwidth: format_bandwidth,
    get_month_ticks: get_month_ticks,
    get_period_label: get_period_label,
    get_sorted_properties: get_sorted_properties,
    init_ui: init_ui,
    is_leap_year: is_leap_year,
    parse_querystring: parse_querystring,
    to_querystring: to_querystring
};

// end of module
})(window, jQuery);