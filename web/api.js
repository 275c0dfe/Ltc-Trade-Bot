  
 function updateTicker(){ 
  $.get("/getData.py?getTicker=true" , function(data){
        $("#Ticker").text("Ltc Price: " + data);
    });
}

setInterval(updateTicker , 3000)
