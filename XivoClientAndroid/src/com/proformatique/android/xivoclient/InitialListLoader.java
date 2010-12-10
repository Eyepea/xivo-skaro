package com.proformatique.android.xivoclient;

import java.io.IOException;
import java.io.PrintStream;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import android.util.Log;

import com.proformatique.android.xivoclient.tools.Constants;

/**
 * This class is a useful lists provider for all class in the app
 * The lists are all loaded just after connection to CTI server
 * 
 * @author cquaquin
 *
 */
public class InitialListLoader {

	private static final String LOG_TAG = "LOAD_LISTS";
	
	/**
	 * Reference available lists
	 */
	String[] lists = new String[] { "users"};//,"history", "phones"};

	public List<HashMap<String, String>> usersList = new ArrayList<HashMap<String, String>>();
	public List<HashMap<String, String>> historyList = new ArrayList<HashMap<String, String>>();
	public List<HashMap<String, String>> phonesList = new ArrayList<HashMap<String, String>>();
	public List<String> Xletslist = new ArrayList<String>();
	public String xivoId = new String();
	
	public static InitialListLoader initialListLoader;
	
	public InitialListLoader(){
		initialListLoader = this;
	}
	
	public int startLoading(){
		int rCode;
		
		for (String list : lists) {
			rCode = initJsonList(list);
			if (rCode < 1) return rCode;
		}
		
		return Constants.OK;
	}

	private int initJsonList(String inputClass) {
		JSONObject jObj = createJsonInputObject(inputClass,"getlist");
		if (jObj!=null){
			try {
				Log.d( LOG_TAG, "Jobj: " + jObj.toString());
				PrintStream output = new PrintStream(Connection.connection.networkConnection.getOutputStream());
				output.println(jObj.toString());
			} catch (IOException e) {
				return Constants.NO_NETWORK_AVAILABLE;
			}
			
			JSONObject ReadLineObject = Connection.connection.readJsonObjectCTI(inputClass);
			if (ReadLineObject!=null){

				try {
					JSONArray jArr = ReadLineObject.getJSONArray("payload");
					int len = jArr.length();

					for(int i = 0; i < len; i++){
						HashMap<String, String> map = new HashMap<String, String>();
						JSONObject jObjCurrent = jArr.getJSONObject(i);
						
						/**
						 * Put here the condition for a new list managed by this class
						 * And select the useful fields to store in the list
						 */
						if (inputClass.equals("users")){
							
							map.put("xivo_userid", jObjCurrent.getString("xivo_userid"));
							map.put("fullname", jObjCurrent.getString("fullname"));
							map.put("phonenum", jObjCurrent.getString("phonenum"));
							map.put("stateid", jObjCurrent.getJSONObject("statedetails").getString("stateid"));
							map.put("stateid_longname", jObjCurrent.getJSONObject("statedetails").getString("longname"));
							usersList.add(map);
						}
						
						Log.d( LOG_TAG, "map : " + map.toString());
					}
				
				} catch (JSONException e) {
					e.printStackTrace();
					return Constants.JSON_POPULATE_ERROR;
				}
			}
		}

		return Constants.OK;
	}

	/**
	 * Send a presence status and check it has been enabled by server
	 * 
	 * @param inputClass
	 * @param function
	 * @return
	 */
	private int initJsonString(String inputClass, String function) {

		JSONObject jObj = createJsonInputObject(inputClass,"available");
		if (jObj!=null){
			try {
				Log.d( LOG_TAG, "Jobj: " + jObj.toString());
				PrintStream output = new PrintStream(Connection.connection.networkConnection.getOutputStream());
				output.println(jObj.toString());
			} catch (IOException e) {
				return Constants.NO_NETWORK_AVAILABLE;
			}
			
			JSONObject jObjCurrent = Connection.connection.readJsonObjectCTI("presence");
			if (jObjCurrent!=null){

				try {
						HashMap<String, String> map = new HashMap<String, String>();

						if (inputClass.equals("users")){
							map.put("xivo_userid", jObjCurrent.getString("xivo_userid"));
						}
						
						Log.d( LOG_TAG, "map : " + map.toString());
				
				} catch (JSONException e) {
					e.printStackTrace();
					return Constants.JSON_POPULATE_ERROR;
				}
			}
		}

		return Constants.OK;
	}
	
	
	private JSONObject createJsonInputObject(String inputClass, String function) {
		JSONObject jObj = new JSONObject();
		try {
			jObj.accumulate("direction", Constants.XIVO_SERVER);
			jObj.accumulate("class",inputClass);
			jObj.accumulate("function", function);
			
			return jObj;
		} catch (JSONException e) {
			return null;
		}
	}
	

	
}
