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
import org.json.JSONException;
import org.json.JSONObject;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.ComponentName;
import android.content.Context;
import android.content.DialogInterface;
import android.content.Intent;
import android.content.ServiceConnection;
import android.os.Bundle;
import android.os.IBinder;
import android.os.StrictMode;
import android.telephony.PhoneStateListener;
import android.telephony.SignalStrength;
import android.telephony.TelephonyManager;
import android.telephony.gsm.GsmCellLocation;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.Menu;
import android.view.View;
import android.view.View.OnClickListener;
import android.view.ViewGroup;
import android.webkit.WebChromeClient;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ProgressBar;
import android.widget.RatingBar;
import android.widget.TextView;
import android.widget.Toast;

import com.stericson.RootTools.RootTools;
import com.stericson.RootTools.execution.Command;

public class WperfActivity extends Activity {
	public int user_agent = 0;
	Command currentWebsiteTcpdump;
	ServiceConnection mConnection;
	TcpdumpService tcpdumpService;
	boolean mBounded;
	public int mSignalStrength = -1;
	public int signalStrengthAtTest = -1;
	public static final String tag = "WperfActivity";
	WebView webView1;
	Button startBtn, rateBtn;
	EditText et;
	ProgressBar pb;
	String url, deviceId, nwOperator;
	RatingBar ratingWidget;
	long pageLoadTime, pageLoadStartTime, pageLoadEndTime; // milliseconds
	HashMap<Integer, Long> partialPageLoadTimes;
	int[] partialPageLoadTimeKeys = new int[] { 50, 75 };
	int keyCtr = 0;
	float rating;
	ArrayList<String> resources;
	int obsId, networkType, gsmCellId;
	public static final String SERVER_BASE = "http://agni.iitd.ac.in:8000";
	public static final String[] TEST_WEBSITES = {
	// "http://www.facebook.com",
	// "http://www.twitter.com", "http://www.quora.com",
	"http://timesofindia.com",
	// "http://www.nytimes.com",
	// "http://bbc.co.uk", "http://cricinfo.com", "http://www.amazon.com",
	// "http://www.dailymotion.com", "http://www.tumblr.com"
	};
	public static final String[] TEST_WEBSITE_SHORT_NAMES = {
	// "facebook",
	// "http://www.twitter.com", "http://www.quora.com",
	"toi",
	// "nytimes",
	// "http://bbc.co.uk", "http://cricinfo.com", "http://www.amazon.com",
	// "http://www.dailymotion.com", "http://www.tumblr.com"
	};
	public int current_site = 0;
	public HashMap<String, WebsiteData> dataMap0;
	public HashMap<String, WebsiteData> dataMap1;

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
		if (current_site == 0 && user_agent == 0) {

			String name = "obs_" + obsId;
			tcpdumpService.startTcpdump(obsId, current_site, name);
		}
		user_agent = 1;
		webView1.getSettings().setUserAgent(user_agent);
		loadWebSiteNumber(current_site);
		user_agent = 1 - user_agent;
	}

	public void loadWebSiteNumber(int n) {

		webView1.clearHistory();
		webView1.clearFormData();
		webView1.clearCache(true);
		webView1.getSettings().setCacheMode(WebSettings.LOAD_NO_CACHE);
		this.deleteDatabase("webview.db");
		this.deleteDatabase("webviewCache.db");

		String ws = TEST_WEBSITES[n];
		// if(mBounded)
		// {
		// tcpdumpService.stopTcpdump();
		// }

		et.setText(ws);
		partialPageLoadTimes.clear();
		keyCtr = 0;
		signalStrengthAtTest = mSignalStrength;
		pageLoadStartTime = System.currentTimeMillis();
		webView1.loadUrl(ws);
	}

	PhoneStateListener phoneStateListener;

	@Override
	public void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		if (!RootTools.isAccessGiven()) {
			TextView tv = new TextView(this);
			tv.setText("Root access not given. Please ensure root access.");
			setContentView(tv);
		}
		if (!RootTools.isBusyboxAvailable())
			RootTools.offerBusyBox(this);
		obtainOneTimeData();
		StrictMode.ThreadPolicy policy = new StrictMode.ThreadPolicy.Builder()
				.permitAll().build();
		StrictMode.setThreadPolicy(policy);
		phoneStateListener = new PhoneStateListener() {
			@Override
			public void onSignalStrengthsChanged(SignalStrength signalStrength) {
				// TODO Auto-generated method stub
				mSignalStrength = signalStrength.getGsmSignalStrength();
				// The above doesn't work, so using signal strength as the
				// number of signal bars appearing in the statusbar
				String s = signalStrength.toString();
				String s2 = s.substring(s.indexOf("gsm|lte"));
				mSignalStrength = Integer.parseInt(s2.substring(8));
				// Toast.makeText(WperfActivity.this, signalStrength.toString(),
				// Toast.LENGTH_SHORT).show();
				super.onSignalStrengthsChanged(signalStrength);
			}
		};
		TelephonyManager tpm = (TelephonyManager) getSystemService(Context.TELEPHONY_SERVICE);
		tpm.listen(phoneStateListener,
				PhoneStateListener.LISTEN_SIGNAL_STRENGTHS);

		Intent mIntent = new Intent(this, TcpdumpService.class);
		// startService(mIntent);
		mConnection = new ServiceConnection() {

			public void onServiceDisconnected(ComponentName name) {
				// TODO Auto-generated method stub
				Toast.makeText(WperfActivity.this, "onServiceDisconnected",
						Toast.LENGTH_SHORT).show();
				mBounded = false;
			}

			public void onServiceConnected(ComponentName name, IBinder service) {
				// TODO Auto-generated method stub
				Toast.makeText(WperfActivity.this, "onServiceConnected",
						Toast.LENGTH_SHORT).show();
				mBounded = true;
				TcpdumpService.LocalBinder b = (TcpdumpService.LocalBinder) service;
				tcpdumpService = b.getServiceInstance();
				startBtn.setEnabled(true);
			}
		};
		boolean r = getApplicationContext().bindService(mIntent, mConnection,
				BIND_AUTO_CREATE);
		// Toast.makeText(this, "bind result: "+r, Toast.LENGTH_SHORT)
		// .show();

		dataMap0 = new HashMap<String, WebsiteData>();
		dataMap1 = new HashMap<String, WebsiteData>();
		partialPageLoadTimes = new HashMap<Integer, Long>();
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
					dataMap0.clear();
					dataMap1.clear();
					current_site = 0;
					startBtn.setEnabled(false);
					current_site = 0;
					loadNextWebsite();
				} else {
					// TODO:Do Some error handling
				}
			}
		});
		startBtn.setEnabled(false);
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
					getRating();

				}
				if (keyCtr < partialPageLoadTimeKeys.length
						&& progress >= partialPageLoadTimeKeys[keyCtr]) {
					partialPageLoadTimes.put(progress,
							System.currentTimeMillis() - pageLoadStartTime);
					keyCtr++;
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
		int x = 0;
		x++;
		if (x == 1) {
			WebsiteData d = new WebsiteData();
			d.rating = 0;
			d.signalStrength = signalStrengthAtTest;
			d.url = TEST_WEBSITES[current_site];
			d.pageLoadTime = pageLoadTime;
			d.partialPageLoadTimes = new HashMap<Integer, Long>(
					partialPageLoadTimes);
			if (user_agent == 1)
				dataMap0.put(TEST_WEBSITES[current_site], d);
			else
				dataMap1.put(TEST_WEBSITES[current_site], d);
			if (user_agent == 0)
				current_site++;
			if (current_site < TEST_WEBSITES.length || user_agent == 1)
				loadNextWebsite();
			else
				sendDataToServer();
			return;
		}
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
						d.signalStrength = signalStrengthAtTest;
						d.url = TEST_WEBSITES[current_site];
						d.pageLoadTime = pageLoadTime;
						d.partialPageLoadTimes = new HashMap<Integer, Long>(
								partialPageLoadTimes);
						if (user_agent == 0)
							dataMap0.put(TEST_WEBSITES[current_site], d);
						else
							dataMap1.put(TEST_WEBSITES[current_site], d);
						current_site++;
						// rateBtn.setEnabled(false);
						if (current_site == TEST_WEBSITES.length
								&& user_agent == 0) {
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
		Toast.makeText(this, "Sending data to server", Toast.LENGTH_SHORT)
				.show();
		HttpClient httpclient = new DefaultHttpClient();
		List<NameValuePair> nameValuePairs = new ArrayList<NameValuePair>(2);
		try {
			JSONObject j = new JSONObject();

			String data = "{";
			String sep = "";
			for (String key : dataMap0.keySet()) {
				data += sep;
				sep = ", ";
				data += "'" + key + "':" + dataMap0.get(key);
			}
			data += "}";
			j.put("0", data);
			data = "{";
			sep = "";
			for (String key : dataMap0.keySet()) {
				data += sep;
				sep = ", ";
				data += "'" + key + "':" + dataMap1.get(key);
			}
			data += "}";
			j.put("1", data);
			nameValuePairs.add(new BasicNameValuePair("data", j.toString()));
			// nameValuePairs.add(new BasicNameValuePair("resources",
			// resources.toString()));
			HttpPost httppost = new HttpPost(SERVER_BASE
					+ "/wperf/addobservation/id/" + obsId);

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
		} catch (JSONException e) {
			// TODO: handle exception
			Log.e(tag, e.toString());
		}

		tcpdumpService.stopTcpdump();
		startBtn.setEnabled(true);
		switchTabInActivity(0);
	}

	@Override
	public boolean onCreateOptionsMenu(Menu menu) {
		getMenuInflater().inflate(R.menu.activity_main, menu);
		return true;
	}

	public void switchTabInActivity(int indexTabToSwitchTo) {

		MainActivity ParentActivity;
		ParentActivity = (MainActivity) this.getParent();
		ParentActivity.switchTab(0);
	}

	@Override
	protected void onDestroy() {
		// TODO Auto-generated method stub
		if (mBounded) {
			try {
				unbindService(mConnection);
			} catch (Exception e) {
				Log.e("WperfActivity", e + "");
			}
			mBounded = false;
		}
		super.onDestroy();
	}
}
