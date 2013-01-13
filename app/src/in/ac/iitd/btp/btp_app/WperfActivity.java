package in.ac.iitd.btp.btp_app;

import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;

import org.apache.http.HttpResponse;
import org.apache.http.NameValuePair;
import org.apache.http.client.ClientProtocolException;
import org.apache.http.client.HttpClient;
import org.apache.http.client.entity.UrlEncodedFormEntity;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.impl.client.DefaultHttpClient;
import org.apache.http.message.BasicNameValuePair;
import org.apache.http.util.EntityUtils;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.Context;
import android.content.DialogInterface;
import android.os.Bundle;
import android.os.StrictMode;
import android.telephony.TelephonyManager;
import android.telephony.gsm.GsmCellLocation;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.Menu;
import android.view.View;
import android.view.View.OnClickListener;
import android.view.ViewGroup;
import android.webkit.WebChromeClient;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ProgressBar;
import android.widget.RatingBar;
import android.widget.Toast;

public class WperfActivity extends Activity {
	public static final String tag = "WperfActivity";
	WebView webView1;
	Button startBtn, rateBtn;
	EditText et;
	ProgressBar pb;
	String url, deviceId, nwOperator;
	RatingBar ratingWidget;
	long pageLoadTime, pageLoadStartTime, pageLoadEndTime; // milliseconds
	float rating;
	ArrayList<String> resources;
	int obsId, networkType, gsmCellId;
	public static final String SERVER_BASE = "http://agni.iitd.ac.in:8000";
	public static final String[] TEST_WEBSITES = { "http://www.facebook.com",
			"http://www.twitter.com", "http://www.quora.com",
			"http://timesofindia.indiatimes.com", "http://www.nytimes.com",
			"http://bbc.co.uk", "http://cricinfo.com", "http://www.amazon.com",
			"http://www.dailymotion.com", "http://www.tumblr.com" };
	public int current_site = 0;
	public HashMap<String, WebsiteData> dataMap;

	void loadUrl(String url) {
		et.setText(url);
		webView1.loadUrl(url);
	}

	void setUrl(String url) {
		this.url = url;
	}

	String getUrl() {
		return url;
	}

	void obtainOneTimeData() {
		TelephonyManager tpm = (TelephonyManager) getSystemService(Context.TELEPHONY_SERVICE);
		deviceId = tpm.getDeviceId();
	}

	void obtainVolatileData() {

		TelephonyManager tpm = (TelephonyManager) getSystemService(Context.TELEPHONY_SERVICE);
		// translateNetworkType just adds our own representation
		networkType = translateNetworkType(tpm.getNetworkType());
		nwOperator = tpm.getNetworkOperator();
		GsmCellLocation gcloc = (GsmCellLocation) tpm.getCellLocation();
		gsmCellId = gcloc.getCid();
	}

	public void loadNextWebsite() {
		loadWebSiteNumber(current_site);
	}

	public void loadWebSiteNumber(int n) {
		String ws = TEST_WEBSITES[n];
		et.setText(ws);
		pageLoadStartTime=System.currentTimeMillis();
		webView1.loadUrl(ws);
	}

	@Override
	public void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		obtainOneTimeData();
		StrictMode.ThreadPolicy policy = new StrictMode.ThreadPolicy.Builder()
				.permitAll().build();
		StrictMode.setThreadPolicy(policy);
		dataMap = new HashMap<String, WebsiteData>();
		resources = new ArrayList<String>();
		setContentView(R.layout.activity_wperf);
		webView1 = (WebView) findViewById(R.id.webView1);
		startBtn = (Button) findViewById(R.id.button1);
		rateBtn = (Button) findViewById(R.id.button2);
		et = (EditText) findViewById(R.id.editText1);
		pb = (ProgressBar) findViewById(R.id.progressBar1);
		ratingWidget = (RatingBar) findViewById(R.id.ratingBar1);
		startBtn.setOnClickListener(new OnClickListener() {
			public void onClick(View v) {
				// TODO Auto-generated method stub
				int newId = getNewIdFromServer();
				if (newId >= 0) {
					obsId = newId;
					dataMap.clear();
					current_site = 0;
					startBtn.setEnabled(false);
					loadNextWebsite();
				} else {
					// TODO:Do Some error handling
				}
			}
		});
		rateBtn.setEnabled(false);
		rateBtn.setOnClickListener(new OnClickListener() {
			
			public void onClick(View v) {
				// TODO Auto-generated method stub
			getRating();	
			}
		});
		webView1.setWebViewClient(new WebViewClient() {
			@Override
			public boolean shouldOverrideUrlLoading(WebView view, String url) {
				// TODO Auto-generated method stub
				loadUrl(url);
				return true;
			}

			@Override
			public void onLoadResource(WebView view, String url) {
				// TODO Auto-generated method stub
				resources.add(url);
				super.onLoadResource(view, url);
			}
		});
		webView1.getSettings().setJavaScriptEnabled(true);
		webView1.setWebChromeClient(new WebChromeClient() {
			@Override
			public void onProgressChanged(WebView view, int progress) {
				// TODO Auto-generated method stub
				if (progress < 100 && pb.getVisibility() == ProgressBar.GONE) {
					pb.setVisibility(ProgressBar.VISIBLE);
				}
				pb.setProgress(progress);
				if (progress == 100) {
					pageLoadEndTime = System.currentTimeMillis();
					pageLoadTime = pageLoadEndTime - pageLoadStartTime;
					// Toast.makeText(WperfActivity.this,
					// "LoadTime: "+pageLoadTime+" ms",
					// Toast.LENGTH_SHORT).show();
					pb.setVisibility(ProgressBar.GONE);
					rateBtn.setEnabled(true);
					
				}
				if (progress == 0) {					
					rateBtn.setEnabled(false);
					Toast.makeText(WperfActivity.this, "progress = 0",
							Toast.LENGTH_SHORT).show();
				}
			}
		});
	}

	int translateNetworkType(int ntype) {
		// identity mapping for now. maybe we'll continue using it.
		// main reason was, the value of the constants can be different
		// http://developer.android.com/reference/android/telephony/TelephonyManager.html#getNetworkType()
		return ntype;
	}

	void getRating() {
		Context mContext = this;
		AlertDialog.Builder builder = new AlertDialog.Builder(mContext);
		// use a custom View defined in xml

		View view = LayoutInflater.from(mContext).inflate(R.layout.rating,
				(ViewGroup) findViewById(R.id.layout_root));
		ratingWidget = (RatingBar) view.findViewById(R.id.ratingBar1);
		builder.setView(view);
		builder.setPositiveButton(android.R.string.ok,
				new DialogInterface.OnClickListener() {
					public void onClick(DialogInterface dialog, int which) {
						// TODO Auto-generated method stub
						rating = ratingWidget.getRating();
						WebsiteData d = new WebsiteData();
						d.rating = rating;
						d.url = TEST_WEBSITES[current_site];
						d.pageLoadTime = pageLoadTime;
						dataMap.put(TEST_WEBSITES[current_site], d);
						current_site++;
						//rateBtn.setEnabled(false);
						if (current_site == TEST_WEBSITES.length) {
							sendDataToServer();
							current_site = 0;
							startBtn.setEnabled(true);
						} else {
							loadNextWebsite();
						}
					}

				});
		AlertDialog alertDialog = builder.create();

		alertDialog.show();
	}

	public int parseId(String s) {
		return Integer.parseInt(s.substring(3).trim());
	}

	public int getNewIdFromServer() {
		obtainVolatileData();
		HttpClient httpclient = new DefaultHttpClient();
		HttpPost httppost = new HttpPost(SERVER_BASE + "/wperf/getnewobsid");
		List<NameValuePair> nameValuePairs = new ArrayList<NameValuePair>(2);
		nameValuePairs.add(new BasicNameValuePair("tester", deviceId));
		nameValuePairs.add(new BasicNameValuePair("gsmCellId", gsmCellId + ""));
		nameValuePairs.add(new BasicNameValuePair("operator", nwOperator + ""));
		nameValuePairs.add(new BasicNameValuePair("networkType", networkType
				+ ""));
		String respStr;
		int id = -1;
		try {
			// set post parameters
			// Execute HTTP Post Request
			httppost.setEntity(new UrlEncodedFormEntity(nameValuePairs));
			HttpResponse response = httpclient.execute(httppost);
			respStr = EntityUtils.toString(response.getEntity());
			id = parseId(respStr);
		} catch (ClientProtocolException e) {
			// TODO Auto-generated catch block
			Log.e(tag, e.toString());
		} catch (IOException e) {
			// TODO Auto-generated catch block
			Log.e(tag, e.toString());
		} catch (Exception e) {
			Log.e(tag, e.toString());
		}
		return id;
	}

	public void sendDataToServer() {
		HttpClient httpclient = new DefaultHttpClient();
		List<NameValuePair> nameValuePairs = new ArrayList<NameValuePair>(2);
		String data = "{";
		String sep="";
		for (String key : dataMap.keySet()) {
			data+=sep;
			sep=", ";
			data += "'" + key + "':" + dataMap.get(key);
		}
		data += "}";
		nameValuePairs.add(new BasicNameValuePair("data", data));		
		// nameValuePairs.add(new BasicNameValuePair("resources",
		// resources.toString()));
		HttpPost httppost = new HttpPost(SERVER_BASE
				+ "/wperf/addobservation/id/" + obsId);

		try {
			// Add your data
			httppost.setEntity(new UrlEncodedFormEntity(nameValuePairs));
			// Execute HTTP Post Request
			HttpResponse response = httpclient.execute(httppost);
			Log.d(tag, "Response: " + response);
		} catch (ClientProtocolException e) {
			// TODO Auto-generated catch block
			Log.e(tag, e.toString());
		} catch (IOException e) {
			// TODO Auto-generated catch block
			Log.e(tag, e.toString());
		}
		switchTabInActivity(0);
	}

	@Override
	public boolean onCreateOptionsMenu(Menu menu) {
		getMenuInflater().inflate(R.menu.activity_main, menu);
		return true;
	}
	public void switchTabInActivity(int indexTabToSwitchTo){
        MainActivity ParentActivity;
        ParentActivity = (MainActivity) this.getParent();
        ParentActivity.switchTab(0);
}
}
