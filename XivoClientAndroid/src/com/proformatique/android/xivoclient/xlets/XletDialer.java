package com.proformatique.android.xivoclient.xlets;

import java.io.IOException;
import java.io.PrintStream;

import org.json.JSONException;
import org.json.JSONObject;

import com.proformatique.android.xivoclient.Connection;
import com.proformatique.android.xivoclient.R;
import com.proformatique.android.xivoclient.tools.Constants;

import android.app.Activity;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.EditText;

public class XletDialer extends Activity implements XletInterface{

	private static final String LOG_TAG = "XLET DIALER";
	EditText phoneNumber;
	
	@Override
	protected void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);

		setContentView(R.layout.xlet_dialer);
		phoneNumber = (EditText) findViewById(R.id.number);
	}
	
    public void clickOnCall(View v) {
    	/**
    	 * Creating Call Json object
    	 */
    	JSONObject jCalling = createJsonCallingObject("originate", null, 
    			phoneNumber.getText().toString());
		try {
			Log.d( LOG_TAG, "jCalling: " + jCalling.toString());
			PrintStream output = new PrintStream(Connection.connection.networkConnection.getOutputStream());
			output.println(jCalling.toString());
		} catch (IOException e) {
			
		}
	
    	
    }
    
	private JSONObject createJsonCallingObject(String inputClass, 
			String phoneNumberSrc,
			String phoneNumberDest) {
		
		JSONObject jObj = new JSONObject();
		String phoneSrc;
		
		if (phoneNumberSrc == null)
			phoneSrc = "user:special:me";
		else phoneSrc = phoneNumberSrc;
		
		try {
			jObj.accumulate("direction", Constants.XIVO_SERVER);
			jObj.accumulate("class",inputClass);
			jObj.accumulate("source", phoneSrc);
			jObj.accumulate("destination", "ext:"+phoneNumberDest);
			
			return jObj;
		} catch (JSONException e) {
			return null;
		}
	}

	
    public void clickOn1(View v) {
    	phoneNumber.append("1");
    }

    public void clickOn2(View v) {
    	phoneNumber.append("2");
    }
	
    public void clickOn3(View v) {
    	phoneNumber.append("3");
    }

    public void clickOn4(View v) {
    	phoneNumber.append("4");
    }

    public void clickOn5(View v) {
    	phoneNumber.append("5");
    }

    public void clickOn6(View v) {
    	phoneNumber.append("6");
    }

    public void clickOn7(View v) {
    	phoneNumber.append("7");
    }

    public void clickOn8(View v) {
    	phoneNumber.append("8");
    }

    public void clickOn9(View v) {
    	phoneNumber.append("9");
    }

    public void clickOn0(View v) {
    	phoneNumber.append("0");
    }

    public void clickOnStar(View v) {
    	phoneNumber.append("*");
    }

    public void clickOnSharp(View v) {
    	phoneNumber.append("#");
    }
}
