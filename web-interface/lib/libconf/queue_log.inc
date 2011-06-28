<?php

#
# XiVO Web-Interface
# Copyright (C) 2006-2011  Proformatique <technique@proformatique.com>
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
    
$array    = array(
    /*
    * The caller abandoned their position in the queue. The position is the 
    * caller's position in the queue when they hungup, the origposition is 
    * the original position the caller was when they first entered the 
    * queue, and the waittime is how long the call had been waiting in the 
    * queue at the time of disconnect.
    */
    'ABANDON'    => array('position','origposition','waittime'),

    /*
    * The agent dumped the caller while listening to the queue announcement.
    */
    'AGENTDUMP'    => array(),

    /*
    * The agent logged in. The channel is recorded.
    */
    'AGENTLOGIN'    => array('channel'),

    /*
    * The callback agent logged in. The login extension and context is recorded. 
    */
    'AGENTCALLBACKLOGIN'    => array('exten@context'),

    /*
    * The agent logged off. The channel is recorded, along with the total time 
    * the agent was logged in. 
    */
    'AGENTLOGOFF'    => array('channel','logintime'),

    /*
    * The callback agent logged off. The last login extension and context is recorded, 
    * along with the total time the agent was logged in, and the reason for the logoff 
    * if it was not a normal logoff (e.g., Autologoff, Chanunavail)
    */
    'AGENTCALLBACKLOGOFF'    => array('exten@context','logintime','reason'),

    /*
     * The caller was connected to an agent, and the call was terminated normally by the agent. 
     * The caller's hold time and the length of the call are both recorded. 
     * The caller's original position in the queue is recorded in origposition.
     */
    'COMPLETEAGENT'    => array('holdtime','calltime','origposition'),

    /*
     * The caller was connected to an agent, and the call was terminated normally by the caller. 
     * The caller's hold time and the length of the call are both recorded. 
     * The caller's original position in the queue is recorded in origposition.
     */
    'COMPLETECALLER'    => array('holdtime','calltime','origposition'),

    /*
     * The configuration has been reloaded (e.g. with asterisk -rx reload)
     */
    'CONFIGRELOAD'    => array(),

    /*
     * The caller was connected to an agent. Hold time represents the amount of time the caller 
     * was on hold. The bridged channel unique ID contains the unique ID of the queue member 
     * channel that is taking the call. This is useful when trying to link recording filenames 
     * to a particular call in the queue. Ringtime represents the time the queue members phone 
     * was ringing prior to being answered.
     */
    'CONNECT'    => array('holdtime','bridgedchanneluniqueid','ringtime'),

    /*
     * A call has entered the queue. URL (if specified) and Caller*ID are placed in the log.
     */
    'ENTERQUEUE'    => array('url','callerid'),

    /*
     * The caller was exited from the queue forcefully because the queue had no reachable members
     * and it's configured to do that to callers when there are no reachable members. The position 
     * is the caller's position in the queue when they hungup, the origposition is the original 
     * position the caller was when they first entered the queue, and the waittime is how long 
     * the call had been waiting in the queue at the time of disconnect.
     */
    'EXITEMPTY'    => array('positionorig','positionwaittime'),

    /*
     * The caller selected to use a menu key to exit the queue. The key and the caller's position 
     * in the queue are recorded. The caller's entry position and amount of time waited is also recorded.
     */
    'EXITWITHKEY'    => array('key','positionorig','positionwaittime'),

    /*
     * The caller was on hold too long and the timeout expired. The position in the queue when the 
     * timeout occurred, the entry position, and the amount of time waited are logged.
     */
    'EXITWITHTIMEOUT'    => array('positionorig','positionwaittime'),

    /*
     * The queueing system has been started for the first time this session.
     */
    'QUEUESTART'    => array(),

    /*
     * After trying for ringtime ms to connect to the available queue member, the attempt ended 
     * without the member picking up the call. Bad queue member!
     */
    'RINGNOANSWER'    => array('ringtime'),

    /*
     * A call was answered by an agent, but the call was dropped because the channels were not compatible.
     */
    'SYSCOMPAT'    => array(),

    /*
     * Caller was transferred to a different extension. Context and extension are recorded. 
     * The caller's hold time and the length of the call are both recorded, as is the caller's 
     * entry position at the time of the transfer. PLEASE remember that transfers performed by 
     * SIP UA's by way of a reinvite may not always be caught by Asterisk and trigger off this event. 
     * The only way to be 100% sure that you will get this event when a transfer is performed by a queue 
     * member is to use the built-in transfer functionality of Asterisk.
     */
    'TRANSFER'    => array('extension','context','holdtime','calltime','origposition'),

    /*
     * 
     */
    'CLOSED'    => array(),

    /*
     * 
     */
    'FULL'        => array(),

    /*
     * 
     */
    'REROUTEGUIDE'    => array(),

    /*
     * 
     */
    'REROUTENUMBER'    => array(),

);
                
?>