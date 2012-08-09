<?php

#
# XiVO Web-Interface
# Copyright (C) 2006-2011  Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

require_once(dwho_file::joinpath(DWHO_PATH_ROOT,'datastorage','helper','table.inc'));

class xivo_service_asterisk_abstract_sql extends dwho_datastorage_helper_table
{
	var $_disable	= 'commented';

	public function __construct(&$dso,$param=array())
	{
		parent::_init(&$dso,$param);
	}

	protected function _stat_common_where($interval)
	{
		if (is_null($interval) === false)
		{
			$this->_dso->wherebetween('time',
					strftime('%Y-%m-%d %H:%M:%S', $interval['beg']),
					strftime('%Y-%m-%d %H:%M:%S.999999', $interval['end']),
					$this->_table);
		}

		$hour_itl = $this->get_param('hour_itl');
		if (is_null($hour_itl) === false)
			$this->_dso->andwhere('EXTRACT(HOUR FROM "'.$this->_table.'".time) BETWEEN '.$hour_itl['beg'].' AND '.($hour_itl['end']-1));

		$days = $this->get_param('days');
		if (is_null($days) === false)
			$this->_dso->andwhere('EXTRACT(DOW FROM "'.$this->_table.'".time) IN ('.implode(',', array_values($days)).')');
	}
}

?>
