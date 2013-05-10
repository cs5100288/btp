package in.ac.iitd.btp.btp_app;

import java.util.HashMap;

import org.json.JSONException;
import org.json.JSONObject;

import android.util.Log;

public class WebsiteData {
	public float rating;
	public String url;
	public long pageLoadTime;
	public int signalStrength;
	
	public HashMap<Integer, Long> partialPageLoadTimes;
	
	public String toString() {
		try{
		JSONObject j = new JSONObject();
		j.put("rating", rating);
		j.put("url", url);
		j.put("pageLoadTime", pageLoadTime);
		j.put("signalStrength", signalStrength);
		j.put("partialPageLoadTimes", partialPageLoadTimes);
		Log.d("WebsiteData", j.toString());
		return j.toString();
		}
		catch(JSONException e)
		{
			Log.e("WebsiteData", e+"");
			return "ERROR";
		}
	}
}
