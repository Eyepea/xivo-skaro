/*
 * XiVO Web-Interface
 * Copyright (C) 2006-2011  Avencall
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

// calculate average for all numeric entries of array
function average(arr) {
	var items = arr.length;
	var sum = 0;
	for ( var i = 0; i < items; i++)
		sum += arr[i];
	return (sum / items);
}

function nl2br(str) {
	if (!str)
		return null;
	return str.replace(/([^>\r\n]?)(\r\n|\n\r|\r|\n)/g, '$1 <br> $2');
}

function xivo_fm_disabled(obj) {
	obj.attr('disabled', 'disabled');
	obj.removeClass('it-enabled').addClass('it-disabled');
}

function xivo_fm_enabled(obj) {
	obj.removeAttr('disabled');
	obj.removeClass('it-disabled').addClass('it-enabled');
}

// Return a helper with preserved width of cells
var fixHelper = function(e, ui) {
	ui.children().each(function() {
		$(this).width($(this).width());
	});
	return ui;
};

var delay = (function() {
	var timer = 0;
	return function(callback, ms) {
		clearTimeout(timer);
		timer = setTimeout(callback, ms);
	};
})();

// object for manage multiselect filter
function clean_ms(input_id, select_from, select_to) {

	var box = dwho_eid(input_id);
	var select = dwho_eid(select_from);
	var select2 = dwho_eid(select_to);
	var select_cache = new Array();

	this.__init = __init;
	this.reset = reset;
	this.build_cache = build_cache;
	this.populate = populate;

	function __init() {
		if (!box || !select || !select2)
			return false;
		box.addEventListener("keyup", populate, false);
		build_cache(select, select_cache);
	}

	function reset() {
		while (select.hasChildNodes()) {
			select.removeChild(select.firstChild);
		}
	}

	function build_cache(arr, to) {
		var nb = arr.length;
		for ( var i = 0; i < nb; i++) {
			var option = arr.options[i];
			to.push(new Option(option.text, option.value));
		}
	}

	function populate(e) {
		update_cache();
		reset();
		var nb = select_cache.length;
		for ( var i = 0; i < nb; i++) {
			var option = select_cache[i];
			var expression = new RegExp(this.value.toLowerCase());
			if (expression.exec(option.text.toLowerCase()))
				select.add(option, null);
		}
	}

	function update_cache() {
		var nb = select2.length;
		for ( var i = 0; i < nb; i++) {
			var option2 = select2.options[i];
			var l = select_cache.length;
			for ( var c = 0; c < l; c++) {
				if (select_cache[c] && select_cache[c].value == option2.value)
					select_cache.splice(c, 1);
			}
		}
	}
}