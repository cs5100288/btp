package in.ac.iitd.btp.btp_app;

import java.io.IOException;
import java.util.concurrent.TimeoutException;

import android.app.Notification;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.app.Service;
import android.content.Intent;
import android.os.Binder;
import android.os.IBinder;
import android.util.Log;
import android.widget.Toast;

import com.stericson.RootTools.RootTools;
import com.stericson.RootTools.exceptions.RootDeniedException;
import com.stericson.RootTools.execution.Command;
import com.stericson.RootTools.execution.Shell;
import com.stericson.RootTools.execution.Shell.OutputHandler;

public class TcpdumpService extends Service {
	Command currentWebsiteTcpdump;
	NotificationManager mNM;
	Shell shell;
	private int NOTIFICATION = R.string.tcpdump_started;
	public final IBinder mBinder = new LocalBinder();

	public class LocalBinder extends Binder {
		public TcpdumpService getServiceInstance() {
			return TcpdumpService.this;
		}
	}

	@Override
	public void onCreate() {
		mNM = (NotificationManager) getSystemService(NOTIFICATION_SERVICE);

		// Display a notification about us starting. We put an icon in the
		// status bar.
		showNotification();
	}

	private void showNotification() {
		showNotification("");
	}

	private void showNotification(String s) {
		CharSequence text = getText(R.string.tcpdump_started);
		showNotification(text, s);
	}

	private void showNotification(CharSequence text, String s) {
		// In this sample, we'll use the same text for the ticker and the
		// expanded notification

		// Set the icon, scrolling text and timestamp
		Notification notification = new Notification(R.drawable.ic_launcher,
				text, System.currentTimeMillis());

		// The PendingIntent to launch our activity if the user selects this
		// notification
		PendingIntent contentIntent = PendingIntent.getActivity(this, 0,
				new Intent(this, WperfActivity.class), 0);

		// Set the info for the views that show in the notification panel.
		notification.setLatestEventInfo(this, s, text, contentIntent);

		// Send the notification.
		mNM.notify(NOTIFICATION, notification);
	}

	@Override
	public IBinder onBind(Intent intent) {
		// TODO Auto-generated method stub
		Toast.makeText(this, "bind called\n", Toast.LENGTH_SHORT).show();
		return mBinder;
	}

	@Override
	public int onStartCommand(Intent intent, int flags, int startId) {
		// TODO Auto-generated method stub
		return START_STICKY;
	}

	public void startTcpdump(int obsId, int websiteNumber, String name) {
		Toast.makeText(this, "start tcpdump called", Toast.LENGTH_SHORT).show();
		Log.d("TcpdumpService", "start tcpdump called");
		// TODO Auto-generated method stub
		try {
			String n = "tcpdump -vv -s 0 -w /sdcard/" + name + ".pcap&";
			// n = "ls &";
			Log.d("TcpdumpService", n);
			// if (shell != null)
			// shell.close();
			shell = RootTools.getShell(true);
			shell.setOutputHandler(new OutputHandler() {
				String identifier;

				public void handleOutput(String output) {
					// TODO Auto-generated method stub
					showNotification(output, "Tcpdump for " + identifier);
					Log.d("RootTools.Shell.OutputHandler", output);
					// Toast.makeText(TcpdumpService.this.getApplicationContext(),
					// output, Toast.LENGTH_SHORT).show();
				}

				OutputHandler init(String s) {
					identifier = s;
					return this;
				}
			}.init("Experiment No. " + obsId));
			currentWebsiteTcpdump = shell.add(new Command(0, n) {
				String shortWebsiteName;

				@Override
				public void output(int arg0, String arg1) {
					// TODO Auto-generated method stub
					// Log.e("TcpdumpService", arg1);
					// showNotification(arg1, "Tcpdump for " +
					// shortWebsiteName);
				}

				Command init(String s) {
					shortWebsiteName = s;
					return this;
				}
			}.init("Experiment No. " + obsId));
			showNotification("Started capture", "Tcpdump for website "
					+ WperfActivity.TEST_WEBSITE_SHORT_NAMES[websiteNumber]);
		}

		catch (IOException e) {
			Log.e("TcpdumpService", e + "");
		} catch (TimeoutException e) {
			Log.e("TcpdumpService", e + "");
		} catch (RootDeniedException e) {
			showNotification("Root Deined");
		}

		return;
	}

	public void stopTcpdump() {
		// TODO Auto-generated method stub
		Log.d("TcpdumpService", "stop service called");
		if (currentWebsiteTcpdump != null) {
			Toast.makeText(this, "tcpdump stopping", Toast.LENGTH_SHORT).show();
			// currentWebsiteTcpdump.terminate("ending dump");
			try {
				// shell.close();
				// shell.kill();
				shell.setOutputHandler(new OutputHandler() {

					public void handleOutput(String output) {
						// TODO Auto-generated method stub

					}
				});
				shell.add(
						new Command(0,
								"for kp in `pidof tcpdump`; do kill -2 $kp; done; echo done;"/*SIGINT*/) {
							@Override
							public void output(int id, String line) {
								// TODO Auto-generated method stub
								mNM.cancel(NOTIFICATION);
							}
						}).waitForFinish();
				mNM.cancel(NOTIFICATION);

			} catch (IOException ioe) {
				Log.e("TcpdumpService", ioe + "");
				Toast.makeText(this, "ioerror closing the shell",
						Toast.LENGTH_SHORT).show();
			} catch (InterruptedException e) {
				// TODO: handle exception
				Log.e("TcpdumpService", e + "");
			}
		}
		return;
	}

	@Override
	public void onDestroy() {
		// Cancel the persistent notification.
		mNM.cancel(NOTIFICATION);

		// Tell the user we stopped.
		Toast.makeText(this, "tcpdump service stopped", Toast.LENGTH_SHORT)
				.show();
		if (shell != null)
			try {
				shell.setOutputHandler(new OutputHandler() {

					public void handleOutput(String output) {
						// TODO Auto-generated method stub

					}
				});
				shell.add(
						new Command(0,
								"for kp in `pidof tcpdump`; do kill $kp; done") {
							@Override
							public void output(int id, String line) {
								// TODO Auto-generated method stub

							}
						}).waitForFinish();
				shell.close();
			} catch (IOException e) {
			} catch (InterruptedException e) {
			}
	}
}
