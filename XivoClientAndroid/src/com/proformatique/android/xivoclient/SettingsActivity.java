package com.proformatique.android.xivoclient;

import android.content.Context;
import android.content.SharedPreferences;
import android.content.SharedPreferences.OnSharedPreferenceChangeListener;
import android.os.Bundle;
import android.preference.PreferenceActivity;
import android.telephony.TelephonyManager;

public class SettingsActivity extends PreferenceActivity{

	SharedPreferences settingsPrefs;
	
	@Override
	protected void onCreate(Bundle savedInstanceState) {

		super.onCreate(savedInstanceState);
        addPreferencesFromResource(R.xml.settings);
        settingsPrefs = getPreferenceManager().getSharedPreferences();
        
        /**
         * Init value for mobile number
         */
        if (settingsPrefs.getString("mobile_number", "").equals("")){
        	TelephonyManager tMgr =(TelephonyManager)getApplicationContext().getSystemService(Context.TELEPHONY_SERVICE);
        	String mobileNumber = tMgr.getLine1Number();
        	SharedPreferences.Editor editor = settingsPrefs.edit();
        	editor.putString("mobile_number", mobileNumber);
        	/**
        	 * TODO : Check that default value is visible when no data exists 
        	 *        in EditText field
        	 */
            //editor.commit();
        }
        
        /**
         * This Listener will trigger when users disable the "save_login" parameter,
         * so the app can erase previously saved login and password
         *  
         */
        settingsPrefs.registerOnSharedPreferenceChangeListener(new OnSharedPreferenceChangeListener() {
			
			@Override
			public void onSharedPreferenceChanged(SharedPreferences sharedPreferences,
					String key) {

				if (key.equals("save_login")){
					Boolean saveLogin = sharedPreferences.getBoolean(key, true);
					
					if (!saveLogin){
						
						SharedPreferences loginSettings;
						loginSettings = getSharedPreferences("login_settings", 0);

						SharedPreferences.Editor editor = loginSettings.edit();

						editor.putString("login", "");
						editor.putString("password", "");
			            editor.commit();

						
					}
				}
				
			}
		});
	}


}
