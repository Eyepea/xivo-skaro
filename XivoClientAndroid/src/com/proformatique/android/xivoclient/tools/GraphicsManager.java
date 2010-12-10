package com.proformatique.android.xivoclient.tools;

import android.content.Context;
import android.content.res.Resources;
import android.graphics.Bitmap;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.PorterDuff;
import android.graphics.drawable.BitmapDrawable;
import android.graphics.drawable.Drawable;
import android.util.Log;
import android.widget.ImageView;

import com.proformatique.android.xivoclient.*;

public class GraphicsManager {
	
	private static final String LOG_TAG = "GRAPHICS_MANAGER";
	private static int currentapiVersion = android.os.Build.VERSION.SDK_INT;
	
	public static int getStateIcon(String stateId){

		int iconId = 0;
		
		  if (stateId.equals("available")){
			  iconId = R.drawable.sym_presence_available;
		  }
		  else if (stateId.equals("berightback")){
			  iconId = R.drawable.sym_presence_idle;
		  }
		  else if (stateId.equals("away")){
			  iconId = R.drawable.sym_presence_idle;
		  }
		  else if (stateId.equals("donotdisturb")){
			  iconId = R.drawable.sym_presence_away;
		  }
		  else if (stateId.equals("outtolunch")){
			  iconId = R.drawable.sym_presence_idle;
		  }
		  else {
			  iconId = R.drawable.sym_presence_offline;
		  }

		return iconId;
	}

	public static int getCallIcon(String direction) {
		int iconId = 0;
		
		if (direction.equals("IN")) {
			iconId = R.drawable.call_received;
		}
		else if (direction.equals("OUT")) {
			iconId = R.drawable.call_sent;
		}
		
		return iconId;
	}

	public static void setIconStateDisplay(Context context, ImageView icon, 
			String color) {
		Log.d( LOG_TAG, "Color State Presence : "+ color);
		  /**
		   * Conversion of bad color strings
		   */
		  color = color.replaceFirst("grey", "gray");
		  icon.setColorFilter(null);
		  
		  if (currentapiVersion <= android.os.Build.VERSION_CODES.ECLAIR_MR1) { 
			  Drawable dr = getDrawableCopy(context, R.drawable.personal_trans);
			  icon.setImageDrawable(dr);
		  }

		  if (!color.equals(""))
			  icon.setColorFilter(Color.parseColor(color), PorterDuff.Mode.MULTIPLY);
		  else
			  icon.setColorFilter(Color.TRANSPARENT, PorterDuff.Mode.MULTIPLY);
		
	}

	public static void setIconPhoneDisplay(Context context, ImageView icon, 
			String color) {
		Log.d( LOG_TAG, "Color Phone : "+ color);
		  /**
		   * Conversion of bad color strings
		   */
		color = color.replaceFirst("grey", "gray");
		icon.setColorFilter(null);
		
		if (currentapiVersion <= android.os.Build.VERSION_CODES.ECLAIR_MR1) { 
			Drawable dr = getDrawableCopy(context, R.drawable.ic_dial_number_wht);
			icon.setImageDrawable(dr);
		}

		if (!color.equals(""))
			icon.setColorFilter(Color.parseColor(color), PorterDuff.Mode.SRC_ATOP);
		  else
			  icon.setColorFilter(Color.TRANSPARENT, PorterDuff.Mode.SRC_ATOP);
		
	}

	private static Drawable getDrawableCopy(Context context, int idRes) {
		  /**
		   * Tricky tip to avoid colors being duplicated :
		   * get a copy of the drawable and apply it on the ImageView
		   */
		  Log.d( LOG_TAG, "Hack : Copy drawable");

		  Resources res = context.getResources();
		  Drawable drawable = res.getDrawable(idRes);
		  drawable.setColorFilter(null);

		  Bitmap iconBitmap = Bitmap.createBitmap(30, 30, Bitmap.Config.ARGB_4444);
		  drawable.setBounds(0, 0, 30, 30); 
		  drawable.draw(new Canvas(iconBitmap));
		  Drawable dr2 = (new BitmapDrawable(res, iconBitmap)).getCurrent();
		
		  return dr2;
		  
	}


}
