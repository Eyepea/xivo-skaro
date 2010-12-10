package com.proformatique.android.xivoclient;

import java.io.IOException;
import java.io.PrintStream;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.Date;
import java.util.HashMap;
import java.util.List;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;
import android.util.Log;
import com.proformatique.android.xivoclient.tools.Constants;

/**
 * This class is a useful lists provider for all class in the app
 * The lists are all initially loaded just after connection to CTI server
 * 
 * @author cquaquin
 *
 */
public class InitialListLoader {

	private static final String LOG_TAG = "LOAD_LISTS";
	
	/**
	 * Reference available lists
	 * WARNING : Let the users list before the others. 
	 * 			 Phones list need users list to be loaded
	 */
	String[] lists = new String[] { "users", "phones"};

	private List<HashMap<String, String>> usersList = new ArrayList<HashMap<String, String>>();
	private List<HashMap<String, String>> historyList = new ArrayList<HashMap<String, String>>();
	private List<String> xletsList = new ArrayList<String>();
	private String xivoId = null;
	private String astId = null;
	private HashMap<String, String> capaPresenceState  = new HashMap<String, String>();
	private List<HashMap<String, String>> statusList = new ArrayList<HashMap<String, String>>();
	private HashMap<String, String> featuresEnablednd = new HashMap<String, String>();
	private HashMap<String, String> featuresBusy = new HashMap<String, String>();
	private HashMap<String, String> featuresRna = new HashMap<String, String>();
	private HashMap<String, String> featuresCallrecord = new HashMap<String, String>();
	private HashMap<String, String> featuresIncallfilter = new HashMap<String, String>();
	private HashMap<String, String> featuresUnc = new HashMap<String, String>();
	private HashMap<String, String> featuresEnablevoicemail = new HashMap<String, String>();

	private static InitialListLoader instance;
	
	public static InitialListLoader getInstance(){
		return instance;
	}
	
	private InitialListLoader(){
		super();
	}

	public static InitialListLoader init(){
		instance = new InitialListLoader();
		return instance;
	}

	public int startLoading(){
		int rCode;
		
		for (String list : lists) {
			rCode = initJsonList(list);
			if (rCode < 1) return rCode;
		}
		
		return Constants.OK;
	}

	@SuppressWarnings("unchecked")
	private int initJsonList(String inputClass) {
		JSONObject jObj = createJsonInputObject(inputClass,"getlist");
		if (jObj!=null){
			try {
				Log.d( LOG_TAG, "Jobj: " + jObj.toString());
				PrintStream output = new PrintStream(Connection.getInstance().getNetworkConnection().getOutputStream());
				output.println(jObj.toString());
			} catch (IOException e) {
				return Constants.NO_NETWORK_AVAILABLE;
			}
			
			JSONObject ReadLineObject = Connection.getInstance().readJsonObjectCTI(inputClass);
			if (ReadLineObject!=null){

				try {
					
					/**
					 * Loading Users list
					 */
					if (inputClass.equals("users")){
						JSONArray jArr = ReadLineObject.getJSONArray("payload");
						int len = jArr.length();

						for(int i = 0; i < len; i++){
							HashMap<String, String> map = new HashMap<String, String>();
							JSONObject jObjCurrent = jArr.getJSONObject(i);
							JSONObject jObjCurrentState = jObjCurrent.getJSONObject("statedetails");
						
							/**
							 * Feed the useful fields to store in the list
							 */
							map.put("xivo_userid", jObjCurrent.getString("xivo_userid"));
							map.put("fullname", jObjCurrent.getString("fullname"));
							map.put("phonenum", jObjCurrent.getString("phonenum"));
							map.put("stateid", jObjCurrentState.getString("stateid"));
							map.put("stateid_longname", jObjCurrentState.getString("longname"));
							map.put("stateid_color", jObjCurrentState.getString("color"));
							map.put("techlist", jObjCurrent.getJSONArray("techlist").getString(0));
							usersList.add(map);

							Log.d( LOG_TAG, "map : " + map.toString());
						}
						/**
						 * Sorting list
						 */
						if (usersList.size()!=0){
							Collections.sort(usersList, new fullNameComparator());
						}
					}
					
					/**
					 * Loading Phones list
					 */
					else if (inputClass.equals("phones")){
						JSONObject jAllPhones = ReadLineObject.getJSONObject("payload").getJSONObject(astId);
						/**
						 * Use users field "techlist" to search objects in phones list
						 */
						int i=0;
						for (HashMap<String, String> mapUser : usersList) {
							JSONObject jPhone = jAllPhones.getJSONObject(mapUser.get("techlist"));
							/**
							 * "Real" phone number is retrieved from phones list
							 */
							mapUser.put("phonenum", jPhone.getString("number"));
							try {
								JSONObject jPhoneStatus = jPhone.getJSONObject("hintstatus");
								mapUser.put("hintstatus_color", jPhoneStatus.getString("color"));
								mapUser.put("hintstatus_code", jPhoneStatus.getString("code"));
								mapUser.put("hintstatus_longname", jPhoneStatus.getString("longname"));
							} catch (JSONException e) {
								Log.d( LOG_TAG, "No Phones status : "+ jPhone.toString());
								mapUser.put("hintstatus_color", "");
								mapUser.put("hintstatus_code", "");
								mapUser.put("hintstatus_longname", "");
							}
							if (mapUser.get("xivo_userid").equals(xivoId)){
								capaPresenceState.put("phonenum", mapUser.get("phonenum"));
								capaPresenceState.put("hintstatus_color", mapUser.get("hintstatus_color"));
								capaPresenceState.put("hintstatus_code", mapUser.get("hintstatus_code"));
								capaPresenceState.put("hintstatus_longname", mapUser.get("hintstatus_longname"));
							}
							usersList.set(i, mapUser);
							i++;
						}
					}
				
				} catch (JSONException e) {
					e.printStackTrace();
					return Constants.JSON_POPULATE_ERROR;
				}
			}
		}

		return Constants.OK;
	}
	
	@SuppressWarnings("unchecked")
	class fullNameComparator implements Comparator
	{
	    public int compare(Object obj1, Object obj2)
	    {
	        HashMap<String, String> update1 = (HashMap<String, String>)obj1;
	        HashMap<String, String> update2 = (HashMap<String, String>)obj2;
	        return update1.get("fullname").compareTo(update2.get("fullname"));
	    }
	}


	/**
	 * Send a presence status and check it has been enabled by server
	 * 
	 * @param inputClass
	 * @param function
	 * @return
	 */
	@SuppressWarnings("unused")
	private int initJsonString(String inputClass, String function) {

		JSONObject jObj = createJsonInputObject(inputClass,"available");
		if (jObj!=null){
			try {
				Log.d( LOG_TAG, "Jobj: " + jObj.toString());
				PrintStream output = new PrintStream(Connection.getInstance().getNetworkConnection().getOutputStream());
				output.println(jObj.toString());
			} catch (IOException e) {
				return Constants.NO_NETWORK_AVAILABLE;
			}
			
			JSONObject jObjCurrent = Connection.getInstance().readJsonObjectCTI("presence");
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
	
	public String getUserId() {
		return astId+"/"+xivoId;
	}

	public String getXivoId() {
		return xivoId;
	}

	public void setXivoId(String xivoId) {
		this.xivoId = xivoId;
	}

	public String getAstId() {
		return astId;
	}

	public void setAstId(String astId) {
		this.astId = astId;
	}

	public List<HashMap<String, String>> getUsersList() {
		return usersList;
	}

	public void setUsersList(List<HashMap<String, String>> usersList) {
		this.usersList = usersList;
	}

	public void replaceUsersList(int i, HashMap<String, String> map) {
		this.usersList.set(i, map);
	}
	
	public List<HashMap<String, String>> getHistoryList() {
		return historyList;
	}

	public void setHistoryList(List<HashMap<String, String>> historyList) {
		this.historyList = historyList;
	}

	public void addHistoryList(HashMap<String, String> map) {
		this.historyList.add(map);
	}
	
	public void clearHistoryList() {
		this.historyList.clear();
	}
	
	@SuppressWarnings("unchecked")
	public void sortHistoryList(){
		Collections.sort(this.historyList, new DateComparator());
	}

	public List<String> getXletsList() {
		return xletsList;
	}
	
	public void setXletsList(List<String> xletsList) {
		this.xletsList = xletsList;
	}

	public HashMap<String, String> getCapaPresenceState() {
		return capaPresenceState;
	}

	public void setCapaPresenceState(HashMap<String, String> capaPresenceState) {
		this.capaPresenceState = capaPresenceState;
	}

	public void putCapaPresenceState(String key, String value) {
		this.capaPresenceState.put(key, value);
	}
	
	public List<HashMap<String, String>> getStatusList() {
		return statusList;
	}

	public void setStatusList(List<HashMap<String, String>> statusList) {
		this.statusList = statusList;
	}

	public void addStatusList(HashMap<String, String> map) {
		this.statusList.add(map);
	}
	
	public HashMap<String, String> getFeaturesEnablednd() {
		return featuresEnablednd;
	}

	public void setFeaturesEnablednd(HashMap<String, String> featuresEnablednd) {
		this.featuresEnablednd = featuresEnablednd;
	}

	public HashMap<String, String> getFeaturesBusy() {
		return featuresBusy;
	}

	public void setFeaturesBusy(HashMap<String, String> featuresBusy) {
		this.featuresBusy = featuresBusy;
	}

	public HashMap<String, String> getFeaturesRna() {
		return featuresRna;
	}

	public void setFeaturesRna(HashMap<String, String> featuresRna) {
		this.featuresRna = featuresRna;
	}

	public HashMap<String, String> getFeaturesCallrecord() {
		return featuresCallrecord;
	}

	public void setFeaturesCallrecord(HashMap<String, String> featuresCallrecord) {
		this.featuresCallrecord = featuresCallrecord;
	}

	public HashMap<String, String> getFeaturesIncallfilter() {
		return featuresIncallfilter;
	}

	public void setFeaturesIncallfilter(HashMap<String, String> featuresIncallfilter) {
		this.featuresIncallfilter = featuresIncallfilter;
	}

	public HashMap<String, String> getFeaturesUnc() {
		return featuresUnc;
	}

	public void setFeaturesUnc(HashMap<String, String> featuresUnc) {
		this.featuresUnc = featuresUnc;
	}

	public HashMap<String, String> getFeaturesEnablevoicemail() {
		return featuresEnablevoicemail;
	}

	public void setFeaturesEnablevoicemail(
			HashMap<String, String> featuresEnablevoicemail) {
		this.featuresEnablevoicemail = featuresEnablevoicemail;
	}





	@SuppressWarnings("unchecked")
	private class DateComparator implements Comparator
	{
		public int compare(Object obj1, Object obj2)
	    {
	    	SimpleDateFormat sd1 = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
	        HashMap<String, String> update1 = (HashMap<String, String>)obj1;
	        HashMap<String, String> update2 = (HashMap<String, String>)obj2;
	        Date d1 = null, d2 = null;
	        try {
				d1 = sd1.parse(update1.get("ts"));
				d2 = sd1.parse(update2.get("ts"));
			} catch (ParseException e) {
				e.printStackTrace();
				return 0;
			}
	        
	        return (((d2.getTime()-d1.getTime())>0)?1:-1);
	    }
	}


}
