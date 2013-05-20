try
{
if (NS_fObType=='0')
{
  var PDId = eval('parent.document.all.' + NS_fPDId);
  var PFId = eval('parent.document.all.' + NS_fPFId);
  var POId = eval('parent.' + NS_fObId);
  var limStr;
  var  limStr = '<DIV ID="' + NS_fDId + '" ' ;
  if (NS_fPosition='1')
    {
     limStr += 'STYLE="position:absolute; left:'+ NS_fLeft + 'px; top:'+ NS_fTop + 'px; ';
    }
  limStr += 'visibility:visible;">';
  limStr += '<OBJECT CLASSID="clsid:D27CDB6E-AE6D-11cf-96B8-444553540000" WIDTH="' + NS_fWidth + 'px" HEIGHT="' + NS_fHeight + '"px CODEBASE="http://download.macromedia.com/pub/shockwave/cabs/flash/swflash.cab" ID="' + NS_fObId + '"><PARAM NAME="MOVIE" VALUE="http://adscontent.indiatimes.com/photo.cms?photoID='+NS_fPId+'"><PARAM NAME="ID" VALUE="' + NS_fObId + '"><PARAM NAME="wmode" VALUE="Transparent"><PARAM NAME="QUALITY" VALUE="high"><PARAM NAME="SCALE" VALUE="SHOWALL"><EMBED NAME="' + NS_fObId + '" SRC="http://adscontent.indiatimes.com/photo.cms?photoID='+NS_fPId+'" WIDTH="' + NS_fWidth + '" HEIGHT="' + NS_fHeight + '" PLAY="false" LOOP="false" QUALITY="high" SCALE="SHOWALL"	swLiveConnect="true" PLUGINSPAGE="http://www.macromedia.com/go/flashplayer/" wmode="transparent"></EMBED></OBJECT></DIV>';
    function mkhtm(){try{if (document.all){if (PDId==null ) setTimeout('mkhtm()',1000);else{PFId.height=0;PFId.width=0;PDId.outerHTML = limStr;parent.document.getElementById(vOId).setVariable("MSID",vPId);parent.document.getElementById(vOId).setVariable("SLOTID",vSId);parent.document.getElementById(NS_fObId).setVariable("CID",NS_fCId);}}else if (document.getElementById){if (parent.document.getElementById(NS_fPDId) ==null )	setTimeout('mkhtm()',1000);else{parent.document.getElementById(NS_fPFId).height=0;parent.document.getElementById(NS_fPFId).width=0;parent.document.getElementById(NS_fPDId).innerHTML = limStr;parent.document.getElementById(NS_fObId).setVariable("MSID",NS_fPId);parent.document.getElementById(NS_fObId).setVariable("SLOTID",NS_fSId);parent.document.getElementById(NS_fOId).setVariable("CID",NS_fCId);	}	}}catch(er){setTimeout('mkhtm()',1000)}	}setTimeout('mkhtm()',1000);
}
else
{
	try
	{ 
  	  var POId;
		//var POId = eval('parent.' + NS_fObId); 
		if (NS_fObId==null ) 
		  {
			POId='obConst';
		  }
		else
		  {
			POId = NS_fObId;
		  }
	}
	catch(er)
	{
		POId='obConst';
	}
  var limStr = '<DIV ID="divObj" NAME="divObj" STYLE="z-index:1000">';
  limStr += '<OBJECT CLASSID="clsid:D27CDB6E-AE6D-11cf-96B8-444553540000" WIDTH="' + NS_fWidth + '" HEIGHT="' + NS_fHeight + '" CODEBASE="http://download.macromedia.com/pub/shockwave/cabs/flash/swflash.cab" ID="' + POId + '">';
  limStr += '<PARAM NAME="MOVIE" VALUE="' + NS_fMsid + '">';
  limStr += '<PARAM NAME="ID" VALUE="'+ POId +'">';
  limStr += '<PARAM NAME="wmode" VALUE="transparent">';
  limStr += '<PARAM NAME="QUALITY" VALUE="high">';
  limStr += '<PARAM NAME="SCALE" VALUE="SHOWALL">';
  limStr += '<param name="allowScriptAccess" value="always">';
  limStr += '<PARAM NAME="flashVars" VALUE="clickTag='+NS_URL+'">';
  limStr += '<EMBED NAME="' + POId + '" SRC="' + NS_fMsid + '" WIDTH="' + NS_fWidth + '" HEIGHT="' + NS_fHeight + '" QUALITY="high" SCALE="SHOWALL" allowScriptAccess="always" swLiveConnect="true" ';
  limStr += 'PLUGINSPAGE="http://www.macromedia.com/shockwave/download/index.cgi?P1_Prod_Version=ShockwaveFlash" ';
  limStr += 'wmode="transparent" ';
  limStr += 'type="application/x-shockwave-flash" ';
  limStr += 'flashVars="clickTag='+NS_URL+'">';
  limStr += ' </EMBED></OBJECT></DIV>';
  document.write(limStr);
  function chngURL()
  {
	NS_URL=unescape(NS_URL);	
	if(window.obConst){window.document["obConst"].SetVariable("clickTag", NS_URL);}
	if(document.obConst){document.obConst.SetVariable("clickTag", NS_URL);}
  }
  if(navigator.userAgent.indexOf("Chrome") != -1)
  {
	setTimeout("chngURL()",100);
  }
}
}
catch (ex)
{}