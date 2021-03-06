<?xml version="1.0" encoding="UTF-8"?>
<device  xsi:type="axl:XIPPhone" ctiid="7" uuid="{89b84111-68bf-4498-8233-d9935482e0f2}">
    <fullConfig>true</fullConfig>
    <deviceProtocol>SIP</deviceProtocol>
    <sshUserId>admin</sshUserId>
    <sshPassword>cisco</sshPassword>
    <ipAddressMode>0</ipAddressMode>
    <allowAutoConfig>true</allowAutoConfig>
    <ipPreferenceModeControl>0</ipPreferenceModeControl>
    <tzdata>
        <tzolsonversion>2009p</tzolsonversion>
        <tzupdater>tzupdater.jar</tzupdater>
    </tzdata>
    <featurePolicyFile>DefaultFP.xml</featurePolicyFile>
    <devicePool  uuid="{1b1b9eb6-7803-11d3-bdf0-00108302ead1}">
        <revertPriority>0</revertPriority>
        <name>Default</name>
        <dateTimeSetting  uuid="{9ec4850a-7748-11d3-bdf0-00108302ead1}">
            <name>CMLocal</name>
            <dateTemplate>M/D/Y</dateTemplate>
            <timeZone></timeZone>
            <olsonTimeZone>America/Montreal</olsonTimeZone>
        </dateTimeSetting>
        <callManagerGroup>
            <name>Default</name>
            <tftpDefault>true</tftpDefault>
            <members>
                <member  priority="0">
                    <callManager>
                        <name>CUCM</name>
                        <description>CUCM</description>
                        <ports>
                            <ethernetPhonePort>2000</ethernetPhonePort>
                            <sipPort>5060</sipPort>
                            <securedSipPort>5061</securedSipPort>
                            <mgcpPorts>
                                <listen>2427</listen>
                                <keepAlive>2428</keepAlive>
                            </mgcpPorts>
                        </ports>
                        <processNodeName>10.97.0.129</processNodeName>
                    </callManager>
                </member>
            </members>
        </callManagerGroup>
        <srstInfo  uuid="{cd241e11-4a58-4d3d-9661-f06c912a18a3}">
            <name>Enable</name>
            <srstOption>Enable</srstOption>
            <userModifiable>true</userModifiable>
            <ipAddr1>10.97.0.129</ipAddr1>
            <port1>2000</port1>
            <ipAddr2></ipAddr2>
            <port2>2000</port2>
            <ipAddr3></ipAddr3>
            <port3>2000</port3>
            <sipIpAddr1></sipIpAddr1>
            <sipPort1>5060</sipPort1>
            <sipIpAddr2></sipIpAddr2>
            <sipPort2>5060</sipPort2>
            <sipIpAddr3></sipIpAddr3>
            <sipPort3>5060</sipPort3>
            <isSecure>false</isSecure>
        </srstInfo>
        <mlppDomainId>-1</mlppDomainId>
        <mlppIndicationStatus>Default</mlppIndicationStatus>
        <preemption>Default</preemption>
        <connectionMonitorDuration>120</connectionMonitorDuration>
    </devicePool>
    <TVS>
        <members>
            <member  priority="0">
                <port>2445</port>
                <address>10.97.0.129</address>
            </member>
        </members>
    </TVS>
    <sipProfile>
        <sipProxies>
            <backupProxy>USECALLMANAGER</backupProxy>
            <backupProxyPort>5060</backupProxyPort>
            <emergencyProxy>USECALLMANAGER</emergencyProxy>
            <emergencyProxyPort>5060</emergencyProxyPort>
            <outboundProxy>USECALLMANAGER</outboundProxy>
            <outboundProxyPort>5060</outboundProxyPort>
            <registerWithProxy>true</registerWithProxy>
        </sipProxies>
        <sipCallFeatures>
            <cnfJoinEnabled>true</cnfJoinEnabled>
            <callForwardURI>x-cisco-serviceuri-cfwdall</callForwardURI>
            <callPickupURI>x-cisco-serviceuri-pickup</callPickupURI>
            <callPickupListURI>x-cisco-serviceuri-opickup</callPickupListURI>
            <callPickupGroupURI>x-cisco-serviceuri-gpickup</callPickupGroupURI>
            <meetMeServiceURI>x-cisco-serviceuri-meetme</meetMeServiceURI>
            <abbreviatedDialURI>x-cisco-serviceuri-abbrdial</abbreviatedDialURI>
            <rfc2543Hold>false</rfc2543Hold>
            <callHoldRingback>2</callHoldRingback>
            <localCfwdEnable>true</localCfwdEnable>
            <semiAttendedTransfer>true</semiAttendedTransfer>
            <anonymousCallBlock>2</anonymousCallBlock>
            <callerIdBlocking>2</callerIdBlocking>
            <dndControl>0</dndControl>
            <remoteCcEnable>false</remoteCcEnable>
            <retainForwardInformation>false</retainForwardInformation>
        </sipCallFeatures>
        <sipStack>
            <sipInviteRetx>6</sipInviteRetx>
            <sipRetx>10</sipRetx>
            <timerInviteExpires>180</timerInviteExpires>
            <timerRegisterExpires>3600</timerRegisterExpires>
            <timerRegisterDelta>5</timerRegisterDelta>
            <timerKeepAliveExpires>120</timerKeepAliveExpires>
            <timerSubscribeExpires>120</timerSubscribeExpires>
            <timerSubscribeDelta>5</timerSubscribeDelta>
            <timerT1>500</timerT1>
            <timerT2>4000</timerT2>
            <maxRedirects>70</maxRedirects>
            <remotePartyID>true</remotePartyID>
            <userInfo>None</userInfo>
        </sipStack>
        <autoAnswerTimer>0</autoAnswerTimer>
        <autoAnswerAltBehavior>false</autoAnswerAltBehavior>
        <autoAnswerOverride>true</autoAnswerOverride>
        <transferOnhookEnabled>false</transferOnhookEnabled>
        <enableVad>false</enableVad>
        <preferredCodec>none</preferredCodec>
        <dtmfAvtPayload>101</dtmfAvtPayload>
        <dtmfDbLevel>3</dtmfDbLevel>
        <dtmfOutofBand>avt</dtmfOutofBand>
        <kpml>3</kpml>
        <phoneLabel>Wouf</phoneLabel>
        <stutterMsgWaiting>0</stutterMsgWaiting>
        <callStats>true</callStats>
        <offhookToFirstDigitTimer>15000</offhookToFirstDigitTimer>
        <T302Timer>15000</T302Timer>
        <silentPeriodBetweenCallWaitingBursts>10</silentPeriodBetweenCallWaitingBursts>
        <disableLocalSpeedDialConfig>true</disableLocalSpeedDialConfig>
        <poundEndOfDial>false</poundEndOfDial>
        <startMediaPort>16384</startMediaPort>
        <stopMediaPort>32766</stopMediaPort>
        <sipLines>
            <line  button="1" lineIndex="1">
                <featureID>9</featureID>
                <featureLabel>301</featureLabel>
                <proxy>USECALLMANAGER</proxy>
                <port>5060</port>
                <name>user301</name>
                <displayName></displayName>
                <autoAnswer>
                    <autoAnswerEnabled>2</autoAnswerEnabled>
                </autoAnswer>
                <callWaiting>3</callWaiting>
                <authName>user301</authName>
                <authPassword>user301</authPassword>
                <sharedLine>false</sharedLine>
                <messageWaitingLampPolicy>1</messageWaitingLampPolicy>
                <messageWaitingAMWI>0</messageWaitingAMWI>
                <messagesNumber>*98</messagesNumber>
                <ringSettingIdle>4</ringSettingIdle>
                <ringSettingActive>5</ringSettingActive>
                <contact>user301</contact>
                <forwardCallInfoDisplay>
                    <callerName>true</callerName>
                    <callerNumber>false</callerNumber>
                    <redirectedNumber>false</redirectedNumber>
                    <dialedNumber>true</dialedNumber>
                </forwardCallInfoDisplay>
                <maxNumCalls>4</maxNumCalls>
                <busyTrigger>2</busyTrigger>
            </line>
            <line  button="2">
                <featureID>21</featureID>
                <featureLabel>User302</featureLabel>
                <speedDialNumber>302</speedDialNumber>
                <featureOptionMask>1</featureOptionMask>
            </line>
        </sipLines>
        <externalNumberMask></externalNumberMask>
        <voipControlPort>5060</voipControlPort>
        <dscpForAudio>184</dscpForAudio>
        <dscpVideo>136</dscpVideo>
        <dscpForTelepresence>128</dscpForTelepresence>
        <ringSettingBusyStationPolicy>0</ringSettingBusyStationPolicy>
        <dialTemplate>dialplan.xml</dialTemplate>
        <softKeyFile>Softkey.xml</softKeyFile>
        <alwaysUsePrimeLine>false</alwaysUsePrimeLine>
        <alwaysUsePrimeLineVoiceMail>false</alwaysUsePrimeLineVoiceMail>
    </sipProfile>
    <MissedCallLoggingOption>1000</MissedCallLoggingOption>
    <commonProfile>
        <phonePassword></phonePassword>
        <backgroundImageAccess>true</backgroundImageAccess>
        <callLogBlfEnabled>2</callLogBlfEnabled>
    </commonProfile>
    <loadInformation>sip8961.9-1-2</loadInformation>

    <vendorConfig>
        <disableSpeaker>false</disableSpeaker>
        <disableSpeakerAndHeadset>false</disableSpeakerAndHeadset>
        <pcPort>0</pcPort>
        <sdio>1</sdio>
        <garp>1</garp>
        <voiceVlanAccess>0</voiceVlanAccess>
        <webAccess>0</webAccess>
        <spanToPCPort>1</spanToPCPort>
        <loggingDisplay>0</loggingDisplay>
        <recordingTone>0</recordingTone>
        <recordingToneLocalVolume>100</recordingToneLocalVolume>
        <recordingToneRemoteVolume>50</recordingToneRemoteVolume>
        <recordingToneDuration></recordingToneDuration>
        <displayOnWhenIncomingCall>1</displayOnWhenIncomingCall>
        <logServer></logServer>
        <g722CodecSupport>0</g722CodecSupport>
        <headsetWidebandUIControl>0</headsetWidebandUIControl>
        <headsetWidebandEnable>0</headsetWidebandEnable>
        <lldpAssetId></lldpAssetId>
        <powerPriority>0</powerPriority>
        <detectCMConnectionFailure>0</detectCMConnectionFailure>
    </vendorConfig>

    <commonConfig>
    </commonConfig>
    <enterpriseConfig>
    </enterpriseConfig>
    <versionStamp>1280870288-91f38f2d-7fff-4a42-87cd-76f9b4a802fc</versionStamp>
    <addOnModules>
    </addOnModules>
    <userLocale>
        <name>french_france</name>
        <uid>1</uid>
        <langCode>fr_FR</langCode>
        <version>8.0.0.1(4)</version>
        <winCharSet>iso-8859-1</winCharSet>
        <ntps>
            <ntp>
                <name>10.97.0.129</name>
                <ntpMode>Unicast</ntpMode>
            </ntp>
        </ntps>
    </userLocale>
    <networkLocale>france</networkLocale>
    <networkLocaleInfo>
        <name>france</name>
        <uid>64</uid>
        <version>8.0.0.1(4)</version>
    </networkLocaleInfo>
    <deviceSecurityMode>1</deviceSecurityMode>
    <idleTimeout>0</idleTimeout>
    <authenticationURL>http://CUCM:8080/ccmcip/authenticate.jsp</authenticationURL>
    <directoryURL>http://10.97.0.130:80/service/ipbx/web_services.php/phonebook/menu</directoryURL>
    <idleURL></idleURL>
    <informationURL>http://CUCM:8080/ccmcip/GetTelecasterHelpText.jsp</informationURL>
    <messagesURL></messagesURL>
    <proxyServerURL></proxyServerURL>
    <servicesURL>http://CUCM:8080/ccmcip/getservicesmenu.jsp</servicesURL>
    <secureAuthenticationURL>https://CUCM:8443/ccmcip/authenticate.jsp</secureAuthenticationURL>
    <secureDirectoryURL>http://10.97.0.130:80/service/ipbx/web_services.php/phonebook/menu</secureDirectoryURL>
    <secureIdleURL></secureIdleURL>
    <secureInformationURL>https://CUCM:8443/ccmcip/GetTelecasterHelpText.jsp</secureInformationURL>
    <secureMessagesURL></secureMessagesURL>
    <secureServicesURL>https://CUCM:8443/ccmcip/getservicesmenu.jsp</secureServicesURL>
    <dscpForSCCPPhoneConfig>96</dscpForSCCPPhoneConfig>
    <dscpForSCCPPhoneServices>0</dscpForSCCPPhoneServices>
    <dscpForCm2Dvce>96</dscpForCm2Dvce>
    <transportLayerProtocol>2</transportLayerProtocol>
    <dndCallAlert>5</dndCallAlert>
    <phonePersonalization>1</phonePersonalization>
    <rollover>0</rollover>
    <singleButtonBarge>0</singleButtonBarge>
    <joinAcrossLines>0</joinAcrossLines>
    <autoCallPickupEnable>false</autoCallPickupEnable>
    <blfAudibleAlertSettingOfIdleStation>0</blfAudibleAlertSettingOfIdleStation>
    <blfAudibleAlertSettingOfBusyStation>0</blfAudibleAlertSettingOfBusyStation>
    <capfAuthMode>0</capfAuthMode>
    <capfList>
        <capf>
            <phonePort>3804</phonePort>
            <processNodeName>CUCM</processNodeName>
        </capf>
    </capfList>
    <certHash></certHash>
    <encrConfig>false</encrConfig>
    <advertiseG722Codec>1</advertiseG722Codec>
    <mobility>
        <handoffdn></handoffdn>
        <dtmfdn></dtmfdn>
        <ivrdn></ivrdn>
        <dtmfHoldCode>*81</dtmfHoldCode>
        <dtmfExclusiveHoldCode>*82</dtmfExclusiveHoldCode>
        <dtmfResumeCode>*83</dtmfResumeCode>
        <dtmfTxfCode>*84</dtmfTxfCode>
        <dtmfCnfCode>*85</dtmfCnfCode>
    </mobility>
    <userId></userId>
    <phoneServices  useHTTPS="true">
        <provisioning>2</provisioning>
        <phoneService  type="1" category="0">
            <name>Missed Calls</name>
            <url>Application:Cisco/MissedCalls</url>
            <vendor></vendor>
            <version></version>
        </phoneService>
        <phoneService  type="2" category="0">
            <name>Voicemail</name>
            <url>Application:Cisco/Voicemail</url>
            <vendor></vendor>
            <version></version>
        </phoneService>
        <phoneService  type="1" category="0">
            <name>Received Calls</name>
            <url>Application:Cisco/ReceivedCalls</url>
            <vendor></vendor>
            <version></version>
        </phoneService>
        <phoneService  type="1" category="0">
            <name>Placed Calls</name>
            <url>Application:Cisco/PlacedCalls</url>
            <vendor></vendor>
            <version></version>
        </phoneService>
        <phoneService  type="1" category="0">
            <name>Personal Directory</name>
            <url>Application:Cisco/PersonalDirectory</url>
            <vendor></vendor>
            <version></version>
        </phoneService>
        <phoneService  type="1" category="0">
            <name>Corporate Directory</name>
            <url>Application:Cisco/CorporateDirectory</url>
            <vendor></vendor>
            <version></version>
        </phoneService>
    </phoneServices>
</device>
