function setProgress(lelem,p)
{
  var progbar=$($(lelem).children()[1]).children()[0]
  var pr=parseInt(p)
  progbar.value=pr
  if(pr==100)
  {
    var tickdiv=$($(lelem).children()[1]).children()[1]
    $(tickdiv).addClass('tick inline')
  }
}

function addLog(l){}
$(function(){
  $("#file_list").children().each(function(index,elem){
    if($(elem).children()[1].innerHTML.length>0)
    {
      var shortfilename=$(elem).children()[0].innerHTML
      var ws=new WebSocket("ws://"+location.host+"/wperf/pcap_progress/"+shortfilename)
      ws.onopen=function(evt){
        }
      ws.onclose=function(evt){ }
      ws.onmessage=function(evt){
        var j=JSON.parse(evt.data)
        setProgress(elem,j.prog)
        addLog(j.Log)
        }
      ws.onerror=function(evt){ }
    }
    });
  
  })
