package in.ac.iitd.btp.btp_app;

public class WebsiteData {
	public float rating;
	public String url;
	public long pageLoadTime;

	public String toString() {
		return "{'rating':"+rating+",'url':'"+url+"','pageLoadTime':"+pageLoadTime+"}";
	}
}
