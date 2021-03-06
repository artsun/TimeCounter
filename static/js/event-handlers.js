

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
    pButt.innerHTML = (pButt.value === "0") ? "<b>Пауза</b>" : "<b>Продолжить</b>";
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
        let inChange = document.getElementById('btnChg');
        if (inChange.value === "1") {
            return
        }
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

    setTimeout(function (){showTime(now, max, h, m, s, 0);}, 1000)
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
    width = (now >= max) ? 0 : width;
    width = (width > 100) ? 100 : width;
    let bar = document.getElementById("bar");
    bar.setAttribute("aria-valuenow", now);
    bar.setAttribute("aria-valuemax", max);
    bar.setAttribute("style", `width: ${width}%`);
    bar.innerHTML = `<b>${Math.round(width)}%</b>`;
}

window.hasDayStarted = function hasDayStarted () {
        resp = fetch(`/setday?started=1`).then(res => res.json()).then(res => (res['started'] === 1) ? execStart() : execStop());
    };

function execStart (){ showTime(); doHide(1); }

function execStop () { showRange(); doHide(0); }

function showRange(val=null) {
    val = (val===null) ? document.getElementById('begind').value : val;
    document.getElementById("MyClockDisplay").innerText = `${val} час.`;
    //doHide()
}

window.updateRange = function updateRange (val){
        document.getElementById('begind').value=val;
        document.getElementById('begindStore').value=val;
        document.getElementById('changedStore').value=val;
        showRange(val);
};

function doHide (started){
    tdStyle(started);
    if (started === 1) {
        document.getElementById('rowBegind').style = "display: none;";
        document.getElementById('rowRange').style = "display: none;";
        document.getElementById('rowControl').style = "";
    } else {
        document.getElementById('rowBegind').style = "";
        document.getElementById('rowRange').style = "";
        document.getElementById('rowControl').style = "display: none;";
    }
}

window.clickChange = function clickChange () {
    document.getElementById('rowBegind').style = "display: none;";
    document.getElementById('rowRange').style = "";
    document.getElementById('rowChanged').style = "";
    document.getElementById('rowControl').style = "display: none;";
    document.getElementById('btnChg').value = "1";
    let val = document.getElementById('changedStore');
    document.getElementById("MyClockDisplay").innerText = `${val.value} час.`;
};

// метки для выполненных дней
window.daysDone = function daysDone () {
        let els = document.getElementsByClassName('vanilla-calendar-date vanilla-calendar-date--active');
        for (let el of els) {
            d = new Date(el.getAttribute('data-calendar-date'));
            if (d.getDay() === 1) {
                el.style = "background: #00D1B2;";
            }
        }
    };

    function tdStyle (active) {
        td = document.getElementsByClassName('vanilla-calendar-date vanilla-calendar-date--active vanilla-calendar-date--today');
        if (active === 1) {
            td[0].setAttribute("style", "background: #5bc0de;");
        } else {
            td[0].setAttribute("style", "");
        }
    }



