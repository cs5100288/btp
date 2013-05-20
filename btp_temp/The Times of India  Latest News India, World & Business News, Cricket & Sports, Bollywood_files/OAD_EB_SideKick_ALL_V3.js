var ebScriptFileName = "OAD_EB_SideKick_ALL_V3.js";

var ebScriptQuery = function(scriptPath) {
  this.scriptPath = scriptPath;
}
ebScriptQuery.prototype = {
  get: function() {
	var srcRegex = new RegExp(this.scriptPath.replace('.', '\\.') + '(\\?.*)?$');
    var scripts = document.getElementsByTagName("script");
    for (var i = 0; i < scripts.length; i++) {
      var script = scripts[i];
      if (script.src && script.src.match(srcRegex)) {
        var query = script.src.match(/\?([^#]*)(#.*)?/);
        return !query ? '' : query[1];
      }
    }
    return '';
  },
  parse: function() {
    var result = {};
    var query = this.get();
    var components = query.split('&');
 
    for (var i = 0; i < components.length; i++) {
      var pair = components[i].split('=');
      var name = pair[0], value = pair[1];
 
      if (!result[name]) result[name] = [];
      // decode
      if (!value) {
        value = 'true';
      } else {
        try {
          value = decodeURIComponent(value);
        } catch (e) {
          value = unescape(value);
        }
      }
 
      // MacIE way
      var values = result[name];
      values[values.length] = value;
    }
    return result;
  },
  flatten: function() {
    var queries = this.parse();
    for (var name in queries) {
      queries[name] = queries[name][0];
    }
    return queries;
  },
  toString: function() {
    return 'ebScriptQuery [path=' + this.scriptPath + ']';
  }
}

//verify by Ad ID or Flight ID
try{
	var gEbQueries = new ebScriptQuery(ebScriptFileName).flatten();	
	if(gEbQueries["type"] == 'oob'){ // out-of-banner/floating ad
		if(typeof(gEbEyes) != "undefined") {			
			// check is the same as the ad is defined in the script
			if(gEbQueries["adid"]){
				for(i = gEbEyes.length-1; i>-1; i--){
					if(gEbEyes[i].adData.nAdID == gEbQueries["adid"]){
						gEbEyes[i].adData.customEventHandler = new ebCCustomEventHandlers();
						break;
					}
				}
			}
			if(gEbQueries["flightid"]){
				for(i = gEbEyes.length-1; i>-1; i--){					
					if(gEbEyes[i].adData.nFlightID == gEbQueries["flightid"]){
						gEbEyes[i].adData.customEventHandler = new ebCCustomEventHandlers();
						break;
					}
				}			
			}
		}
	} else{ //rich banner / default
		if(typeof(gEbBanners) != "undefined"){			
			if(gEbQueries["adid"]){	
				for(i = gEbBanners.length-1; i>-1; i--){
					if(gEbBanners[i].adData.nAdID == gEbQueries["adid"]){
						gEbBanners[i].adData.customEventHandler = new ebCCustomEventHandlers();
						break;
					}
				}
			}
			if(gEbQueries["flightid"]){
				for(i = gEbBanners.length-1; i>-1; i--){			
					if(gEbBanners[i].adData.nFlightID == gEbQueries["flightid"]){
						gEbBanners[i].adData.customEventHandler = new ebCCustomEventHandlers();
						break;
					}
				}	
			}
			
		}
	}
}catch(e){}


var strMainPanelName = "SideKick"; // panel name in ACM
var nOpenAnimationLength = gEbQueries["nOpenAnimationLength"] ? gEbQueries["nOpenAnimationLength"] : 2000;
var nCloseAnimationLength = gEbQueries["nCloseAnimationLength"] ? gEbQueries["nCloseAnimationLength"] : 2000;


var SKParamsObj = new SKParams();

function SKParams()
{
	// this object holds all the "global" params
	this.originalScrollWidth = 0; // scroll width before expansion
	this.expandedScrollWidth = 0; // scroll width after expansion
	this.distanceToScroll 	 = 0; // expandedScrollWidth - originalScrollWidth
	this.currentStatus 		 = "Normal"; // tracker for current situation. Normal/Openeing/Open/Closing
	this.movementInterval 	 = null; // holds the animation interval ID
	this.targetFlashObjID 	 = null; // holds the panel SWF object ID
	this.gPanelObj 			 = null; // Panel 
	this.objTargetWin 		 = null; // ref to display window
	this.DU					 = null; // DU reference
	this.isStrictDocType	 = false;
	this.dtAnimationStart;
	this.initialBackgroundObj	= null;
	this._skinUsed              = false;
	this.autoCloseTimeout		= null;
	this.autoCloseTime			= gEbQueries["autoCloseTime"] ? gEbQueries["autoCloseTime"] : 0;
}

// easing function by Robert Penner
function easeInOutQuad(t, b, c, d)
{
	t = t/(d/2);
	if (t < 1) return c/2*t*t + b;
	t--;
	return -c/2 * (t*(t-2) - 1) + b;
}

// this function starts the close sequence and should be called from the panel close button using ebCommand.
// Example:
// fscommand("ebCommand", "customClosePanel()");
function customClosePanel()
{
	try
	{
		if(SKParamsObj.currentStatus != "Closing")
		{
			SKParamsObj.currentStatus = "Closing";
			SKParamsObj.distanceToScroll = SKParamsObj.expandedScrollWidth - SKParamsObj.originalScrollWidth;
			if(SKParamsObj.distanceToScroll > 0) // check if any scroll is neccesary
			{
				gEbDbg.info("OAD_EB_SideKick_ALL.js: Start close animation");
				clearInterval(SKParamsObj.movementInterval);
				SKParamsObj.dtAnimationStart = new Date();
				SKParamsObj.movementInterval = setInterval(doScrollLeft, 20);
			}
			else
			{
				SKParamsObj.DU.ebhideHandler(strMainPanelName);
				SKParamsObj.currentStatus = "Normal";
			}
		}
	}
	catch(e) {gEbDbg.error("Error in " + ebScriptFileName + ":customClosePanel(): " + e.description)}
}

// for backwards compatability
function _eb_customClosePanel()
{
	customClosePanel();
}

function startOpenSquence()
{
	try
	{
		if(SKParamsObj.currentStatus == "Normal")
		{
			SKParamsObj.currentStatus = "Opening";
			SKParamsObj.distanceToScroll = SKParamsObj.expandedScrollWidth - SKParamsObj.originalScrollWidth;
			if(SKParamsObj.distanceToScroll > 0) // check if any scroll is neccesary
			{
				gEbDbg.info(ebScriptFileName + ": Start open animation");
				clearInterval(SKParamsObj.movementInterval);
				SKParamsObj.dtAnimationStart = new Date();
				SKParamsObj.movementInterval = setInterval(doScrollRight, 20);
			}
			else
			{
				SKParamsObj.currentStatus = "Open";
				setTimeout(startPanelPlay, 200); // waiting for the flash panel to properly initialize, otherwise the ExternalInterface call fails.
			}

			if(!(gEbBC.isMac() && gEbBC.isFF()))
			{
				// FF on Mac doesn't recieve the mouseover event until the mouse enters the panel and then leaves it.
				skOnMouseOut();
			}
		}
	}
	catch(e) {gEbDbg.error("Error in " + ebScriptFileName + ":startOpenSquence(): " + e.description)}
}

// called every 20 milisconds to create the "opening" animation (vertical scroll to the right)
function doScrollRight()
{
	try
	{
		var currentTime = new Date();
		var timePassed = currentTime.getTime() - SKParamsObj.dtAnimationStart.getTime();
		var currentYScroll = 0;
		currentYScroll = (SKParamsObj.isStrictDocType && !gEbBC.isSafari()) ? SKParamsObj.objTargetWin.document.documentElement.scrollTop : SKParamsObj.objTargetWin.document.body.scrollTop;
		
		if(timePassed<nOpenAnimationLength)
		{
			var scrollAmount = easeInOutQuad(timePassed, 0, SKParamsObj.distanceToScroll, nOpenAnimationLength);
			SKParamsObj.objTargetWin.scrollTo(scrollAmount, currentYScroll);
		}
		else
		{
			clearInterval(SKParamsObj.movementInterval);
			SKParamsObj.objTargetWin.scrollTo(SKParamsObj.distanceToScroll, currentYScroll);
			SKParamsObj.currentStatus = "Open";
			gEbDbg.info(ebScriptFileName + ": open animation finished");
			startPanelPlay();
		}
	}
	catch(e) {gEbDbg.error("Error in " + ebScriptFileName + ":doScrollRight(): " + e.description)}
}

// called every 20 milisconds to create the "closing" animation (vertical scroll to the left)
function doScrollLeft()
{
	try
	{
		var currentTime = new Date();
		var timePassed = currentTime.getTime() - SKParamsObj.dtAnimationStart.getTime();
		var currentYScroll = 0;
		currentYScroll = (SKParamsObj.isStrictDocType && !gEbBC.isSafari()) ? SKParamsObj.objTargetWin.document.documentElement.scrollTop : SKParamsObj.objTargetWin.document.body.scrollTop;

		if(timePassed<nCloseAnimationLength)
		{
			var scrollAmount = easeInOutQuad(timePassed, 0, SKParamsObj.distanceToScroll, nCloseAnimationLength);
			SKParamsObj.objTargetWin.scrollTo(SKParamsObj.distanceToScroll-scrollAmount, currentYScroll);
		}
		else
		{
			clearInterval(SKParamsObj.movementInterval);
			SKParamsObj.DU.ebhideHandler(strMainPanelName);
			SKParamsObj.objTargetWin.scrollTo(0, currentYScroll);
			SKParamsObj.currentStatus = "Normal";
			resetSkin();
			gEbDbg.info(ebScriptFileName + ": close animation finished");
		}
	}
	catch(e) {gEbDbg.error("Error in " + ebScriptFileName + ":doScrollLeft(): " + e.description)}
}

// called after the "openeing" scroll has finished.
// it calls the "ebPageReady()" inside the panel SWF
function startPanelPlay()
{
	try
	{
		var panelSwf = getSWF(SKParamsObj.targetFlashObjID);
		gEbDbg.info(ebScriptFileName + ": calling ebPageReady() function inside panel '" + strMainPanelName + "'");
		panelSwf.ebPageReady();
	}
	catch(e) {gEbDbg.error("Error in " + ebScriptFileName + ":startPanelPlay(): " + e.description)}
}

//this function retrives the flash object in order to call a function inside the SWF using ExternalInterface
function getSWF(movieName)
{
	try
	{
		if (navigator.appName.indexOf("Microsoft") != -1)
		{
			return SKParamsObj.objTargetWin[movieName];
		}
		else
		{
			return SKParamsObj.objTargetWin.document[movieName];
		}
	}
	catch(e) {gEbDbg.error("Error in " + ebScriptFileName + ":getSWF(): " + e.description)}
}


function skOnMouseOut()
{
	try
	{
		if(SKParamsObj.autoCloseTime != 0)
		{
			clearTimeout(SKParamsObj.autoCloseTimeout);
			SKParamsObj.autoCloseTimeout = setTimeout("autoCloseSideKickPanel()", SKParamsObj.autoCloseTime);
		}
	}
	catch(e) {gEbDbg.error("Error in " + ebScriptFileName + ":skOnMouseOut(): " + e.description)}
}

function skOnMouseOver()
{
	clearTimeout(SKParamsObj.autoCloseTimeout);
}

function autoCloseSideKickPanel()
{
	try
	{
		if(SKParamsObj.currentStatus != "Closing")
		{
			gEbDbg.info(ebScriptFileName + ": auto closing '" + strMainPanelName + "' panel");
			clearInterval(SKParamsObj.movementInterval);
			SKParamsObj.DU.hidePanel(strMainPanelName, true);
			SKParamsObj.currentStatus = "Normal";
			resetSkin();
		}
	}
	catch(e) {gEbDbg.error("Error in " + ebScriptFileName + ":autoCloseSideKickPanel(): " + e.description)}
}

function getDocWidthHeight()
{
  var myWidth = 0, myHeight = 0;
  if( typeof( SKParamsObj.objTargetWin.innerWidth ) == 'number' ) {
    //Non-IE
    myWidth = SKParamsObj.objTargetWin.innerWidth;
    myHeight = SKParamsObj.objTargetWin.innerHeight;
  } else if( SKParamsObj.objTargetWin.document.documentElement && ( SKParamsObj.objTargetWin.document.documentElement.clientWidth || SKParamsObj.objTargetWin.document.documentElement.clientHeight ) ) {
    //IE 6+ in 'standards compliant mode'
    myWidth = SKParamsObj.objTargetWin.document.documentElement.clientWidth;
    myHeight = SKParamsObj.objTargetWin.document.documentElement.clientHeight;
  } else if( SKParamsObj.objTargetWin.document.body && ( SKParamsObj.objTargetWin.document.body.clientWidth || SKParamsObj.objTargetWin.document.body.clientHeight ) ) {
    //IE 4 compatible
    myWidth = SKParamsObj.objTargetWin.document.body.clientWidth;
    myHeight = SKParamsObj.objTargetWin.document.body.clientHeight;
  }
  return [myWidth, myHeight];
}

try{
gEbDbg.delimiter("================= Using '" + ebScriptFileName + "' Custom Script =====================");
}catch(e){}

function ebCCustomEventHandlers()
{
	this.onClientScriptsLoaded = function(objName) {}

	this.onBeforeAddRes = function(objName) {}

	this.onHandleInteraction = function(objName, intName, strObjID)	{}
	this.onBeforeDefaultBannerShow = function(objName) {}

	this.onAfterDefaultBannerShow = function(objName)
	{
		try
		{
			SKParamsObj.initialBackgroundObj = new ebCBackgroundEx(gEbDisplayPage.TI.getDoc());
			// fix for www.orange.es (CAS-16127-LLT5ZB)
			// in IE6, the eyeDiv needs a change in some attribute in order to show
			// i'm changing the eyediv's z-index to +1
			if(gEbBC.isIE() && gEbBC.getVersion()==6)
			{
			    try
			    {
			        gEbDisplayPage.TI.getDoc().getElementById("eyeDiv").style.zIndex += 1;
			    }
			    catch(e) {gEbDbg.error("Error in " + ebScriptFileName + ":onBeforePanelShow():Fix for www.orange.es: " + e.description)}
			}			
		}
		catch(e) {gEbDbg.error("Error in " + ebScriptFileName + ":onAfterDefaultBannerShow(): " + e.description)}
	}

	this.onBeforeRichFlashShow = function(objName) {}
	this.onAfterRichFlashShow = function(objName) {}
	
	this.onBeforePanelShow = function(objName, panelName)
	{
		
		try
		{
		    // the following script should only act when the calling panel name is the one defined in strMainPanelName
		    if(panelName.toLowerCase()!=strMainPanelName.toLowerCase()) return;
			
			
			// retrive current "scroll" properties (before a vertical scroll is added to the page) and save them in the params object
			var DU = eval(objName);
			SKParamsObj.objTargetWin = gEbDisplayPage.TI.getWin();
			
			
			var clientArea = new ebCClientArea(gEbDisplayPage.TI);
			clientArea.calc();
			SKParamsObj.isStrictDocType = clientArea.fStrictDocType;
			if(gEbBC.isIE())
			{
				SKParamsObj.originalScrollWidth = clientArea.container.scrollWidth;
			}
			else
			{
				if(clientArea.fStrictDocType == true)
				{
					// changed by Tatyana Smirnov 25/08/2010 (CAS-27786-ZXHXTM)
					// documentElement.scrollWidth replaced with documentElement.clientWidth
					// should fix FireFox scrolling problem starting from the second expansion
					SKParamsObj.originalScrollWidth = SKParamsObj.objTargetWin.document.documentElement.clientWidth;
				}
				else
				{
					SKParamsObj.originalScrollWidth = SKParamsObj.objTargetWin.document.body.clientWidth;
				}
			}
			
			// Added by Guy Meiri on 10.20.09 (CAS-20206-9ZHVWB)
			// Should fix cases where the browser already have an initial scroll before the SideKick panel is expanded.
			if(gEbBC.isIE())
			{
				SKParamsObj.originalScrollWidth = SKParamsObj.originalScrollWidth - (Math.abs(SKParamsObj.objTargetWin.document.documentElement.scrollWidth - getDocWidthHeight()[0]));
			}
			else
			{
				SKParamsObj.originalScrollWidth = SKParamsObj.originalScrollWidth - (Math.abs(SKParamsObj.objTargetWin.document.body.scrollWidth - getDocWidthHeight()[0]));
			}
		}
		catch(e) {gEbDbg.error("Error in " + ebScriptFileName + ":onBeforePanelShow(): " + e.description)}
		
	}

	this.onAfterPanelShow = function(objName, panelName)
	{
		try
		{
		    // the following script should only act when the calling panel name is the one defined in strMainPanelName
		    if(panelName.toLowerCase()!=strMainPanelName.toLowerCase()) return;
			
			// retrive current "scroll" properties (after a vertical scroll is added to the page) and save them in the params object
			var DU = eval(objName);
			SKParamsObj.DU = DU;
			if(panelName.toLowerCase()==strMainPanelName.toLowerCase())
			{
				var panelObj = DU.ad.panels[panelName.toLowerCase()];
				SKParamsObj.gPanelObj = panelObj;
				SKParamsObj.targetFlashObjID = panelObj.flashObj.id;
			}
			
			gEbTI.addEventHandler("mouseout","skOnMouseOut", SKParamsObj.gPanelObj.panelDiv);
			gEbTI.addEventHandler("mouseover","skOnMouseOver", SKParamsObj.gPanelObj.panelDiv);

			var clientArea = new ebCClientArea(gEbDisplayPage.TI);
			clientArea.calc();
			SKParamsObj.isStrictDocType = clientArea.fStrictDocType;
			
			if(gEbBC.isIE())
			{
				SKParamsObj.expandedScrollWidth = clientArea.container.scrollWidth;
			}
			else
			{
				SKParamsObj.expandedScrollWidth = (SKParamsObj.objTargetWin.document.body.scrollWidth > SKParamsObj.objTargetWin.document.documentElement.scrollWidth) ? SKParamsObj.objTargetWin.document.body.scrollWidth : SKParamsObj.objTargetWin.document.documentElement.scrollWidth;
			}
			
			startOpenSquence();
		}
		catch(e) {gEbDbg.error("Error in " + ebScriptFileName + ":onAfterPanelShow(): " + e.description)}
	}
	
	this.onBeforePanelHide = function(objName, panelName) {}

	this.onAfterPanelHide = function(objName, panelName)
	{
		gEbTI.removeEventHandler("mouseout","skOnMouseOut", SKParamsObj.gPanelObj.panelDiv);
		gEbTI.removeEventHandler("mouseover","skOnMouseOver", SKParamsObj.gPanelObj.panelDiv);
		SKParamsObj.currentStatus = "Normal";
		clearInterval(SKParamsObj.movementInterval);
	}

	this.onBeforeAdClose = function(objName) {}
	this.onAfterAdClose = function(objName) {}
	this.onBeforeIntroShow = function(objName) {}
	this.onAfterIntroShow = function(objName) {}
	this.onBeforeIntroHide = function(objName) {}
	this.onAfterIntroHide = function(objName) {}
	this.onBeforeRemShow = function(objName) {}
	this.onAfterRemShow = function(objName) {}
	this.onBeforeRemHide = function(objName) {}
	this.onAfterRemHide = function(objName) {}
	this.onBeforeMiniSiteShow = function(objName) {}
	this.onAfterMiniSiteShow = function(objName) {}
	this.onBeforeMiniSiteHide = function(objName) {}
	this.onAfterMiniSiteHide = function(objName) {}
}

// support for site "skin".
// added by Guy Meiri on 3/24/09

function setSkin(strBgImgSrc, strColor, strBgRepeat, fScrollWithPage)
{
	var skinEnabled = true;
	// If not FF3 then set background-attachment to "scroll"
	try
	{
		if(gEbBC.isFF() && gEbBC.getVersion() < 3)
		{
			
			if(SKParamsObj.initialBackgroundObj.strAttachment != "scroll")
			{
				skinEnabled = false;
			}
			else
			{
				skinEnabled = true;
				fScrollWithPage = "scroll";
			}
		}
	}
	catch(e) {}
	
	if(skinEnabled)
	{
		 SKParamsObj._skinUsed = true;
		try
		{
			var strBg = "";
		    strBg += strColor;
			if (strBgImgSrc != "")
			{
				strBg += " url('" + strBgImgSrc + "') ";
			}
			else
			{
				strBg += " none ";
			}
			strBg += strBgRepeat;
		    strBg += " " + fScrollWithPage;
			strBg += " 0 0";
			gEbDisplayPage.TI.getDoc().body.style.background = strBg;
		}
		catch(e) {}
	}
}

function resetSkin()
{
    if(SKParamsObj._skinUsed)
    {
		try
		{
		    var docBody = gEbDisplayPage.TI.getDoc().body;
		    if (SKParamsObj.initialBackgroundObj.fOldStyle == true)
		    {
			    docBody.backgroundImage = SKParamsObj.initialBackgroundObj.strImgSrc;
			    docBody.style.backgroundImage = "";
		    }
		    else
			{
			    docBody.style.backgroundImage = SKParamsObj.initialBackgroundObj.strImgSrc;
			}
			
		    docBody.style.backgroundColor = SKParamsObj.initialBackgroundObj.strColor;

		    if (SKParamsObj.initialBackgroundObj.strImgSrc != "")
		    {
			    docBody.style.backgroundRepeat = SKParamsObj.initialBackgroundObj.strRepeat;
			    docBody.style.backgroundAttachment = SKParamsObj.initialBackgroundObj.strAttachment;
			    docBody.style.backgroundPosition = SKParamsObj.initialBackgroundObj.strPosition;
		    }
		}
		catch(e) { }
    }
}

// Class to hold all initial page background properties
function ebCBackgroundEx(doc)
{
	this.fOldStyle = true;
	this.strColor = "";
	this.strImgSrc = "";
	this.strRepeat = "";
	this.strAttachment = "";
	this.strPosition = "";
	
	var docBody = doc.body;
		
	if(gEbBC.isIE())
	{
		try
		{
			if(docBody.currentStyle.backgroundImage != "")
			{
				this.fOldStyle = false;
				this.strImgSrc = docBody.currentStyle.backgroundImage;
			}
			else
			{
				if (docBody.background != "")
				{
					this.fOldStyle = true;
					this.strImgSrc = docBody.background;
				}
			}
			
			if (docBody.currentStyle.backgroundImage != "")
			{
				this.fOldStyle = false;
				this.strImgSrc = docBody.currentStyle.backgroundImage;
			}
			else
				if (docBody.background != "")
				{
					this.fOldStyle = true;
					this.strImgSrc = docBody.background;
				}
			
			if (docBody.bgColor != "")
				this.strColor = docBody.bgColor;
			if (docBody.currentStyle.backgroundColor != "")
				this.strColor = docBody.currentStyle.backgroundColor;
				
			if (docBody.currentStyle.backgroundRepeat != "")
				this.strRepeat = docBody.currentStyle.backgroundRepeat;
				
			if (docBody.currentStyle.backgroundAttachment != "")
				this.strAttachment = docBody.currentStyle.backgroundAttachment;
				
			if (docBody.currentStyle.backgroundPosition != "")
				this.strPosition = docBody.currentStyle.backgroundPositionX + " " + docBody.currentStyle.backgroundPositionY;
		}
		catch(e){gEbDbg.error("Error in " + ebScriptFileName + ":ebCBackgroundEx(), IE:" + e.description)}
	}
	else
	{
		try
		{
			if (doc.defaultView.getComputedStyle(docBody, null).backgroundImage != "")
			{
				this.fOldStyle = false;
				this.strImgSrc = doc.defaultView.getComputedStyle(docBody, null).backgroundImage;
			}
			else
			{
				if (docBody.background != "")
				{
					this.fOldStyle = true;
					this.strImgSrc = docBody.background;
				}
			}
			
			if (doc.defaultView.getComputedStyle(docBody, null).bgColor != "")
				this.strColor = doc.defaultView.getComputedStyle(docBody, null).bgColor;
				
			if (doc.defaultView.getComputedStyle(docBody, null).backgroundColor != "")
				this.strColor = doc.defaultView.getComputedStyle(docBody, null).backgroundColor;
				
			if (doc.defaultView.getComputedStyle(docBody, null).backgroundRepeat != "")
				this.strRepeat = doc.defaultView.getComputedStyle(docBody, null).backgroundRepeat;
				
			if (doc.defaultView.getComputedStyle(docBody, null).backgroundAttachment != "")
				this.strAttachment = doc.defaultView.getComputedStyle(docBody, null).backgroundAttachment;

			if (doc.defaultView.getComputedStyle(docBody, null).backgroundPosition != "")
				this.strPosition = doc.defaultView.getComputedStyle(docBody, null).backgroundPosition;
		}
		catch(e) {gEbDbg.error("Error in " + ebScriptFileName + ":ebCBackgroundEx(), Not IE:" + e.description)}
	}
}
