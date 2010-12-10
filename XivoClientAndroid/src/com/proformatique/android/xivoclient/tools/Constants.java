package com.proformatique.android.xivoclient.tools;

public final class Constants {

	/**
	 * Return codes
	 */
	public static final int NO_NETWORK_AVAILABLE = -2;
	public static final int BAD_HOST = -1;
	public static final int NOT_CTI_SERVER = -3;
	public static final int JSON_POPULATE_ERROR = -4;	
	public static final int OK = 1;
	public static final int CONNECTION_OK = 2;
	public static final int LOGIN_KO = 0;

	
	/**
	 * Application constants
	 */
	public static final String XIVO_SERVER= "xivoserver";
	public static final String XIVO_ASTID= "xivo";
	public static final String XIVO_CONTEXT= "default";
	public static final String XIVO_LOGIN_VERSION = "9999";
	public static final String XIVO_VERSION = "1.1";
	public static final String XIVO_LOGIN_OK = "login_id_ok";
	public static final String XIVO_PASSWORD_OK = "login_pass_ok";
	public static final String XIVO_LOGIN_KO = "loginko";
	public static final String XIVO_LOGIN_CAPAS_OK = "login_capas_ok";
}
