function execJS(strExec, objScript) {
    var bSaf = (navigator.userAgent.indexOf('Safari') != -1);
    var bOpera = (navigator.userAgent.indexOf('Opera') != -1);
    var bMoz = (navigator.appName == 'Netscape');
    try {
        if (bSaf) {
            objScript.text = strExec;
        } else if (bOpera) {
            objScript.text = strExec;
        } else if (bMoz) {
            objScript.textContent = strExec;
        } else {
            objScript.text = strExec;
        }
    } catch (e) {}
};
try {
    for (j = 0; j < nsjxSetups.length; j++) {
        var objNSJX = eval('nsjx' + nsjxSetups[j]);
        if (objNSJX != null) {
            for (i = 0; i < objNSJX.adUnits.length; i++) {
                var objCreative = eval('objNSJX.ad' + objNSJX.adUnits[i]);
                var container = document.getElementById('ad' + objNSJX.adUnits[i]);
                if ((objCreative.crtype != null) && (container != null)) {
                    switch (objCreative.crtype) {
                    case "image":
                        {
                            var ac = document.createElement('a');
                            ac.href = objNSJX.clpath + "?msid=" + objCreative.msid + "&cid=" + objCreative.cid + "&slotid=" + objCreative.slotid;
                            ac.target = "_blank";
                            var img = document.createElement('img');
                            img.src = objNSJX.crpath + "photo/" + objCreative.msid + ".cms";
                            img.width = objCreative.width;
                            img.height = objCreative.height;
                            img.border = "0"
                            container.appendChild(ac);
                            ac.appendChild(img);
                            break;
                        }
                    case "flash":
                        {
                            var NS_fMsid = objNSJX.crpath + 'photo/' + objCreative.msid + '.cms'
                            var NS_URL = objNSJX.clpath + "%3Fmsid=" + objCreative.msid + "%26cid=" + objCreative.cid + "%26slotid=" + objCreative.slotid;
                            var limStr = '<DIV ID="divObj" NAME="divObj" STYLE="z-index:1000">';
                            limStr += '<OBJECT CLASSID="clsid:D27CDB6E-AE6D-11cf-96B8-444553540000" WIDTH="' + objCreative.width + '" HEIGHT="' + objCreative.height + '" CODEBASE="http://download.macromedia.com/pub/shockwave/cabs/flash/swflash.cab" ID="obConst">';
                            limStr += '<PARAM NAME="MOVIE" VALUE="' + NS_fMsid + '">';
                            limStr += '<PARAM NAME="ID" VALUE="obConst">';
                            limStr += '<PARAM NAME="wmode" VALUE="transparent">';
                            limStr += '<PARAM NAME="QUALITY" VALUE="high">';
                            limStr += '<PARAM NAME="SCALE" VALUE="SHOWALL">';
                            limStr += '<param name="allowScriptAccess" value="always">';
                            limStr += '<PARAM NAME="flashVars" VALUE="clickTag=' + NS_URL + '">';
                            limStr += '<EMBED NAME="obConst" SRC="' + NS_fMsid + '" WIDTH="' + objCreative.width + '" HEIGHT="' + objCreative.height + '" QUALITY="high" SCALE="SHOWALL" allowScriptAccess="always" swLiveConnect="true" ';
                            limStr += 'PLUGINSPAGE="http://www.macromedia.com/shockwave/download/index.cgi?P1_Prod_Version=ShockwaveFlash" ';
                            limStr += 'wmode="transparent" ';
                            limStr += 'type="application/x-shockwave-flash" ';
                            limStr += 'flashVars="clickTag=' + NS_URL + '">';
                            limStr += ' </EMBED></OBJECT></DIV>';
                            container.insertAdjacentHTML('beforeEnd', limStr);

                            function chngURL() {
                                try {
                                    NS_URL = unescape(NS_URL);
                                    if (window.obConst) {
                                        window.document["obConst"].SetVariable("clickTag", NS_URL);
                                    }
                                    if (document.obConst) {
                                        document.obConst.SetVariable("clickTag", NS_URL);
                                    }
                                } catch (e) {}
                            }
                            if (navigator.userAgent.indexOf("Chrome") != -1) {
                                setTimeout("chngURL()", 100);
                            }
                            break;
                        }
                    case "html":
                        {
                            objCreative.crtext();
                            container.innerHTML = document.getElementById('rsHidden' + objCreative.slotid).innerHTML;
                            document.getElementById('rsHidden' + objCreative.slotid).innerHTML = "";
                            break;
                        }
                    }
                }
            }
        }
    }
} catch (e) {}