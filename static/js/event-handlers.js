

window.sendSelDate = async function sendSelDate(data, elem) {
	selected_date = new Date(data['date']);
    window.location.replace(`?day=${selected_date.getDate()}&month=${selected_date.getMonth()+1}&year=${selected_date.getFullYear()}`);
};

window.setTime = function (h, m, s){
    h_d = (h < 10) ? "0" + h : h;
    m_d = (m < 10) ? "0" + m : m;
    s_d = (s < 10) ? "0" + s : s;

    return h_d + ":" + m_d + ":" + s_d
};

window.refreshBreaks = function(){
    document.getElementById("Breaks").innerHTML ='';
    fetch(`/refreshbreaks?do=true`).then(response => response.json()).then(res => {for (let br of res['breaks']) document.getElementById("Breaks").innerHTML += `<td>${br}</td><br>`});
};


window.setPauseLabel = function(){
    let pButt = document.getElementById("paused");
    pButt.innerText = (pButt.value === "0") ? "Пауза" : "Продолжить";
};

window.calcShowTime = function calcShowTime(h, m, s){
        if (s > 0){
            s -= 1;
        } else {
            if (m>0){
                m -= 1;
                s = 59;
            } else {
                m = (h>0) ? 59 : 0;
                s = (m>0) ? 59 : 0;
                h = (h>0) ? h-1: h;
            }
        }
        return {hour: h, minute: m, second:  s}
    };

window.showTime = async function showTime(now=0, max=100, h=0, m=0, s=0, was_started=1){
    if (was_started===1){
            let response = await fetch(`/refreshtimer?do=true`);
            let resp = await response.json();
            now = resp['now'];
            max = resp['max'];
            h = resp['getHours'];
            m = resp['getMinutes'];
            s = resp['getSeconds'];
            console.log(resp);
            was_started = 0;
        }
        let is_pause = document.getElementById("paused");
    if (is_pause.value ==="0"){
        let calculated = calcShowTime(h, m, s);
        h = calculated.hour;
        m = calculated.minute;
        s = calculated.second;
        now -= 1;
    }
    let width = 100 - (now / (max / 100));
    barSet(now, max, width);

    let time = setTime(h, m, s);

    document.getElementById("MyClockDisplay").innerText = time;
    document.getElementById("MyClockDisplay").textContent = time;

    setTimeout(function (){showTime(now, max, h, m, s, 0);}, 1000);

};

window.checkFinished = function checkFinished(){
       let finishd = document.getElementById("finishd");
       return (finishd.value === "True" || ("{{today != None}}" !== "True")) ? 1: 0;
    };

window.clickPause = function clickPause(v) {
        if (checkFinished()==="True"){
            return
        }
    let pButt = document.getElementById("paused");
    pButt.value = (v === "1") ? "0" : "1";
    setPauseLabel();
    fetch(`/setday?paused=1`).then(res => refreshBreaks());
};

function barSet(now, max, width){
    let bar = document.getElementById("bar");
    bar.setAttribute("aria-valuenow", now);
    bar.setAttribute("aria-valuemax", max);
    bar.setAttribute("style", `width: ${width}%`);
    bar.innerHTML = `<b>${Math.round(width)}%</b>`;
}

window.barOnloadSetter = function barOnloadSetter() {
    let start = document.getElementById("start");
    let fin = document.getElementById("fin");
    if (start === null || fin === null){
        barSet(0, 100, 0);
        return
    }
    start = start.getAttribute("value");
    fin = fin.getAttribute("value");
    let complete = start / (fin / 100);
    barSet(start, fin, complete);
};
