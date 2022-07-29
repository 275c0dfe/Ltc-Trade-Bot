function setCookie(cname, cvalue, exdays) {
    const d = new Date();
    d.setTime(d.getTime() + (exdays * 24 * 60 * 60 * 1000));
    let expires = "expires="+d.toUTCString();
    document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/";
    }

    function getCookie(cname) {
    let name = cname + "=";
    let ca = document.cookie.split(';');
    for(let i = 0; i < ca.length; i++) {
        let c = ca[i];
        while (c.charAt(0) == ' ') {
        c = c.substring(1);
        }
        if (c.indexOf(name) == 0) {
        return c.substring(name.length, c.length);
        }
    }
    return "";
    }  

function updateTicker(){ 
  $.get("/scripts/getData.py?getTicker=true" , function(data){
        $("#Ticker").text("Ltc Price: " + data);
    });
}

function updateHistory(){
    $.get("/scripts/getData.py?getHistory=true" , function(data){
        
        var elements = data.split(/\n/);
        
        var container = $(".history_container")
        var selem = "";
        for(var i=0;i<elements.length; i++){
            if (elements[i] != ""){
            selem += "<li class='history_element'>" + elements[i] + "</li>";
            }
        }
        
        container.html(selem);
    });
}

function updateBalance(){
    $.get("/scripts/getData.py?getBalance=true" , function(data){
        var elements = data.split(/,/);
        var ltc = elements[0];
        var usd = elements[1];
        $("#ltc_balance").text("Ltc: " + ltc);
        $("#usd_balance").text("Usd: " + usd);
    });
}



var bot_values = {"enable_bot":false , "buy_input":"50" , "sell_input":"50" , "buy_margin":"0.01" , "sell_margin":"0.015"}
var value_is_modified = false;
var value_name = "";

function modifyBotValue(name , value){
    $.get("/scripts/setData" + name + "=" + value);
}

function revertValue(name){

    $( "#" + name).val(bot_values[name]);
    var rs = $("#" + name);
    var container = rs.parent().children();
    
    for (var i = 0;i<2; i++){
        rs.parent().children().last().remove();
    }

    
    
    value_name = "";
    value_is_modified = false;
}

function onDocumentLoad(){

    function modified_text(event){
        console.log(event);
        value_name = event.srcElement.id;
        var container = $(event.path[1]);
        
        if (container.children().length < 4){
        $("<a onclick='modifyBotValue(\"" + value_name + "\" , " + event.srcElement.value + ")' class='button'>Save " + event.srcElement.value + "</a> <a onclick='revertValue(\"" + value_name +"\")' class='button'>Revert</a>").insertAfter("#" + value_name);
        
        }
        else{
            sv = container.children()[2]
            $(sv).text("Save " + event.srcElement.value);
        }
        value_is_modified = true;
    }

    var controls = ["buy_input" , "sell_input" , "buy_margin" , "sell_margin"];

    for(var i =0; i<controls.length;i++){
        control = controls[i];
        console.log(control)
        var crl = document.getElementById(control);
        console.log(crl)
        crl.addEventListener("keyup" , modified_text);
    }
}
function updateBotValues(){
    $.get("/scripts/getData.py?getBotInfo=true" , function(data){
        var elements = data.split(/,/);
        var enab = elements[0];
        var buy_price = elements[1];
        var sell_price = elements[2];
        var buy_margin = elements[3];
        var sell_margin = elements[4];
        if(value_is_modified){
            
            if(value_name != "enable_bot"){
                if(enab == "True"){
                    $("#enable_bot").prop("checked" , true);
                }
                else{
                    $("#enable_bot").prop("checked" , false);
                }
            }
        

        
            if(value_name != "buy_input"){
                $("#buy_input").val(buy_price);
            }
        
        
            if(value_name != "sell_input"){
                $("#sell_input").val(sell_price);
            }
        
        
            if(value_name != "buy_margin"){
                $("#buy_margin").val(buy_margin);
            }
        
        
            if(value_name != "sell_margin"){
                $("#sell_margin").val(sell_margin);
            }
        }
        else{
            if(enab == "True"){
                $("#enable_bot").prop("checked" , true);
            }
            else{
                $("#enable_bot").prop("checked" , false);
            }
            $("#buy_input").val(buy_price);
            $("#sell_input").val(sell_price);
            $("#buy_margin").val(buy_margin);
            $("#sell_margin").val(sell_margin);
        }
        
        bot_values.enable = enab;
        bot_values.buy_input = buy_price;
        bot_values.sell_input = sell_price;
        bot_values.buy_margin = buy_margin;
        bot_values.sell_margin = sell_margin;
    });
}




function updateApp(){
    sid = getCookie("Session_Id");
    if(sid == ""){
        document.location.replace("/web/login.html")
    }
    updateTicker();
    updateBalance();
    updateHistory();
    updateBotValues();
}

function shutdownApp(){
    $.get("/shutdown.py");
    alert("App Offline");
}

function shutdownPrompt(){
    let res = prompt("You are about to shutdown the app are you sure you would like to continue?(yes/no)")
    if(res == "yes"){
        shutdownApp();
    }
}

updateApp();
setInterval(updateApp , 3000);
setTimeout(onDocumentLoad , 1000);